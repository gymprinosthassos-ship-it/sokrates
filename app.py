import os
import streamlit as st
from google import genai
from google.genai import types

# Διαδρομή εικονιδίου Σωκράτη
AVATAR_PATH = os.path.join(os.path.dirname(__file__), "socrates.jpg")
avatar_image = AVATAR_PATH if os.path.exists(AVATAR_PATH) else "🧔"

# 1. Ρύθμιση σελίδας
st.set_page_config(
    page_title="Σωκράτης",
    page_icon=avatar_image,
    layout="centered",
    initial_sidebar_state="expanded"
)

# Προσαρμοσμένο CSS - 2 τόνους πιο σκούρο γαλάζιο
st.markdown("""
<style>
    /* Κλείδωμα σε Light Mode για όλες τις συσκευές ανεξαρτήτως λειτουργικού */
    :root {
        color-scheme: light !important;
    }
    
    /* Ολόκληρη η σελίδα σε 2 τόνους πιο σκούρο γαλάζιο */
    .stApp {
        background: linear-gradient(180deg, #d3e6fa 0%, #bddcf7 100%) !important;
        color: #0f172a !important;
    }
    
    /* Πλαϊνή στήλη */
    [data-testid="stSidebar"] {
        background-color: #b0d3f4 !important;
        border-right: 1px solid #90bfe9 !important;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #0f172a !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Πλαίσια μηνυμάτων συνομιλίας (Μαθητή & Σωκράτη) */
    .stChatMessage, [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #a8cfee !important;
        box-shadow: 0 4px 12px rgba(15, 60, 120, 0.08) !important;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    
    /* Έντονα σκούρα γράμματα & μαθηματικά παντού */
    .stChatMessage *, [data-testid="stChatMessage"] *, .katex, .katex * {
        color: #0f172a !important;
    }
    
    /* Κάτω μπάρα πληκτρολόγησης */
    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background: transparent !important;
    }
    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 1px solid #90bfe9 !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #0f172a !important;
        background-color: #ffffff !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }
    
    .main-header {
        text-align: center;
        padding-bottom: 0.5rem;
    }
    
    .socratic-badge {
        background-color: #b9d8f6 !important;
        color: #0f3460 !important;
        padding: 4px 16px;
        border-radius: 14px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.4rem;
        border: 1px solid #97c2eb;
    }
    
    [data-testid="stChatMessage"] img {
        width: 46px !important;
        height: 46px !important;
        border-radius: 50% !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Μόνιμη Αποθήκευση & Ανάκτηση API Key
SECRETS_PATH = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")

def load_saved_key():
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return st.secrets["GEMINI_API_KEY"].strip()
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

def save_key_permanently(key):
    os.makedirs(os.path.dirname(SECRETS_PATH), exist_ok=True)
    with open(SECRETS_PATH, "w", encoding="utf-8") as f:
        f.write(f'GEMINI_API_KEY = "{key.strip()}"\n')

api_key = load_saved_key()

# Επικεφαλίδα
st.markdown(f"""
<div class="main-header">
    <span class="socratic-badge">Τάξη & Σκέψη</span>
    <h1 style="margin: 0.2rem 0;">Σωκράτης</h1>
    <p style="color:#555;font-size:0.95rem;margin-top:2px;"><i>«Το να γνωρίζεις ότι δεν γνωρίζεις είναι το πρώτο βήμα της σοφίας.»</i></p>
</div>
""", unsafe_allow_html=True)

# Αν ΔΕΝ υπάρχει αποθηκευμένο κλειδί, το ζητάμε μία φορά
if not api_key:
    st.markdown("---")
    st.info("👋 **Καλωσήρθατε!** Επικολλήστε παρακάτω το API Key **μία φορά** (θα αποθηκευτεί μόνιμα):")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        input_key = st.text_input("🔑 Gemini API Key:", type="password", placeholder="AIzaSy...")
    with col2:
        st.write("")
        submit_btn = st.button("💾 Αποθήκευση", type="primary", use_container_width=True)
        
    if submit_btn:
        if input_key.strip():
            save_key_permanently(input_key.strip())
            st.session_state.messages = []
            st.success("Το κλειδί αποθηκεύτηκε μόνιμα!")
            st.rerun()
        else:
            st.error("Παρακαλώ επικολλήστε πρώτα το κλειδί.")
            
    st.caption("🔒 Το κλειδί σώζεται τοπικά και δεν θα σας ξαναζητηθεί.")
    st.stop()

# 3. Ταχύτατα Μοντέλα Υψηλής Διαθεσιμότητας (Αποδεδειγμένα χωρίς όρια)
FAST_CHAT_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest"
]
active_model = "gemini-3.5-flash-lite"

with st.sidebar:
    # Εμφάνιση εικονιδίου σε 3πλάσιο μέγεθος (162px)
    if os.path.exists(AVATAR_PATH):
        col_l, col_img, col_r = st.columns([1, 6, 1])
        with col_img:
            st.image(AVATAR_PATH, width=162)
    st.markdown("<h2 style='text-align:center;margin-top:0.2rem;margin-bottom:0.5rem;'>Σωκράτης</h2>", unsafe_allow_html=True)
    
    GYMNASIO_SUBJECTS = [
        "🌟 Όλα τα μαθήματα (Γενικό)",
        "📐 Μαθηματικά (Άλγεβρα & Γεωμετρία)",
        "📖 Νεοελληνική Γλώσσα & Έκθεση",
        "📚 Νεοελληνική Λογοτεχνία",
        "🏛️ Αρχαία Ελληνική Γλώσσα",
        "🏺 Αρχαία από Μετάφραση (Ομήρου Έπη, Ελένη)",
        "⚡ Φυσική",
        "🧪 Χημεία",
        "🧬 Βιολογία",
        "🌍 Γεωλογία - Γεωγραφία",
        "📜 Ιστορία",
        "⚖️ Κοινωνική & Πολιτική Αγωγή (ΚΠΑ)",
        "🕊️ Θρησκευτικά",
        "💻 Πληροφορική",
        "🔧 Τεχνολογία",
        "🇬🇧 Αγγλικά",
        "🇫🇷 Γαλλικά",
        "🇩🇪 Γερμανικά",
        "🎨 Καλλιτεχνικά",
        "🎵 Μουσική",
        "🏡 Οικιακή Οικονομία"
    ]
    
    selected_subject = st.selectbox(
        "📚 Μάθημα:",
        GYMNASIO_SUBJECTS,
        index=0
    )
    
    if st.button("🔄 Νέα Συζήτηση", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    with st.expander("💡 Οδηγίες για μαθητές"):
        st.caption("""
        * **Γράψε την απορία σου** ή την άσκηση.
        * **Δεν δίνω έτοιμες λύσεις!** Σε καθοδηγώ με ερωτήσεις.
        * Μη φοβάσαι τα λάθη.
        """)

    with st.expander("⚙️ Ρυθμίσεις"):
        selected_model_choice = st.selectbox(
            "Μοντέλο AI:",
            ["gemini-3.5-flash-lite (Αστραπιαίο <1s)", "gemini-3.5-flash", "gemini-3.6-flash"],
            index=0
        )
        if "3.6" in selected_model_choice:
            active_model = "gemini-3.6-flash"
        elif "3.5-flash" in selected_model_choice and "lite" not in selected_model_choice:
            active_model = "gemini-3.5-flash"
        else:
            active_model = "gemini-3.5-flash-lite"

        if st.button("🗑️ Διαγραφή Key", use_container_width=True):
            if os.path.exists(SECRETS_PATH):
                os.remove(SECRETS_PATH)
            st.session_state.messages = []
            st.rerun()

# 4. Αρχικοποίηση ιστορικού μηνυμάτων
if "messages" not in st.session_state:
    st.session_state.messages = []

# Μήνυμα υποδοχής
if len(st.session_state.messages) == 0:
    welcome_text = f"Χαίρε! Είμαι ο **Σωκράτης**. Με ποιο θέμα ή άσκηση ασχολείσαι σήμερα στο μάθημα: **{selected_subject}**; Πες μου τι σκέφτεσαι και πού έχεις δυσκολευτεί!"
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})

# Εμφάνιση παλαιότερων μηνυμάτων με το νέο avatar
for msg in st.session_state.messages:
    msg_avatar = avatar_image if msg["role"] == "assistant" else "🎓"
    with st.chat_message(msg["role"], avatar=msg_avatar):
        st.markdown(msg["content"])

# 5. Κατασκευή Σωκρατικού System Prompt
system_instruction = f"""
Είσαι ο Σωκράτης, ο αρχαίος Έλληνας φιλόσοφος, που λειτουργεί ως υποστηρικτικός καθοδηγητής για μαθητές Γυμνασίου (12-15 ετών) στην Ελλάδα.
Είσαι πρόσχαρος, σοφός, υπομονετικός και χαμογελαστός.
Μάθημα: "{selected_subject}".

ΑΠΑΡΑΒΙΑΣΤΟΙ ΚΑΝΟΝΕΣ:
1. ΠΟΤΕ μην δίνεις έτοιμη τη λύση ή το τελικό αποτέλεσμα.
2. Εφάρμοσε τη Σωκρατική Μαιευτική Μέθοδο: απάντησε με 1-2 σύντομες, καθοδηγητικές ερωτήσεις.
3. Αν ο μαθητής πει "όχι" ή "δεν ξέρω", δώσε μία πολύ απλή, κατανοητή εξήγηση-βάση και κάνε μια ευκολότερη ερώτηση.
4. Σύντομες, άμεσες αποκρίσεις (1-3 προτάσεις) ώστε ο διάλογος να είναι ζωντανός και γρήγορος.
5. Χρησιμοποίησε LaTeX για μαθηματικά (π.χ. $2 \\cdot 3^3$).
"""

# 6. Επεξεργασία νέας εισόδου από τον μαθητή
if prompt := st.chat_input("Γράψε την απάντηση ή την ερώτησή σου εδώ..."):
    with st.chat_message("user", avatar="🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=avatar_image):
        response_container = st.empty()
        full_response = ""
        success = False

        models_to_try = [active_model] + [m for m in FAST_CHAT_MODELS if m != active_model]

        try:
            client = genai.Client(api_key=api_key)
            
            history = []
            for m in st.session_state.messages:
                if len(history) == 0 and m["role"] != "user":
                    continue
                role = "user" if m["role"] == "user" else "model"
                if history and history[-1].role == role:
                    continue
                history.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=m["content"])]
                ))

            # Άμεση δοκιμή μοντέλων με zero-delay failover
            for model_name in models_to_try:
                try:
                    chat = client.chats.create(
                        model=model_name,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.7,
                        ),
                        history=history if history else None,
                    )
                    
                    response = chat.send_message_stream(prompt)
                    full_response = ""
                    for chunk in response:
                        try:
                            text_piece = chunk.text
                        except Exception:
                            text_piece = ""
                        if text_piece:
                            full_response += text_piece
                            response_container.markdown(full_response + "▌")
                    
                    if full_response.strip():
                        success = True
                        response_container.markdown(full_response)
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        break
                except Exception:
                    continue

            if not success:
                st.warning("⚠️ Προσωρινό πρόβλημα σύνδεσης. Παρακαλώ ξαναστείλτε την ερώτηση.")

        except Exception as e:
            st.error(f"⚠️ Παρουσιάστηκε πρόβλημα επικοινωνίας: {e}")
