"""
session_store.py — Μηχανισμός Τοπικής Ανάκτησης Συνεδρίας (Session Recovery)
για τον «Σωκράτη AI Tutor Γυμνασίου».

Διασφαλίζει ότι οι μαθητές στα tablets δεν χάνουν τη συνομιλία τους αν:
1. Σβήσει η οθόνη του tablet (Screen Sleep / Doze mode).
2. Αλλάξουν καρτέλα για να διαβάσουν το σχολικό βιβλίο (Tab Switching).
3. Πέσει στιγμιαία το Wi-Fi του σχολείου (Network Reconnect).
4. Γίνει κατά λάθος ανανέωση της σελίδας (Pull-to-refresh).

Χρησιμοποιεί SQLite σε λειτουργία WAL (Write-Ahead Logging) για άμεση,
ταχύτατη (<3ms) και ασφαλή παράλληλη πρόσβαση από πολλαπλά tablets ταυτόχρονα.
"""

import os
import time
import json
import sqlite3
from typing import Dict, List, Optional, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "socrates_sessions.db")

def _get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Δημιουργεί σύνδεση SQLite με αυξημένο timeout και λειτουργία WAL."""
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db(db_path: str = DB_PATH) -> None:
    """Αρχικοποιεί τον πίνακα αποθήκευσης συνεδριών αν δεν υπάρχει."""
    try:
        with _get_connection(db_path) as conn:
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
            conn.commit()
    except Exception as e:
        print(f"[SessionStore] Σφάλμα αρχικοποίησης βάσης: {e}")

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

# Αυτόματη αρχικοποίηση κατά το import
init_db()
