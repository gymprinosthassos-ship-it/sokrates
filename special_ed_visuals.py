"""
special_ed_visuals.py — Παιδαγωγικό Εποπτικό Υλικό & Οπτικές Κάρτες Ειδικής Αγωγής
για τον «Σωκράτη AI Tutor» (Γυμνάσιο).

Σχεδιασμένο ειδικά για μαθητές με Ειδικές Εκπαιδευτικές Ανάγκες (ΕΕΑ),
Μαθησιακές Δυσκολίες, ΔΕΠΥ και Νοητική Υστέρηση (Ελαφριά / Μέτρια).

Περιλαμβάνει:
1. Καθαρές, διανυσματικές SVG απεικονίσεις χωρίς γνωστικό θόρυβο (visual clutter).
2. Κείμενο Easy-to-Read (Εύκολο στην Ανάγνωση) με μικρές, απλές προτάσεις.
3. Χειροπιαστά αναλογικά παραδείγματα από την καθημερινή ζωή.
4. Αυτόματη αντιστοίχιση με βάση λέξεις-κλειδιά της συνομιλίας ή του μαθήματος.
"""

from typing import Dict, List, Optional
import unicodedata
import re

def _norm(text: str) -> str:
    """Καθαρίζει και κανονικοποιεί κείμενο για αναζήτηση λέξεων-κλειδιών."""
    if not text:
        return ""
    t = text.lower()
    t = unicodedata.normalize('NFD', t)
    t = "".join(c for c in t if unicodedata.category(c) != 'Mn')
    return t

PEDAGOGICAL_CARDS: Dict[str, dict] = {
    # =========================================================================
    # 📐 ΜΑΘΗΜΑΤΙΚΑ
    # =========================================================================
    "math_fractions": {
        "id": "math_fractions",
        "title": "🍕 Τα Κλάσματα (Μοιράζουμε σε Ίσα Μέρη)",
        "subject_tag": "Μαθηματικά",
        "keywords": ["κλασμα", "κλασματα", "παρονομαστη", "αριθμητη", "ισα μερη", "μισο", "τεταρτο", "διαιρεση", "1/4", "1/2", "3/4"],
        "svg": """<svg viewBox="0 0 540 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="540" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <!-- Πίτσα / Κύκλος χωρισμένος σε 4 μέρη -->
  <g transform="translate(85, 90)">
    <circle r="60" fill="#fef08a" stroke="#ca8a04" stroke-width="3"/>
    <!-- 4 κομμάτια -->
    <path d="M 0 0 L 0 -60 A 60 60 0 0 1 60 0 Z" fill="#f97316" stroke="#c2410c" stroke-width="2"/>
    <path d="M 0 0 L 60 0 A 60 60 0 0 1 0 60 Z" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
    <path d="M 0 0 L 0 60 A 60 60 0 0 1 -60 0 Z" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
    <path d="M 0 0 L -60 0 A 60 60 0 0 1 0 -60 Z" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
    <circle cx="26" cy="-26" r="5" fill="#dc2626"/>
    <circle cx="32" cy="-12" r="4.5" fill="#dc2626"/>
    <text x="30" y="-40" font-size="11" font-weight="bold" fill="#7c2d12" text-anchor="middle">1 μέρος</text>
  </g>
  <!-- Επεξήγηση Κλάσματος -->
  <g transform="translate(180, 45)">
    <rect width="90" height="85" rx="10" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <text x="45" y="32" font-size="24" font-weight="bold" fill="#1d4ed8" text-anchor="middle">1</text>
    <line x1="18" y1="42" x2="72" y2="42" stroke="#1d4ed8" stroke-width="3"/>
    <text x="45" y="70" font-size="24" font-weight="bold" fill="#1d4ed8" text-anchor="middle">4</text>
  </g>
  <!-- Ετικέτες με βέλη στα δεξιά του κουτιού -->
  <g transform="translate(285, 45)">
    <text x="0" y="32" font-size="12" font-weight="600" fill="#1e40af">← Αριθμητής <tspan fill="#64748b" font-weight="normal">(πόσα πήρα)</tspan></text>
    <text x="0" y="70" font-size="12" font-weight="600" fill="#1e40af">← Παρονομαστής <tspan fill="#64748b" font-weight="normal">(όλα τα ίσα μέρη)</tspan></text>
  </g>
  <text x="270" y="162" font-size="13" font-weight="bold" fill="#0f172a" text-anchor="middle">Το 1/4 σημαίνει: 1 κομμάτι από τα 4 ίσα κομμάτια!</text>
</svg>""",
        "easy_points": [
            "Κόβουμε μία πίτσα σε 4 ολόιδια κομμάτια.",
            "Τρώμε το 1 κομμάτι.",
            "Αυτό γράφεται 1/4 (ένα τέταρτο)."
        ],
        "analogy": "Όταν μοιράζεις μια σοκολάτα με 4 φίλους σου, ο καθένας παίρνει 1 από τα 4 ίσα κομμάτια!"
    },

    "math_equation_balance": {
        "id": "math_equation_balance",
        "title": "⚖️ Η Εξίσωση είναι σαν μια Ζυγαριά",
        "subject_tag": "Μαθηματικά",
        "keywords": ["εξισωση", "εξισωσεις", "αγνωστος", "αγνωστο", "λυση εξισωσης", "ζυγαρια", "ισοτητα", "ισον"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <!-- Βάση ζυγαριάς -->
  <polygon points="210,130 195,160 225,160" fill="#64748b"/>
  <!-- Κεντρικός πυλώνας & ράβδος -->
  <line x1="210" y1="65" x2="210" y2="130" stroke="#475569" stroke-width="6"/>
  <line x1="100" y1="65" x2="320" y2="65" stroke="#0284c7" stroke-width="6" stroke-linecap="round"/>
  <!-- Αριστερός δίσκος -->
  <line x1="100" y1="65" x2="70" y2="110" stroke="#94a3b8" stroke-width="2"/>
  <line x1="100" y1="65" x2="130" y2="110" stroke="#94a3b8" stroke-width="2"/>
  <ellipse cx="100" cy="110" rx="40" ry="10" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>
  <!-- Αντικείμενα αριστερά: x + 2 -->
  <rect x="75" y="85" width="26" height="24" rx="4" fill="#3b82f6"/>
  <text x="88" y="102" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">x</text>
  <circle cx="115" cy="97" r="10" fill="#fbbf24" stroke="#d97706" stroke-width="1.5"/>
  <text x="115" y="101" font-size="12" font-weight="bold" fill="#78350f" text-anchor="middle">2</text>
  <!-- Σύμβολο ίσον στο κέντρο -->
  <circle cx="210" cy="65" r="16" fill="#ffffff" stroke="#0284c7" stroke-width="3"/>
  <text x="210" y="72" font-size="20" font-weight="bold" fill="#0284c7" text-anchor="middle">=</text>
  <!-- Δεξιός δίσκος -->
  <line x1="320" y1="65" x2="290" y2="110" stroke="#94a3b8" stroke-width="2"/>
  <line x1="320" y1="65" x2="350" y2="110" stroke="#94a3b8" stroke-width="2"/>
  <ellipse cx="320" cy="110" rx="40" ry="10" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>
  <!-- Αντικείμενο δεξιά: 6 -->
  <circle cx="320" cy="94" r="15" fill="#10b981" stroke="#047857" stroke-width="2"/>
  <text x="320" y="100" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">6</text>
  <text x="210" y="152" font-size="12" fill="#334155" text-anchor="middle">Αριστερά: x + 2 = Δεξιά: 6</text>
  <text x="210" y="170" font-size="13" font-weight="bold" fill="#0369a1" text-anchor="middle">Ό,τι βγάζουμε από τη μία μεριά, βγάζουμε και από την άλλη!</text>
</svg>""",
        "easy_points": [
            "Η εξίσωση είναι σαν ζυγαριά που στέκεται ίσια.",
            "Η αριστερή πλευρά ζυγίζει ακριβώς όσο η δεξιά.",
            "Για να βρούμε το x, βγάζουμε το 2 και από τις δύο μεριές: x = 6 - 2 = 4!"
        ],
        "analogy": "Αν έχεις ένα κρυμμένο δώρο και 2 ευρώ στην τσέπη και όλα μαζί κάνουν 6 ευρώ, το δώρο κάνει 4 ευρώ!"
    },

    "math_pythagoras": {
        "id": "math_pythagoras",
        "title": "📐 Το Πυθαγόρειο Θεώρημα (Ορθογώνιο Τρίγωνο)",
        "subject_tag": "Μαθηματικά",
        "keywords": ["πυθαγορειο", "θεωρημα", "ορθογωνιο τριγωνο", "υποτεινουσα", "καθετες πλευρες", "γωνια 90"],
        "svg": """<svg viewBox="0 0 420 190" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="190" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <g transform="translate(130, 130)">
    <!-- Τρίγωνο 3-4-5 -->
    <polygon points="0,0 80,0 0,-60" fill="#dbeafe" stroke="#1d4ed8" stroke-width="3"/>
    <!-- Ορθή γωνία -->
    <rect x="0" y="-14" width="14" height="14" fill="none" stroke="#dc2626" stroke-width="2"/>
    <circle cx="7" cy="-7" r="2" fill="#dc2626"/>
    <!-- Πλευρές -->
    <text x="40" y="18" font-size="13" font-weight="bold" fill="#1e40af" text-anchor="middle">βάση (a = 4)</text>
    <text x="-35" y="-28" font-size="13" font-weight="bold" fill="#1e40af" text-anchor="middle">ύψος (b = 3)</text>
    <text x="56" y="-38" font-size="13" font-weight="bold" fill="#b91c1c" text-anchor="middle">υποτείνουσα (c = 5)</text>
  </g>
  <g transform="translate(245, 30)">
    <rect width="155" height="110" rx="10" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
    <text x="77" y="26" font-size="13" font-weight="bold" fill="#92400e" text-anchor="middle">Ο Κανόνας του Πυθαγόρα:</text>
    <text x="77" y="55" font-size="18" font-weight="bold" fill="#b45309" text-anchor="middle">a² + b² = c²</text>
    <text x="77" y="80" font-size="12" fill="#78350f" text-anchor="middle">3² + 4² = 9 + 16 = 25</text>
    <text x="77" y="98" font-size="13" font-weight="bold" fill="#047857" text-anchor="middle">Άρα c = 5!</text>
  </g>
  <text x="210" y="175" font-size="12.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Ισχύει ΠΑΝΤΑ στα τρίγωνα που έχουν μία γωνία «πι» (ορθή γωνία 90°)!</text>
</svg>""",
        "easy_points": [
            "Κοιτάμε ένα τρίγωνο με μία ορθή γωνία (σαν γωνία τετραδίου).",
            "Η μεγαλύτερη πλάγια πλευρά λέγεται «υποτείνουσα».",
            "Αν ενώσουμε τα τετράγωνα των δύο μικρών πλευρών, φτιάχνουν το τετράγωνο της μεγάλης!"
        ],
        "analogy": "Όταν ανεβαίνεις μία ράμπα για αναπηρικό αμαξίδιο, η ράμπα είναι η υποτείνουσα που σε πάει επάνω!"
    },

    "math_number_line": {
        "id": "math_number_line",
        "title": "🌡️ Ο Άξονας των Αριθμών (Θετικοί & Αρνητικοί)",
        "subject_tag": "Μαθηματικά",
        "keywords": ["αξονας", "αρνητικοι", "θετικοι", "αριθμοι", "μηδεν", "μειον", "θερμοκρασια", "υπογειο"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <!-- Άξονας -->
  <line x1="30" y1="85" x2="390" y2="85" stroke="#1e293b" stroke-width="4" marker-end="url(#arrow)"/>
  <!-- Μηδέν στο κέντρο -->
  <line x1="210" y1="70" x2="210" y2="100" stroke="#0284c7" stroke-width="4"/>
  <circle cx="210" cy="85" r="7" fill="#0284c7"/>
  <text x="210" y="118" font-size="16" font-weight="bold" fill="#0284c7" text-anchor="middle">0</text>
  <text x="210" y="55" font-size="11" font-weight="bold" fill="#0284c7" text-anchor="middle">Αρχή (Μηδέν)</text>
  <!-- Αρνητικοί αριστερά -->
  <line x1="150" y1="75" x2="150" y2="95" stroke="#ef4444" stroke-width="3"/>
  <text x="150" y="116" font-size="14" font-weight="bold" fill="#dc2626" text-anchor="middle">-1</text>
  <line x1="90" y1="75" x2="90" y2="95" stroke="#ef4444" stroke-width="3"/>
  <text x="90" y="116" font-size="14" font-weight="bold" fill="#dc2626" text-anchor="middle">-2</text>
  <line x1="45" y1="75" x2="45" y2="95" stroke="#ef4444" stroke-width="3"/>
  <text x="45" y="116" font-size="14" font-weight="bold" fill="#dc2626" text-anchor="middle">-3</text>
  <rect x="35" y="38" width="130" height="24" rx="6" fill="#fee2e2"/>
  <text x="100" y="54" font-size="11" font-weight="bold" fill="#b91c1c" text-anchor="middle">❄️ Αρνητικοί (Κάτω/Κρύο)</text>
  <!-- Θετικοί δεξιά -->
  <line x1="270" y1="75" x2="270" y2="95" stroke="#10b981" stroke-width="3"/>
  <text x="270" y="116" font-size="14" font-weight="bold" fill="#059669" text-anchor="middle">+1</text>
  <line x1="330" y1="75" x2="330" y2="95" stroke="#10b981" stroke-width="3"/>
  <text x="330" y="116" font-size="14" font-weight="bold" fill="#059669" text-anchor="middle">+2</text>
  <line x1="375" y1="75" x2="375" y2="95" stroke="#10b981" stroke-width="3"/>
  <text x="375" y="116" font-size="14" font-weight="bold" fill="#059669" text-anchor="middle">+3</text>
  <rect x="255" y="38" width="130" height="24" rx="6" fill="#d1fae5"/>
  <text x="320" y="54" font-size="11" font-weight="bold" fill="#047857" text-anchor="middle">☀️ Θετικοί (Πάνω/Ζέστη)</text>
  <text x="210" y="155" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">Όσο πάμε δεξιά, οι αριθμοί μεγαλώνουν. Όσο πάμε αριστερά, μικραίνουν!</text>
</svg>""",
        "easy_points": [
            "Στη μέση είναι το 0.",
            "Δεξιά είναι οι θετικοί αριθμοί (+1, +2, +3): σαν να κερδίζεις βαθμούς.",
            "Αριστερά είναι οι αρνητικοί αριθμοί (-1, -2, -3): σαν να πέφτει η θερμοκρασία κάτω από το μηδέν."
        ],
        "analogy": "Σαν το ασανσέρ: το ισόγειο είναι το 0, οι όροφοι είναι +1, +2 και το υπόγειο γκαράζ είναι το -1!"
    },

    # =========================================================================
    # 📜 ΙΣΤΟΡΙΑ
    # =========================================================================
    "history_parthenon": {
        "id": "history_parthenon",
        "title": "🏛️ Ο Παρθενώνας & η Αρχαία Αθήνα (Δημοκρατία)",
        "subject_tag": "Ιστορία",
        "keywords": ["παρθενωνας", "ακροπολη", "αθηνα", "περικλης", "δημοκρατια", "χρυσους αιων", "εκκλησια του δημου", "αρχαια ελλαδα"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#eff6ff" stroke="#bfdbfe" stroke-width="2"/>
  <!-- Ο Βράχος της Ακρόπολης -->
  <path d="M 40 145 Q 120 120 210 125 Q 310 120 380 145 L 390 170 L 30 170 Z" fill="#cbd5e1"/>
  <!-- Ο Ναός (Παρθενώνας) -->
  <g transform="translate(100, 35)">
    <!-- Αέτωμα -->
    <polygon points="110,10 0,35 220,35" fill="#fef08a" stroke="#ca8a04" stroke-width="2.5"/>
    <rect x="0" y="35" width="220" height="12" fill="#fed7aa" stroke="#c2410c" stroke-width="1.5"/>
    <!-- Κίονες (Κολώνες) -->
    <rect x="10" y="47" width="14" height="48" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>
    <rect x="42" y="47" width="14" height="48" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>
    <rect x="74" y="47" width="14" height="48" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>
    <rect x="104" y="47" width="14" height="48" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>
    <rect x="134" y="47" width="14" height="48" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>
    <rect x="164" y="47" width="14" height="48" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>
    <rect x="196" y="47" width="14" height="48" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>
    <!-- Βάση κρηπίδωμα -->
    <rect x="-8" y="95" width="236" height="12" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
  </g>
  <text x="210" y="162" font-size="13" font-weight="bold" fill="#0f172a" text-anchor="middle">Ο Παρθενώνας χτίστηκε στην Αθήνα προς τιμήν της θεάς Αθηνάς.</text>
</svg>""",
        "easy_points": [
            "Ο Παρθενώνας είναι ο πιο διάσημος αρχαίος ναός στην Ακρόπολη της Αθήνας.",
            "Τον έχτισαν οι Αθηναίοι την εποχή του Περικλή με λευκό μάρμαρο.",
            "Εκεί γεννήθηκε η Δημοκρατία: οι πολίτες ψήφιζαν όλοι μαζί στην Εκκλησία του Δήμου!"
        ],
        "analogy": "Όπως ψηφίζετε στην τάξη σηκώνοντας το χέρι για να διαλέξετε πρόεδρο, έτσι αποφάσιζαν και οι αρχαίοι Αθηναίοι!"
    },

    "history_knossos": {
        "id": "history_knossos",
        "title": "🐂 Ο Μινωικός Πολιτισμός & το Ανάκτορο της Κνωσού",
        "subject_tag": "Ιστορία",
        "keywords": ["κνωσος", "μινωικος", "μινοας", "κρητη", "ανακτορο", "ταυροκαθαψια", "λαβυρινθος", "μινωταυρος"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#fefce8" stroke="#fef08a" stroke-width="2"/>
  <!-- Κόκκινοι κίονες Κνωσού -->
  <g transform="translate(60, 30)">
    <rect x="20" y="30" width="20" height="80" fill="#dc2626" rx="3"/>
    <rect x="70" y="30" width="20" height="80" fill="#dc2626" rx="3"/>
    <rect x="10" y="20" width="90" height="15" fill="#1e293b" rx="2"/>
    <rect x="5" y="110" width="100" height="15" fill="#e2e8f0" rx="2"/>
    <!-- Κέρατα καθοσιώσεως -->
    <path d="M 25 15 Q 35 3 45 15 Q 55 3 65 15" fill="none" stroke="#b45309" stroke-width="4"/>
  </g>
  <!-- Ταύρος / Ταυροκαθάψια -->
  <g transform="translate(200, 45)">
    <rect width="180" height="85" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
    <text x="90" y="30" font-size="28" text-anchor="middle">🐂 🤸</text>
    <text x="90" y="58" font-size="12" font-weight="bold" fill="#991b1b" text-anchor="middle">Ταυροκαθάψια</text>
    <text x="90" y="74" font-size="10.5" fill="#475569" text-anchor="middle">Άλμα πάνω από τον ταύρο χωρίς όπλα!</text>
  </g>
  <text x="210" y="162" font-size="13" font-weight="bold" fill="#78350f" text-anchor="middle">Οι Μινωίτες ζούσαν στην Κρήτη, αγαπούσαν τη θάλασσα και δεν είχαν τείχη!</text>
</svg>""",
        "easy_points": [
            "Ο πρώτος μεγάλος πολιτισμός στην Ευρώπη άνθισε στην Κρήτη.",
            "Το ανάκτορο της Κνωσού ήταν τεράστιο, σαν λαβύρινθος, με όμορφες τοιχογραφίες.",
            "Έκαναν ένα διάσημο άθλημα, τα «Ταυροκαθάψια»: πηδούσαν πάνω από την πλάτη του ταύρου!"
        ],
        "analogy": "Φαντάσου ένα τεράστιο παλάτι γεμάτο δωμάτια, χρώματα, δελφίνια στους τοίχους και γιορτές στην αυλή!"
    },

    "history_byzantium_hagia_sophia": {
        "id": "history_byzantium_hagia_sophia",
        "title": "👑 Το Βυζάντιο & η Αγία Σοφία (Ιουστινιανός)",
        "subject_tag": "Ιστορία",
        "keywords": ["αγια σοφια", "βυζαντιο", "κωνσταντινουπολη", "ιουστινιανος", "τρούλος", "ψηφιδωτα", "μεσαιωνας"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#fafaf9" stroke="#e7e5e4" stroke-width="2"/>
  <!-- Αγία Σοφία με μεγάλο τρούλο -->
  <g transform="translate(130, 25)">
    <!-- Κεντρικός Τρούλος -->
    <path d="M 30 75 Q 80 10 130 75 Z" fill="#eab308" stroke="#ca8a04" stroke-width="3"/>
    <circle cx="80" cy="18" r="4" fill="#ca8a04"/>
    <line x1="80" y1="12" x2="80" y2="4" stroke="#ca8a04" stroke-width="2"/>
    <line x1="76" y1="8" x2="84" y2="8" stroke="#ca8a04" stroke-width="2"/>
    <!-- Παράθυρα τρούλου -->
    <circle cx="55" cy="65" r="3" fill="#ffffff"/>
    <circle cx="70" cy="62" r="3" fill="#ffffff"/>
    <circle cx="80" cy="61" r="3" fill="#ffffff"/>
    <circle cx="90" cy="62" r="3" fill="#ffffff"/>
    <circle cx="105" cy="65" r="3" fill="#ffffff"/>
    <!-- Κτήριο βάση & αψίδες -->
    <rect x="20" y="75" width="120" height="50" fill="#fed7aa" stroke="#ea580c" stroke-width="2"/>
    <path d="M 0 100 Q 20 75 40 100 L 40 125 L 0 125 Z" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5"/>
    <path d="M 120 100 Q 140 75 160 100 L 160 125 L 120 125 Z" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5"/>
  </g>
  <text x="210" y="152" font-size="12" fill="#44403c" text-anchor="middle">Χτίστηκε από τον Αυτοκράτορα Ιουστινιανό στην Κωνσταντινούπολη.</text>
  <text x="210" y="169" font-size="13" font-weight="bold" fill="#854d0e" text-anchor="middle">Ο τεράστιος χρυσός τρούλος φαινόταν σαν να κρέμεται από τον ουρανό!</text>
</svg>""",
        "easy_points": [
            "Η Αγία Σοφία είναι το σπουδαιότερο μνημείο της Βυζαντινής Αυτοκρατορίας.",
            "Την έχτισαν οι αρχιτέκτονες Ανθέμιος και Ισίδωρος σε μόλις 5 χρόνια.",
            "Είχε χιλιάδες λαμπερά χρυσά ψηφιδωτά στους τοίχους."
        ],
        "analogy": "Ο τρούλος είναι σαν ένα τεράστιο χρυσό καπάκι που στεγάζει έναν ολόκληρο λόφο!"
    },

    # =========================================================================
    # 🧬 ΒΙΟΛΟΓΙΑ
    # =========================================================================
    "biology_cell": {
        "id": "biology_cell",
        "title": "🔬 Το Κύτταρο (Το Μικρό Τουβλάκι της Ζωής)",
        "subject_tag": "Βιολογία",
        "keywords": ["κυτταρο", "πυρηνας", "μεμβρανη", "κυτταροπλασμα", "μιτοχονδριο", "οργανισμοι", "ζωικο", "φυτικο"],
        "svg": """<svg viewBox="0 0 520 190" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="520" height="190" rx="14" fill="#f0fdf4" stroke="#bbf7d0" stroke-width="2"/>
  <!-- Κύτταρο (Ζελέ και μεμβράνη) -->
  <g transform="translate(130, 90)">
    <!-- Κυτταρική Μεμβράνη -->
    <ellipse rx="95" ry="65" fill="#dcfce7" stroke="#16a34a" stroke-width="4"/>
    <!-- Πυρήνας στο κέντρο -->
    <circle cx="-10" cy="0" r="30" fill="#93c5fd" stroke="#1d4ed8" stroke-width="3"/>
    <circle cx="-10" cy="0" r="12" fill="#1e40af"/>
    <!-- Μιτοχόνδριο (Ενέργεια) -->
    <ellipse cx="50" cy="-25" rx="16" ry="9" fill="#fca5a5" stroke="#dc2626" stroke-width="2"/>
    <ellipse cx="45" cy="30" rx="16" ry="9" fill="#fca5a5" stroke="#dc2626" stroke-width="2"/>
    <!-- Χυμοτόπιο -->
    <ellipse cx="-55" cy="-25" rx="14" ry="10" fill="#fef08a" stroke="#ca8a04" stroke-width="1.5"/>
  </g>
  <!-- Ετικέτες με βέλη -->
  <g transform="translate(265, 25)">
    <text x="0" y="25" font-size="12" font-weight="bold" fill="#15803d">1. Μεμβράνη: <tspan font-weight="normal" fill="#334155">Ο τοίχος γύρω-γύρω</tspan></text>
    <text x="0" y="55" font-size="12" font-weight="bold" fill="#1d4ed8">2. Πυρήνας: <tspan font-weight="normal" fill="#334155">Το «μυαλό» του κυττάρου</tspan></text>
    <text x="0" y="85" font-size="12" font-weight="bold" fill="#166534">3. Κυτταρόπλασμα: <tspan font-weight="normal" fill="#334155">Το ζελέ στο εσωτερικό</tspan></text>
    <text x="0" y="115" font-size="12" font-weight="bold" fill="#dc2626">4. Μιτοχόνδριο: <tspan font-weight="normal" fill="#334155">Η μπαταρία / ενέργεια</tspan></text>
  </g>
  <text x="260" y="175" font-size="13" font-weight="bold" fill="#14532d" text-anchor="middle">Όλοι οι ζωντανοί οργανισμοί (άνθρωποι, ζώα, φυτά) αποτελούνται από κύτταρα!</text>
</svg>""",
        "easy_points": [
            "Όπως ένα σπίτι χτίζεται από πολλά τούβλα, έτσι και το σώμα μας χτίζεται από κύτταρα.",
            "Η μεμβράνη προστατεύει το κύτταρο σαν πόρτα.",
            "Ο πυρήνας δίνει τις εντολές για να ζει και να μεγαλώνει."
        ],
        "analogy": "Το κύτταρο είναι σαν ένα αυγό: το τσόφλι είναι η μεμβράνη, το ασπράδι είναι το κυτταρόπλασμα και ο κρόκος είναι ο πυρήνας!"
    },

    "biology_photosynthesis": {
        "id": "biology_photosynthesis",
        "title": "🌱 Η Φωτοσύνθεση (Πώς Τρέφονται τα Φυτά)",
        "subject_tag": "Βιολογία",
        "keywords": ["φωτοσυνθεση", "φυτα", "ηλιος", "χλωροφυλλη", "οξυγονο", "διοξειδιο", "τροφη φυτων"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f0fdf4" stroke="#86efac" stroke-width="2"/>
  <!-- Ήλιος -->
  <circle cx="65" cy="45" r="24" fill="#facc15" stroke="#eab308" stroke-width="3"/>
  <text x="65" y="50" font-size="20" text-anchor="middle">☀️</text>
  <text x="65" y="85" font-size="11" font-weight="bold" fill="#854d0e" text-anchor="middle">+ Φως Ήλιου</text>
  <!-- Φυτό -->
  <g transform="translate(190, 40)">
    <line x1="20" y1="90" x2="20" y2="20" stroke="#15803d" stroke-width="6"/>
    <!-- Φύλλα -->
    <path d="M 20 50 Q -15 30 0 10 Q 15 30 20 50 Z" fill="#22c55e" stroke="#15803d" stroke-width="2"/>
    <path d="M 20 60 Q 55 40 40 20 Q 25 40 20 60 Z" fill="#22c55e" stroke="#15803d" stroke-width="2"/>
    <!-- Γλάστρα -->
    <polygon points="5,90 35,90 30,120 10,120" fill="#b45309"/>
    <text x="20" y="105" font-size="9" fill="#ffffff" text-anchor="middle">💧 Νερό</text>
  </g>
  <!-- Είσοδος & Έξοδος -->
  <g transform="translate(260, 45)">
    <rect width="140" height="85" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <text x="70" y="24" font-size="11.5" font-weight="bold" fill="#0369a1" text-anchor="middle">Τι παίρνει το φυτό:</text>
    <text x="70" y="42" font-size="11" fill="#334155" text-anchor="middle">Ήλιο + Νερό + Διοξείδιο</text>
    <line x1="20" y1="50" x2="120" y2="50" stroke="#e2e8f0" stroke-width="1.5"/>
    <text x="70" y="66" font-size="11.5" font-weight="bold" fill="#15803d" text-anchor="middle">Τι μας χαρίζει:</text>
    <text x="70" y="82" font-size="12" font-weight="bold" fill="#16a34a" text-anchor="middle">🌿 Τροφή & 💨 Οξυγόνο!</text>
  </g>
  <text x="210" y="165" font-size="13" font-weight="bold" fill="#166534" text-anchor="middle">Τα φυτά μαγειρεύουν μόνα τους την τροφή τους χρησιμοποιώντας το φως του ήλιου!</text>
</svg>""",
        "easy_points": [
            "Τα πράσινα φυτά πίνουν νερό από τις ρίζες και παίρνουν φως από τον ήλιο.",
            "Με αυτά φτιάχνουν τη δική τους τροφή (σάκχαρα).",
            "Ταυτόχρονα βγάζουν καθαρό οξυγόνο για να αναπνέουμε εμείς!"
        ],
        "analogy": "Σαν ένα μικρό εργοστάσιο που δουλεύει με ηλιακή ενέργεια και καθαρίζει τον αέρα του πλανήτη!"
    },

    # =========================================================================
    # ⚡ ΦΥΣΙΚΗ
    # =========================================================================
    "physics_gravity": {
        "id": "physics_gravity",
        "title": "🍎 Η Βαρύτητα & η Έλξη της Γης (Νεύτωνας)",
        "subject_tag": "Φυσική",
        "keywords": ["βαρυτητα", "νευτωνας", "βαρος", "μαζα", "μηλο", "πεφτει", "ελξη", "βαρυτητα γης"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#e2e8f0" stroke-width="2"/>
  <!-- Δέντρο και μήλο -->
  <g transform="translate(60, 20)">
    <!-- Κορμός -->
    <rect x="50" y="60" width="20" height="80" fill="#78350f" rx="3"/>
    <!-- Φύλλωμα -->
    <circle cx="60" cy="50" r="45" fill="#16a34a"/>
    <!-- Μήλο που πέφτει -->
    <circle cx="85" cy="85" r="9" fill="#dc2626"/>
    <!-- Διακεκομμένη γραμμή πτώσης -->
    <line x1="85" y1="95" x2="85" y2="135" stroke="#dc2626" stroke-width="2" stroke-dasharray="4"/>
    <polygon points="85,140 81,132 89,132" fill="#dc2626"/>
  </g>
  <!-- Επεξηγηματικό πλαίσιο -->
  <g transform="translate(180, 35)">
    <rect width="215" height="95" rx="10" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <text x="107" y="26" font-size="13" font-weight="bold" fill="#1d4ed8" text-anchor="middle">Γιατί όλα πέφτουν κάτω;</text>
    <text x="107" y="48" font-size="11.5" fill="#334155" text-anchor="middle">Η Γη λειτουργεί σαν ένας γιγάντιος μαγνήτης!</text>
    <text x="107" y="66" font-size="11.5" fill="#334155" text-anchor="middle">Τραβάει όλα τα σώματα προς το κέντρο της.</text>
    <text x="107" y="85" font-size="12" font-weight="bold" fill="#0284c7" text-anchor="middle">Αυτή η δύναμη λέγεται Βαρύτητα (Βάρος)!</text>
  </g>
  <text x="210" y="165" font-size="13" font-weight="bold" fill="#0f172a" text-anchor="middle">Χάρη στη βαρύτητα πατάμε γερά στη Γη και δεν πετάμε στο διάστημα!</text>
</svg>""",
        "easy_points": [
            "Αν αφήσεις ένα μολύβι ή ένα μήλο από τα χέρια σου, πέφτει πάντα κάτω.",
            "Η Γη έχει μία μυστική δύναμη, τη «βαρύτητα», που τραβάει τα πάντα προς τα κάτω.",
            "Χάρη στη βαρύτητα δεν αιωρούμαστε στον αέρα!"
        ],
        "analogy": "Όταν πηδάς ψηλά στο τραμπολίνο, η βαρύτητα είναι αυτή που σε ξαναφέρνει γλυκά πίσω στη Γη!"
    },

    "physics_electric_circuit": {
        "id": "physics_electric_circuit",
        "title": "💡 Το Ηλεκτρικό Κύκλωμα (Πώς Ανάβει η Λάμπα)",
        "subject_tag": "Φυσική",
        "keywords": ["κυκλωμα", "ρευμα", "μπαταρια", "λαμπα", "λαμπακι", "καλωδιο", "διακοπτης", "ηλεκτρισμος"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <!-- Κλειστό κύκλωμα -->
  <g transform="translate(60, 30)">
    <!-- Καλώδια (ορθογώνιο) -->
    <rect x="20" y="20" width="260" height="80" fill="none" stroke="#2563eb" stroke-width="4" rx="10"/>
    <!-- Μπαταρία αριστερά -->
    <rect x="10" y="45" width="20" height="30" fill="#dc2626" rx="3"/>
    <rect x="15" y="40" width="10" height="5" fill="#94a3b8"/>
    <text x="20" y="65" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">+</text>
    <text x="20" y="95" font-size="10" fill="#475569" text-anchor="middle">Μπαταρία</text>
    <!-- Διακόπτης επάνω -->
    <circle cx="130" cy="20" r="5" fill="#0f172a"/>
    <circle cx="170" cy="20" r="5" fill="#0f172a"/>
    <line x1="130" y1="20" x2="170" y2="20" stroke="#16a34a" stroke-width="4"/>
    <text x="150" y="10" font-size="10" font-weight="bold" fill="#16a34a" text-anchor="middle">Διακόπτης Κλειστός (ON)</text>
    <!-- Λάμπα δεξιά -->
    <circle cx="280" cy="60" r="16" fill="#fef08a" stroke="#ca8a04" stroke-width="2"/>
    <text x="280" y="66" font-size="16" text-anchor="middle">💡</text>
    <text x="280" y="95" font-size="10" font-weight="bold" fill="#ca8a04" text-anchor="middle">Η λάμπα ανάβει!</text>
  </g>
  <text x="210" y="152" font-size="12" fill="#334155" text-anchor="middle">Για να ανάψει η λάμπα, το καλώδιο πρέπει να κάνει πλήρη κλειστό κύκλο.</text>
  <text x="210" y="169" font-size="13" font-weight="bold" fill="#1d4ed8" text-anchor="middle">Όταν κλείνουμε τον διακόπτη, το ρεύμα ταξιδεύει και ανάβει το φως!</text>
</svg>""",
        "easy_points": [
            "Η μπαταρία δίνει την ενέργεια (σαν καρδιά που στέλνει ρεύμα).",
            "Τα καλώδια είναι οι δρόμοι απ' όπου περνάει το ρεύμα.",
            "Αν ο διακόπτης είναι κλειστός, ο δρόμος είναι ανοιχτός και η λάμπα ανάβει!"
        ],
        "analogy": "Όταν πατάς τον διακόπτη στο δωμάτιό σου, ενώνεις το καλώδιο και αμέσως ανάβει το φως!"
    },

    # =========================================================================
    # 🌍 ΓΕΩΓΡΑΦΙΑ
    # =========================================================================
    "geography_greece_map": {
        "id": "geography_greece_map",
        "title": "🗺️ Ο Χάρτης της Ελλάδας & ο Προσανατολισμός",
        "subject_tag": "Γεωγραφία",
        "keywords": ["χαρτης", "ελλαδα", "πυξιδα", "βορρας", "νοτος", "ανατολη", "δυση", "αιγαιο", "ιονιο", "νησια", "βουνα"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f0f9ff" stroke="#bae6fd" stroke-width="2"/>
  <!-- Πυξίδα Αριστερά -->
  <g transform="translate(70, 85)">
    <circle r="40" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>
    <line x1="0" y1="-32" x2="0" y2="32" stroke="#64748b" stroke-width="2"/>
    <line x1="-32" y1="0" x2="32" y2="0" stroke="#64748b" stroke-width="2"/>
    <!-- Βέλος Βορρά κόκκινο -->
    <polygon points="0,-32 -7,0 7,0" fill="#dc2626"/>
    <polygon points="0,32 -7,0 7,0" fill="#3b82f6"/>
    <text x="0" y="-36" font-size="12" font-weight="bold" fill="#dc2626" text-anchor="middle">Β (Βορράς)</text>
    <text x="0" y="47" font-size="11" font-weight="bold" fill="#1e3a8a" text-anchor="middle">Ν (Νότος)</text>
    <text x="36" y="4" font-size="11" font-weight="bold" fill="#0f172a">Α</text>
    <text x="-44" y="4" font-size="11" font-weight="bold" fill="#0f172a">Δ</text>
  </g>
  <!-- Σχηματική Ελλάδα -->
  <g transform="translate(170, 30)">
    <rect width="220" height="100" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <text x="110" y="25" font-size="13" font-weight="bold" fill="#0284c7" text-anchor="middle">🇬🇷 Η Χώρα μας στον Χάρτη</text>
    <text x="110" y="46" font-size="11" fill="#334155" text-anchor="middle">🌊 Δυτικά: Ιόνιο Πέλαγος</text>
    <text x="110" y="64" font-size="11" fill="#334155" text-anchor="middle">🌊 Ανατολικά: Αιγαίο Πέλαγος (Νησιά)</text>
    <text x="110" y="84" font-size="11" fill="#334155" text-anchor="middle">☀️ Νότια: Κρήτη & Μεσόγειος</text>
  </g>
  <text x="210" y="165" font-size="13" font-weight="bold" fill="#0369a1" text-anchor="middle">Ο Βορράς είναι πάντα επάνω στον χάρτη και ο Νότος είναι κάτω!</text>
</svg>""",
        "easy_points": [
            "Ο χάρτης μάς δείχνει πού βρίσκονται τα μέρη από ψηλά.",
            "Η πυξίδα μάς δείχνει τα 4 σημεία: Βορράς (πάνω), Νότος (κάτω), Ανατολή (δεξιά), Δύση (αριστερά).",
            "Η Ελλάδα περιβάλλεται από όμορφες θάλασσες και χιλιάδες νησιά!"
        ],
        "analogy": "Όταν βγαίνει ο ήλιος το πρωί, κοιτάζει προς την Ανατολή. Όταν βασιλεύει το απόγευμα, κρύβεται στη Δύση!"
    },

    # =========================================================================
    # 🏺 ΑΡΧΑΙΑ & ΟΔΥΣΣΕΙΑ
    # =========================================================================
    "literature_odyssey_trojan_horse": {
        "id": "literature_odyssey_trojan_horse",
        "title": "🐴 Ο Οδυσσέας & ο Δούρειος Ίππος (Τροία)",
        "subject_tag": "Οδύσσεια / Ιλιάδα",
        "keywords": ["οδυσσεας", "δουρειος ιππος", "τροια", "ομηρος", "οδυσσεια", "ιλιαδα", "πολυφημος", "νοστος"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#fffbeb" stroke="#fef3c7" stroke-width="2"/>
  <!-- Ξύλινο Άλογο -->
  <g transform="translate(60, 20)">
    <!-- Σώμα αλόγου -->
    <rect x="40" y="40" width="70" height="50" rx="8" fill="#b45309" stroke="#78350f" stroke-width="2"/>
    <!-- Λαιμός & κεφάλι -->
    <polygon points="100,40 125,15 140,25 110,60" fill="#b45309" stroke="#78350f" stroke-width="2"/>
    <!-- Πόδια -->
    <rect x="45" y="90" width="10" height="35" fill="#92400e"/>
    <rect x="95" y="90" width="10" height="35" fill="#92400e"/>
    <!-- Ρόδες στη βάση -->
    <circle cx="50" cy="128" r="8" fill="#78350f"/>
    <circle cx="100" cy="128" r="8" fill="#78350f"/>
    <!-- Κρυμμένοι πολεμιστές στο εσωτερικό -->
    <rect x="55" y="55" width="40" height="22" rx="4" fill="#fef08a" stroke="#ca8a04"/>
    <text x="75" y="70" font-size="10" font-weight="bold" fill="#78350f" text-anchor="middle">⚔️ Έλληνες</text>
  </g>
  <!-- Επεξήγηση -->
  <g transform="translate(200, 35)">
    <rect width="195" height="95" rx="10" fill="#ffffff" stroke="#fed7aa" stroke-width="2"/>
    <text x="97" y="26" font-size="13" font-weight="bold" fill="#9a3412" text-anchor="middle">Το Τέχνασμα του Οδυσσέα</text>
    <text x="97" y="48" font-size="11" fill="#431407" text-anchor="middle">Έφτιαξαν ένα τεράστιο ξύλινο άλογο.</text>
    <text x="97" y="66" font-size="11" fill="#431407" text-anchor="middle">Μέσα κρύφτηκαν οι γενναίοι πολεμιστές.</text>
    <text x="97" y="86" font-size="11.5" font-weight="bold" fill="#c2410c" text-anchor="middle">Έτσι κατέκτησαν την Τροία!</text>
  </g>
  <text x="210" y="165" font-size="13" font-weight="bold" fill="#78350f" text-anchor="middle">Ο Οδυσσέας νίκησε με τη σκέψη και την εξυπνάδα του, όχι μόνο με τη δύναμη!</text>
</svg>""",
        "easy_points": [
            "Ο πόλεμος της Τροίας κρατούσε 10 ολόκληρα χρόνια.",
            "Ο πολυμήχανος Οδυσσέας σκέφτηκε ένα έξυπνο κόλπο: ένα ξύλινο άλογο.",
            "Οι Τρώες το έβαλαν μέσα στην πόλη και τη νύχτα οι Έλληνες άνοιξαν τις πύλες!"
        ],
        "analogy": "Όταν ένα πρόβλημα φαίνεται δύσκολο, η εξυπνάδα και η υπομονή βρίσκουν πάντα τη λύση!"
    },

    # =========================================================================
    # 💻 ΠΛΗΡΟΦΟΡΙΚΗ
    # =========================================================================
    "informatics_computer_parts": {
        "id": "informatics_computer_parts",
        "title": "💻 Τα Μέρη του Υπολογιστή (Υλικό & Λογισμικό)",
        "subject_tag": "Πληροφορική",
        "keywords": ["υπολογιστης", "πληροφορικη", "οθονη", "ποντικι", "πληκτρολογιο", "κεντρικη μοναδα", "υλικο", "λογισμικο", "scratch"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <!-- Οθόνη -->
  <g transform="translate(60, 25)">
    <rect x="0" y="0" width="110" height="75" rx="6" fill="#1e293b"/>
    <rect x="5" y="5" width="100" height="65" rx="3" fill="#38bdf8"/>
    <text x="55" y="42" font-size="20" text-anchor="middle">🖥️</text>
    <polygon points="50,75 60,75 65,95 45,95" fill="#64748b"/>
    <rect x="35" y="95" width="40" height="6" fill="#475569" rx="2"/>
    <text x="55" y="115" font-size="11" font-weight="bold" fill="#0369a1" text-anchor="middle">Οθόνη (Βλέπουμε)</text>
  </g>
  <!-- Πληκτρολόγιο & Ποντίκι -->
  <g transform="translate(195, 45)">
    <rect x="0" y="30" width="85" height="30" rx="4" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
    <text x="42" y="50" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">⌨️ Πληκτρολόγιο</text>
    <ellipse cx="115" cy="45" rx="14" ry="18" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
    <text x="115" y="50" font-size="10" font-weight="bold" fill="#334155" text-anchor="middle">🖱️</text>
    <text x="70" y="85" font-size="11" font-weight="bold" fill="#475569" text-anchor="middle">Συσκευές Εισόδου (Γράφουμε / Διαλέγουμε)</text>
  </g>
  <text x="210" y="162" font-size="13" font-weight="bold" fill="#0f172a" text-anchor="middle">Το Υλικό είναι ό,τι αγγίζουμε. Το Λογισμικό είναι τα προγράμματα και τα παιχνίδια!</text>
</svg>""",
        "easy_points": [
            "Ο υπολογιστής αποτελείται από την οθόνη (όπου βλέπουμε εικόνες και βίντεο).",
            "Το πληκτρολόγιο και το ποντίκι μάς βοηθούν να του δίνουμε εντολές.",
            "Η κεντρική μονάδα (πύργος) είναι ο «εγκέφαλος» που σκέφτεται αστραπιαία!"
        ],
        "analogy": "Το σώμα σου είναι το υλικό (χέρια, μάτια). Οι σκέψεις και οι γνώσεις σου είναι το λογισμικό!"
    },

    # =========================================================================
    # 🧪 ΧΗΜΕΙΑ
    # =========================================================================
    "chemistry_water_molecule": {
        "id": "chemistry_water_molecule",
        "title": "💧 Το Μόριο του Νερού (H₂O) & τα Άτομα",
        "subject_tag": "Χημεία",
        "keywords": ["χημεια", "χημικη", "μοριο", "μορια", "μοριο νερου", "ατομο", "ατομα", "υδρογονο", "οξυγονο", "h2o", "χημικη ενωση", "χημικος δεσμος"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f0f9ff" stroke="#bae6fd" stroke-width="2"/>
  <!-- Μόριο Νερού σαν κεφάλι με αυτάκια (Mickey Mouse) -->
  <g transform="translate(110, 85)">
    <!-- Κεντρικό Οξυγόνο κόκκινο -->
    <circle cx="0" cy="15" r="38" fill="#ef4444" stroke="#b91c1c" stroke-width="3"/>
    <text x="0" y="22" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle">O</text>
    <text x="0" y="65" font-size="11" font-weight="bold" fill="#b91c1c" text-anchor="middle">1 Οξυγόνο</text>
    <!-- Αριστερό Υδρογόνο μπλε -->
    <circle cx="-35" cy="-25" r="22" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2.5"/>
    <text x="-35" y="-19" font-size="16" font-weight="bold" fill="#ffffff" text-anchor="middle">H</text>
    <!-- Δεξιό Υδρογόνο μπλε -->
    <circle cx="35" cy="-25" r="22" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2.5"/>
    <text x="35" y="-19" font-size="16" font-weight="bold" fill="#ffffff" text-anchor="middle">H</text>
    <text x="0" y="-40" font-size="11" font-weight="bold" fill="#1d4ed8" text-anchor="middle">2 Υδρογόνα</text>
  </g>
  <!-- Επεξηγηματικό Πλαίσιο -->
  <g transform="translate(225, 30)">
    <rect width="180" height="105" rx="10" fill="#ffffff" stroke="#93c5fd" stroke-width="2"/>
    <text x="90" y="26" font-size="14" font-weight="bold" fill="#0369a1" text-anchor="middle">Ο Τύπος: H₂O</text>
    <line x1="20" y1="36" x2="160" y2="36" stroke="#e2e8f0" stroke-width="1.5"/>
    <text x="90" y="58" font-size="11.5" fill="#334155" text-anchor="middle">🔹 2 μικρά Υδρογόνα (H)</text>
    <text x="90" y="78" font-size="11.5" fill="#334155" text-anchor="middle">+ 1 μεγάλο Οξυγόνο (O)</text>
    <text x="90" y="98" font-size="12" font-weight="bold" fill="#16a34a" text-anchor="middle">= 1 Σταγόνα Νερό!</text>
  </g>
  <text x="210" y="165" font-size="13" font-weight="bold" fill="#0c4a6e" text-anchor="middle">Όλα τα πράγματα γύρω μας φτιάχνονται ενώνοντας μικρά-μικρά άτομα!</text>
</svg>""",
        "easy_points": [
            "Κάθε σταγόνα νερού αποτελείται από δισεκατομμύρια μικροσκοπικά μόρια.",
            "Κάθε μόριο νερού έχει 1 άτομο Οξυγόνου και 2 άτομα Υδρογόνου.",
            "Μοιάζει με ένα κεφαλάκι με δύο αυτάκια που είναι σφιχτά αγκαλιασμένα!"
        ],
        "analogy": "Σαν ένα παιχνίδι Lego: ενώνεις ένα κόκκινο τουβλάκι με δύο μπλε τουβλάκια και φτιάχνεις νερό!"
    },

    # =========================================================================
    # 📖 ΝΕΟΕΛΛΗΝΙΚΗ ΓΛΩΣΣΑ
    # =========================================================================
    "language_sentence_structure": {
        "id": "language_sentence_structure",
        "title": "🧱 Η Δομή της Πρότασης (Ποιος; Τι κάνει; Τι;)",
        "subject_tag": "Νεοελληνική Γλώσσα",
        "keywords": ["γλωσσα", "προταση", "υποκειμενο", "ρημα", "αντικειμενο", "συνταξη", "γραμματικη", "ενεργεια"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#fdfbf7" stroke="#e2e8f0" stroke-width="2"/>
  <!-- 3 Χρωματιστά Τουβλάκια Πρότασης -->
  <g transform="translate(20, 45)">
    <!-- Υποκείμενο -->
    <rect x="0" y="0" width="115" height="65" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
    <text x="57" y="25" font-size="12" font-weight="bold" fill="#1e40af" text-anchor="middle">ΥΠΟΚΕΙΜΕΝΟ</text>
    <text x="57" y="44" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">Ο Νίκος</text>
    <text x="57" y="58" font-size="10" fill="#64748b" text-anchor="middle">(Ποιος;)</text>
    <!-- Βέλος -->
    <text x="127" y="38" font-size="18" fill="#94a3b8">→</text>
    <!-- Ρήμα -->
    <rect x="140" y="0" width="115" height="65" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
    <text x="197" y="25" font-size="12" font-weight="bold" fill="#92400e" text-anchor="middle">ΡΗΜΑ</text>
    <text x="197" y="44" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">διαβάζει</text>
    <text x="197" y="58" font-size="10" fill="#64748b" text-anchor="middle">(Τι κάνει;)</text>
    <!-- Βέλος -->
    <text x="267" y="38" font-size="18" fill="#94a3b8">→</text>
    <!-- Αντικείμενο -->
    <rect x="280" y="0" width="105" height="65" rx="8" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
    <text x="332" y="25" font-size="12" font-weight="bold" fill="#166534" text-anchor="middle">ΑΝΤΙΚΕΙΜΕΝΟ</text>
    <text x="332" y="44" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">το βιβλίο</text>
    <text x="332" y="58" font-size="10" fill="#64748b" text-anchor="middle">(Τι διαβάζει;)</text>
  </g>
  <rect x="60" y="125" width="300" height="32" rx="6" fill="#f1f5f9"/>
  <text x="210" y="146" font-size="13.5" font-weight="bold" fill="#0f172a" text-anchor="middle">«Ο Νίκος διαβάζει το βιβλίο.»</text>
</svg>""",
        "easy_points": [
            "Μία απλή πρόταση χρειάζεται 3 βασικά μέρη.",
            "Υποκείμενο: Ποιος κάνει κάτι; (π.χ. Ο Νίκος, η γάτα, ο ήλιος).",
            "Ρήμα: Τι ενέργεια κάνει; (π.χ. τρέχει, γράφει, λάμπει).",
            "Αντικείμενο: Σε ποιον ή σε τι πηγαίνει η ενέργεια."
        ],
        "analogy": "Σαν ένα τρενάκι με 3 βαγόνια: η μηχανή οδηγεί (Υποκείμενο), η ρόδα κινείται (Ρήμα) και το βαγόνι ακολουθεί (Αντικείμενο)!"
    },

    # =========================================================================
    # 🏛️ ΚΟΙΝΩΝΙΚΗ & ΠΟΛΙΤΙΚΗ ΑΓΩΓΗ
    # =========================================================================
    "civics_rights_rules": {
        "id": "civics_rights_rules",
        "title": "🤝 Δικαιώματα & Κανόνες στο Σχολείο (Συνεργασία)",
        "subject_tag": "Κοινωνική & Πολιτική Αγωγή",
        "keywords": ["κοινωνικη", "πολιτικη αγωγη", "δικαιωματα", "υποχρεωσεις", "κανονες", "σχολειο", "σεβασμος", "ισοτητα", "συνεργασια", "ομαδα"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#faf5ff" stroke="#e9d5ff" stroke-width="2"/>
  <!-- Δύο πυλώνες: Δικαίωμα & Υποχρέωση -->
  <g transform="translate(50, 30)">
    <!-- Δικαίωμα -->
    <rect width="145" height="100" rx="10" fill="#ffffff" stroke="#a855f7" stroke-width="2"/>
    <text x="72" y="28" font-size="20" text-anchor="middle">🌟</text>
    <text x="72" y="52" font-size="12.5" font-weight="bold" fill="#7e22ce" text-anchor="middle">ΔΙΚΑΙΩΜΑ</text>
    <text x="72" y="74" font-size="10.5" fill="#475569" text-anchor="middle">Έχω δικαίωμα να μαθαίνω,</text>
    <text x="72" y="90" font-size="10.5" fill="#475569" text-anchor="middle">να παίζω &amp; να με σέβονται!</text>
  </g>
  <!-- Σύμβολο Ισότητας / Συνεργασίας -->
  <circle cx="210" cy="80" r="16" fill="#f3e8ff" stroke="#a855f7" stroke-width="2"/>
  <text x="210" y="86" font-size="18" text-anchor="middle">🤝</text>
  <g transform="translate(225, 30)">
    <!-- Υποχρέωση / Κανόνας -->
    <rect width="145" height="100" rx="10" fill="#ffffff" stroke="#3b82f6" stroke-width="2"/>
    <text x="72" y="28" font-size="20" text-anchor="middle">🛡️</text>
    <text x="72" y="52" font-size="12.5" font-weight="bold" fill="#1d4ed8" text-anchor="middle">ΥΠΟΧΡΕΩΣΗ</text>
    <text x="72" y="74" font-size="10.5" fill="#475569" text-anchor="middle">Έχω ευθύνη να σέβομαι,</text>
    <text x="72" y="90" font-size="10.5" fill="#475569" text-anchor="middle">να βοηθώ &amp; να ακούω!</text>
  </g>
  <text x="210" y="162" font-size="13" font-weight="bold" fill="#581c87" text-anchor="middle">Όταν τηρούμε τους κανόνες, όλοι νιώθουμε ασφαλείς και χαρούμενοι!</text>
</svg>""",
        "easy_points": [
            "Όλοι οι μαθητές έχουν ίσα δικαιώματα στη μάθηση και στο παιχνίδι.",
            "Κάθε δικαίωμα συνοδεύεται από σεβασμό στους συμμαθητές μας.",
            "Οι κανόνες της τάξης υπάρχουν για να μας προστατεύουν και να είμαστε ομάδα."
        ],
        "analogy": "Όπως σε ένα επιτραπέζιο παιχνίδι, αν όλοι ακολουθούν τους κανόνες, όλοι διασκεδάζουν και περνούν όμορφα!"
    },

    # =========================================================================
    # 🏃 ΦΥΣΙΚΗ ΑΓΩΓΗ & ΥΓΕΙΑ (ΜΕΛΙΣΠΗ)
    # =========================================================================
    "pe_healthy_habits": {
        "id": "pe_healthy_habits",
        "title": "🏃‍♂️ Η Πυραμίδα της Υγείας & Άσκησης",
        "subject_tag": "Φυσική Αγωγή",
        "keywords": ["φυσικη αγωγη", "γυμναστικη", "σωματικη ασκηση", "αθλητισμος", "πυραμιδα υγειας", "διατροφη", "υγιεινη ζωη", "μελισπη", "αθλημα"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f0fdf4" stroke="#bbf7d0" stroke-width="2"/>
  <!-- 4 Πυλώνες Ευεξίας -->
  <g transform="translate(30, 30)">
    <rect x="0" y="0" width="80" height="85" rx="8" fill="#ffffff" stroke="#22c55e" stroke-width="2"/>
    <text x="40" y="32" font-size="24" text-anchor="middle">🏃</text>
    <text x="40" y="58" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">Κίνηση</text>
    <text x="40" y="74" font-size="9" fill="#475569" text-anchor="middle">Καθημερινά</text>

    <rect x="95" y="0" width="80" height="85" rx="8" fill="#ffffff" stroke="#3b82f6" stroke-width="2"/>
    <text x="135" y="32" font-size="24" text-anchor="middle">💧</text>
    <text x="135" y="58" font-size="11" font-weight="bold" fill="#1d4ed8" text-anchor="middle">Νερό</text>
    <text x="135" y="74" font-size="9" fill="#475569" text-anchor="middle">6-8 ποτήρια</text>

    <rect x="190" y="0" width="80" height="85" rx="8" fill="#ffffff" stroke="#eab308" stroke-width="2"/>
    <text x="230" y="32" font-size="24" text-anchor="middle">🍎</text>
    <text x="230" y="58" font-size="11" font-weight="bold" fill="#a16207" text-anchor="middle">Φρούτα</text>
    <text x="230" y="74" font-size="9" fill="#475569" text-anchor="middle">Ενέργεια</text>

    <rect x="285" y="0" width="80" height="85" rx="8" fill="#ffffff" stroke="#8b5cf6" stroke-width="2"/>
    <text x="325" y="32" font-size="24" text-anchor="middle">😴</text>
    <text x="325" y="58" font-size="11" font-weight="bold" fill="#6d28d9" text-anchor="middle">Ύπνος</text>
    <text x="325" y="74" font-size="9" fill="#475569" text-anchor="middle">9 ώρες</text>
  </g>
  <text x="210" y="152" font-size="12" fill="#334155" text-anchor="middle">Σύμφωνα με το ψηφιακό βιβλίο Φυσικής Αγωγής στη Μελίσπη (IEP).</text>
  <text x="210" y="169" font-size="13" font-weight="bold" fill="#14532d" text-anchor="middle">«Νους υγιής εν σώματι υγιεί» — Το σώμα δυναμώνει και το μυαλό λάμπει!</text>
</svg>""",
        "easy_points": [
            "Το σώμα μας χρειάζεται κίνηση, παιχνίδι και καθαρό αέρα κάθε μέρα.",
            "Πίνουμε άφθονο δροσερό νερό για να ξεδιψάει ο οργανισμός.",
            "Κοιμόμαστε νωρίς το βράδυ για να ξεκουράζεται το μυαλό μας."
        ],
        "analogy": "Το σώμα σου είναι σαν ένα αγωνιστικό αυτοκίνητο: θέλει καλό καύσιμο (υγιεινό φαγητό) και καλή συντήρηση (ύπνο και γυμναστική)!"
    },

    # =========================================================================
    # ⚙️ ΤΕΧΝΟΛΟΓΙΑ
    # =========================================================================
    "tech_lever_simple_machines": {
        "id": "tech_lever_simple_machines",
        "title": "🏗️ Ο Μοχλός & οι Απλές Μηχανές (Αρχιμήδης)",
        "subject_tag": "Τεχνολογία",
        "keywords": ["τεχνολογια", "μοχλος", "μηχανη", "αρχιμηδης", "βαρος", "υπομοχλιο", "εργαλειο", "δυναμη", "τραμπαλα"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <!-- Τραμπάλα / Μοχλός -->
  <g transform="translate(60, 40)">
    <!-- Τρίγωνο υπομόχλιο -->
    <polygon points="120,90 105,120 135,120" fill="#64748b"/>
    <circle cx="120" cy="90" r="5" fill="#0f172a"/>
    <text x="120" y="135" font-size="10.5" font-weight="bold" fill="#475569" text-anchor="middle">Υπομόχλιο (Κέντρο)</text>
    <!-- Ράβδος κεκλιμένη -->
    <line x1="20" y1="110" x2="280" y2="70" stroke="#0284c7" stroke-width="6" stroke-linecap="round"/>
    <!-- Βαρύ φορτίο αριστερά -->
    <rect x="25" y="85" width="35" height="25" rx="4" fill="#ef4444"/>
    <text x="42" y="102" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">Βάρος</text>
    <!-- Χέρι / Μικρή δύναμη δεξιά -->
    <circle cx="270" cy="65" r="14" fill="#22c55e"/>
    <text x="270" y="70" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">↓</text>
    <text x="270" y="45" font-size="10.5" font-weight="bold" fill="#15803d" text-anchor="middle">Μικρή Δύναμη</text>
  </g>
  <text x="210" y="152" font-size="12" fill="#334155" text-anchor="middle">Όσο πιο μακριά πιέζουμε από το κέντρο, τόσο πιο εύκολα σηκώνουμε το βάρος!</text>
  <text x="210" y="169" font-size="13" font-weight="bold" fill="#0369a1" text-anchor="middle">«Δώστε μου ένα σημείο να στηριχτώ και θα κινήσω τη Γη!» — Αρχιμήδης</text>
</svg>""",
        "easy_points": [
            "Ο μοχλός είναι ένα από τα αρχαιότερα και πιο έξυπνα εργαλεία του ανθρώπου.",
            "Μοιάζει με μια τραμπάλα στην παιδική χαρά.",
            "Μας επιτρέπει να σηκώνουμε τεράστια βάρη βάζοντας ελάχιστη δύναμη."
        ],
        "analogy": "Όταν ανοίγεις ένα καπάκι με ένα κουτάλι ή κόβεις χαρτί με το ψαλίδι, χρησιμοποιείς μοχλούς!"
    },

    # =========================================================================
    # 🫀 ΒΙΟΛΟΓΙΑ — ΑΝΘΡΩΠΙΝΟ ΣΩΜΑ
    # =========================================================================
    "biology_human_heart": {
        "id": "biology_human_heart",
        "title": "🫀 Η Καρδιά & το Αίμα (Η Αντλία της Ζωής)",
        "subject_tag": "Βιολογία",
        "keywords": ["καρδια", "αιμα", "κυκλοφορια", "παλμος", "οξυγονο", "αιμοφορα", "αντλια", "σφυγμος", "σωμα"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#fff1f2" stroke="#fecdd3" stroke-width="2"/>
  <!-- Καρδιά κεντρική -->
  <g transform="translate(100, 75)">
    <path d="M 0 -25 C -35 -60 -70 5 0 45 C 70 5 35 -60 0 -25 Z" fill="#e11d48" stroke="#9f1239" stroke-width="3"/>
    <text x="0" y="5" font-size="24" text-anchor="middle">💓</text>
    <text x="0" y="60" font-size="11" font-weight="bold" fill="#9f1239" text-anchor="middle">Χτυπάει ~75 φορές/λεπτό!</text>
  </g>
  <!-- Επεξήγηση Κυκλοφορίας -->
  <g transform="translate(210, 30)">
    <rect width="180" height="95" rx="10" fill="#ffffff" stroke="#fda4af" stroke-width="1.5"/>
    <text x="90" y="24" font-size="12.5" font-weight="bold" fill="#be123c" text-anchor="middle">Πώς Δουλεύει:</text>
    <text x="90" y="46" font-size="11" fill="#334155" text-anchor="middle">🔴 Κόκκινο Αίμα: με Οξυγόνο</text>
    <text x="90" y="64" font-size="11" fill="#334155" text-anchor="middle">🔵 Μπλε Αίμα: επιστρέφει πίσω</text>
    <text x="90" y="84" font-size="11.5" font-weight="bold" fill="#047857" text-anchor="middle">Τρέφει όλο το σώμα μας!</text>
  </g>
  <text x="210" y="165" font-size="13" font-weight="bold" fill="#881337" text-anchor="middle">Η καρδιά είναι ένας δυνατός μυς που δεν κουράζεται ποτέ!</text>
</svg>""",
        "easy_points": [
            "Η καρδιά έχει το μέγεθος της γροθιάς σου και βρίσκεται στο στήθος.",
            "Λειτουργεί σαν αυτόματη αντλία που στέλνει αίμα σε όλο το σώμα.",
            "Το αίμα μεταφέρει οξυγόνο και φαγητό στα κύτταρά μας."
        ],
        "analogy": "Όπως το λάστιχο του κήπου ποτίζει όλα τα λουλούδια, έτσι τα αγγεία δίνουν ζωή σε κάθε γωνιά του σώματός μας!"
    },

    # =========================================================================
    # 🏛️ ΑΡΧΑΙΑ ΕΛΛΗΝΙΚΗ ΓΛΩΣΣΑ
    # =========================================================================
    "ancient_word_parts": {
        "id": "ancient_word_parts",
        "title": "🏛️ Τα Μέρη της Λέξης: Θέμα & Κατάληξη",
        "subject_tag": "Αρχαία Ελληνική Γλώσσα",
        "keywords": ["αρχαια", "θεμα", "καταληξη", "καταληξεις", "μερη λεξης", "λογος", "λυω", "ριζα", "κλιση"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <text x="210" y="32" font-size="15" font-weight="bold" fill="#0f172a" text-anchor="middle">Η Λέξη στα Αρχαία: «λόγ-ος» (ὁ λόγος)</text>
  <g transform="translate(70, 50)">
    <rect width="130" height="70" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="2.5"/>
    <text x="65" y="36" font-size="24" font-weight="bold" fill="#1d4ed8" text-anchor="middle">λόγ-</text>
    <text x="65" y="58" font-size="12" font-weight="bold" fill="#1e40af" text-anchor="middle">ΘΕΜΑ (σταθερό)</text>
  </g>
  <text x="210" y="93" font-size="28" font-weight="bold" fill="#64748b" text-anchor="middle">+</text>
  <g transform="translate(225, 50)">
    <rect width="130" height="70" rx="10" fill="#ffedd5" stroke="#ea580c" stroke-width="2.5"/>
    <text x="65" y="36" font-size="24" font-weight="bold" fill="#c2410c" text-anchor="middle">-ος</text>
    <text x="65" y="58" font-size="12" font-weight="bold" fill="#9a3412" text-anchor="middle">ΚΑΤΑΛΗΞΗ (αλλάζει)</text>
  </g>
  <rect x="50" y="132" width="320" height="34" rx="8" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1"/>
  <text x="210" y="154" font-size="12" font-weight="bold" fill="#334155" text-anchor="middle">Σαν τρένο: Η μηχανή (Θέμα) μένει ίδια, το βαγόνι (Κατάληξη) αλλάζει!</text>
</svg>""",
        "easy_points": [
            "Κάθε λέξη στα αρχαία χωρίζεται σε δύο μέρη: Θέμα και Κατάληξη.",
            "Το Θέμα (λόγ-) μας δείχνει τη σημασία της λέξης και μένει σταθερό.",
            "Η Κατάληξη (-ος) αλλάζει στο τέλος ανάλογα με την πτώση (λόγ-ος, λόγ-ου, λόγ-ον)."
        ],
        "analogy": "Σκέψου ένα τρένο: Το θέμα είναι η μηχανή που δεν αλλάζει ποτέ, και η κατάληξη είναι το βαγόνι που αλλάζει στο τέλος!"
    },

    "ancient_declension_2": {
        "id": "ancient_declension_2",
        "title": "📜 Η β' Κλίση Ουσιαστικών (-ος, -ον)",
        "subject_tag": "Αρχαία Ελληνική Γλώσσα",
        "keywords": ["β κλιση", "δευτερα κλιση", "ουσιαστικα", "πτωσεις", "ονομαστικη", "γενικη", "δοτικη", "αιτιατικη", "κλητικη", "αρσενικα", "ουδετερα"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <text x="210" y="26" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">Οι 5 Πτώσεις στα Αρχαία: «ὁ λόγος» (Ενικός Αριθμός)</text>
  <g transform="translate(15, 42)">
    <rect x="0" y="0" width="74" height="85" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <text x="37" y="22" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">Ονομ.</text>
    <text x="37" y="48" font-size="14" font-weight="bold" fill="#1d4ed8" text-anchor="middle">ὁ λόγος</text>
    <text x="37" y="72" font-size="11" fill="#475569" text-anchor="middle">-ος</text>
    <rect x="78" y="0" width="74" height="85" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <text x="115" y="22" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">Γεν.</text>
    <text x="115" y="48" font-size="14" font-weight="bold" fill="#1d4ed8" text-anchor="middle">τοῦ λόγου</text>
    <text x="115" y="72" font-size="11" fill="#475569" text-anchor="middle">-ου</text>
    <rect x="156" y="0" width="74" height="85" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
    <text x="193" y="22" font-size="11" font-weight="bold" fill="#92400e" text-anchor="middle">Δοτ.</text>
    <text x="193" y="48" font-size="14" font-weight="bold" fill="#b45309" text-anchor="middle">τῷ λόγῳ</text>
    <text x="193" y="72" font-size="11" fill="#92400e" text-anchor="middle">-ῳ (υπογρ.)</text>
    <rect x="234" y="0" width="74" height="85" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <text x="271" y="22" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">Αιτ.</text>
    <text x="271" y="48" font-size="14" font-weight="bold" fill="#1d4ed8" text-anchor="middle">τὸν λόγον</text>
    <text x="271" y="72" font-size="11" fill="#475569" text-anchor="middle">-ον</text>
    <rect x="312" y="0" width="74" height="85" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
    <text x="349" y="22" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">Κλητ.</text>
    <text x="349" y="48" font-size="14" font-weight="bold" fill="#15803d" text-anchor="middle">ὦ λόγε</text>
    <text x="349" y="72" font-size="11" fill="#15803d" text-anchor="middle">-ε</text>
  </g>
  <text x="210" y="155" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">Προσοχή στη Δοτική: παίρνει πάντοτε υπογεγραμμένη (ῳ)!</text>
</svg>""",
        "easy_points": [
            "Η β' κλίση περιλαμβάνει αρσενικά και θηλυκά σε -ος (ὁ λόγος) και ουδέτερα σε -ον (τὸ δῶρον).",
            "Στα αρχαία έχουμε 5 πτώσεις: Ονομαστική, Γενική, Δοτική, Αιτιατική, Κλητική.",
            "Η Δοτική πτώση δεν υπάρχει στα νέα ελληνικά και παίρνει υπογεγραμμένη (τῷ λόγῳ)."
        ],
        "analogy": "Όπως αλλάζεις ρούχα ανάλογα με την περίσταση, έτσι και η λέξη αλλάζει κατάληξη ανάλογα με τον ρόλο της στην πρόταση!"
    },

    "ancient_verbs_omega": {
        "id": "ancient_verbs_omega",
        "title": "✍️ Τα Ρήματα σε -ω (Ενεστώτας: λύ-ω)",
        "subject_tag": "Αρχαία Ελληνική Γλώσσα",
        "keywords": ["ρημα", "ρηματα", "ενεστωτας", "λυω", "κλιση ρηματων", "ενεργητικη φωνη", "προσωπα"],
        "svg": """<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
  <rect width="420" height="180" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <text x="210" y="26" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">Κλίση Ρήματος στον Ενεστώτα: «λύ-ω» (λύνω)</text>
  <g transform="translate(30, 42)">
    <rect width="170" height="92" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <text x="85" y="22" font-size="12" font-weight="bold" fill="#1e40af" text-anchor="middle">Ενικός Αριθμός</text>
    <text x="20" y="44" font-size="13" fill="#1e293b">ἐγὼ <b>λύ-ω</b></text>
    <text x="20" y="64" font-size="13" fill="#1e293b">σὺ <b>λύ-εις</b></text>
    <text x="20" y="84" font-size="13" fill="#1e293b">οὗτος <b>λύ-ει</b></text>
  </g>
  <g transform="translate(220, 42)">
    <rect width="170" height="92" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
    <text x="85" y="22" font-size="12" font-weight="bold" fill="#15803d" text-anchor="middle">Πληθυντικός Αριθμός</text>
    <text x="20" y="44" font-size="13" fill="#1e293b">ἡμεῖς <b>λύ-ομεν</b></text>
    <text x="20" y="64" font-size="13" fill="#1e293b">ὑμεῖς <b>λύ-ετε</b></text>
    <text x="20" y="84" font-size="13" fill="#1e293b">οὗτοι <b>λύ-ουσι(ν)</b></text>
  </g>
  <text x="210" y="156" font-size="12" font-weight="bold" fill="#334155" text-anchor="middle">Οι καταλήξεις είναι: -ω, -εις, -ει, -ομεν, -ετε, -ουσι(ν)</text>
</svg>""",
        "easy_points": [
            "Τα βαρύτονα ρήματα στα αρχαία τελειώνουν σε -ω (λύω, γράφω, λέγω).",
            "Το θέμα λύ- μένει ίδιο σε όλα τα πρόσωπα.",
            "Αλλάζουν μόνο οι καταλήξεις: -ω, -εις, -ει, -ομεν, -ετε, -ουσι(ν)."
        ],
        "analogy": "Το ρήμα είναι σαν μια μηχανή που αλλάζει ταχύτητα ανάλογα με το ποιος οδηγεί (εγώ, εσύ, αυτός)!"
    }
}

def _subject_matches(card_subject_tag: str, current_subject: str) -> bool:
    """Ελέγχει αν το μάθημα της κάρτας ταιριάζει ΑΥΣΤΗΡΑ με το επιλεγμένο μάθημα."""
    if not current_subject:
        return True
    
    cur = _norm(current_subject)
    if "ολα τα μαθηματα" in cur or "γενικο" in cur:
        return True
        
    tag = _norm(card_subject_tag)
    
    # 1. Αρχαία Ελληνική Γλώσσα (Αυστηρός διαχωρισμός από άλλα μαθήματα)
    if "αρχαια ελληνικη γλωσσα" in cur or ("αρχαια" in cur and "μεταφραση" not in cur and "οδυσσεια" not in cur):
        return tag == "αρχαια ελληνικη γλωσσα" or tag == "αρχαια"
        
    # 2. Αρχαία Μετάφραση / Ομήρου Οδύσσεια
    if "οδυσσεια" in cur or "ιλιαδα" in cur or "αρχαια μεταφραση" in cur:
        return "οδυσσεια" in tag or "ιλιαδα" in tag or "ομηρ" in tag
        
    # 3. Νεοελληνική Γλώσσα
    if "νεοελληνικη γλωσσα" in cur:
        return "νεοελληνικη γλωσσα" in tag or tag == "γλωσσα"
        
    # 4. Νεοελληνική Λογοτεχνία
    if "λογοτεχνια" in cur:
        return "λογοτεχνια" in tag
        
    # 5. Μαθηματικά
    if "μαθηματικα" in cur or "αλγεβρα" in cur or "γεωμετρια" in cur:
        return "μαθηματικα" in tag
        
    # 6. Φυσική (και ΟΧΙ Φυσική Αγωγή)
    if "φυσικη" in cur and "αγωγη" not in cur:
        return "φυσικη" in tag and "αγωγη" not in tag
        
    # 7. Φυσική Αγωγή (Γυμναστική)
    if "φυσικη αγωγη" in cur or "γυμναστικη" in cur:
        return "φυσικη αγωγη" in tag
        
    # 8. Χημεία
    if "χημεια" in cur:
        return "χημεια" in tag
        
    # 9. Βιολογία
    if "βιολογια" in cur:
        return "βιολογια" in tag
        
    # 10. Ιστορία
    if "ιστορια" in cur:
        return "ιστορια" in tag
        
    # 11. Γεωγραφία
    if "γεωγραφια" in cur:
        return "γεωγραφια" in tag
        
    # 12. Πληροφορική
    if "πληροφορικη" in cur:
        return "πληροφορικη" in tag
        
    # 13. Κοινωνική & Πολιτική Αγωγή
    if "κοινωνικη" in cur or "πολιτικη αγωγη" in cur:
        return "κοινωνικη" in tag or "πολιτικη" in tag
        
    # 14. Τεχνολογία
    if "τεχνολογια" in cur:
        return "τεχνολογια" in tag
        
    return tag in cur or cur in tag

def find_matching_card(text: str, subject: str = "", grade: str = "") -> Optional[dict]:
    """
    Εντοπίζει αυτόματα την καταλληλότερη παιδαγωγική οπτική κάρτα
    με ΑΥΣΤΗΡΟ φιλτράρισμα μαθήματος και λέξεων-κλειδιών (ακριβή όρια λέξεων).
    """
    if not text:
        return None
    
    clean_text = _norm(text)
    
    # Φιλτράρισμα: Εξετάζουμε ΜΟΝΟ κάρτες που ανήκουν στο τρέχον μάθημα!
    candidate_cards = [
        card for card in PEDAGOGICAL_CARDS.values()
        if _subject_matches(card.get("subject_tag", ""), subject)
    ]
    
    if not candidate_cards:
        return None
        
    best_card = None
    max_score = 0
    
    for card in candidate_cards:
        score = 0
        matches_count = 0
        for kw in card["keywords"]:
            norm_kw = _norm(kw)
            # Ακέραια ταύτιση λέξεων (όχι υποσυμβολοσειρές π.χ. "ασκηση" σε "εξασκηση")
            pattern = r'(?<!\w)' + re.escape(norm_kw) + r'(?!\w)'
            if re.search(pattern, clean_text):
                score += len(norm_kw)
                matches_count += 1
        
        # Απαιτούμε είτε μία ισχυρή λέξη-κλειδί (>=6 γράμματα) είτε τουλάχιστον 2 ταυτίσεις
        if (score >= 6 or matches_count >= 2) and score > max_score:
            max_score = score
            best_card = card
            
    return best_card

def get_cards_for_subject(subject: str) -> List[dict]:
    """Επιστρέφει όλες τις διαθέσιμες οπτικές κάρτες για το συγκεκριμένο μάθημα (χωρίς άσχετες διαρροές)."""
    matches = [
        card for card in PEDAGOGICAL_CARDS.values()
        if _subject_matches(card.get("subject_tag", ""), subject)
    ]
    return matches

_SIMPLIFIED_BOTTOM_TEXTS = {
    "biology_cell": "Όλοι οι οργανισμοί (άνθρωποι, ζώα, φυτά) αποτελούνται από κύτταρα!",
    "biology_photosynthesis": "Τα φυτά φτιάχνουν τροφή χρησιμοποιώντας το φως του ήλιου!",
    "literature_odyssey_trojan_horse": "Ο Οδυσσέας νίκησε με τη σκέψη και την εξυπνάδα του!",
    "informatics_computer_parts": "Υλικό είναι ό,τι αγγίζουμε — Λογισμικό είναι τα προγράμματα!",
}

def _expand_svg_to_540(cid: str, svg_str: str) -> str:
    """Προσαρμόζει αυτόματα τα SVG στα 540px πλάτος ώστε να μην κόβεται κανένα στοιχείο ή κείμενο."""
    if not svg_str or 'viewBox=' not in svg_str:
        return svg_str
    m_vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_str)
    if not m_vb:
        return svg_str
    orig_w = int(m_vb.group(1))
    orig_h = int(m_vb.group(2))
    
    if orig_w == 540:
        return svg_str
        
    pad_x = (540 - orig_w) // 2
    
    # 1. Update viewBox
    svg_str = re.sub(rf'viewBox="0 0 {orig_w} (\d+)"', r'viewBox="0 0 540 \1"', svg_str, count=1)
    
    # 2. Update background rect
    svg_str = re.sub(rf'<rect width="{orig_w}" height="{orig_h}"', rf'<rect width="540" height="{orig_h}"', svg_str, count=1)
    
    # 3. Find background rect closing tag
    rect_pattern = rf'<rect width="540" height="{orig_h}"[^>]*/>'
    rect_m = re.search(rect_pattern, svg_str)
    if not rect_m:
        return svg_str
    rect_end = rect_m.end()
    
    before_bottom = svg_str[rect_end:]
    
    center_x = orig_w // 2
    text_center_matches = list(re.finditer(rf'<text\s+x="{center_x}"', before_bottom))
    if not text_center_matches:
        return svg_str
    
    first_bottom_idx = text_center_matches[0].start()
    inner_graphics = before_bottom[:first_bottom_idx]
    bottom_texts = before_bottom[first_bottom_idx:]
    
    bottom_texts = re.sub(rf'<text\s+x="{center_x}"', '<text x="270"', bottom_texts)
    
    if cid in _SIMPLIFIED_BOTTOM_TEXTS:
        bottom_texts = re.sub(r'(<text[^>]*>)(.*?)(</text>)', rf'\g<1>{_SIMPLIFIED_BOTTOM_TEXTS[cid]}\g<3>', bottom_texts)
    
    def tune_fs(m):
        fs = float(m.group(1))
        new_fs = 11.5 if fs >= 13 else (11.0 if fs >= 12 else fs)
        return f'font-size="{new_fs}"'
    bottom_texts = re.sub(r'font-size="([\d\.]+)"', tune_fs, bottom_texts)
    
    new_svg = (
        svg_str[:rect_end]
        + f"\n  <g transform=\"translate({pad_x}, 0)\">"
        + inner_graphics
        + "  </g>\n"
        + bottom_texts
    )
    return new_svg

# Αυτόματη εξομάλυνση όλων των καρτών σε πλάτος 540px με άνετα περιθώρια
for _cid, _card in PEDAGOGICAL_CARDS.items():
    _card["svg"] = _expand_svg_to_540(_cid, _card["svg"])

def render_visual_card_html(card: dict) -> str:
    """Παράγει κομψό, προσβάσιμο HTML για την προβολή της οπτικής κάρτας στην οθόνη."""
    if card and isinstance(card, dict) and card.get("id") in PEDAGOGICAL_CARDS:
        card = PEDAGOGICAL_CARDS[card["id"]]
    card_id = card.get("id", "")
    card_svg = _expand_svg_to_540(card_id, card.get("svg", ""))
    points_html = "".join([f"<li style='margin-bottom: 3px;'>{p}</li>" for p in card["easy_points"]])
    clean_svg = " ".join(line.strip() for line in card_svg.splitlines() if line.strip())
    
    html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{
    box-sizing: border-box;
  }}
  body {{
    margin: 0;
    padding: 2px 4px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: transparent;
  }}
  .pedagogical-visual-card {{
    background: #ffffff;
    border: 2px solid #3b82f6;
    border-radius: 12px;
    padding: 10px 14px;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.12);
    width: 100%;
  }}
  .card-svg-container {{
    margin: 6px 0;
    text-align: center;
    background: #f8fafc;
    border-radius: 8px;
    padding: 6px;
  }}
  .card-svg-container svg {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
  }}
  .card-easy-read {{
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 6px;
  }}
</style>
</head>
<body>
<div class="pedagogical-visual-card">
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
    <span style="font-weight: 800; color: #1e3a8a; font-size: 0.98rem;">{card['title']}</span>
    <span style="background: #dbeafe; color: #1e40af; font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 8px;">{card['subject_tag']}</span>
  </div>
  <div class="card-svg-container">
    {clean_svg}
  </div>
  <div class="card-easy-read">
    <div style="font-weight: 800; color: #14532d; font-size: 0.86rem; margin-bottom: 3px;">💡 Τι μαθαίνουμε από την εικόνα (Easy-to-Read):</div>
    <ul style="margin: 0; padding-left: 18px; color: #1e293b; font-size: 0.86rem; line-height: 1.4;">{points_html}</ul>
    <div style="margin-top: 5px; font-size: 0.82rem; color: #334155; font-style: italic;">🍎 <b>Παράδειγμα:</b> {card['analogy']}</div>
  </div>
</div>
</body>
</html>"""
    return html_code
