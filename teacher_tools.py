"""
teacher_tools.py — Εργαλεία Βοηθού Εκπαιδευτικού & Χάρτης Παρανοήσεων
για τον «Σωκράτη AI Tutor Γυμνασίου».

Περιλαμβάνει:
1. Χάρτη Παρανοήσεων Μαθητών (Misconceptions Heatmap) με Dual Persistence (SQLite WAL + JSON).
2. Αυτοαξιολόγηση Σωκρατικής Ποιότητας (4-Point Socratic Turn Evaluator).
3. Παραγωγή 45λεπτης Παρουσιάσης & Διαγράμματος για τον Διαδραστικό Πίνακα.
4. Εξαγωγή εκτυπώσιμων αρχείων Word (.docx) για την τάξη (Worksheets & Tests).
5. Κοινή ροή streaming AI για τα εργαλεία καθηγητή με προστασία Rate-Limit.
"""

import os
import io
import re
import json
import time
import datetime
import tempfile
import html as html_lib
from typing import Dict, List, Optional, Any, Tuple

# pyrefly: ignore [missing-import]
try:
    import streamlit as st
except ImportError:
    st = None

from security_engine import normalize_text, ends_with_question, is_student_real_attempt
from session_store import db_save_misconception, db_load_misconceptions
from gemini_resilience import call_gemini_with_retry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WRITABLE_DATA_DIR = tempfile.gettempdir()
MISCONCEPTIONS_LOG_PATH = os.path.join(WRITABLE_DATA_DIR, "socrates_misconceptions_log.json")

# -------------------------------------------------------------
# 1. Χάρτης Παρανοήσεων Μαθητών (Αποθήκευση, Ομαδοποίηση & Συγχώνευση)
# -------------------------------------------------------------
def _normalize_topic_key(topic: str) -> str:
    norm = normalize_text(topic or "")
    norm = re.sub(r'[^\w\s]', ' ', norm)
    stop_words = {"ο", "η", "το", "οι", "τα", "του", "της", "των", "στο", "στη", "στην", "στα", "στις", "σε"}
    tokens = [w for w in norm.split() if w and w not in stop_words]
    return " ".join(tokens) if tokens else norm.strip()

def merge_misconceptions_records(existing: list, incoming: list):
    """Ενώνει στατιστικά από πολλές συσκευές/τάμπλετ χωρίς διπλοεγγραφές."""
    seen = set()
    merged = []
    for r in existing:
        if not isinstance(r, dict) or not r.get("topic"):
            continue
        key = r.get("uid") or f"{r.get('timestamp','')}|{r.get('grade','')}|{r.get('subject','')}|{_normalize_topic_key(r.get('topic',''))}|{r.get('example','')}"
        if key not in seen:
            seen.add(key)
            merged.append(r)
    added = 0
    for r in incoming:
        if not isinstance(r, dict) or not r.get("topic"):
            continue
        key = r.get("uid") or f"{r.get('timestamp','')}|{r.get('grade','')}|{r.get('subject','')}|{_normalize_topic_key(r.get('topic',''))}|{r.get('example','')}"
        if key not in seen:
            seen.add(key)
            merged.append(r)
            added += 1
    return merged, added

def load_misconceptions_log() -> list:
    """Φορτώνει όλες τις καταγεγραμμένες παρανοήσεις συνδυάζοντας SQLite WAL και τοπικό αρχείο JSON."""
    # 1. Φόρτωση από μόνιμη SQLite WAL
    db_records = db_load_misconceptions()

    # 2. Φόρτωση από τοπικό αρχείο JSON (αν υπάρχει)
    file_records = []
    if os.path.exists(MISCONCEPTIONS_LOG_PATH):
        try:
            with open(MISCONCEPTIONS_LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    file_records = data
        except Exception:
            pass

    # 3. Απρόσκοπτη συγχώνευση χωρίς διπλότυπα
    merged, _ = merge_misconceptions_records(db_records, file_records)
    return merged

def save_misconceptions_log(records: list):
    """Αποθηκεύει τις παρανοήσεις σε JSON και διασφαλίζει εγγραφή στην SQLite WAL."""
    try:
        with open(MISCONCEPTIONS_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    # Διασφάλιση ότι κάθε εγγραφή υπάρχει στην SQLite
    for r in records:
        if isinstance(r, dict) and r.get("topic"):
            db_save_misconception(r)

def record_misconception(grade: str, subject: str, topic: str, example: str, status: str = "CAUGHT"):
    """Καταγράφει ανώνυμα (GDPR) μία παρανόηση μαθητή στον Χάρτη Παρανοήσεων (Dual Persistence)."""
    clean_topic = (topic or "").strip()[:60]
    if not clean_topic or clean_topic.upper() in ("NONE", "N/A"):
        return None
    clean_example = (example or "").strip()[:140]
    now = datetime.datetime.now()
    rec = {
        "uid": f"{now.strftime('%Y%m%d%H%M%S%f')}_{abs(hash((grade, subject, clean_topic, clean_example))) % 100000}",
        "date": now.strftime("%Y-%m-%d"),
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "grade": grade,
        "subject": subject,
        "topic": clean_topic,
        "example": clean_example,
        "status": status,
    }
    # 1. Άμεση αποθήκευση στην SQLite WAL
    db_save_misconception(rec)

    # 2. Ενημέρωση και στο αρχείο JSON
    records = load_misconceptions_log()
    records.append(rec)
    save_misconceptions_log(records)
    return rec

def aggregate_misconceptions(records: list, grade_filter: str = "Όλες", subject_filter: str = "Όλα", period_filter: str = "Όλο το διάστημα") -> list:
    """Φιλτράρει, ομαδοποιεί και ταξινομεί τις παρανοήσεις από τη συχνότερη προς τη σπανιότερη."""
    cutoff_date = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    grouped = {}
    for r in records:
        if not isinstance(r, dict) or not r.get("topic"):
            continue
        if grade_filter != "Όλες" and r.get("grade") != grade_filter:
            continue
        if subject_filter != "Όλα" and r.get("subject") != subject_filter:
            continue
        if period_filter == "Αυτή την εβδομάδα" and str(r.get("date", "")) < cutoff_date:
            continue
        t_key = _normalize_topic_key(r.get("topic", ""))
        if not t_key:
            continue
        if t_key not in grouped:
            grouped[t_key] = {
                "key": t_key,
                "label": r.get("topic", "").strip(),
                "count": 0,
                "examples": {},
                "subjects": set(),
                "grades": set(),
            }
        grouped[t_key]["count"] += 1
        if r.get("subject"):
            grouped[t_key]["subjects"].add(r["subject"])
        if r.get("grade"):
            grouped[t_key]["grades"].add(r["grade"])
        ex = (r.get("example") or "").strip()
        if ex:
            grouped[t_key]["examples"][ex] = grouped[t_key]["examples"].get(ex, 0) + 1

    result = []
    for item in grouped.values():
        sorted_ex = sorted(item["examples"].items(), key=lambda x: x[1], reverse=True)[:3]
        result.append({
            "key": item["key"],
            "label": item["label"],
            "count": item["count"],
            "top_examples": sorted_ex,
            "subjects": sorted(list(item["subjects"])),
            "grades": sorted(list(item["grades"])),
        })
    result.sort(key=lambda x: x["count"], reverse=True)
    return result

def format_misconceptions_markdown(records: list) -> str:
    """Δημιουργεί σύνοψη του Χάρτη Παρανοήσεων για την αναφορά του Καθηγητή (.md)."""
    agg = aggregate_misconceptions(records)
    if not agg:
        return ""
    lines = [
        "\n---\n",
        "## 🗺️ Χάρτης Παρανοήσεων Τάξης (Σύνοψη)",
        f"- **Συνολικές Καταγεγραμμένες Παρανοήσεις:** {len(records)} περιστατικά",
        "",
    ]
    for idx, item in enumerate(agg[:8], 1):
        subj_str = ", ".join(item["subjects"][:2])
        ex_str = f" *(π.χ. «{item['top_examples'][0][0]}»)*" if item["top_examples"] else ""
        lines.append(f"{idx}. **{item['label']}** ({subj_str}): **{item['count']} φορές**{ex_str}")
    return "\n".join(lines) + "\n"

# -------------------------------------------------------------
# 2. Κρυφός Μηχανισμός Αυτοαξιολόγησης Σωκρατικής Ποιότητας
# -------------------------------------------------------------
def evaluate_socratic_turn(
    student_prompt: str,
    final_response: str,
    gave_solution: bool,
    misconception_status: str,
    support_level: str,
    prev_consec_explanations: int,
    rewritten: bool = False,
):
    """Υπολογίζει τη Σωκρατική βαθμολογία (0-100%) βάσει των 4 κριτηρίων."""
    score = 100

    # Κριτήριο 1: Έδωσε έτοιμη λύση (-50 + επανεγγραφή)
    pen_solution = 50 if gave_solution else 0
    score -= pen_solution

    # Κριτήριο 2: Έθεσε ερώτηση στο τέλος (-25 αν όχι)
    has_q = ends_with_question(final_response)
    pen_question = 0 if has_q else 25
    score -= pen_question

    # Κριτήριο 3: Συνεχόμενες εξηγήσεις χωρίς προσπάθεια μαθητή (Επίπεδο 1: έως 4, Επίπεδα 2-3: έως 3)
    max_allowed = 4 if support_level == "LEVEL_1" else 3
    if is_student_real_attempt(student_prompt):
        new_consec = 0
    else:
        new_consec = prev_consec_explanations + 1
    extra_expl = max(0, new_consec - max_allowed)
    pen_consec = 15 * extra_expl
    score -= pen_consec

    # Κριτήριο 4: Εντοπισμός & διόρθωση παρανόησης (+5 έως 100%, -18 αν αγνοήθηκε)
    if misconception_status == "CAUGHT":
        delta_misc = 5
    elif misconception_status == "IGNORED":
        delta_misc = -18
    else:
        delta_misc = 0
    score += delta_misc

    final_score = max(0, min(100, score))
    record = {
        "score": final_score,
        "gave_solution": gave_solution,
        "rewritten": rewritten,
        "pen_solution": pen_solution,
        "ended_with_question": has_q,
        "pen_question": pen_question,
        "consecutive_explanations": new_consec,
        "max_explanations": max_allowed,
        "pen_consec": pen_consec,
        "misconception_status": misconception_status,
        "delta_misc": delta_misc,
        "support_level": support_level,
    }
    return record, new_consec

def format_socratic_audit_markdown(audits: list) -> str:
    """Δημιουργεί καθαρή έκθεση Σωκρατικής Ποιότητας (μόνο για Καθηγητή & εξαγωγή σημειώσεων)."""
    if not audits:
        return ""
    avg_score = round(sum(a["score"] for a in audits) / len(audits))
    rewrites = sum(1 for a in audits if a.get("rewritten"))
    q_ok = sum(1 for a in audits if a.get("ended_with_question"))
    consec_pen = sum(1 for a in audits if a.get("pen_consec", 0) > 0)
    misc_caught = sum(1 for a in audits if a.get("misconception_status") == "CAUGHT")
    misc_ignored = sum(1 for a in audits if a.get("misconception_status") == "IGNORED")

    lines = [
        "\n---\n",
        f"## 🏛️ Κρυφή Αυτοαξιολόγηση Σωκρατικής Ποιότητας (Για τον Εκπαιδευτικό)",
        f"- **Συνολική Σωκρατική Ποιότητα Διαλόγου:** **{avg_score}%** *(σε {len(audits)} απαντήσεις)*",
        f"- **1. Έλεγχος Έτοιμης Λύσης:** {rewrites} αυτόματες επανεγγραφές *(αποτροπή έτοιμης λύσης)*",
        f"- **2. Καθοδηγητική Ερώτηση στο Τέλος:** {q_ok}/{len(audits)} απαντήσεις έκλεισαν με ερώτηση",
        f"- **3. Συνεχόμενες Εξηγήσεις χωρίς Προσπάθεια:** {consec_pen} γύροι ξεπέρασαν το όριο",
        f"- **4. Παρανοήσεις Μαθητή:** {misc_caught} εντοπίστηκαν & διορθώθηκαν (+5%), {misc_ignored} αγνοήθηκαν (-18%)",
        "",
        "### Αναλυτικά ανά απάντηση:",
    ]
    for idx, a in enumerate(audits, 1):
        sol_txt = "ΝΑΙ (-50, ξαναγράφτηκε)" if a["gave_solution"] else "ΟΧΙ (OK)"
        q_txt = "ΝΑΙ (OK)" if a["ended_with_question"] else "ΟΧΙ (-25)"
        c_txt = f"{a['consecutive_explanations']}/{a['max_explanations']}" + (f" (-{a['pen_consec']})" if a["pen_consec"] else " (OK)")
        m_map = {"CAUGHT": "Εντοπίστηκε (+5)", "IGNORED": "Αγνοήθηκε (-18)", "NONE": "Καμία (0)"}
        m_txt = m_map.get(a["misconception_status"], "Καμία (0)")
        lines.append(
            f"- **Απάντηση #{idx} — {a['score']}%** | Λύση: {sol_txt} | Ερώτηση: {q_txt} | Εξηγήσεις: {c_txt} | Παρανόηση: {m_txt}"
        )
    return "\n".join(lines) + "\n"

# -------------------------------------------------------------
# 3. Παραγωγή 45λεπτης Παρουσίασης & Εξαγωγή DOCX
# -------------------------------------------------------------
def generate_45min_lesson_json(
    grade: str,
    subject: str,
    topic: str,
    book_topics: str,
    extra_notes: str = "",
    client = None,
    api_key: str = ""
):
    """Παράγει δομημένη 45λεπτη παρουσίαση σε καθαρό JSON με rate-limit resilience."""
    import app
    if client is None:
        key = api_key or app.load_saved_key()
        client = app.get_genai_client(key)

    active_m = "gemini-3.5-flash-lite"
    if st is not None and "active_model" in st.session_state:
        active_m = st.session_state.active_model
    ordered_models = list(dict.fromkeys([active_m, "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash"]))

    prompt_json = f"""
Είσαι έμπειρος εκπαιδευτικός Γυμνασίου στην Ελλάδα. Ετοίμασε μια ολοκληρωμένη 45λεπτη διδασκαλία σε στυλ σύνοψης για προβολή στον διαδραστικό πίνακα.

ΣΤΟΙΧΕΙΑ:
- Τάξη: {grade}
- Μάθημα: {subject}
- Επίσημη ύλη: {book_topics}
- Θέμα / Κεφάλαιο της ώρας: {topic}
{f'- Επιπλέον οδηγίες καθηγητή: {extra_notes}' if extra_notes.strip() else ''}

ΕΠΕΣΤΡΕΨΕ ΑΠΟΚΛΕΙΣΤΙΚΑ ΕΓΚΥΡΟ JSON (χωρίς κανένα επιπλέον κείμενο γύρω του) με ΑΚΡΙΒΩΣ αυτή τη δομή:
{{
  "title": "Καθαρός τίτλος μαθήματος",
  "hook_question": "Μία έξυπνη, προκλητική σωκρατική ερώτηση αφόρμησης για την τάξη",
  "hook_context": "Σύντομη εισαγωγή 2 προτάσεων που συνδέει το θέμα με τη ζωή των μαθητών",
  "key_cards": [
    {{"icon": "🏛️", "term": "Έννοια-Κλειδί 1", "desc": "Καθαρή, απλή επεξήγηση 1-2 σύντομων προτάσεων"}},
    {{"icon": "📜", "term": "Έννοια-Κλειδί 2", "desc": "Καθαρή, απλή επεξήγηση 1-2 σύντομων προτάσεων"}},
    {{"icon": "⚖️", "term": "Έννοια-Κλειδί 3", "desc": "Καθαρή, απλή επεξήγηση 1-2 σύντομων προτάσεων"}},
    {{"icon": "🌟", "term": "Έννοια-Κλειδί 4", "desc": "Καθαρή, απλή επεξήγηση 1-2 σύντομων προτάσεων"}}
  ],
  "diagram": {{
    "type": "flow",
    "center": "Κεντρικός Άξονας Μαθήματος (3-6 λέξεις)",
    "nodes": [
      {{"step": "1", "label": "Τίτλος 1ου σταδίου/κλάδου", "detail": "Σύντομη φράση 5-10 λέξεων"}},
      {{"step": "2", "label": "Τίτλος 2ου σταδίου/κλάδου", "detail": "Σύντομη φράση 5-10 λέξεων"}},
      {{"step": "3", "label": "Τίτλος 3ου σταδίου/κλάδου", "detail": "Σύντομη φράση 5-10 λέξεων"}},
      {{"step": "4", "label": "Τίτλος 4ου σταδίου/κλάδου", "detail": "Σύντομη φράση 5-10 λέξεων"}}
    ]
  }},
  "discussion_questions": [
    "Ερώτηση κριτικής σκέψης 1 για την ολομέλεια",
    "Ερώτηση κριτικής σκέψης 2 (σύγκριση ή δίλημμα)",
    "Σύντομη ομαδική δραστηριότητα 5-10 λεπτών στην τάξη"
  ],
  "summary_points": [
    "Βασικό συμπέρασμα 1 που πρέπει να θυμούνται οι μαθητές",
    "Βασικό συμπέρασμα 2",
    "Βασικό συμπέρασμα 3"
  ],
  "mini_quiz": [
    {{"q": "Ερώτηση γρήγορου ελέγχου 1", "a": "Σαφής σύντομη απάντηση 1"}},
    {{"q": "Ερώτηση γρήγορου ελέγχου 2", "a": "Σαφής σύντομη απάντηση 2"}},
    {{"q": "Ερώτηση γρήγορου ελέγχου 3", "a": "Σαφής σύντομη απάντηση 3"}}
  ]
}}
"""
    t0 = time.time()
    for m_name in ordered_models:
        for try_no_think in (True, False):
            try:
                cfg = app.build_fast_config(
                    m_name,
                    disable_thinking=try_no_think,
                    temperature=0.5,
                    max_output_tokens=1800,
                    response_mime_type="application/json",
                )
                resp = call_gemini_with_retry(
                    client.models.generate_content,
                    model=m_name,
                    contents=prompt_json,
                    config=cfg,
                )
                raw = (resp.text or "").strip()
                raw = re.sub(r'^```(?:json)?\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)
                parsed = json.loads(raw)
                if isinstance(parsed, dict) and parsed.get("title") and parsed.get("key_cards"):
                    return parsed, m_name, (time.time() - t0)
            except Exception as err:
                err_txt = str(err).lower()
                if try_no_think and ("thinking" in err_txt or "invalid_argument" in err_txt or "400" in err_txt):
                    continue
                break
    return None, "", (time.time() - t0)

def render_lesson_diagram_html(diagram_data: dict) -> str:
    """Δημιουργεί καθαρό οπτικό διάγραμμα (εννοιολογικό χάρτη / ροή) για τον διαδραστικό πίνακα."""
    center = html_lib.escape(str(diagram_data.get("center", "Κεντρική Έννοια")))
    nodes = diagram_data.get("nodes", [])[:4]
    palette = [
        ("#eff6ff", "#2563eb", "#1e3a8a"),
        ("#ecfdf5", "#059669", "#065f46"),
        ("#fffbeb", "#d97706", "#78350f"),
        ("#faf5ff", "#7c3aed", "#4c1d95"),
    ]
    cards_html = []
    for idx, n in enumerate(nodes):
        bg, brd, txt = palette[idx % len(palette)]
        step = html_lib.escape(str(n.get("step", idx + 1)))
        lbl = html_lib.escape(str(n.get("label", "")))
        det = html_lib.escape(str(n.get("detail", "")))
        cards_html.append(
            f'<div style="background:{bg}; border:2px solid {brd}; border-radius:14px; padding:14px 16px; box-shadow:0 3px 10px rgba(15,23,42,0.06);">'
            f'  <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">'
            f'    <span style="background:{brd}; color:#fff; width:26px; height:26px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:800; font-size:0.85rem; flex-shrink:0;">{step}</span>'
            f'    <span style="font-weight:800; color:{txt}; font-size:1.02rem; line-height:1.25;">{lbl}</span>'
            f'  </div>'
            f'  <div style="color:#334155; font-size:0.93rem; line-height:1.4;">{det}</div>'
            f'</div>'
        )

    return (
        f'<div style="background:#ffffff; border:2px solid #bfdbfe; border-radius:16px; padding:20px; margin:8px 0;">'
        f'  <div style="text-align:center; margin-bottom:14px;">'
        f'    <div style="display:inline-block; background:linear-gradient(135deg,#1d4ed8,#0c335e); color:#ffffff; padding:10px 24px; border-radius:999px; font-weight:800; font-size:1.12rem; box-shadow:0 4px 12px rgba(29,78,216,0.25);">🗺️ {center}</div>'
        f'  </div>'
        f'  <div style="text-align:center; color:#2563eb; font-size:1.25rem; font-weight:800; margin-bottom:12px;">⬇️ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ⬇️</div>'
        f'  <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px;">'
        f'    {"".join(cards_html)}'
        f'  </div>'
        f'</div>'
    )

def lesson_json_to_markdown(data: dict) -> str:
    """Μετατρέπει την 45λεπτη παρουσίαση σε καθαρό Markdown για εξαγωγή σε Word (.docx)."""
    lines = [
        f"## 1. ΑΦΟΡΜΗΣΗ (5')",
        f"- **Κεντρική Ερώτηση:** {data.get('hook_question', '')}",
        f"- {data.get('hook_context', '')}",
        "",
        f"## 2. ΕΝΝΟΙΕΣ-ΚΛΕΙΔΙΑ (15')",
    ]
    for c in data.get("key_cards", []):
        lines.append(f"- **{c.get('term', '')}:** {c.get('desc', '')}")
    diag = data.get("diagram", {})
    lines.append("")
    lines.append(f"## 3. ΟΠΤΙΚΟ ΔΙΑΓΡΑΜΜΑ / ΔΟΜΗ (10') — {diag.get('center', '')}")
    for n in diag.get("nodes", []):
        lines.append(f"- **Βήμα {n.get('step', '')} — {n.get('label', '')}:** {n.get('detail', '')}")
    lines.append("")
    lines.append("## 4. ΕΡΩΤΗΣΕΙΣ ΣΥΖΗΤΗΣΗΣ & ΔΡΑΣΤΗΡΙΟΤΗΤΑ (10')")
    for q in data.get("discussion_questions", []):
        lines.append(f"- {q}")
    lines.append("")
    lines.append("## 5. ΣΥΝΟΨΗ «ΤΙ ΚΡΑΤΑΜΕ» (5')")
    for s in data.get("summary_points", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## ΕΝΔΕΙΚΤΙΚΕΣ ΑΠΑΝΤΗΣΕΙΣ (ΜΙΝΙ-ΚΟΥΙΖ)")
    for i, item in enumerate(data.get("mini_quiz", []), 1):
        lines.append(f"- **Ερώτηση {i}:** {item.get('q', '')} — *Απάντηση:* {item.get('a', '')}")
    return "\n".join(lines)

def build_school_docx(
    title: str,
    subtitle: str,
    markdown_body: str,
    include_student_header: bool = True,
    split_solutions_page: bool = False,
):
    """Δημιουργεί καθαρό, εκτυπώσιμο αρχείο Word (.docx) στη μνήμη για χρήση στην τάξη."""
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except Exception:
        return None

    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(1.8)
        section.bottom_margin = Cm(1.8)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # Επικεφαλίδα σχολείου
    p_school = doc.add_paragraph()
    p_school.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_school.paragraph_format.space_after = Pt(2)
    r_school = p_school.add_run("Γυμνάσιο Πρίνου Θάσου  •  Σωκράτης AI Tutor")
    r_school.font.size = Pt(9.5)
    r_school.font.bold = True
    r_school.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Κύριος τίτλος
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run(title)
    r_title.font.size = Pt(15)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0C, 0x33, 0x5E)

    # Υπότιτλος (Τάξη / Μάθημα / Ημερομηνία)
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(10)
    r_sub = p_sub.add_run(subtitle)
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # Πεδίο στοιχείων μαθητή (για φωτοτυπία)
    if include_student_header:
        p_st = doc.add_paragraph()
        p_st.paragraph_format.space_before = Pt(4)
        p_st.paragraph_format.space_after = Pt(10)
        r_st = p_st.add_run("Ονοματεπώνυμο: _____________________________   Τμήμα: ______   Ημερομηνία: ____________")
        r_st.font.size = Pt(10.5)
        r_st.font.bold = True

    def _add_formatted_runs(paragraph, text_line: str):
        clean_line = re.sub(r'[\U00010000-\U0010ffff\u2600-\u27bf\ufe0f]', '', text_line)
        parts = re.split(r'(\*\*[^*]+\*\*)', clean_line)
        for part in parts:
            if not part:
                continue
            if part.startswith("**") and part.endswith("**") and len(part) > 4:
                run = paragraph.add_run(part[2:-2])
                run.bold = True
            else:
                paragraph.add_run(part.replace("*", "").replace("`", ""))

    solutions_page_broken = False
    for raw_line in markdown_body.splitlines():
        line = raw_line.strip()
        if not line or line in ("---", "***", "___"):
            continue

        if split_solutions_page and not solutions_page_broken:
            up = line.upper()
            if any(k in up for k in ["ΕΝΔΕΙΚΤΙΚΕΣ ΑΠΑΝΤΗΣΕΙΣ", "ΑΠΑΝΤΗΣΕΙΣ & ΛΥΣΕΙΣ", "ΛΥΣΕΙΣ:", "ΚΡΙΤΗΡΙΑ ΑΞΙΟΛΟΓΗΣΗΣ"]):
                doc.add_page_break()
                solutions_page_broken = True

        if line.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(re.sub(r'[\U00010000-\U0010ffff\u2600-\u27bf\ufe0f*]', '', line[4:]).strip())
            r.bold = True
            r.font.size = Pt(12)
            r.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)
        elif line.startswith("## ") or line.startswith("# "):
            heading_txt = line.lstrip("#").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(re.sub(r'[\U00010000-\U0010ffff\u2600-\u27bf\ufe0f*]', '', heading_txt).strip())
            r.bold = True
            r.font.size = Pt(13)
            r.font.color.rgb = RGBColor(0x0C, 0x33, 0x5E)
        elif line.startswith("- ") or line.startswith("* ") or line.startswith("• "):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(3)
            _add_formatted_runs(p, line[2:].strip())
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            _add_formatted_runs(p, line)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

def run_teacher_ai_stream(prompt_text: str, stream_container, max_tokens: int = 1600):
    """Κοινή γρήγορη ροή παραγωγής AI για όλα τα εργαλεία του Καθηγητή με rate-limit resilience."""
    import app
    key = app.load_saved_key()
    client = app.get_genai_client(key)

    active_m = "gemini-3.5-flash-lite"
    if st is not None and "active_model" in st.session_state:
        active_m = st.session_state.active_model
    ordered_models = list(dict.fromkeys([active_m, "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash"]))

    t_start = time.time()
    for m_name in ordered_models:
        for try_no_think in (True, False):
            try:
                cfg = app.build_fast_config(
                    m_name,
                    disable_thinking=try_no_think,
                    temperature=0.65,
                    max_output_tokens=max_tokens,
                )
                resp_stream = call_gemini_with_retry(
                    client.models.generate_content_stream,
                    model=m_name,
                    contents=prompt_text,
                    config=cfg,
                )
                full_text = ""
                last_flush = time.time()
                for chunk in resp_stream:
                    if chunk.text:
                        full_text += chunk.text
                        now_t = time.time()
                        if now_t - last_flush >= 0.03:
                            stream_container.markdown(full_text + "▌")
                            last_flush = now_t
                if full_text.strip():
                    stream_container.markdown(full_text)
                    return full_text.strip(), m_name, (time.time() - t_start)
            except Exception as err:
                err_txt = str(err).lower()
                if try_no_think and ("thinking" in err_txt or "invalid_argument" in err_txt or "400" in err_txt):
                    continue
                break
    return "", "", (time.time() - t_start)
