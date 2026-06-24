import streamlit as st
import math
import random

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Angle Quest 📐",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Space+Mono:wght@700&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; }
#MainMenu, footer, header { visibility: hidden; }

.hero { text-align: center; padding: 1.6rem 1rem 0.6rem; }
.hero h1 {
    font-family: 'Nunito', sans-serif; font-weight: 900;
    font-size: clamp(2rem, 5vw, 3.4rem);
    background: linear-gradient(90deg, #f7971e, #ffd200, #f7971e);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -1px; margin-bottom: 0.2rem;
}
.hero p { color: #c9d1d9; font-size: 1rem; margin: 0; }

.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px; padding: 1.4rem; margin-bottom: 0.8rem;
    backdrop-filter: blur(10px);
}
.card h3 { color: #ffd200; margin: 0 0 0.5rem; }

.badge { display:inline-block; padding:0.3rem 0.9rem; border-radius:50px; font-weight:700; font-size:0.82rem; margin:0.2rem; }
.badge-acute    { background:#6ee7f7; color:#0a2540; }
.badge-right    { background:#a78bfa; color:#1e0a40; }
.badge-obtuse   { background:#fbbf24; color:#3b1f00; }
.badge-straight { background:#fb923c; color:#3b0f00; }
.badge-reflex   { background:#f472b6; color:#3b0030; }

.angle-canvas {
    background: rgba(255,255,255,0.04); border-radius:16px;
    border:1px solid rgba(255,255,255,0.1);
    display:flex; justify-content:center; align-items:center; padding:1rem;
}
.feedback-correct {
    background:rgba(52,211,153,0.2); border:2px solid #34d399;
    border-radius:12px; padding:0.8rem 1.2rem; color:#d1fae5;
    font-weight:700; font-size:1rem; margin-top:0.6rem;
}
.feedback-wrong {
    background:rgba(248,113,113,0.2); border:2px solid #f87171;
    border-radius:12px; padding:0.8rem 1.2rem; color:#fee2e2;
    font-weight:700; font-size:1rem; margin-top:0.6rem;
}
.rule-box {
    background:rgba(167,139,250,0.15); border:2px solid #a78bfa;
    border-radius:12px; padding:0.8rem 1.2rem; color:#ede9fe;
    font-size:0.95rem; margin-top:0.5rem;
}
.stButton > button {
    font-family:'Nunito',sans-serif; font-weight:800; border-radius:50px;
    padding:0.55rem 1.8rem; font-size:1rem; transition:transform 0.15s;
}
.stButton > button:hover { transform:scale(1.04); }
[data-testid="metric-container"] {
    background:rgba(255,255,255,0.06); border-radius:14px;
    padding:0.7rem 1rem; border:1px solid rgba(255,255,255,0.1);
}
[data-testid="metric-container"] label { color:#9ca3af !important; font-size:0.78rem !important; }
[data-testid="metric-value"] { color:#ffd200 !important; font-family:'Space Mono',monospace !important; font-size:1.5rem !important; }
input[type="number"] {
    background:rgba(255,255,255,0.08) !important;
    border:2px solid rgba(255,255,255,0.2) !important;
    border-radius:10px !important; color:#f0f4f8 !important;
    font-family:'Space Mono',monospace !important; font-size:1.1rem !important;
}
div[role="radiogroup"] label {
    background:rgba(255,255,255,0.08); border:2px solid rgba(255,255,255,0.15);
    border-radius:50px; padding:0.4rem 1.1rem; cursor:pointer;
    font-weight:700; color:#e2e8f0; font-size:0.95rem; transition:all 0.15s;
}
div[role="radiogroup"] label:hover { background:rgba(247,151,30,0.2); border-color:#f7971e; }
hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
def init():
    defaults = dict(page="home", score=0, streak=0, best_streak=0,
                    total=0, correct=0, q=None, feedback=None,
                    answered=False, mode="calculate")
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()


# ── Angle type definitions ─────────────────────────────────────────────────────
TYPES = {
    "Acute":    {"range": (1,  89),  "colour": "#6ee7f7", "emoji": "🔵",
                 "desc": "Less than 90°. Think of a sharp pencil tip! ✏️"},
    "Right":    {"range": (90, 90),  "colour": "#a78bfa", "emoji": "🟣",
                 "desc": "Exactly 90°. Like the corner of a book or a square tile. 📐"},
    "Obtuse":   {"range": (91, 179), "colour": "#fbbf24", "emoji": "🟡",
                 "desc": "Between 90° and 180°. Bigger than a right angle. 🛋️"},
    "Straight": {"range": (180,180), "colour": "#fb923c", "emoji": "🟠",
                 "desc": "Exactly 180°. A perfectly flat, straight line. 📏"},
    "Reflex":   {"range": (181,359), "colour": "#f472b6", "emoji": "🩷",
                 "desc": "Between 180° and 360°. The big wrap-around angle. 🌀"},
}

def classify(d):
    if d < 90:    return "Acute"
    if d == 90:   return "Right"
    if d < 180:   return "Obtuse"
    if d == 180:  return "Straight"
    return "Reflex"


# ── SVG helpers ────────────────────────────────────────────────────────────────
def svg_angle(deg, colour="#ffd200", size=300, mark_right=False):
    cx = cy = size // 2
    r = size * 0.34
    rad = math.radians(deg)
    x1, y1 = cx + r, cy
    x2, y2 = cx + r * math.cos(rad), cy - r * math.sin(rad)
    arc_r = size * 0.14
    large = 1 if deg > 180 else 0
    ax, ay = cx + arc_r * math.cos(rad), cy - arc_r * math.sin(rad)
    arc_d = f"M {cx+arc_r:.1f} {cy} A {arc_r:.1f} {arc_r:.1f} 0 {large} 0 {ax:.1f} {ay:.1f}"
    right_sq = (f'<polyline points="{cx+14},{cy} {cx+14},{cy-14} {cx},{cy-14}" '
                f'fill="none" stroke="{colour}" stroke-width="2.5"/>') if mark_right else ""
    return f"""
<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:{size}px">
  <defs><marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0,8 3,0 6" fill="{colour}" opacity="0.8"/></marker></defs>
  <line x1="{cx}" y1="{cy}" x2="{x1:.1f}" y2="{y1:.1f}"
        stroke="{colour}" stroke-width="3.5" stroke-linecap="round" marker-end="url(#arr)"/>
  <line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}"
        stroke="{colour}" stroke-width="3.5" stroke-linecap="round" marker-end="url(#arr)"/>
  <circle cx="{cx}" cy="{cy}" r="5" fill="{colour}"/>
  <path d="{arc_d}" fill="none" stroke="{colour}" stroke-width="2.5" opacity="0.7"/>
  {right_sq}
  <text x="{cx+55}" y="{cy-16}" fill="{colour}"
        font-family="Space Mono,monospace" font-size="17" font-weight="700">{deg}°</text>
</svg>"""


def svg_unknown(known, rule, colour="#ffd200", size=310):
    cx = cy = size // 2
    r = int(size * 0.38)

    if rule == "angles_on_line":
        parts = [f'<line x1="{cx-r}" y1="{cy}" x2="{cx+r}" y2="{cy}" '
                 f'stroke="rgba(255,255,255,0.3)" stroke-width="2"/>']
        cum = 0
        for a in known:
            cum += a
            rad = math.radians(cum)
            ex = cx + r * math.cos(math.pi - rad)
            ey = cy - r * math.sin(math.pi - rad)
            parts.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" '
                         f'stroke="{colour}" stroke-width="3" stroke-linecap="round"/>')
            mr = math.radians(cum - a / 2)
            lx = cx + 52 * math.cos(math.pi - mr)
            ly = cy - 52 * math.sin(math.pi - mr)
            parts.append(f'<text x="{lx:.0f}" y="{ly:.0f}" fill="#ffd200" '
                         f'font-family="Space Mono,monospace" font-size="14" '
                         f'text-anchor="middle" dominant-baseline="middle">{a}°</text>')
        rm = math.radians(cum + (180 - cum) / 2)
        ux = cx + 52 * math.cos(math.pi - rm)
        uy = cy - 52 * math.sin(math.pi - rm)
        parts.append(f'<text x="{ux:.0f}" y="{uy:.0f}" fill="#f472b6" '
                     f'font-family="Space Mono,monospace" font-size="16" font-weight="700" '
                     f'text-anchor="middle" dominant-baseline="middle">?°</text>')
        inner = "\n".join(parts)

    elif rule == "angles_at_point":
        parts = []
        cum = 0
        for a in known:
            cum += a
            rad = math.radians(cum)
            ex = cx + r * math.cos(rad)
            ey = cy - r * math.sin(rad)
            parts.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" '
                         f'stroke="{colour}" stroke-width="3" stroke-linecap="round"/>')
            mr = math.radians(cum - a / 2)
            lx = cx + 58 * math.cos(mr)
            ly = cy - 58 * math.sin(mr)
            parts.append(f'<text x="{lx:.0f}" y="{ly:.0f}" fill="#ffd200" '
                         f'font-family="Space Mono,monospace" font-size="14" '
                         f'text-anchor="middle" dominant-baseline="middle">{a}°</text>')
        rm = math.radians(cum + (360 - cum) / 2)
        ux = cx + 58 * math.cos(rm)
        uy = cy - 58 * math.sin(rm)
        parts.append(f'<text x="{ux:.0f}" y="{uy:.0f}" fill="#f472b6" '
                     f'font-family="Space Mono,monospace" font-size="16" font-weight="700" '
                     f'text-anchor="middle" dominant-baseline="middle">?°</text>')
        inner = "\n".join(parts)

    else:  # vertically_opposite
        v = known[0]
        rad = math.radians(v)
        ex1 = cx + r * math.cos(math.pi - rad)
        ey1 = cy - r * math.sin(math.pi - rad)
        ex2 = cx + r * math.cos(-rad)
        ey2 = cy - r * math.sin(-rad)
        inner = (f'<line x1="{cx-r}" y1="{cy}" x2="{cx+r}" y2="{cy}" stroke="{colour}" stroke-width="3"/>'
                 f'<line x1="{ex1:.1f}" y1="{ey1:.1f}" x2="{ex2:.1f}" y2="{ey2:.1f}" stroke="{colour}" stroke-width="3"/>'
                 f'<text x="{cx+26}" y="{cy-18}" fill="#ffd200" font-family="Space Mono,monospace" font-size="14">{v}°</text>'
                 f'<text x="{cx-62}" y="{cy+26}" fill="#ffd200" font-family="Space Mono,monospace" font-size="14">{v}°</text>'
                 f'<text x="{cx-62}" y="{cy-18}" fill="#f472b6" font-family="Space Mono,monospace" font-size="16" font-weight="700">?°</text>'
                 f'<text x="{cx+26}" y="{cy+26}" fill="#f472b6" font-family="Space Mono,monospace" font-size="16" font-weight="700">?°</text>')

    return f"""
<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:{size}px">
  <circle cx="{cx}" cy="{cy}" r="5" fill="{colour}"/>
  {inner}
</svg>"""


# ── Question generators ────────────────────────────────────────────────────────
def _safe_known_line_2():
    a, b = random.randint(20, 70), random.randint(20, 70)
    return [a, b] if a + b < 170 else [35, 45]

def _safe_known_point_3():
    a, b, c = random.randint(40, 90), random.randint(40, 90), random.randint(40, 90)
    return [a, b, c] if a + b + c < 340 else [80, 90, 70]

def _safe_known_point_2():
    a, b = random.randint(60, 150), random.randint(60, 120)
    return [a, b] if a + b < 340 else [100, 120]

SCENARIOS = [
    {
        "rule": "angles_on_line",
        "desc": "Two angles sit on a straight line. One angle is {k0}°. What is angle ?°?",
        "hint": "Angles on a straight line always add up to 180°.\nSo ? = 180° − {k0}° = {ans}°.",
        "known_fn": lambda: [random.randint(20, 150)],
        "ans_fn":   lambda k: 180 - k[0],
    },
    {
        "rule": "angles_on_line",
        "desc": "Three angles sit on a straight line: {k0}° and {k1}°. What is the missing angle ?°?",
        "hint": "Angles on a straight line add up to 180°.\nSo ? = 180° − {k0}° − {k1}° = {ans}°.",
        "known_fn": _safe_known_line_2,
        "ans_fn":   lambda k: 180 - sum(k),
    },
    {
        "rule": "angles_at_point",
        "desc": "Three angles meet at a point: {k0}°, {k1}°, and {k2}°. Find the missing angle ?°.",
        "hint": "Angles at a point always add up to 360°.\nSo ? = 360° − {k0}° − {k1}° − {k2}° = {ans}°.",
        "known_fn": _safe_known_point_3,
        "ans_fn":   lambda k: 360 - sum(k),
    },
    {
        "rule": "angles_at_point",
        "desc": "Two angles meet at a point: {k0}° and {k1}°. What is the unknown angle ?°?",
        "hint": "Angles at a point add up to 360°.\nSo ? = 360° − {k0}° − {k1}° = {ans}°.",
        "known_fn": _safe_known_point_2,
        "ans_fn":   lambda k: 360 - sum(k),
    },
    {
        "rule": "vertically_opposite",
        "desc": "Two straight lines cross each other. One angle is {k0}°. What is the angle marked ?°?",
        "hint": "Angles on a straight line add up to 180°.\nVertically opposite angles are equal.\nSo ? = 180° − {k0}° = {ans}°.",
        "known_fn": lambda: [random.randint(20, 160)],
        "ans_fn":   lambda k: 180 - k[0],
    },
]

def gen_calculate_q():
    sc = random.choice(SCENARIOS)
    known = sc["known_fn"]()
    answer = sc["ans_fn"](known)
    if answer <= 0 or answer >= 360:   # safety fallback
        known, answer = [60], 120
    fmt = {f"k{i}": v for i, v in enumerate(known)}
    fmt["ans"] = answer
    return {
        "rule":   sc["rule"],
        "known":  known,
        "answer": answer,
        "desc":   sc["desc"].format(**fmt),
        "hint":   sc["hint"].format(**fmt),
    }

def gen_identify_q():
    cat = random.choice(list(TYPES.keys()))
    lo, hi = TYPES[cat]["range"]
    deg = lo if lo == hi else random.randint(lo, hi)
    wrong = random.sample([k for k in TYPES if k != cat], 3)
    opts = wrong + [cat]
    random.shuffle(opts)
    return {"angle": deg, "answer": cat, "options": opts}


# ── Navigation ─────────────────────────────────────────────────────────────────
def nav(page):
    st.session_state.page = page
    st.session_state.q = None
    st.session_state.feedback = None
    st.session_state.answered = False


# ── Shared scoreboard ──────────────────────────────────────────────────────────
def show_score():
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⭐ Score", st.session_state.score)
    c2.metric("🔥 Streak", st.session_state.streak)
    c3.metric("🏆 Best Streak", st.session_state.best_streak)
    c4.metric("✅ Correct", f"{st.session_state.correct}/{st.session_state.total}")


# ── HOME ───────────────────────────────────────────────────────────────────────
def page_home():
    st.markdown(
        '<div class="hero"><h1>📐 Angle Quest</h1>'
        '<p>Become an angle master! Learn, practise, and level up 🚀</p></div>',
        unsafe_allow_html=True)
    st.markdown("")

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown('<div class="card" style="text-align:center">'
                    '<div style="font-size:2.8rem">📖</div><h3>Learn</h3>'
                    '<p style="color:#9ca3af;font-size:0.9rem">Meet all 5 angle types with diagrams and tips</p>'
                    '</div>', unsafe_allow_html=True)
        if st.button("Start Learning →", key="hl", use_container_width=True):
            nav("learn")

    with c2:
        st.markdown('<div class="card" style="text-align:center">'
                    '<div style="font-size:2.8rem">🔢</div><h3>Calculate</h3>'
                    '<p style="color:#9ca3af;font-size:0.9rem">Find unknown angles using angle rules</p>'
                    '</div>', unsafe_allow_html=True)
        if st.button("Start Calculating →", key="hc", use_container_width=True):
            st.session_state.mode = "calculate"
            nav("quiz")

    with c3:
        st.markdown('<div class="card" style="text-align:center">'
                    '<div style="font-size:2.8rem">🎯</div><h3>Identify</h3>'
                    '<p style="color:#9ca3af;font-size:0.9rem">Name the angle type from its diagram</p>'
                    '</div>', unsafe_allow_html=True)
        if st.button("Start Identifying →", key="hi", use_container_width=True):
            st.session_state.mode = "identify"
            nav("quiz")

    if st.session_state.total > 0:
        st.divider()
        st.markdown("<p style='text-align:center;color:#9ca3af;font-size:0.82rem;"
                    "margin-bottom:0.4rem'>YOUR PROGRESS</p>", unsafe_allow_html=True)
        show_score()


# ── LEARN ──────────────────────────────────────────────────────────────────────
def page_learn():
    st.markdown('<div class="hero"><h1 style="font-size:2.1rem">📖 Angle Types</h1></div>',
                unsafe_allow_html=True)

    tabs = st.tabs([f"{v['emoji']} {k}" for k, v in TYPES.items()])
    for tab, (name, info) in zip(tabs, TYPES.items()):
        with tab:
            lo, hi = info["range"]
            ex = lo if lo == hi else (lo + hi) // 2
            col_svg, col_txt = st.columns([1, 1], gap="large")
            with col_svg:
                st.markdown(
                    f'<div class="angle-canvas">'
                    f'{svg_angle(ex, info["colour"], mark_right=(name=="Right"))}'
                    f'</div>',
                    unsafe_allow_html=True)
            with col_txt:
                rng = f"Exactly {lo}°" if lo == hi else f"{lo}° – {hi}°"
                st.markdown(f"""<div class="card">
                  <span class="badge badge-{name.lower()}">{name} angle</span>
                  <p style="color:#e2e8f0;font-size:1.05rem;margin-top:0.7rem">{info['desc']}</p>
                  <p style="color:#9ca3af;font-size:0.88rem;margin-bottom:0">Range: <b style="color:#ffd200">{rng}</b></p>
                </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("""<div class="card"><h3>📏 Key Angle Rules to Remember</h3>
      <table style="color:#e2e8f0;width:100%;border-collapse:collapse">
        <tr style="border-bottom:1px solid rgba(255,255,255,0.1)">
          <td style="padding:0.55rem 0.8rem">📐 Angles on a straight line</td>
          <td style="padding:0.55rem 0.8rem;color:#ffd200;font-weight:700;font-family:'Space Mono',monospace">add up to 180°</td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.1)">
          <td style="padding:0.55rem 0.8rem">⭕ Angles at a point</td>
          <td style="padding:0.55rem 0.8rem;color:#ffd200;font-weight:700;font-family:'Space Mono',monospace">add up to 360°</td>
        </tr>
        <tr>
          <td style="padding:0.55rem 0.8rem">✖️ Vertically opposite angles</td>
          <td style="padding:0.55rem 0.8rem;color:#ffd200;font-weight:700;font-family:'Space Mono',monospace">are equal</td>
        </tr>
      </table></div>""", unsafe_allow_html=True)

    if st.button("← Back to Home", key="lb"):
        nav("home")


# ── QUIZ ───────────────────────────────────────────────────────────────────────
def page_quiz():
    mode = st.session_state.mode
    title = ("🔢 Calculate the Unknown Angle"
             if mode == "calculate" else "🎯 Identify the Angle Type")
    st.markdown(f'<div class="hero"><h1 style="font-size:2rem">{title}</h1></div>',
                unsafe_allow_html=True)
    show_score()
    st.divider()

    # Generate a new question if needed
    if st.session_state.q is None:
        st.session_state.q = gen_calculate_q() if mode == "calculate" else gen_identify_q()
        st.session_state.feedback = None
        st.session_state.answered = False

    q = st.session_state.q

    # ── CALCULATE mode ─────────────────────────────────────────────────────────
    if mode == "calculate":
        st.markdown(f'<div class="card"><p style="color:#e2e8f0;font-size:1.05rem;margin:0">'
                    f'❓ {q["desc"]}</p></div>', unsafe_allow_html=True)

        col_svg, col_form = st.columns([1, 1], gap="large")

        with col_svg:
            st.markdown(f'<div class="angle-canvas">{svg_unknown(q["known"], q["rule"])}</div>',
                        unsafe_allow_html=True)

        with col_form:
            st.markdown("<p style='color:#e2e8f0;font-weight:700;margin-bottom:0.3rem'>"
                        "Type your answer (°) and press Check:</p>",
                        unsafe_allow_html=True)
            user_ans = st.number_input(
                "Answer", min_value=1, max_value=359, step=1,
                key="calc_input", label_visibility="collapsed")

            if not st.session_state.answered:
                if st.button("✅ Check My Answer", key="chk", use_container_width=True):
                    correct = q["answer"]
                    if user_ans == correct:
                        st.session_state.score += 10
                        st.session_state.streak += 1
                        st.session_state.best_streak = max(
                            st.session_state.best_streak, st.session_state.streak)
                        st.session_state.correct += 1
                        st.session_state.feedback = (
                            "correct",
                            f"🎉 Brilliant! The answer is {correct}°. You got +10 points!")
                    else:
                        st.session_state.streak = 0
                        st.session_state.feedback = (
                            "wrong",
                            f"Not quite — the answer was {correct}°. You entered {user_ans}°.")
                    st.session_state.total += 1
                    st.session_state.answered = True
                    st.rerun()

            if st.session_state.feedback:
                kind, msg = st.session_state.feedback
                css = "feedback-correct" if kind == "correct" else "feedback-wrong"
                st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)
                hint_html = q["hint"].replace("\n", "<br>")
                st.markdown(f'<div class="rule-box">💡 <b>Explanation:</b><br>{hint_html}</div>',
                            unsafe_allow_html=True)
                if st.button("➡️ Next Question", key="nxt", use_container_width=True):
                    st.session_state.q = None
                    st.rerun()

    # ── IDENTIFY mode ──────────────────────────────────────────────────────────
    else:
        deg = q["angle"]
        cat = classify(deg)
        colour = TYPES[cat]["colour"]

        col_svg, col_form = st.columns([1, 1], gap="large")

        with col_svg:
            st.markdown(
                f'<div class="angle-canvas">'
                f'{svg_angle(deg, colour, mark_right=(deg == 90))}'
                f'</div>',
                unsafe_allow_html=True)
            st.markdown(f'<p style="text-align:center;color:#9ca3af;font-size:0.85rem;'
                        f'margin-top:0.3rem">The angle shown is {deg}°</p>',
                        unsafe_allow_html=True)

        with col_form:
            st.markdown("<p style='color:#e2e8f0;font-weight:700;margin-bottom:0.3rem'>"
                        "What type of angle is this?</p>", unsafe_allow_html=True)
            user_choice = st.radio(
                "Choose:", q["options"], key="id_radio",
                label_visibility="collapsed")

            if not st.session_state.answered:
                if st.button("✅ Check My Answer", key="chk_id", use_container_width=True):
                    correct = q["answer"]
                    if user_choice == correct:
                        st.session_state.score += 10
                        st.session_state.streak += 1
                        st.session_state.best_streak = max(
                            st.session_state.best_streak, st.session_state.streak)
                        st.session_state.correct += 1
                        st.session_state.feedback = (
                            "correct",
                            f"🎉 Correct! {deg}° is a {correct} angle. +10 points!")
                    else:
                        st.session_state.streak = 0
                        st.session_state.feedback = (
                            "wrong",
                            f"Not quite! You said {user_choice}, "
                            f"but {deg}° is a {correct} angle.")
                    st.session_state.total += 1
                    st.session_state.answered = True
                    st.rerun()

            if st.session_state.feedback:
                kind, msg = st.session_state.feedback
                css = "feedback-correct" if kind == "correct" else "feedback-wrong"
                correct = q["answer"]
                st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="rule-box">💡 <b>Remember:</b> {TYPES[correct]["desc"]}</div>',
                    unsafe_allow_html=True)
                if st.button("➡️ Next Question", key="nxt_id", use_container_width=True):
                    st.session_state.q = None
                    st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Home", key="qhome", use_container_width=True):
            nav("home")
    with c2:
        other = "identify" if mode == "calculate" else "calculate"
        lbl = "Switch to Identify 🎯" if mode == "calculate" else "Switch to Calculate 🔢"
        if st.button(lbl, key="qswitch", use_container_width=True):
            st.session_state.mode = other
            nav("quiz")


# ── Router ─────────────────────────────────────────────────────────────────────
{"home": page_home, "learn": page_learn, "quiz": page_quiz}[st.session_state.page]()
