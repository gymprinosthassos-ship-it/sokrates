"""
games_engine.py — Μηχανισμός Παιχνιδιών, Κουίζ & Μονομαχίας 2 Παικτών
για τον «Σωκράτη AI Tutor Γυμνασίου».

Περιλαμβάνει:
1. Πολιτική ξεκλειδώματος παιχνιδιών (Teacher Policy: Study Goal 3/3, Unlocked All, Disabled).
2. Υπολογισμό ξεκλειδώματος ανάλογα με το Επίπεδο Υποστήριξης (Ειδική Αγωγή vs Τυπικό).
3. Μετρητή Συνολικής Επίδοσης Προσπάθειας Συνεδρίας (0–100).
4. Αυτόματη παραγωγή ερωτήσεων Μονομαχίας 2 Παικτών & Μίνι-Παιχνιδιών (AI JSON με Rate-Limit Resilience).
5. Δίκαιη αξιολόγηση ελεύθερης απάντησης μαθητή (Judge Free Answer).
6. Ζωντανές Εποπτικές Κάρτες-Σχεδιαγράμματα (Live Visual Cards).
"""

import os
import re
import json
import time
import tempfile
import html as html_lib
from typing import Dict, List, Optional, Any, Tuple

# pyrefly: ignore [missing-import]
try:
    import streamlit as st
except ImportError:
    st = None

from security_engine import normalize_text
from gemini_resilience import call_gemini_with_retry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WRITABLE_DATA_DIR = tempfile.gettempdir()
DUEL_SETTINGS_PATH = os.path.join(WRITABLE_DATA_DIR, "socrates_duel_settings.json")

# -------------------------------------------------------------
# 1. Κοινή Μνήμη Τάξης & Πολιτική Εκπαιδευτικού
# -------------------------------------------------------------
def _get_st_cache_resource():
    if st is not None:
        return st.cache_resource(show_spinner=False)
    return lambda fn: fn

@_get_st_cache_resource()
def get_shared_classroom_store() -> dict:
    """Κοινή μνήμη τάξης στον διακομιστή: σε κάθε νέο άνοιγμα ξεκινά ΚΛΕΙΔΩΜΕΝΟ (study_goal 0/3)."""
    return {"duel_policy": "study_goal", "unlocked_all_ts": 0.0}

def load_duel_policy() -> str:
    """Επιστρέφει τη ρύθμιση Καθηγητή: 'study_goal' (προεπιλογή κλειδωμένο) | 'unlocked_all' | 'disabled'."""
    store = get_shared_classroom_store()
    pol = store.get("duel_policy", "study_goal")
    if pol == "unlocked_all":
        ts = float(store.get("unlocked_all_ts", 0.0) or 0.0)
        if ts > 0 and (time.time() - ts) > 45 * 60:
            store["duel_policy"] = "study_goal"
            store["unlocked_all_ts"] = 0.0
            return "study_goal"
    return pol if pol in ("study_goal", "unlocked_all", "disabled") else "study_goal"

def save_duel_policy(policy: str):
    """Αποθηκεύει τη ρύθμιση εκπαιδευτικού για τα παιχνίδια."""
    if policy not in ("study_goal", "unlocked_all", "disabled"):
        policy = "study_goal"
    store = get_shared_classroom_store()
    store["duel_policy"] = policy
    store["unlocked_all_ts"] = time.time() if policy == "unlocked_all" else 0.0
    try:
        with open(DUEL_SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump({"policy": policy}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_effort_points(delta: int) -> int:
    """Ενημερώνει τον μετρητή συνολικής επίδοσης/προσπάθειας (0–100) μόνο για την τρέχουσα συνεδρία."""
    if st is None:
        return 0
    cur = int(st.session_state.get("effort_score", 0))
    new_val = max(0, min(100, cur + int(delta)))
    st.session_state.effort_score = new_val
    return new_val

def render_effort_score_banner():
    """Εμφανίζει ένα μικρό απαλό πράσινο τετράγωνο πάνω δεξιά μόνο με το '0/100' της συνεδρίας."""
    if st is None:
        return
    score = max(0, min(100, int(st.session_state.get("effort_score", 0))))
    st.markdown(f"""
    <div title="Συνολική επίδοση προσπάθειας συνεδρίας (μηδενίζει με το κλείσιμο)" style="
        position: fixed;
        top: 14px;
        right: 28px;
        z-index: 99990;
        width: 72px;
        height: 58px;
        background-color: #dcfce7;
        border: 2px solid #4ade80;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #14532d;
        font-size: 1.0rem;
        font-weight: 900;
        letter-spacing: -0.3px;
        box-shadow: 0 4px 12px rgba(22, 101, 52, 0.16);
        user-select: none;
    ">
        {score}/100
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Κανόνες Ξεκλειδώματος Παιχνιδιών (Unlock Rules)
# -------------------------------------------------------------
def compute_duel_unlock_status(
    policy: str,
    support_level: str,
    study_steps: int,
    confirmed_correct: int,
    warning_penalty: int,
    has_active_warning: bool,
) -> dict:
    """Υπολογίζει αν είναι ξεκλείδωτη η Μονομαχία 2 Παικτών βάσει πολιτικής Καθηγητή & προόδου μαθητή."""
    if policy == "disabled":
        return {
            "unlocked": False,
            "disabled_by_teacher": True,
            "progress": 0,
            "target": 3,
            "label": "🔒 Παιχνίδια & Κουίζ (Κλειστό)",
            "help": "Η ενότητα «Παιχνίδια & Κουίζ» είναι απενεργοποιημένη από τον εκπαιδευτικό.",
        }
    if policy == "unlocked_all":
        return {
            "unlocked": True,
            "disabled_by_teacher": False,
            "progress": 3,
            "target": 3,
            "label": "🎮 Παιχνίδια & Κουίζ",
            "help": "Ξεκλείδωτο για όλη την τάξη από τον εκπαιδευτικό!",
        }

    # Προεπιλογή: 'study_goal'
    base_target = 2 if support_level == "LEVEL_1" else 3
    target = base_target + max(0, warning_penalty)
    progress = min(target, max(0, study_steps))

    if support_level == "LEVEL_1":
        unlocked = (study_steps >= target) and (not has_active_warning)
    else:
        unlocked = (study_steps >= target) and (confirmed_correct >= 1) and (not has_active_warning)

    if unlocked:
        return {
            "unlocked": True,
            "disabled_by_teacher": False,
            "progress": target,
            "target": target,
            "label": f"🎮 Παιχνίδια & Κουίζ (🔑 {target}/{target})",
            "help": "Μπράβο! Ξεκλείδωσες 1 συνεδρία στην ενότητα «Παιχνίδια & Κουίζ»!",
        }

    reason_hint = (
        f"Κάνε {target} ουσιαστικές προσπάθειες στο μάθημα"
        + (" (και τουλάχιστον 1 σωστό βήμα)" if support_level != "LEVEL_1" else "")
        + " για να ξεκλειδώσεις 1 συνεδρία στα Παιχνίδια & Κουίζ!"
    )
    return {
        "unlocked": False,
        "disabled_by_teacher": False,
        "progress": progress,
        "target": target,
        "label": f"🔒 Παιχνίδια & Κουίζ (🔑 {progress} / {target})",
        "help": reason_hint,
    }

def question_references_choices(question_text: str) -> bool:
    """Εντοπίζει αν η διατύπωση μιας ερώτησης αναφέρεται σε επιλογές ('παρακάτω', 'επόμενα' κ.λπ.)."""
    norm_q = normalize_text(question_text or "")
    patterns = [
        r"\bπαρακατω\b",
        r"\bεπομεν[αοηω]\w*\b",
        r"\bεπιλογ\w*\b",
        r"\bαπο τα παραπανω\b",
        r"\bαπο τις παραπανω\b",
        r"\bποιο απο τα\b",
        r"\bποια απο τις\b",
        r"\bποιος απο τους\b",
    ]
    return any(re.search(p, norm_q) for p in patterns)

def choices_match(chosen_text: str, correct_text: str) -> bool:
    """Ασφαλής σύγκριση επιλεγμένου κουμπιού με τη σωστή επιλογή (αγνοεί προθέματα 'Α)', '1.' κ.λπ.)."""
    def _strip_prefix(s: str) -> str:
        t = normalize_text(str(s or "")).strip()
        t = re.sub(r'^(?:[αβγδα-δ1-4]\s*[\)\.\-:]\s*)', '', t).strip()
        return t
    c1 = _strip_prefix(chosen_text)
    c2 = _strip_prefix(correct_text)
    if not c1 or not c2:
        return False
    return c1 == c2 or (len(c2) >= 4 and c2 in c1) or (len(c1) >= 4 and c1 in c2)

# -------------------------------------------------------------
# 3. Παραγωγή Ερωτήσεων AI με Προστασία Rate-Limit
# -------------------------------------------------------------
def generate_duel_questions_json(
    grade: str,
    subject: str,
    book_topics: str,
    support_level: str,
    chapter_focus: str = "",
    client = None,
    api_key: str = ""
):
    """Παράγει και τις 6 ερωτήσεις της Μονομαχίας σε ΜΙΑ (1) κλήση AI με rate-limit resilience."""
    import app
    if client is None:
        key = api_key or app.load_saved_key()
        client = app.get_genai_client(key)

    active_m = "gemini-3.5-flash-lite"
    if st is not None and "active_model" in st.session_state:
        active_m = st.session_state.active_model

    ordered_models = [active_m, "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash"]
    ordered_models = list(dict.fromkeys(ordered_models))

    lvl_instr = (
        "ΠΟΛΥ ΑΠΛΕΣ, σύντομες προτάσεις (4-8 λέξεις), κατάλληλες για Επίπεδο 1 / Ειδική Αγωγή, χωρίς παγίδες."
        if support_level == "LEVEL_1"
        else ("Απλή, καθαρή διατύπωση για Γυμνάσιο (Επίπεδο 2)." if support_level == "LEVEL_2" else "Ερωτήσεις κατανόησης & κριτικής σκέψης επιπέδου Γυμνασίου.")
    )
    open_q_rule = (
        ""
        if support_level == "LEVEL_1"
        else "- ΑΥΣΤΗΡΟΣ ΚΑΝΟΝΑΣ: Οι ερωτήσεις πρέπει να είναι ΑΝΟΙΧΤΕΣ (χωρίς να προϋποθέτουν ότι ο μαθητής βλέπει επιλογές). ΑΠΑΓΟΡΕΥΕΤΑΙ να γράφεις «Ποια από τις παρακάτω...», «Ποιο από τα επόμενα...» ή παρόμοιες φράσεις!"
    )

    duel_prompt = f"""
Είσαι ο Σωκράτης, εκπαιδευτικός Γυμνασίου στην Ελλάδα.
Ετοίμασε ΑΚΡΙΒΩΣ 6 σύντομες, διασκεδαστικές και παιδαγωγικές ερωτήσεις για μια «Μονομαχία 2 Παικτών» (3 γύροι ανά παίκτη).

ΣΤΟΙΧΕΙΑ:
- Τάξη: {grade}
- Μάθημα: {subject}
- Επίσημη ύλη: {book_topics}
{f'- Ειδικό κεφάλαιο/θέμα: {chapter_focus}' if chapter_focus.strip() else ''}
- Επίπεδο δυσκολίας: {lvl_instr}
{open_q_rule}

ΕΠΕΣΤΡΕΨΕ ΑΠΟΚΛΕΙΣΤΙΚΑ ΕΓΚΥΡΟ JSON (χωρίς κανένα επιπλέον κείμενο) με λίστα 6 αντικειμένων:
{{
  "questions": [
    {{
      "q": "Σύντομη, ξεκάθαρη, αυτοτελής ερώτηση (ΠΟΤΕ 'ποια από τις παρακάτω')",
      "choices": ["Επιλογή Α", "Επιλογή Β", "Επιλογή Γ"],
      "correct_choice": "Επιλογή Α",
      "expected_answer": "Σύντομη σωστή απάντηση (1 πρόταση)",
      "hint": "Ένα μικρό σωκρατικό στοιχείο για 2η ευκαιρία (ΧΩΡΙΣ να δίνει την έτοιμη απάντηση!)",
      "topic": "Σύντομη κατηγορία 2-3 λέξεων (π.χ. Δυνάμεις, Περσικοί Πόλεμοι)"
    }}
  ]
}}
Βεβαιώσου ότι το correct_choice ταιριάζει ΑΚΡΙΒΩΣ με μία από τις 3 choices και ότι υπάρχουν ακριβώς 6 ερωτήσεις.
"""
    for m_name in ordered_models:
        for try_no_think in (True, False):
            try:
                cfg = app.build_fast_config(
                    m_name,
                    disable_thinking=try_no_think,
                    temperature=0.6,
                    max_output_tokens=1600,
                    response_mime_type="application/json",
                )
                resp = call_gemini_with_retry(
                    client.models.generate_content,
                    model=m_name,
                    contents=duel_prompt,
                    config=cfg
                )
                raw = (resp.text or "").strip()
                raw = re.sub(r'^```(?:json)?\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)
                parsed = json.loads(raw)
                qs = parsed.get("questions", []) if isinstance(parsed, dict) else []
                if isinstance(qs, list) and len(qs) >= 6:
                    return qs[:6]
            except Exception as err:
                err_txt = str(err).lower()
                if try_no_think and ("thinking" in err_txt or "invalid_argument" in err_txt or "400" in err_txt):
                    continue
                break
    return None

def judge_duel_free_answer(
    question_text: str,
    expected_answer: str,
    student_answer: str,
    client = None,
    api_key: str = ""
) -> bool:
    """Ελέγχει δίκαια, νοηματικά και επιεικώς ελεύθερη απάντηση μαθητή."""
    norm_st = normalize_text(student_answer or "").strip()
    if not norm_st or norm_st in ("δεν ξερω", "δεν εχω ιδεα", "πασο", "παραδιδω", "οχι", "τιποτα", "?"):
        return False
    norm_exp = normalize_text(expected_answer or "").strip()
    if norm_st == norm_exp or (len(norm_st) >= 4 and (norm_st in norm_exp or norm_exp in norm_st)):
        return True

    import app
    if client is None:
        key = api_key or app.load_saved_key()
        client = app.get_genai_client(key)

    active_m = "gemini-3.5-flash-lite"
    if st is not None and "active_model" in st.session_state:
        active_m = st.session_state.active_model
    ordered_models = list(dict.fromkeys([active_m, "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash"]))

    judge_p = f"""Είσαι ένας δίκαιος, επιεικής καθηγητής Γυμνασίου στην Ελλάδα και βαθμολογείς μια απάντηση μαθητή σε εκπαιδευτικό παιχνίδι.

Ερώτηση: {question_text}
Ενδεικτική σωστή απάντηση: {expected_answer}
Απάντηση μαθητή: {student_answer}

ΚΑΝΟΝΕΣ ΑΞΙΟΛΟΓΗΣΗΣ (ΠΟΛΥ ΣΗΜΑΝΤΙΚΟ):
- Κρίνε με βάση το ΝΟΗΜΑ και την ΚΑΤΑΝΟΗΣΗ, ΟΧΙ αν έγραψε τις ίδιες ακριβώς λέξεις!
- Απάντησε YES αν η απάντηση του μαθητή:
  1. Είναι νοηματικά σωστή ή στο περίπου σωστή και δείχνει ότι κατάλαβε την ουσία.
  2. Χρησιμοποιεί δικά του λόγια, συνώνυμα, περίφραση, συντομογραφία ή διαφορετική πτώση/χρόνο.
  3. Έχει ορθογραφικά λάθη ή λείπουν τόνοι.
  4. Δίνει μια άλλη εξίσου σωστή απάντηση στην ερώτηση (ακόμα κι αν διαφέρει από την ενδεικτική).
  5. Γράφει αριθμούς ολογράφως ή με ψηφία.
- Απάντησε NO ΜΟΝΟ αν η απάντηση είναι ξεκάθαρα λανθασμένη, αντίθετη από τη σωστή, άσχετη ή τυχαία.

Απάντησε ΑΠΟΚΛΕΙΣΤΙΚΑ με μία λέξη: YES ή NO."""

    try:
        for m_name in ordered_models:
            for try_no_think in (True, False):
                try:
                    cfg = app.build_fast_config(m_name, disable_thinking=try_no_think, temperature=0.0, max_output_tokens=20)
                    r = call_gemini_with_retry(
                        client.models.generate_content,
                        model=m_name,
                        contents=judge_p,
                        config=cfg
                    )
                    ans_u = (r.text or "").strip().upper()
                    if "YES" in ans_u or "ΝΑΙ" in ans_u:
                        return True
                    if "NO" in ans_u or "ΟΧΙ" in ans_u:
                        return False
                except Exception as err:
                    err_txt = str(err).lower()
                    if try_no_think and ("thinking" in err_txt or "invalid_argument" in err_txt or "400" in err_txt):
                        continue
                    break
    except Exception:
        pass

    import difflib
    stop_w = {"στην", "στον", "στη", "στο", "απο", "για", "με", "την", "τον", "των", "του", "της", "ειναι", "ηταν", "οτι", "πως"}
    exp_words = [w for w in re.sub(r'[^\w\s]', ' ', norm_exp).split() if len(w) >= 4 and w not in stop_w]
    st_words = [w for w in re.sub(r'[^\w\s]', ' ', norm_st).split() if len(w) >= 3 and w not in stop_w]
    if not exp_words or not st_words:
        return False
    for ew in exp_words:
        stem = ew[:5] if len(ew) >= 5 else ew
        for sw in st_words:
            if stem in sw or difflib.SequenceMatcher(None, ew, sw).ratio() >= 0.74:
                return True
    return False

def generate_mini_game_json(
    game_type: str,
    grade: str,
    subject: str,
    book_topics: str,
    support_level: str,
    chapter_focus: str = "",
    client = None,
    api_key: str = ""
):
    """Παράγει σε ΜΙΑ (1) κλήση AI όλο το περιεχόμενο για: 'detective', 'myth_truth', 'ladder5' ή 'escape'."""
    import app
    if client is None:
        key = api_key or app.load_saved_key()
        client = app.get_genai_client(key)

    active_m = "gemini-3.5-flash-lite"
    if st is not None and "active_model" in st.session_state:
        active_m = st.session_state.active_model
    ordered_models = list(dict.fromkeys([active_m, "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash"]))

    lvl_instr = (
        "ΠΟΛΥ ΑΠΛΕΣ προτάσεις (4-8 λέξεις), Easy-to-Read για Επίπεδο 1 / Ειδική Αγωγή, χωρίς παγίδες."
        if support_level == "LEVEL_1"
        else ("Απλή, καθαρή διατύπωση (Επίπεδο 2 Γυμνασίου)." if support_level == "LEVEL_2" else "Επίπεδο Γυμνασίου με κριτική σκέψη.")
    )
    focus_line = f"- Ειδικό κεφάλαιο/θέμα: {chapter_focus}" if chapter_focus.strip() else ""

    if game_type == "detective":
        schema_instr = """
Ετοίμασε ΑΚΡΙΒΩΣ 5 σύντομες προτάσεις για το παιχνίδι «🕵️ Βρες το Λάθος του Σωκράτη!».
Σε κάθε πρόταση, ο Σωκράτης κάνει ΕΠΙΤΗΔΕΣ 1 ξεκάθαρο λάθος (ιστορικό, μαθηματικό, επιστημονικό ή εννοιολογικό).
ΕΠΕΣΤΡΕΨΕ ΑΠΟΚΛΕΙΣΤΙΚΑ ΕΓΚΥΡΟ JSON:
{
  "items": [
    {
      "statement": "Η πρόταση του Σωκράτη που περιέχει 1 λάθος",
      "choices": ["Διόρθωση Α (σωστή)", "Διόρθωση Β", "Διόρθωση Γ"],
      "correct_choice": "Διόρθωση Α (σωστή)",
      "explanation": "Σύντομη επεξήγηση 1 πρότασης γιατί αυτό ήταν το λάθος",
      "hint": "Ένα μικρό σωκρατικό στοιχείο χωρίς να δίνει την έτοιμη απάντηση",
      "topic": "Σύντομη κατηγορία 2-3 λέξεων"
    }
  ]
}"""
        expected_len = 5
    elif game_type == "myth_truth":
        schema_instr = """
Ετοίμασε ΑΚΡΙΒΩΣ 5 ζωντανές δηλώσεις (μείγμα Αλήθειας & Μύθου) για το παιχνίδι «⚖️ Μύθος ή Αλήθεια;».
ΕΠΕΣΤΡΕΨΕ ΑΠΟΚΛΕΙΣΤΙΚΑ ΕΓΚΥΡΟ JSON:
{
  "items": [
    {
      "statement": "Σαφής δήλωση από την ύλη του μαθήματος",
      "is_true": true,
      "explanation": "Σύντομη, ζεστή εξήγηση 1 πρότασης από τον Σωκράτη",
      "topic": "Σύντομη κατηγορία 2-3 λέξεων"
    }
  ]
}"""
        expected_len = 5
    elif game_type == "ladder5":
        lvl5_style = (
            "ΚΑΙ ΤΑ 5 ΣΚΑΛΟΠΑΤΙΑ να είναι σε ΠΟΛΥ ΑΠΛΗ γλώσσα (1-2 μικρές προτάσεις), Easy-to-Read, με φιλικά εικονίδια (emoji), χωρίς παγίδες, και 3 ξεκάθαρες επιλογές (choices)."
            if support_level == "LEVEL_1"
            else "Κλιμάκωσε ΣΤΑΔΙΑΚΑ τη δυσκολία: το Επίπεδο 1 να είναι ΠΟΛΥ ΕΥΚΟΛΟ (για να πάρει θάρρος ο μαθητής), το 2 βασική κατανόηση, το 3 σύνδεση εννοιών, το 4 εφαρμογή/κρίση και το 5 απαιτητική ερώτηση σύνθεσης (Δάσκαλος της Ενότητας). ΑΥΣΤΗΡΟΣ ΚΑΝΟΝΑΣ: Οι ερωτήσεις πρέπει να είναι ΑΝΟΙΧΤΕΣ και ΑΥΤΟΤΕΛΕΙΣ! ΑΠΑΓΟΡΕΥΕΤΑΙ να γράφεις «Ποια από τις παρακάτω...», «Ποιο από τα επόμενα...» ή φράσεις που προϋποθέτουν επιλογές!"
        )
        schema_instr = f"""
Ετοίμασε ΑΚΡΙΒΩΣ 5 διαδοχικές ερωτήσεις/μίνι ασκήσεις για το παιχνίδι «🏔️ Πρόκληση 5 Επιπέδων».
Τα 5 σκαλοπάτια έχουν ΑΚΡΙΒΩΣ αυτούς τους τίτλους:
1: "🌱 Ζέσταμα"
2: "🧭 Εξερευνητής"
3: "📚 Γνώστης"
4: "♟️ Στρατηγός"
5: "🏆 Δάσκαλος της Ενότητας"
{lvl5_style}
ΕΠΕΣΤΡΕΨΕ ΑΠΟΚΛΕΙΣΤΙΚΑ ΕΓΚΥΡΟ JSON:
{{
  "items": [
    {{
      "level_num": 1,
      "level_name": "🌱 Ζέσταμα",
      "icon": "🌱",
      "question": "Σαφής, αυτοτελής ερώτηση/μίνι άσκηση για αυτό το σκαλοπάτι",
      "choices": ["Επιλογή Α", "Επιλογή Β", "Επιλογή Γ"],
      "correct_choice": "Επιλογή Α",
      "expected_answer": "Σύντομη αναμενόμενη σωστή απάντηση (1-6 λέξεις)",
      "hint": "Μικρό σωκρατικό στοιχείο για 2η ευκαιρία (ΧΩΡΙΣ έτοιμη λύση)",
      "explanation": "Σύντομη, ενθαρρυντική επιβεβαίωση 1 πρότασης",
      "topic": "Σύντομη κατηγορία 2-3 λέξεων"
    }}
  ]
}}"""
        expected_len = 5
    else:  # escape
        schema_instr = """
Ετοίμασε ΑΚΡΙΒΩΣ 4 διαδοχικούς γρίφους-λουκέτα για το παιχνίδι «🔐 Απόδραση από τη Βιβλιοθήκη του Σωκράτη».
Κάθε λουκέτο έχει ένα μικρό ατμοσφαιρικό σενάριο 1 πρότασης και 1 ερώτηση γνώσεων από το μάθημα.
ΕΠΕΣΤΡΕΨΕ ΑΠΟΚΛΕΙΣΤΙΚΑ ΕΓΚΥΡΟ JSON:
{
  "items": [
    {
      "lock_title": "Λουκέτο 1: Η Πύλη των Χειρογράφων",
      "riddle": "Σύντομος γρίφος/ερώτηση από το μάθημα",
      "choices": ["Επιλογή Α", "Επιλογή Β", "Επιλογή Γ"],
      "correct_choice": "Επιλογή Α",
      "hint": "Μικρό σωκρατικό στοιχείο για 2η ευκαιρία (χωρίς έτοιμη λύση)",
      "explanation": "Τι ξεκλείδωσε (1 σύντομη πρόταση εμπέδωσης)",
      "topic": "Σύντομη κατηγορία 2-3 λέξεων"
    }
  ]
}"""
        expected_len = 4

    full_p = f"""
Είσαι ο Σωκράτης, εκπαιδευτικός Γυμνασίου στην Ελλάδα.
- Τάξη: {grade}
- Μάθημα: {subject}
- Επίσημη ύλη: {book_topics}
{focus_line}
- Επίπεδο: {lvl_instr}

{schema_instr}
Βεβαιώσου ότι οι επιλογές (choices) είναι ανακατεμένες και ότι το correct_choice ταιριάζει ΑΚΡΙΒΩΣ με μία από τις choices.
"""
    for m_name in ordered_models:
        for try_no_think in (True, False):
            try:
                cfg = app.build_fast_config(
                    m_name,
                    disable_thinking=try_no_think,
                    temperature=0.6,
                    max_output_tokens=2000 if game_type == "ladder5" else 1600,
                    response_mime_type="application/json",
                )
                resp = call_gemini_with_retry(
                    client.models.generate_content,
                    model=m_name,
                    contents=full_p,
                    config=cfg
                )
                raw = (resp.text or "").strip()
                raw = re.sub(r'^```(?:json)?\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)
                parsed = json.loads(raw)
                items = parsed.get("items", []) if isinstance(parsed, dict) else []
                if isinstance(items, list) and len(items) >= expected_len:
                    return items[:expected_len]
            except Exception as err:
                err_txt = str(err).lower()
                if try_no_think and ("thinking" in err_txt or "invalid_argument" in err_txt or "400" in err_txt):
                    continue
                break
    return None

def generate_live_visual_card_json(
    grade: str,
    subject: str,
    book_topics: str,
    support_level: str,
    topic_focus: str = "",
    recent_chat: str = "",
    client = None,
    api_key: str = ""
):
    """Παράγει επιτόπου μια Ζωντανή Εποπτική Κάρτα-Σχεδιάγραμμα για ΟΠΟΙΟΔΗΠΟΤΕ μάθημα/κεφάλαιο του ΙΕΠ."""
    import app
    if client is None:
        key = api_key or app.load_saved_key()
        client = app.get_genai_client(key)

    active_m = "gemini-3.5-flash-lite"
    if st is not None and "active_model" in st.session_state:
        active_m = st.session_state.active_model
    ordered_models = list(dict.fromkeys([active_m, "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash"]))

    lvl_rule = (
        "ΕΠΙΠΕΔΟ 1 (Ειδική Αγωγή / Easy-to-Read): ΠΟΛΥ ΑΠΛΕΣ λέξεις, 4-8 λέξεις σε κάθε κουτάκι, φιλικά emoji, χωρίς δύσκολους όρους."
        if support_level == "LEVEL_1"
        else ("ΕΠΙΠΕΔΟ 2 (Απλοποιημένο Γυμνασίου): Καθαρή, απλή γλώσσα βήμα-βήμα." if support_level == "LEVEL_2" else "ΕΠΙΠΕΔΟ 3 (Τυπικό Γυμνασίου): Ακριβείς σχολικοί όροι από το επίσημο βιβλίο ΙΕΠ.")
    )
    focus_str = f"- Συγκεκριμένο θέμα/κεφάλαιο: {topic_focus.strip()}" if (topic_focus or "").strip() else ""
    chat_str = f"- Τρέχουσα συζήτηση μαθητή (φτιάξε την κάρτα πάνω σε αυτό!): {recent_chat[:450]}" if (recent_chat or "").strip() else ""

    prompt_card = f"""
Είσαι ο Σωκράτης, εκπαιδευτικός Γυμνασίου στην Ελλάδα.
Δημιούργησε μια καθαρή, ευχάριστη **Ζωντανή Εποπτική Κάρτα-Σχεδιάγραμμα** βασισμένη ΑΠΟΚΛΕΙΣΤΙΚΑ στα τρέχοντα επίσημα σχολικά βιβλία του ΙΕΠ (ebooks.edu.gr).

ΣΤΟΙΧΕΙΑ:
- Τάξη: {grade}
- Μάθημα: {subject}
- Επίσημη ύλη ΙΕΠ: {book_topics}
{focus_str}
{chat_str}
- Επίπεδο: {lvl_rule}

ΕΠΕΣΤΡΕΨΕ ΑΠΟΚΛΕΙΣΤΙΚΑ ΕΓΚΥΡΟ JSON (χωρίς κανένα επιπλέον κείμενο):
{{
  "title": "Σύντομος, καθαρός τίτλος κάρτας",
  "icon": "🌟",
  "central_idea": "Η κεντρική ιδέα σε 1 πολύ καθαρή και κατανοητή πρόταση",
  "steps": [
    {{"icon": "1️⃣", "heading": "Σύντομος τίτλος 1", "text": "Πολύ σύντομη εξήγηση (έως 12 λέξεις)"}},
    {{"icon": "2️⃣", "heading": "Σύντομος τίτλος 2", "text": "Πολύ σύντομη εξήγηση (έως 12 λέξεις)"}},
    {{"icon": "3️⃣", "heading": "Σύντομος τίτλος 3", "text": "Πολύ σύντομη εξήγηση (έως 12 λέξεις)"}}
  ],
  "everyday_example": "1 απτό, ζωντανό παράδειγμα από την καθημερινή ζωή (1 πρόταση)",
  "remember_rule": "1 χρυσός κανόνας για να το θυμάται εύκολα ο μαθητής"
}}
"""
    for m_name in ordered_models:
        for try_no_think in (True, False):
            try:
                cfg = app.build_fast_config(
                    m_name,
                    disable_thinking=try_no_think,
                    temperature=0.5,
                    max_output_tokens=1100,
                    response_mime_type="application/json",
                )
                resp = call_gemini_with_retry(
                    client.models.generate_content,
                    model=m_name,
                    contents=prompt_card,
                    config=cfg
                )
                raw = (resp.text or "").strip()
                raw = re.sub(r'^```(?:json)?\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)
                try:
                    parsed = json.loads(raw)
                except Exception:
                    m_obj = re.search(r'\{[\s\S]*\}', raw)
                    parsed = json.loads(m_obj.group(0)) if m_obj else None
                if isinstance(parsed, dict) and parsed.get("title") and parsed.get("steps"):
                    parsed["_grade"] = grade
                    parsed["_subject"] = subject
                    return parsed
            except Exception as err:
                err_txt = str(err).lower()
                if try_no_think and ("thinking" in err_txt or "invalid_argument" in err_txt or "400" in err_txt):
                    continue
                break
    return None

def render_live_visual_card_markdown(card: dict, fallback_grade: str = "", fallback_subject: str = ""):
    """Αποδίδει μια Ζωντανή Εποπτική Κάρτα-Σχεδιάγραμμα με καθαρό, ευανάγνωστο HTML."""
    if not isinstance(card, dict) or st is None:
        return
    c_title = html_lib.escape(str(card.get("title", "Εποπτική Κάρτα")))
    c_icon = html_lib.escape(str(card.get("icon", "🖼️")))
    c_idea = html_lib.escape(str(card.get("central_idea", "")))
    c_example = html_lib.escape(str(card.get("everyday_example", "")))
    c_rule = html_lib.escape(str(card.get("remember_rule", "")))
    c_grade = html_lib.escape(str(card.get("_grade", fallback_grade)))
    c_subj = html_lib.escape(str(card.get("_subject", fallback_subject)))
    steps = card.get("steps", []) if isinstance(card.get("steps"), list) else []

    step_palettes = [
        ("#eff6ff", "#60a5fa", "#1e3a8a"),
        ("#f5f3ff", "#a78bfa", "#4c1d95"),
        ("#ecfdf5", "#34d399", "#065f46"),
        ("#fff7ed", "#fb923c", "#7c2d12"),
    ]
    step_blocks = []
    for idx_s, stp in enumerate(steps[:4]):
        bg, bd, fg = step_palettes[idx_s % len(step_palettes)]
        s_ic = html_lib.escape(str(stp.get("icon", f"{idx_s+1}️⃣")))
        s_hd = html_lib.escape(str(stp.get("heading", "")))
        s_tx = html_lib.escape(str(stp.get("text", "")))
        step_blocks.append(
            f'<div style="flex:1 1 160px; background:{bg}; border:2px solid {bd}; border-radius:12px; padding:10px 12px; text-align:center;">'
            f'<div style="font-size:1.35rem; line-height:1.1; margin-bottom:4px;">{s_ic}</div>'
            f'<div style="font-size:0.9rem; font-weight:800; color:{fg}; margin-bottom:3px;">{s_hd}</div>'
            f'<div style="font-size:0.84rem; color:#1e293b; line-height:1.35;">{s_tx}</div>'
            f'</div>'
        )
    flow_html = '<div style="display:flex; align-items:center; justify-content:center; font-size:1.2rem; color:#64748b; font-weight:800;">➡️</div>'.join(step_blocks)

    st.markdown(f"""
    <div style="background:#ffffff; border:2px solid #93c5fd; border-radius:16px; overflow:hidden; box-shadow:0 4px 14px rgba(15,52,96,0.09); margin:10px 0 8px 0;">
        <div style="background:linear-gradient(135deg,#dbeafe 0%,#bfdbfe 100%); border-bottom:1.5px solid #93c5fd; color:#0c335e; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
            <div style="font-size:1.08rem; font-weight:800; color:#0c335e !important;">{c_icon} {c_title}</div>
            <div style="font-size:0.78rem; font-weight:700; background:#ffffff; border:1px solid #93c5fd; padding:3px 10px; border-radius:999px; color:#1e3a8a !important;">{c_grade} • {c_subj}</div>
        </div>
        <div style="padding:14px 16px;">
            <div style="background:#f8fafc; border-left:4px solid #2563eb; border-radius:8px; padding:8px 12px; margin-bottom:12px; font-size:0.93rem; color:#0f172a;">
                <b>🎯 Κεντρική Ιδέα:</b> {c_idea}
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:stretch; margin-bottom:12px;">
                {flow_html}
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:10px;">
                <div style="background:#ecfdf5; border:1.5px solid #6ee7b7; border-radius:10px; padding:9px 12px; font-size:0.86rem; color:#065f46;">
                    <b>🍎 Παράδειγμα από τη ζωή:</b><br>{c_example}
                </div>
                <div style="background:#fef9c3; border:1.5px solid #facc15; border-radius:10px; padding:9px 12px; font-size:0.86rem; color:#713f12;">
                    <b>💡 Θυμήσου αυτό!</b><br>{c_rule}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
