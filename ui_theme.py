"""
ui_theme.py — Προσαρμοσμένο CSS, Θέμα Εμφάνισης, Screen Wake Lock & Οπτικά Εφέ
για τον «Σωκράτη AI Tutor Γυμνασίου».

Περιλαμβάνει:
1. Πλήρες γαλάζιο σχολικό θέμα CSS (Light Mode, καθαρότητα, απόκρυψη περιττών μενού).
2. Screen Wake Lock & Keep-Alive για αποτροπή αναστολής λειτουργίας των σχολικών tablets.
3. Γιορτινά βεγγαλικά υποδοχής (Web Audio API & HTML5 Canvas).
4. Οπτικά badges, κάρτες ειδοποιήσεων ανάκτησης συνεδρίας και πρωτοκόλλου κρίσης.
"""

# pyrefly: ignore [missing-import]
import streamlit as st
import streamlit.components.v1 as components

CUSTOM_CSS = """
<style>
    :root {
        color-scheme: light !important;
    }
    
    /* 1. Γέμισμα με γαλάζιο της κορυφής του παραθύρου */
    html, body, .stApp {
        background-color: #d3e6fa !important;
        background: linear-gradient(180deg, #d3e6fa 0%, #bddcf7 100%) !important;
        color: #0f172a !important;
    }
    header,
    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    .stAppHeader {
        background-color: transparent !important;
        background: transparent !important;
        height: 2.75rem !important;
        display: flex !important;
        align-items: center !important;
        z-index: 99999 !important;
    }
    [data-testid="stToolbar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: transparent !important;
    }
    /* Κουμπί ανοίγματος/ανάπτυξης μενού (Βέλος) */
    [data-testid="stExpandSidebarButton"],
    button[data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        cursor: pointer !important;
        background-color: #b0d3f4 !important;
        border: 1.5px solid #84bee7 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(15, 60, 120, 0.18) !important;
        padding: 4px 8px !important;
        color: #082f56 !important;
        z-index: 999999 !important;
    }
    [data-testid="stExpandSidebarButton"] *,
    [data-testid="stSidebarCollapsedControl"] * {
        color: #082f56 !important;
        fill: #082f56 !important;
    }
    /* Απόκρυψη Deploy button, MainMenu και περιττών στοιχείων κεφαλίδας */
    [data-testid="stDeployButton"],
    .stDeployButton,
    button[data-testid="stDeployButton"],
    [data-testid="stToolbarActions"],
    .stToolbarActions,
    [data-testid="stMainMenu"],
    #MainMenu,
    [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Αποκλειστικό Light Mode: Πλήρης εξουδετέρωση Dark Mode */
    @media (prefers-color-scheme: dark) {
        :root, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"] {
            color-scheme: light !important;
            background-color: #d3e6fa !important;
            color: #082f56 !important;
        }
    }

    /* 2. Κύριο περιεχόμενο: Άμεση προβολή από την κορυφή χωρίς περιττό κενό */
    .block-container,
    [data-testid="block-container"],
    [data-testid="stMainBlockContainer"],
    .main .block-container {
        padding-top: 0.7rem !important;
        margin-top: 0rem !important;
        padding-bottom: 6.5rem !important;
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
        max-width: 960px !important;
    }
    iframe[height="0"] {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Ισορροπημένες αποστάσεις (gaps) για άνετη πλοήγηση */
    [data-testid="stVerticalBlock"],
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        gap: 0.60rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0.55rem !important;
    }
    
    /* 3. Πλαϊνή στήλη: Αναδυόμενη (Slide-in από αριστερά προς τα δεξιά) */
    [data-testid="stSidebar"] {
        background-color: #b0d3f4 !important;
        border-right: 1px solid #90bfe9 !important;
    }
    [data-testid="stSidebarHeader"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        padding: 0.15rem 0.4rem 0rem 0.4rem !important;
        height: auto !important;
        min-height: 0 !important;
        background: transparent !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        color: #082f56 !important;
        background-color: #c4e1f7 !important;
        border: 1px solid #84bee7 !important;
        border-radius: 6px !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        color: #082f56 !important;
        fill: #082f56 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"],
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
        gap: 0.35rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #0f172a !important;
    }

    /* Αρμονικά μπλε κουμπιά σε όλη την εφαρμογή & καθαρό κείμενο */
    .stApp button[kind="primary"],
    .stApp button[data-testid="stBaseButton-primary"],
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        border: 1.5px solid #1e3a8a !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(29, 78, 216, 0.22) !important;
    }
    .stApp button[kind="primary"] p,
    .stApp button[kind="primary"] span,
    .stApp button[data-testid="stBaseButton-primary"] p,
    .stApp button[data-testid="stBaseButton-primary"] span,
    [data-testid="stSidebar"] button[kind="primary"] p,
    [data-testid="stSidebar"] button[kind="primary"] span,
    [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p,
    [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
        background-color: #d8ebfb !important;
        border: 1.5px solid #8bbfe6 !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button p {
        font-size: 0.78rem !important;
        white-space: nowrap !important;
    }

    /* Ετικέτες πεδίων (Labels) - ευανάγνωστες */
    [data-testid="stWidgetLabel"] {
        min-height: auto !important;
        margin-bottom: 0.15rem !important;
    }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        font-size: 0.86rem !important;
        margin-bottom: 0.15rem !important;
        font-weight: 600 !important;
    }

    /* 4. Όλα τα Dropdowns & Selectbox σε απαλό γαλάζιο & λειτουργικό ύψος */
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] {
        background-color: #cce5f9 !important;
        border-color: #8bbfe6 !important;
        color: #0f172a !important;
        border-radius: 10px !important;
        min-height: 2.35rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    div[data-baseweb="select"] * {
        color: #0f172a !important;
        font-size: 0.88rem !important;
    }
    div[data-baseweb="popover"],
    ul[role="listbox"],
    li[role="option"] {
        background-color: #d7ecfa !important;
        color: #0f172a !important;
    }

    /* 5. Μηνύματα συνομιλίας: ευρύχωρα, ευανάγνωστα και καλαίσθητα */
    .stChatMessage, [data-testid="stChatMessage"] {
        background-color: #e4f1fb !important;
        border: 1px solid #a3cef0 !important;
        box-shadow: 0 2px 8px rgba(15, 60, 120, 0.06) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.05rem !important;
        margin-bottom: 0.5rem !important;
    }
    .stChatMessage p, [data-testid="stChatMessage"] p {
        font-size: 0.95rem !important;
        line-height: 1.55 !important;
        margin-bottom: 0.35rem !important;
    }
    .stChatMessage *, [data-testid="stChatMessage"] *, .katex, .katex * {
        color: #0f172a !important;
    }
    [data-testid="stChatMessage"] img {
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
        padding-top: 0 !important;
    }

    /* 6. Κάτω μπάρα πληκτρολόγησης (stChatInput) με καθαρό αδιαφανές φόντο */
    [data-testid="stBottom"] {
        background: linear-gradient(to top, #c3def7 82%, rgba(195, 222, 247, 0) 100%) !important;
        padding-top: 1.0rem !important;
        padding-bottom: 0.7rem !important;
    }
    [data-testid="stBottom"] > div {
        background: transparent !important;
    }
    [data-testid="stChatInput"] {
        background-color: #d6ecfb !important;
        border: 1.5px solid #84bee7 !important;
        border-radius: 12px !important;
        box-shadow: 0 3px 10px rgba(15, 60, 120, 0.07) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #0f172a !important;
        background-color: #d6ecfb !important;
        font-size: 0.94rem !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #476685 !important;
    }

    /* 7. Όλα τα κουμπιά: άνετο μέγεθος κλικ */
    .stButton > button,
    a[data-testid="stLinkButton"] {
        background-color: #d5ebfb !important;
        color: #0b2f56 !important;
        border: 1.5px solid #94c4ea !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        min-height: 2.35rem !important;
        padding: 0.4rem 0.85rem !important;
        box-shadow: 0 2px 5px rgba(15, 60, 120, 0.05);
        transition: all 0.15s ease !important;
        text-decoration: none !important;
    }
    .stButton > button:hover,
    a[data-testid="stLinkButton"]:hover {
        background-color: #bfdff7 !important;
        border-color: #6daae0 !important;
        color: #072342 !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #ff5252 !important;
        color: #ffffff !important;
        border: none !important;
    }

    /* 8. Πτυσσόμενα πλαίσια (Expanders) */
    [data-testid="stExpander"] {
        background-color: #cde6f9 !important;
        border: 1px solid #93c4eb !important;
        border-radius: 10px !important;
        margin-bottom: 0.4rem !important;
    }
    [data-testid="stExpander"] summary {
        background-color: #cde6f9 !important;
        color: #0b2f56 !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        padding: 0.4rem 0.7rem !important;
        min-height: auto !important;
    }
    [data-testid="stExpander"] div[role="region"] {
        background-color: #d8edf9 !important;
        border-radius: 0 0 10px 10px !important;
        padding: 0.55rem 0.75rem !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: #d6ecfb !important;
        border: 1px dashed #7db4dc !important;
        padding: 0.6rem !important;
    }

    /* 9. Καλαίσθητη & Ισορροπημένη Κεφαλίδα */
    .main-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px;
        padding: 0.1rem 0 0.45rem 0;
        margin-bottom: 0.45rem;
        border-bottom: 1.5px solid #a3cbee;
    }
    .main-header-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .main-header h1 {
        margin: 0 !important;
        font-size: 1.7rem !important;
        line-height: 1.2 !important;
        color: #0c335e !important;
        font-weight: 800 !important;
    }
    .socratic-badge {
        background-color: #b9d8f6 !important;
        color: #0f3460 !important;
        padding: 3px 11px;
        border-radius: 12px;
        font-size: 0.80rem;
        font-weight: 700;
        border: 1px solid #97c2eb;
    }
    .header-quote {
        color: #274d75;
        font-size: 0.85rem;
        font-style: italic;
        margin: 0;
    }
    
    /* Κόκκινο Καμπανάκι Παραβίασης */
    @keyframes pulse-bell {
        0% { transform: scale(1); }
        50% { transform: scale(1.15); }
        100% { transform: scale(1); }
    }
    .red-bell-alert {
        background: #fee2e2;
        border: 2px solid #ef4444;
        border-radius: 14px;
        padding: 12px 18px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #991b1b;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.2);
    }
    .red-bell-icon {
        font-size: 2rem;
        animation: pulse-bell 1.2s infinite ease-in-out;
        display: inline-block;
    }
    
    .lockout-card {
        background: #ffffff;
        border: 3px solid #dc2626;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        color: #991b1b;
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.25);
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
    .lockout-card h2 {
        color: #dc2626 !important;
        margin-top: 0.5rem;
    }

    /* 10. Απαλά παστέλ χρώματα & ισορροπημένη διάταξη αριστερού μενού */
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        height: 2.2rem !important;
        min-height: 2.2rem !important;
        padding: 0.35rem 0.6rem 0 0.6rem !important;
        margin-bottom: 0.15rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 0.35rem !important;
        padding-bottom: 0.5rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.52rem !important;
    }
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] a[data-testid="stLinkButton"] {
        min-height: 2.3rem !important;
        padding: 0.34rem 0.78rem !important;
        font-size: 0.87rem !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        min-height: 2.3rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        margin-bottom: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        padding: 0.4rem 0.72rem !important;
        font-size: 0.87rem !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_teacher button[kind="secondary"],
    [data-testid="stSidebar"] .st-key-side_btn_teacher button[data-testid="stBaseButton-secondary"] {
        background-color: #86efac !important;
        border: 1.5px solid #16a34a !important;
        color: #052e16 !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_teacher button[kind="secondary"]:hover,
    [data-testid="stSidebar"] .st-key-side_btn_teacher button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #4ade80 !important;
        border-color: #15803d !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_teacher button[kind="primary"],
    [data-testid="stSidebar"] .st-key-side_btn_teacher button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
        border: 1.5px solid #14532d !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_teacher button[kind="primary"] p,
    [data-testid="stSidebar"] .st-key-side_btn_teacher button[data-testid="stBaseButton-primary"] p {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-testid="stLinkButton"] a,
    [data-testid="stSidebar"] a[data-testid="stLinkButton"] {
        background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%) !important;
        border: 1.5px solid #94a3b8 !important;
        color: #1e293b !important;
        box-shadow: 0 2px 6px rgba(71, 85, 105, 0.14) !important;
    }
    [data-testid="stSidebar"] [data-testid="stLinkButton"] a:hover,
    [data-testid="stSidebar"] a[data-testid="stLinkButton"]:hover {
        background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%) !important;
        border-color: #64748b !important;
        color: #0f172a !important;
    }
    [data-testid="stSidebar"] .st-key-side_subject_select div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .st-key-side_subject_select div[data-baseweb="select"] {
        background-color: #d1fae5 !important;
        border-color: #6ee7b7 !important;
        color: #064e3b !important;
    }
    [data-testid="stSidebar"] .st-key-side_subject_select div[data-baseweb="select"] * {
        color: #064e3b !important;
    }
    [data-testid="stSidebar"] .st-key-side_exp_yli [data-testid="stExpander"],
    [data-testid="stSidebar"] .st-key-side_exp_yli [data-testid="stExpander"] summary {
        background-color: #ddd6fe !important;
        border-color: #a78bfa !important;
        color: #3b0764 !important;
    }
    [data-testid="stSidebar"] .st-key-side_exp_yli [data-testid="stExpander"] div[role="region"] {
        background-color: #ede9fe !important;
    }
    [data-testid="stSidebar"] .st-key-side_exp_cards [data-testid="stExpander"],
    [data-testid="stSidebar"] .st-key-side_exp_cards [data-testid="stExpander"] summary {
        background-color: #fed7aa !important;
        border-color: #fb923c !important;
        color: #7c2d12 !important;
    }
    [data-testid="stSidebar"] .st-key-side_exp_cards [data-testid="stExpander"] div[role="region"] {
        background-color: #ffedd5 !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_duel_open button {
        background: linear-gradient(135deg, #facc15 0%, #d97706 100%) !important;
        border: 1.5px solid #92400e !important;
        color: #451a03 !important;
        padding-left: 0.35rem !important;
        padding-right: 0.35rem !important;
        box-shadow: 0 3px 10px rgba(217, 119, 6, 0.3) !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_duel_open button:hover {
        background: linear-gradient(135deg, #eab308 0%, #b45309 100%) !important;
        border-color: #78350f !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_duel_open button p {
        color: #451a03 !important;
        font-weight: 800 !important;
        font-size: 0.77rem !important;
        white-space: nowrap !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_duel_locked button {
        background: linear-gradient(135deg, #fde68a 0%, #fcd34d 100%) !important;
        border: 1.5px solid #b45309 !important;
        color: #451a03 !important;
        padding-left: 0.35rem !important;
        padding-right: 0.35rem !important;
        opacity: 0.94 !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_duel_locked button p {
        color: #451a03 !important;
        font-weight: 700 !important;
        font-size: 0.77rem !important;
        white-space: nowrap !important;
    }
    [data-testid="stSidebar"] .st-key-side_exp_settings [data-testid="stExpander"],
    [data-testid="stSidebar"] .st-key-side_exp_settings [data-testid="stExpander"] summary {
        background-color: #cbd8e8 !important;
        border-color: #94a3b8 !important;
        color: #0f172a !important;
    }
    [data-testid="stSidebar"] .st-key-side_exp_settings [data-testid="stExpander"] div[role="region"] {
        background-color: #e2ecf5 !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_transparency button {
        background-color: #fbcfe8 !important;
        border: 1.5px solid #f472b6 !important;
        color: #831843 !important;
    }
    [data-testid="stSidebar"] .st-key-side_btn_transparency button:hover {
        background-color: #f9a8d4 !important;
        border-color: #ec4899 !important;
    }

    /* 11. Χρώματα κουμπιών παιχνιδιών */
    .st-key-btn_open_game_duel button { background-color: #2563eb !important; border: 1.5px solid #1d4ed8 !important; color: #ffffff !important; }
    .st-key-btn_open_game_duel button:hover { background-color: #1d4ed8 !important; }
    .st-key-btn_open_game_detective button { background-color: #7c3aed !important; border: 1.5px solid #6d28d9 !important; color: #ffffff !important; }
    .st-key-btn_open_game_detective button:hover { background-color: #6d28d9 !important; }
    .st-key-btn_open_game_myth button { background-color: #059669 !important; border: 1.5px solid #047857 !important; color: #ffffff !important; }
    .st-key-btn_open_game_myth button:hover { background-color: #047857 !important; }
    .st-key-btn_open_game_escape button { background-color: #d97706 !important; border: 1.5px solid #b45309 !important; color: #ffffff !important; }
    .st-key-btn_open_game_escape button:hover { background-color: #b45309 !important; }
    .st-key-btn_open_game_ladder5 button { background-color: #0d9488 !important; border: 1.5px solid #0f766e !important; color: #ffffff !important; }
    .st-key-btn_open_game_ladder5 button:hover { background-color: #0f766e !important; }
    .st-key-btn_open_game_duel button p,
    .st-key-btn_open_game_detective button p,
    .st-key-btn_open_game_myth button p,
    .st-key-btn_open_game_escape button p,
    .st-key-btn_open_game_ladder5 button p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
</style>
"""

def apply_custom_theme():
    """Εφαρμόζει το πλήρες γαλάζιο θέμα CSS."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def apply_wake_lock_and_keepalive():
    """Ενεργοποιεί Screen Wake Lock & Keep-Alive pings για σχολικά tablets."""
    keepalive_script = """
    <script>
    // 1. Screen Wake Lock: Αποτρέπει το σβήσιμο της οθόνης στα tablets κατά το μάθημα
    let wakeLock = null;
    async function acquireWakeLock() {
        try {
            if ('wakeLock' in navigator) {
                wakeLock = await navigator.wakeLock.request('screen');
            }
        } catch (e) {}
    }
    acquireWakeLock();
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            acquireWakeLock();
        }
    });

    // 2. WebSocket Keep-Alive: Αποτρέπει το κλείσιμο της σύνδεσης Streamlit από αδράνεια Wi-Fi
    setInterval(() => {
        try {
            fetch(window.location.href, { method: 'HEAD', cache: 'no-store' }).catch(() => {});
        } catch (e) {}
    }, 20000);
    </script>
    """
    components.html(keepalive_script, height=0, width=0)

def render_welcome_fireworks():
    """Εμφανίζει απαλά, γιορτινά βεγγαλικά με ήχο μία φορά στο άνοιγμα του Σωκράτη."""
    components.html(
        """
        <script>
        (function() {
            const doc = window.parent ? window.parent.document : document;
            const win = window.parent || window;
            if (doc.getElementById("socrates_fireworks_canvas")) return;

            const canvas = doc.createElement("canvas");
            canvas.id = "socrates_fireworks_canvas";
            canvas.style.position = "fixed";
            canvas.style.top = "0";
            canvas.style.left = "0";
            canvas.style.width = "100vw";
            canvas.style.height = "100vh";
            canvas.style.pointerEvents = "none";
            canvas.style.zIndex = "999999";
            doc.body.appendChild(canvas);

            const ctx = canvas.getContext("2d");
            function resize() {
                canvas.width = win.innerWidth;
                canvas.height = win.innerHeight;
            }
            resize();

            const AudioCtx = win.AudioContext || win.webkitAudioContext;
            let audioCtx = null;
            function playFireworkPop(delaySec) {
                if (!AudioCtx) return;
                try {
                    if (!audioCtx) audioCtx = new AudioCtx();
                    if (audioCtx.state === "suspended") {
                        audioCtx.resume().catch(() => {});
                    }
                    const now = audioCtx.currentTime + delaySec;

                    const osc = audioCtx.createOscillator();
                    const oscGain = audioCtx.createGain();
                    osc.type = "triangle";
                    osc.frequency.setValueAtTime(170, now);
                    osc.frequency.exponentialRampToValueAtTime(42, now + 0.18);
                    oscGain.gain.setValueAtTime(0.18, now);
                    oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
                    osc.connect(oscGain);
                    oscGain.connect(audioCtx.destination);
                    osc.start(now);
                    osc.stop(now + 0.24);

                    const bufferSize = Math.floor(audioCtx.sampleRate * 0.35);
                    const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
                    const output = noiseBuffer.getChannelData(0);
                    for (let i = 0; i < bufferSize; i++) {
                        output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.35));
                    }
                    const whiteNoise = audioCtx.createBufferSource();
                    whiteNoise.buffer = noiseBuffer;
                    const filter = audioCtx.createBiquadFilter();
                    filter.type = "bandpass";
                    filter.frequency.setValueAtTime(1600, now);
                    const noiseGain = audioCtx.createGain();
                    noiseGain.gain.setValueAtTime(0.11, now);
                    noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.34);
                    whiteNoise.connect(filter);
                    filter.connect(noiseGain);
                    noiseGain.connect(audioCtx.destination);
                    whiteNoise.start(now);
                } catch (e) {}
            }

            const unlockOnce = function() {
                if (audioCtx && audioCtx.state === "suspended") {
                    audioCtx.resume().then(() => playFireworkPop(0)).catch(() => {});
                }
                doc.removeEventListener("click", unlockOnce);
                doc.removeEventListener("touchstart", unlockOnce);
            };
            doc.addEventListener("click", unlockOnce, { once: true });
            doc.addEventListener("touchstart", unlockOnce, { once: true });

            const colors = ["#fbbf24", "#38bdf8", "#f472b6", "#34d399", "#a78bfa", "#fb923c"];
            const particles = [];

            function createBurst(cx, cy) {
                const count = 42;
                const baseColor = colors[Math.floor(Math.random() * colors.length)];
                for (let i = 0; i < count; i++) {
                    const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.25;
                    const speed = 2.2 + Math.random() * 4.5;
                    particles.push({
                        x: cx,
                        y: cy,
                        vx: Math.cos(angle) * speed,
                        vy: Math.sin(angle) * speed,
                        alpha: 1,
                        decay: 0.015 + Math.random() * 0.012,
                        radius: 2 + Math.random() * 2.5,
                        color: Math.random() > 0.35 ? baseColor : colors[Math.floor(Math.random() * colors.length)]
                    });
                }
            }

            const bursts = [
                { t: 100, x: 0.32, y: 0.28 },
                { t: 500, x: 0.68, y: 0.24 },
                { t: 950, x: 0.50, y: 0.20 },
                { t: 1350, x: 0.78, y: 0.34 }
            ];
            bursts.forEach((b, idx) => {
                setTimeout(() => {
                    createBurst(canvas.width * b.x, canvas.height * b.y);
                    playFireworkPop(0);
                }, b.t);
            });

            let startTime = performance.now();
            function animate(now) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                for (let i = particles.length - 1; i >= 0; i--) {
                    const p = particles[i];
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.06;
                    p.vx *= 0.985;
                    p.alpha -= p.decay;
                    if (p.alpha <= 0) {
                        particles.splice(i, 1);
                        continue;
                    }
                    ctx.save();
                    ctx.globalAlpha = p.alpha;
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }
                if (now - startTime < 3100 || particles.length > 0) {
                    win.requestAnimationFrame(animate);
                } else {
                    if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
                }
            }
            win.requestAnimationFrame(animate);
        })();
        </script>
        """,
        height=0,
    )

def render_recovery_banner():
    """Εμφανίζει ενημερωτική κάρτα & toast αυτόματης ανάκτησης συνομιλίας."""
    st.toast("✅ Η προηγούμενη συνομιλία σου ανακτήθηκε επιτυχώς!", icon="🔄")
    st.markdown("""
    <div style="background: #e0f2fe; border: 1.5px solid #38bdf8; border-radius: 10px; padding: 6px 12px; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.1rem;">🔄</span>
        <span style="color: #0369a1; font-weight: 700; font-size: 0.88rem;">Η συνομιλία σου ανακτήθηκε αυτόματα μετά την επανασύνδεση του tablet!</span>
    </div>
    """, unsafe_allow_html=True)

def render_crisis_alert_html() -> str:
    """Επιστρέφει το HTML προβολής τηλεφώνων υποστήριξης ανηλίκων & bullying."""
    return """
    <div style="background: #fef2f2; border: 2px solid #ef4444; border-radius: 14px; padding: 16px; margin-bottom: 1rem; color: #991b1b;">
        <h3>❤️ Δεν είσαι μόνος/η σου — Υπάρχουν άνθρωποι που μπορούν να σε βοηθήσουν άμεσα!</h3>
        <p>Αν αντιμετωπίζεις δυσκολίες, εκφοβισμό (bullying), πίεση ή νιώθεις στενοχώρια, μίλησε άμεσα στους γονείς σου, σε έναν εκπαιδευτικό ή κάλεσε <b>δωρεάν & ανώνυμα</b>:</p>
        <ul>
            <li>📞 <b>1056 — Εθνική Τηλεφωνική Γραμμή SOS</b> («Το Χαμόγελο του Παιδιού» — 24/7, Δωρεάν)</li>
            <li>📞 <b>116 111 — Ευρωπαϊκή Γραμμή Υποστήριξης Παιδιών & Εφήβων</b> (Δωρεάν)</li>
            <li>📞 <b>10306 — Γραμμή Ψυχοκοινωνικής Υποστήριξης</b> (24/7, Δωρεάν & Ανώνυμη)</li>
            <li>🌐 <b><a href="https://stop-bullying.gov.gr" target="_blank" style="color: #991b1b; text-decoration: underline;">stop-bullying.gov.gr</a></b> — Εθνική Πλατφόρμα κατά της Σχολικής Βίας</li>
        </ul>
    </div>
    """
