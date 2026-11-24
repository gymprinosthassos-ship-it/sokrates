"""
gemini_resilience.py — Μηχανισμός Ανθεκτικότητας στο Όριο Ρυθμού (Rate-Limit 15 RPM)
& Αυτόματης Ουράς Αναμονής (Smart Retry with Exponential Backoff)
για τον «Σωκράτη AI Tutor Γυμνασίου».

Προστατεύει τη λειτουργία στην τάξη όταν πολλά tablets (π.χ. 7-15) στέλνουν
αιτήματα ταυτόχρονα. Αντί να εμφανιστεί σφάλμα HTTP 429 (Resource Exhausted),
το σύστημα περιμένει διακριτικά 1.5s -> 3.0s -> 5.0s με ευγενική ενημέρωση
στον μαθητή και επαναλαμβάνει την κλήση επιτυχώς.
"""

import time
import random

# pyrefly: ignore [missing-import]
try:
    import streamlit as st
except ImportError:
    st = None

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
