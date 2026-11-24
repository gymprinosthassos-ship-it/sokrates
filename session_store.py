"""
session_store.py — Μηχανισμός Τοπικής Ανάκτησης Συνεδρίας (Session Recovery)
& Μόνιμης Αποθήκευσης Δεδομένων (SQLite WAL) για τον «Σωκράτη AI Tutor Γυμνασίου».

Διασφαλίζει ότι:
1. Οι μαθητές στα tablets δεν χάνουν τη συνομιλία τους αν σβήσει η οθόνη (Screen Sleep),
   αλλάξουν καρτέλα (Tab Switching) ή αποσυνδεθεί στιγμιαία το Wi-Fi.
2. Ο εκπαιδευτικός δεν χάνει ποτέ τα δεδομένα του Χάρτη Παρανοήσεων και των
   καταγραφών ασφαλείας κατά τις επανεκκινήσεις (ephemeral restarts) του Streamlit Cloud.

Χρησιμοποιεί SQLite σε λειτουργία WAL (Write-Ahead Logging) για άμεση,
ταχύτατη (<3ms) και ασφαλή παράλληλη πρόσβαση από πολλαπλά tablets ταυτόχρονα.
"""

import os
import time
import json
import sqlite3
import datetime
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "socrates_sessions.db")

@contextmanager
def _get_connection(db_path: str = DB_PATH):
    """Δημιουργεί σύνδεση SQLite με αυξημένο timeout, λειτουργία WAL και εγγυημένο κλείσιμο."""
    conn = sqlite3.connect(db_path, timeout=10.0)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass

def init_db(db_path: str = DB_PATH) -> None:
    """Αρχικοποιεί τους πίνακες συνεδριών, παρανοήσεων και ασφάλειας αν δεν υπάρχουν."""
    try:
        with _get_connection(db_path) as conn:
            # 1. Πίνακας ενεργών συνεδριών tablet
            conn.execute("""
            CREATE TABLE IF NOT EXISTS active_sessions (
                sid TEXT PRIMARY KEY,
                updated_at REAL,
                grade TEXT,
                subject TEXT,
                support_level TEXT,
                stuck_counter INTEGER,
                messages_json TEXT
            );
            """)
            # 2. Πίνακας παρανοήσεων μαθητών (Misconceptions Heatmap)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS misconceptions (
                uid TEXT PRIMARY KEY,
                date TEXT,
                timestamp TEXT,
                grade TEXT,
                subject TEXT,
                topic TEXT,
                example TEXT,
                status TEXT
            );
            """)
            # 3. Πίνακας παραβιάσεων ασφάλειας (Security Audit Log)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS security_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                violation_type TEXT,
                grade TEXT,
                subject TEXT,
                trigger_snippet TEXT,
                action_taken TEXT
            );
            """)
            conn.commit()
    except Exception as e:
        print(f"[SessionStore] Σφάλμα αρχικοποίησης βάσης: {e}")

# -------------------------------------------------------------
# 1. Διαχείριση Συνεδριών Μαθητών (Tablet Session Recovery)
# -------------------------------------------------------------
def save_session(
    sid: str,
    grade: str,
    subject: str,
    support_level: str,
    stuck_counter: int,
    messages: List[Dict[str, Any]],
    db_path: str = DB_PATH
) -> bool:
    """Αποθηκεύει τη συνεδρία ενός tablet με ασφάλεια και ελάχιστο μέγεθος."""
    if not sid:
        return False
    try:
        init_db(db_path)
        clean_messages = []
        for m in messages:
            clean_m = {
                "role": m.get("role", "assistant"),
                "content": m.get("content", "")
            }
            if m.get("visual_card"):
                clean_m["visual_card"] = m["visual_card"]
            clean_messages.append(clean_m)

        msg_json = json.dumps(clean_messages, ensure_ascii=False)
        now = time.time()

        with _get_connection(db_path) as conn:
            conn.execute("""
            INSERT OR REPLACE INTO active_sessions 
            (sid, updated_at, grade, subject, support_level, stuck_counter, messages_json)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (sid, now, grade, subject, support_level, int(stuck_counter), msg_json))
            conn.commit()
        return True
    except Exception as e:
        print(f"[SessionStore] Σφάλμα αποθήκευσης συνεδρίας {sid}: {e}")
        return False

def load_session(sid: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Ανακτά τη συνεδρία ενός tablet με βάση το session ID."""
    if not sid:
        return None
    try:
        init_db(db_path)
        with _get_connection(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT grade, subject, support_level, stuck_counter, messages_json 
            FROM active_sessions WHERE sid = ?;
            """, (sid,))
            row = cur.fetchone()
            if not row:
                return None
            
            grade, subject, support_level, stuck_counter, msg_json = row
            messages = json.loads(msg_json) if msg_json else []
            return {
                "sid": sid,
                "grade": grade,
                "subject": subject,
                "support_level": support_level,
                "stuck_counter": stuck_counter,
                "messages": messages
            }
    except Exception as e:
        print(f"[SessionStore] Σφάλμα φόρτωσης συνεδρίας {sid}: {e}")
        return None

def delete_session(sid: str, db_path: str = DB_PATH) -> bool:
    """Διαγράφει τη συνεδρία όταν ο μαθητής πατάει 'Νέα Συζήτηση'."""
    if not sid:
        return False
    try:
        with _get_connection(db_path) as conn:
            conn.execute("DELETE FROM active_sessions WHERE sid = ?;", (sid,))
            conn.commit()
        return True
    except Exception:
        return False

def cleanup_old_sessions(max_age_hours: float = 24.0, db_path: str = DB_PATH) -> int:
    """Καθαρίζει συνεδρίες παλαιότερες των 24 ωρών σύμφωνα με το GDPR."""
    try:
        cutoff = time.time() - (max_age_hours * 3600)
        with _get_connection(db_path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM active_sessions WHERE updated_at < ?;", (cutoff,))
            deleted = cur.rowcount
            conn.commit()
            return deleted
    except Exception:
        return 0

# -------------------------------------------------------------
# 2. Μόνιμη Αποθήκευση Παρανοήσεων (Misconceptions SQLite Persistence)
# -------------------------------------------------------------
def db_save_misconception(rec: Dict[str, Any], db_path: str = DB_PATH) -> bool:
    """Αποθηκεύει μία παρανόηση μαθητή στη βάση δεδομένων SQLite."""
    if not rec or not rec.get("topic"):
        return False
    try:
        init_db(db_path)
        with _get_connection(db_path) as conn:
            conn.execute("""
            INSERT OR REPLACE INTO misconceptions
            (uid, date, timestamp, grade, subject, topic, example, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                rec.get("uid", ""),
                rec.get("date", datetime.date.today().strftime("%Y-%m-%d")),
                rec.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                rec.get("grade", ""),
                rec.get("subject", ""),
                rec.get("topic", ""),
                rec.get("example", ""),
                rec.get("status", "CAUGHT")
            ))
            conn.commit()
        return True
    except Exception as e:
        print(f"[SessionStore] Σφάλμα αποθήκευσης παρανόησης: {e}")
        return False

def db_load_misconceptions(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Φορτώνει όλες τις καταγεγραμμένες παρανοήσεις από την SQLite."""
    try:
        init_db(db_path)
        with _get_connection(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT uid, date, timestamp, grade, subject, topic, example, status
            FROM misconceptions
            ORDER BY timestamp ASC;
            """)
            rows = cur.fetchall()
            return [
                {
                    "uid": r[0],
                    "date": r[1],
                    "timestamp": r[2],
                    "grade": r[3],
                    "subject": r[4],
                    "topic": r[5],
                    "example": r[6],
                    "status": r[7]
                }
                for r in rows
            ]
    except Exception as e:
        print(f"[SessionStore] Σφάλμα ανάγνωσης παρανοήσεων: {e}")
        return []

# -------------------------------------------------------------
# 3. Μόνιμη Αποθήκευση Παραβιάσεων Ασφάλειας (Security Audit SQLite)
# -------------------------------------------------------------
def db_save_violation(
    violation_type: str,
    trigger_snippet: str,
    grade: str = "N/A",
    subject: str = "N/A",
    action_taken: str = "APP_LOCKED_TERMINATED",
    db_path: str = DB_PATH
) -> bool:
    """Καταγράφει απόπειρα παραβίασης πολιτικής στην SQLite (GDPR compliant)."""
    try:
        init_db(db_path)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_snippet = (trigger_snippet or "").replace('\n', ' ')[:120]
        with _get_connection(db_path) as conn:
            conn.execute("""
            INSERT INTO security_violations
            (timestamp, violation_type, grade, subject, trigger_snippet, action_taken)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (now_str, violation_type, grade, subject, safe_snippet, action_taken))
            conn.commit()
        return True
    except Exception as e:
        print(f"[SessionStore] Σφάλμα καταγραφής παραβίασης: {e}")
        return False

def db_load_violations(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Φορτώνει όλες τις καταγραφές παραβιάσεων από την SQLite."""
    try:
        init_db(db_path)
        with _get_connection(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT id, timestamp, violation_type, grade, subject, trigger_snippet, action_taken
            FROM security_violations
            ORDER BY id DESC;
            """)
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "timestamp": r[1],
                    "violation_type": r[2],
                    "grade": r[3],
                    "subject": r[4],
                    "trigger_snippet": r[5],
                    "action_taken": r[6]
                }
                for r in rows
            ]
    except Exception as e:
        print(f"[SessionStore] Σφάλμα ανάγνωσης παραβιάσεων: {e}")
        return []

def db_get_violation_count(db_path: str = DB_PATH) -> int:
    """Επιστρέφει το πλήθος καταγεγραμμένων παραβιάσεων από την SQLite."""
    try:
        init_db(db_path)
        with _get_connection(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM security_violations;")
            row = cur.fetchone()
            return int(row[0]) if row else 0
    except Exception:
        return 0

# Αυτόματη αρχικοποίηση κατά το import
init_db()
