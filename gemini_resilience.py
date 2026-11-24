"""
gemini_resilience.py — Μηχανισμός Ανθεκτικότητας στο Όριο Ρυθμού (Rate-Limit 15 RPM)
& Αυτόματης Ουράς Αναμονής (Smart Retry with Exponential Backoff)
για τον «Σωκράτη AI Tutor Γυμνασίου».

Προστατεύει τη λειτουργία στην τάξη όταν πολλά tablets (π.χ. 7-15) στέλνουν
αιτήματα ταυτόχρονα. Αντί να εμφανιστεί σφάλμα HTTP 429 (Resource Exhausted),
το σύστημα περιμένει διακριτικά 1.5s -> 3.0s -> 5.0s με ευγενική ενημέρωση
στον μαθητή και επαναλαμβάνει την κλήση επιτυχώς.
"""

import os
import time
import random
from google import genai
from google.genai import types

# pyrefly: ignore [missing-import]
try:
    import streamlit as st
except ImportError:
    st = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_PATH = os.path.join(BASE_DIR, ".streamlit", "secrets.toml")

def load_saved_key() -> str:
    """Φορτώνει το GEMINI_API_KEY από Streamlit secrets, κρυπτογραφημένο αρχείο ή περιβάλλον."""
    if st is not None:
        try:
            if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
                return st.secrets["GEMINI_API_KEY"].strip()
        except Exception:
            pass

    for folder in [BASE_DIR, os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "antigravity", "scratch", "socratic-mentor"))]:
        ks_file = os.path.join(folder, ".key_store")
        fs_file = os.path.join(folder, ".fernet_seed")
        if os.path.exists(ks_file) and os.path.exists(fs_file):
            try:
                from cryptography.fernet import Fernet
                with open(fs_file, "rb") as sf, open(ks_file, "rb") as kf:
                    decrypted = Fernet(sf.read().strip()).decrypt(kf.read().strip()).decode("utf-8").strip()
                    if decrypted:
                        return decrypted
            except Exception:
                pass

    if os.path.exists(SECRETS_PATH):
        try:
            with open(SECRETS_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            k = parts[1].strip().strip('"').strip("'")
                            if k:
                                return k
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "").strip()

def save_key_permanently(key: str):
    """Αποθηκεύει το API key σε secrets.toml & κρυπτογραφημένο .key_store."""
    os.makedirs(os.path.dirname(SECRETS_PATH), exist_ok=True)
    with open(SECRETS_PATH, "w", encoding="utf-8") as f:
        f.write(f'GEMINI_API_KEY = "{key.strip()}"\n')
    try:
        from cryptography.fernet import Fernet
        fs_file = os.path.join(BASE_DIR, ".fernet_seed")
        ks_file = os.path.join(BASE_DIR, ".key_store")
        seed = Fernet.generate_key()
        with open(fs_file, "wb") as sf:
            sf.write(seed)
        enc = Fernet(seed).encrypt(key.strip().encode("utf-8"))
        with open(ks_file, "wb") as kf:
            kf.write(enc)
    except Exception:
        pass

def _cache_resource_dec():
    if st is not None:
        return st.cache_resource(show_spinner=False)
    return lambda fn: fn

@_cache_resource_dec()
def get_genai_client(key: str):
    return genai.Client(
        api_key=key,
        http_options=types.HttpOptions(
            timeout=20000,
            retry_options=types.HttpRetryOptions(attempts=1)
        )
    )

def build_fast_config(model_name: str, disable_thinking: bool = True, **kwargs):
    """Δημιουργεί ρυθμίσεις άμεσης απόκρισης (με ασφαλή απενεργοποίηση εσωτερικής σκέψης)."""
    if disable_thinking:
        try:
            kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        except Exception:
            pass
    return types.GenerateContentConfig(**kwargs)

def is_rate_limit_error(err: Exception) -> bool:
    """Ελέγχει αν το σφάλμα οφείλεται σε όριο ρυθμού (429) ή προσωρινό φόρτο διακομιστή (503)."""
    err_msg = str(err).lower()
    return any(k in err_msg for k in [
        "429", "resource_exhausted", "quota", "rate limit",
        "503", "unavailable", "overloaded"
    ])

def call_gemini_with_retry(
    fn,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.8,
    status_placeholder = None,
    **kwargs
):
    """
    Εκτελεί συνάρτηση κλήσης Gemini API με έξυπνη επανάληψη (Exponential Backoff + Jitter).
    
    Αν δεχτεί HTTP 429 / Rate Limit, περιμένει ευγενικά και ξαναδοκιμάζει αντί να καταρρεύσει.
    """
    delay = initial_delay
    last_err = None

    for attempt in range(1, max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_err = e
            if is_rate_limit_error(e) and attempt < max_retries:
                jitter = random.uniform(0.1, 0.5)
                wait_time = delay + jitter
                if status_placeholder is not None and hasattr(status_placeholder, "info"):
                    status_placeholder.info(
                        f"⏳ Ο Σωκράτης σκέφτεται... (Μικρή αναμονή {wait_time:.1f}δλ. λόγω κίνησης στην τάξη)",
                        icon="⏳"
                    )
                time.sleep(wait_time)
                delay *= 1.8
            else:
                raise e

    raise last_err

def send_chat_stream_with_retry(
    chat,
    message_parts,
    max_retries: int = 3,
    initial_delay: float = 1.8,
    status_placeholder = None
):
    """
    Εκκινεί stream απάντησης chat με προστασία από Rate Limit 429.
    """
    delay = initial_delay
    last_err = None

    for attempt in range(1, max_retries + 1):
        try:
            return chat.send_message_stream(message_parts)
        except Exception as e:
            last_err = e
            if is_rate_limit_error(e) and attempt < max_retries:
                jitter = random.uniform(0.1, 0.5)
                wait_time = delay + jitter
                if status_placeholder is not None and hasattr(status_placeholder, "info"):
                    status_placeholder.info(
                        f"⏳ Ο Σωκράτης ετοιμάζει την απάντηση... ({attempt}/{max_retries})",
                        icon="⏳"
                    )
                time.sleep(wait_time)
                delay *= 1.8
            else:
                raise e

    raise last_err
