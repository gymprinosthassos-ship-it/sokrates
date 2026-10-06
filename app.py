import os
import datetime
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 0. Διαδρομή Εικονιδίων Σωκράτη (256px HD Edition)
# -------------------------------------------------------------
AVATAR_PATH_PNG = os.path.join(os.path.dirname(__file__), "socrates_256.png")
AVATAR_PATH_JPG = os.path.join(os.path.dirname(__file__), "socrates.jpg")

if os.path.exists(AVATAR_PATH_PNG):
    avatar_image = AVATAR_PATH_PNG
elif os.path.exists(AVATAR_PATH_JPG):
    avatar_image = AVATAR_PATH_JPG
else:
    avatar_image = "🧔"

# -------------------------------------------------------------
# 1. Ρύθμιση Σελίδας
# -------------------------------------------------------------
st.set_page_config(
    page_title="Σωκράτης — AI Tutor Γυμνασίου",
    page_icon=avatar_image,
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 2. Προσαρμοσμένο CSS (Light Mode + Εκπαιδευτικό Γαλάζιο Θέμα)
# -------------------------------------------------------------
st.markdown("""
<style>
    /* Κλείδωμα σε Light Mode για όλες τις συσκευές */
    :root {
        color-scheme: light !important;
    }
    
    /* Γαλάζιο φόντο */
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
    
    /* Πλαίσια μηνυμάτων συνομιλίας */
    .stChatMessage, [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #a8cfee !important;
        box-shadow: 0 4px 12px rgba(15, 60, 120, 0.08) !important;
        border-radius: 14px;
        margin-bottom: 0.5rem;
    }
    
    /* Έντονα σκούρα γράμματα & LaTeX */
    .stChatMessage *, [data-testid="stChatMessage"] *, .katex, .katex * {
        color: #0f172a !important;
    }
    
    /* Avatar Σωκράτη και Μαθητή */
    [data-testid="stChatMessage"] img {
        width: 48px !important;
        height: 48px !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    
    /* Κάτω μπάρα πληκτρολόγησης */
    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background: transparent !important;
    }
    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 1px solid #90bfe9 !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(15, 60, 120, 0.06);
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
        padding-bottom: 0.4rem;
    }
    
    .socratic-badge {
        background-color: #b9d8f6 !important;
        color: #0f3460 !important;
        padding: 4px 16px;
        border-radius: 14px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.3rem;
        border: 1px solid #97c2eb;
    }

    /* Κουμπιά γρήγορης βοήθειας */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid #9bc5ea;
        font-weight: 600;
    }
    
    /* Expander εικόνας */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid #a8cfee;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. Μόνιμη Αποθήκευση & Ανάκτηση API Key
# -------------------------------------------------------------
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

# Επικεφαλίδα Εφαρμογής
st.markdown(f"""
<div class="main-header">
    <span class="socratic-badge">Τάξη & Σκέψη</span>
    <h1 style="margin: 0.2rem 0;">Σωκράτης</h1>
    <p style="color:#334155;font-size:0.95rem;margin-top:2px;"><i>«Το να γνωρίζεις ότι δεν γνωρίζεις είναι το πρώτο βήμα της σοφίας.»</i></p>
</div>
""", unsafe_allow_html=True)

# Αν ΔΕΝ υπάρχει αποθηκευμένο κλειδί, το ζητάμε μία φορά
if not api_key:
    st.markdown("---")
    st.info("👋 **Καλωσήρθατε!** Επικολλήστε παρακάτω το Gemini API Key **μία φορά** (θα αποθηκευτεί μόνιμα):")
    
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

# -------------------------------------------------------------
# 4. Μοντέλα AI & Πλαϊνή Στήλη Επιλογών
# -------------------------------------------------------------
FAST_CHAT_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest"
]
active_model = "gemini-3.5-flash-lite"

with st.sidebar:
    # Εμφάνιση avatar σε κατάλληλη διάσταση
    if os.path.exists(avatar_image):
        col_l, col_img, col_r = st.columns([1, 4, 1])
        with col_img:
            st.image(avatar_image, width=150)
    st.markdown("<h2 style='text-align:center;margin-top:0.2rem;margin-bottom:0.5rem;'>Σωκράτης</h2>", unsafe_allow_html=True)
    
    # 1. Επιλογή Τάξης Γυμνασίου
    GYMNASIO_GRADES = [
        "Α' Γυμνασίου",
        "Β' Γυμνασίου",
        "Γ' Γυμνασίου"
    ]
    selected_grade = st.selectbox(
        "🏫 Τάξη:",
        GYMNASIO_GRADES,
        index=0,
        help="Προσαρμόζει αυτόματα το λεξιλόγιο και την ύλη στο κατάλληλο επίπεδο."
    )

    # 2. Επιλογή Μαθήματος
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
    
    # Μετρητής Βημάτων Στοχασμού
    if "messages" in st.session_state:
        user_turns = len([m for m in st.session_state.messages if m["role"] == "user"])
    else:
        user_turns = 0
    st.metric(label="🧠 Βήματα Στοχασμού", value=user_turns)

    # Κουμπί Επαναφοράς / Νέας Συζήτησης
    if st.button("🔄 Νέα Συζήτηση", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.current_image = None
        st.session_state.pending_prompt = None
        st.rerun()

    # Εξαγωγή Σημειώσεων Μελέτης (Download Chat)
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        notes_md = f"# 📜 Σημειώσεις Μελέτης — Σωκράτης AI Tutor\n\n"
        notes_md += f"- **Ημερομηνία:** {datetime.date.today().strftime('%d/%m/%Y')}\n"
        notes_md += f"- **Τάξη:** {selected_grade}\n"
        notes_md += f"- **Μάθημα:** {selected_subject}\n\n"
        notes_md += "---\n\n"
        for m in st.session_state.messages:
            sender = "🎓 Μαθητής" if m["role"] == "user" else "🧔 Σωκράτης"
            notes_md += f"### {sender}\n{m['content']}\n\n"
        
        st.download_button(
            label="📥 Λήψη Σημειώσεων (.md)",
            data=notes_md.encode("utf-8"),
            file_name=f"sokrates_notes_{selected_grade[:2]}_{selected_subject.split()[1]}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with st.expander("💡 Οδηγίες για μαθητές"):
        st.caption("""
        * **Γράψε την απορία σου** ή φωτογράφισε την άσκηση.
        * **Δεν δίνω έτοιμες λύσεις!** Σε καθοδηγώ με ερωτήσεις.
        * Μη φοβάσαι τα λάθη — μέσα από αυτά μαθαίνουμε.
        * Πάτα **«Άκουσε τον Σωκράτη»** για να ακούσεις την απάντηση δυνατά!
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

# -------------------------------------------------------------
# 5. Αρχικοποίηση Ιστορικού Μηνυμάτων
# -------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# Μήνυμα υποδοχής προσαρμοσμένο στην τάξη
if len(st.session_state.messages) == 0:
    welcome_text = (
        f"Χαίρε! Είμαι ο **Σωκράτης**. Βλέπω ότι είσαι στην **{selected_grade}** και ασχολείσαι με το μάθημα: "
        f"**{selected_subject}**.\n\n"
        f"Ποιο θέμα ή ποια άσκηση σε δυσκολεύει σήμερα; Μπορείς να μου γράψεις την απορία σου ή να ανεβάσεις φωτογραφία από το βιβλίο σου!"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})

# -------------------------------------------------------------
# 6. Εμφάνιση Μηνυμάτων & Λειτουργία Text-to-Speech
# -------------------------------------------------------------
def render_tts_widget(text_content):
    """Ενσωματώνει κουμπί φωνητικής ανάγνωσης με το Web Speech API του browser"""
    clean_text = text_content.replace('"', '\\"').replace("'", "\\'").replace("\n", " ").replace("`", "")
    html_code = f"""
    <div style="margin-top: 4px; margin-bottom: 2px;">
        <button id="tts_btn" onclick="toggleSpeech()" style="
            background: #e6f2fc;
            color: #0f3460;
            border: 1px solid #9dc3e6;
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 0.80rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s ease;
        ">
            🔊 Άκουσε τον Σωκράτη
        </button>
    </div>
    <script>
    let isSpeaking = false;
    function toggleSpeech() {{
        if (!('speechSynthesis' in window)) {{
            alert('Ο περιηγητής δεν υποστηρίζει φωνητική ανάγνωση.');
            return;
        }}
        const btn = document.getElementById('tts_btn');
        if (isSpeaking) {{
            window.speechSynthesis.cancel();
            isSpeaking = false;
            btn.innerHTML = '🔊 Άκουσε τον Σωκράτη';
            return;
        }}
        window.speechSynthesis.cancel();
        const text = "{clean_text}";
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = 'el-GR';
        utter.rate = 0.95;
        utter.onstart = function() {{
            isSpeaking = true;
            btn.innerHTML = '⏹️ Διακοπή Ομιλίας';
        }};
        utter.onend = function() {{
            isSpeaking = false;
            btn.innerHTML = '🔊 Άκουσε τον Σωκράτη';
        }};
        utter.onerror = function() {{
            isSpeaking = false;
            btn.innerHTML = '🔊 Άκουσε τον Σωκράτη';
        }};
        window.speechSynthesis.speak(utter);
    }}
    </script>
    """
    components.html(html_code, height=36)

# Εμφάνιση ιστορικού
for i, msg in enumerate(st.session_state.messages):
    msg_avatar = avatar_image if msg["role"] == "assistant" else "🎓"
    with st.chat_message(msg["role"], avatar=msg_avatar):
        # Αν το μήνυμα είχε εικόνα, την εμφανίζουμε
        if "image_bytes" in msg and msg["image_bytes"]:
            st.image(msg["image_bytes"], caption="📷 Φωτογραφία άσκησης", width=280)
        st.markdown(msg["content"])
        
        # Εμφάνιση κουμπιού ανάγνωσης μόνο στο τελευταίο μήνυμα του Σωκράτη
        if msg["role"] == "assistant" and i == len(st.session_state.messages) - 1:
            render_tts_widget(msg["content"])

# -------------------------------------------------------------
# 7. Πολυτροπικότητα (Multimodal): Ανέβασμα Εικόνας / Κάμερα
# -------------------------------------------------------------
with st.expander("📷 Φωτογράφισε ή ανέβασε άσκηση (Βιβλίο / Τετράδιο)", expanded=False):
    col_up1, col_up2 = st.columns([3, 2])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Ανέβασε αρχείο εικόνας:",
            type=["jpg", "jpeg", "png", "webp"],
            key="img_file_uploader",
            help="Φωτογράφισε την άσκηση από το σχολικό βιβλίο ή το τετράδιό σου"
        )
        camera_file = st.camera_input("Ή τράβηξε φωτογραφία με την κάμερα:", key="cam_file_uploader")
        
        # Επιλογή της πιο πρόσφατης εικόνας
        selected_img = uploaded_file if uploaded_file is not None else camera_file
        if selected_img is not None:
            st.session_state.current_image = {
                "bytes": selected_img.getvalue(),
                "type": selected_img.type or "image/jpeg"
            }
    
    with col_up2:
        if st.session_state.current_image:
            st.image(st.session_state.current_image["bytes"], caption="Προεπισκόπηση επιλεγμένης άσκησης", use_container_width=True)
            if st.button("❌ Αφαίρεση Εικόνας", use_container_width=True):
                st.session_state.current_image = None
                st.rerun()

# -------------------------------------------------------------
# 8. Κουμπιά Γρήγορης Βοήθειας (Quick Action Chips)
# -------------------------------------------------------------
st.write("")
col_h1, col_h2, col_h3, col_h4 = st.columns(4)

with col_h1:
    if st.button("💡 Ένα στοιχείο (hint)", use_container_width=True):
        st.session_state.pending_prompt = "Μπορείς να μου δώσεις ένα μικρό στοιχείο (hint) για να με βοηθήσεις να σκεφτώ το επόμενο βήμα;"
        st.rerun()

with col_h2:
    if st.button("🔍 Κάν' το πιο απλό", use_container_width=True):
        st.session_state.pending_prompt = "Δυσκολεύτηκα να το καταλάβω. Μπορείς να μου το θέσεις με πιο απλό τρόπο ή πιο απλή ερώτηση;"
        st.rerun()

with col_h3:
    if st.button("🍎 Παράδειγμα", use_container_width=True):
        st.session_state.pending_prompt = "Μπορείς να μου δώσεις ένα παράδειγμα από την καθημερινή ζωή για να το φανταστώ καλύτερα;"
        st.rerun()

with col_h4:
    if st.button("✅ Το βρήκα, έλεγξέ με!", use_container_width=True):
        st.session_state.pending_prompt = "Νομίζω ότι έφτασα στη λύση! Μπορείς να με ελέγξεις αν το σκέφτηκα σωστά;"
        st.rerun()

# -------------------------------------------------------------
# 9. Κατασκευή Σωκρατικού System Prompt
# -------------------------------------------------------------
grade_guidelines = {
    "Α' Γυμνασίου": "Ο μαθητής είναι στην Α' Γυμνασίου (12-13 ετών). Χρησιμοποίησε πολύ απλή, φιλική γλώσσα, εισαγωγικές έννοιες, επιβράβευση σε κάθε προσπάθεια και απόφυγε προχωρημένη ορολογία.",
    "Β' Γυμνασίου": "Ο μαθητής είναι στη Β' Γυμνασίου (13-14 ετών). Ενθάρρυνε τη λογική σύνδεση με προηγούμενες γνώσεις, βαθύτερους συλλογισμούς και χρήση των κατάλληλων όρων.",
    "Γ' Γυμνασίου": "Ο μαθητής είναι στη Γ' Γυμνασίου (14-15 ετών). Προετοιμάζεται για το Λύκειο. Χρησιμοποίησε ακριβή επιστημονική και φιλολογική ορολογία, αυστηρότερη μεθοδολογία και βαθύτερη ανάλυση."
}

system_instruction = f"""
Είσαι ο Σωκράτης, ο αρχαίος Έλληνας φιλόσοφος, που λειτουργεί ως υποστηρικτικός καθοδηγητής και AI Tutor για μαθητές Γυμνασίου στην Ελλάδα.
Είσαι πρόσχαρος, σοφός, υπομονετικός και χαμογελαστός.
Τάξη Μαθητή: {selected_grade}.
{grade_guidelines.get(selected_grade, "")}
Μάθημα: "{selected_subject}".

ΑΠΑΡΑΒΙΑΣΤΟΙ ΚΑΝΟΝΕΣ:
1. ΠΟΤΕ μην δίνεις έτοιμη τη λύση, το τελικό αποτέλεσμα ή έτοιμη απάντηση.
2. Εφάρμοσε τη Σωκρατική Μαιευτική Μέθοδο: απάντησε με 1-2 σύντομες, διερευνητικές ερωτήσεις που καθοδηγούν τη σκέψη του μαθητή.
3. Αν ο μαθητής στείλει φωτογραφία άσκησης, διάβασε προσεκτικά την εκφώνηση/σχήμα και κάνε ερώτηση για το πρώτο δεδομένο που παρατηρεί.
4. Αν ο μαθητής πει "όχι" ή "δεν ξέρω", δώσε μία πολύ απλή εξήγηση-βάση και κάνε μια ευκολότερη ερώτηση.
5. Σύντομες, άμεσες αποκρίσεις (1-3 προτάσεις) ώστε ο διάλογος να είναι ζωντανός.
6. Χρησιμοποίησε LaTeX για μαθηματικά και φυσική (π.χ. $2 \\cdot 3^3$ ή $F = m \\cdot a$).
7. Όταν ο μαθητής φτάσει μόνος του στη σωστή λύση, επιβράβευσέ τον θερμά ("Εύγε!", "Μπράβο!", "Ακριβώς!") για την ανακάλυψή του.
"""

# -------------------------------------------------------------
# 10. Επεξεργασία Εισόδου (Κείμενο ή Quick Action Chip ή Φωτογραφία)
# -------------------------------------------------------------
chat_input_val = st.chat_input("Γράψε την απάντηση ή την ερώτησή σου εδώ...")

# Έλεγχος αν υποβλήθηκε prompt είτε από το πληκτρολόγιο είτε από τα Quick Action Chips
prompt = None
if chat_input_val:
    prompt = chat_input_val
elif st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    # Έλεγχος αν επισυνάπτεται ενεργή φωτογραφία
    active_img_data = st.session_state.current_image
    
    # Εμφάνιση μηνύματος μαθητή
    with st.chat_message("user", avatar="🎓"):
        if active_img_data:
            st.image(active_img_data["bytes"], caption="📷 Επισυναπτόμενη εικόνα", width=280)
        st.markdown(prompt)

    # Εμφάνιση απάντησης Σωκράτη με streaming
    with st.chat_message("assistant", avatar=avatar_image):
        response_container = st.empty()
        full_response = ""
        success = False

        models_to_try = [active_model] + [m for m in FAST_CHAT_MODELS if m != active_model]

        try:
            client = genai.Client(api_key=api_key)
            
            # Δόμηση ιστορικού κειμένου για το μοντέλο
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

            # Προετοιμασία περιεχομένου για αποστολή (πολυτροπικό αν υπάρχει εικόνα)
            message_parts = []
            if active_img_data:
                message_parts.append(
                    types.Part.from_bytes(
                        data=active_img_data["bytes"],
                        mime_type=active_img_data["type"]
                    )
                )
            message_parts.append(types.Part.from_text(text=prompt))

            # Zero-delay failover ανάμεσα σε μοντέλα
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
                    
                    response = chat.send_message_stream(message_parts)
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
                        
                        # Καταγραφή στο ιστορικό
                        user_msg_record = {"role": "user", "content": prompt}
                        if active_img_data:
                            user_msg_record["image_bytes"] = active_img_data["bytes"]
                            # Καθαρίζουμε την εικόνα μετά την αποστολή για να μην επαναστέλνεται σε κάθε ερώτηση
                            st.session_state.current_image = None
                        
                        st.session_state.messages.append(user_msg_record)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
                        # Έλεγχος για Σωκρατική Επιβράβευση (Gamification)
                        praise_words = ["εύγε", "μπράβο", "συγχαρητήρια", "πολύ σωστά", "ακριβώς", "το βρήκες", "εξαιρετική σκέψη"]
                        if any(w in full_response.lower() for w in praise_words):
                            st.balloons()
                            st.success("🌟 **Εύγε!** Κατέκτησες τη γνώση με τη δική σου σκέψη!")
                        
                        # Εμφάνιση TTS κουμπιού
                        render_tts_widget(full_response)
                        break
                except Exception:
                    continue

            if not success:
                st.warning("⚠️ Προσωρινό πρόβλημα επικοινωνίας με το μοντέλο AI. Παρακαλώ ξαναστείλτε την ερώτηση.")

        except Exception as e:
            st.error(f"⚠️ Παρουσιάστηκε πρόβλημα επικοινωνίας: {e}")
