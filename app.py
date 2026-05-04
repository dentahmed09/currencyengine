import streamlit as st

st.set_page_config(
    page_title="منصة المَالِك التعليمية",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap');

* {
    direction: rtl;
    font-family: 'Tajawal', sans-serif !important;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 100% !important; padding-bottom: 0 !important; }
[data-testid="stAppViewContainer"] { background: transparent; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Page Background - Gradient similar to image */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: -1;
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

/* Navbar */
.navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 3rem;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(255,255,255,0.2);
    position: sticky; top: 0; z-index: 999;
}
.nav-logo { font-size: 1.5rem; font-weight: 900; color: #fff; }
.nav-logo span { color: #FFD700; }
.nav-links { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.nav-btn {
    border: none; border-radius: 50px; padding: 0.5rem 1.2rem;
    font-size: 0.9rem; font-family: 'Tajawal', sans-serif;
    cursor: pointer; transition: all 0.3s;
    background: rgba(255,255,255,0.15); color: #fff;
}
.nav-btn:hover { background: rgba(255,215,0,0.3); }
.nav-btn.active { background: #FFD700; color: #1a1a2e; font-weight: 700; }

/* Hero Section */
.hero {
    text-align: center;
    padding: 3rem 2rem 1rem 2rem;
    color: #fff;
}
.hero h1 {
    font-size: clamp(1.8rem, 5vw, 2.8rem);
    font-weight: 900;
    margin-bottom: 0.5rem;
}
.hero h1 span { color: #FFD700; }
.hero p {
    font-size: 1rem;
    opacity: 0.85;
    max-width: 600px;
    margin: 0 auto 1.5rem auto;
}
.hero-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}
.btn-primary {
    background: #FFD700;
    color: #1a1a2e;
    border: none;
    border-radius: 50px;
    padding: 0.7rem 1.8rem;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s;
}
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(255,215,0,0.4);
}
.btn-outline {
    background: transparent;
    color: #fff;
    border: 2px solid #FFD700;
    border-radius: 50px;
    padding: 0.65rem 1.8rem;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s;
}
.btn-outline:hover {
    background: rgba(255,215,0,0.2);
    transform: translateY(-2px);
}

/* Section */
.section {
    padding: 2rem 3rem;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.2rem;
}
.section-subtitle {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.7);
    margin-bottom: 2rem;
}

/* Features Grid - 4 cards similar to image */
.features-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
}

/* Yellow Background Cards */
.feature-card {
    background: #FFD700;
    border-radius: 20px;
    padding: 1.8rem 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.feature-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

/* Icon circle */
.feature-icon {
    width: 65px;
    height: 65px;
    background: rgba(26, 26, 46, 0.15);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 auto 1rem auto;
    color: #1a1a2e;
}

.feature-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}
.feature-desc {
    font-size: 0.8rem;
    color: #3a3a5e;
    line-height: 1.5;
}

/* Study Plan Card */
.study-plan {
    background: rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin-top: 2rem;
    text-align: center;
}
.study-plan-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #FFD700;
    margin-bottom: 0.5rem;
}
.study-plan-text {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.8);
}

/* Footer */
.footer {
    text-align: center;
    padding: 1.5rem;
    color: rgba(255,255,255,0.5);
    font-size: 0.8rem;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin-top: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
    .features-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    .section {
        padding: 1.5rem;
    }
    .navbar {
        padding: 0.8rem 1rem;
        flex-direction: column;
        gap: 0.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

# ── Navigation Bar ─────────────────────────────────────────────────────────
PAGES = [
    ("home", "🏠 الرئيسية"),
    ("courses", "📚 الدورات"),
    ("videos", "🎬 الفيديوهات"),
    ("contact", "📞 اتصل بنا")
]

def render_navbar():
    nav_html = '<div class="navbar"><div class="nav-logo">📚 <span>منصة المَالِك</span> التعليمية</div><div class="nav-links">'
    for pid, plabel in PAGES:
        cls = "nav-btn active" if st.session_state.page == pid else "nav-btn"
        nav_html += f'<button class="{cls}" onclick="window.location.href=\'?page={pid}\'">{plabel}</button>'
    nav_html += '</div></div>'
    st.markdown(nav_html, unsafe_allow_html=True)

# Read URL param
params = st.query_params
if "page" in params:
    st.session_state.page = params["page"]

render_navbar()

# ═══════════════════════════════════════════════════════════════════════════
# HOME PAGE - Similar to the image
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    
    # Hero Section
    st.markdown("""
    <div class="hero">
        <h1>📚 <span>منصة المَالِك</span> التعليمية</h1>
        <p>نقدم دورات في اللغة الإنجليزية مصممة خصيصاً لتتناسب مع جميع المستويات<br>ونوفر لك جميع خدمات تعليمية استثنائية</p>
        <div class="hero-buttons">
            <button class="btn-primary">📖 تصفح جميع دوراتنا</button>
            <button class="btn-outline">🎯 تعلم طريقة الاستشراف</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section - 4 Yellow Cards
    st.markdown('<div class="section">', unsafe_allow_html=True)
    
    # The 4 cards as in the image
    features = [
        {
            "icon": "📅",
            "title": "جدول دراسية\nخطة وصول دراسية",
            "desc": "مخصصة تناسب وقتك\nوأهدافك التعليمية"
        },
        {
            "icon": "⚡",
            "title": "تدريب فوري",
            "desc": "تمارين واختبارات بعد كل درس\nلتطبيق ما تعلمته"
        },
        {
            "icon": "👨‍🏫",
            "title": "مدربون خبراء",
            "desc": "شرح سلس من مدربين\nمختصين في شرح التقنيات\nاللازمة"
        },
        {
            "icon": "🎯",
            "title": "دورات مختلفة",
            "desc": "دورات مختلفة لتحقيق نتائج\nسريعة في وقت قصير"
        }
    ]
    
    # Create 4 cards grid
    cols = st.columns(4)
    for idx, feature in enumerate(features):
        with cols[idx]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{feature['icon']}</div>
                <div class="feature-title">{feature['title']}</div>
                <div class="feature-desc">{feature['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Optional: Study Plan Section (like in the image)
    st.markdown("""
    <div class="section">
        <div class="study-plan">
            <div class="study-plan-title">📋 جدول دراسي مخصص</div>
            <div class="study-plan-text">خطط دراسية مرنة تناسب وقتك وتساعدك على تحقيق أهدافك التعليمية بفعالية</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        © 2025 منصة المَالِك التعليمية — جميع الحقوق محفوظة
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# COURSES PAGE
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "courses":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📚 جميع دوراتنا</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">اختر الدورة المناسبة لك وابدأ رحلة التعلم</div>', unsafe_allow_html=True)
    
    courses = [
        {"name": "IELTS Master", "level": "متقدم", "hours": 40, "icon": "🎓"},
        {"name": "STEP Preparation", "level": "متوسط", "hours": 30, "icon": "📝"},
        {"name": "English Speaking", "level": "مبتدئ", "hours": 25, "icon": "🗣️"},
        {"name": "Writing Skills", "level": "متوسط", "hours": 20, "icon": "✍️"},
    ]
    
    for course in courses:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.1); border-radius:12px; padding:1rem; margin-bottom:1rem">
                    <div style="display:flex; gap:1rem; align-items:center">
                        <div style="font-size:2rem">{course['icon']}</div>
                        <div>
                            <div style="font-weight:bold; color:#FFD700">{course['name']}</div>
                            <div style="font-size:0.8rem; opacity:0.7">المستوى: {course['level']} | {course['hours']} ساعة</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown('<div style="padding:1rem">🎁 مجاني</div>', unsafe_allow_html=True)
            with col3:
                st.button("انضم الآن", key=f"join_{course['name']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# VIDEOS PAGE
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "videos":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 الفيديوهات التعليمية</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">أكثر من 100 فيديو تعليمي لمساعدتك في رحلة التعلم</div>', unsafe_allow_html=True)
    
    videos = [
        {"title": "مقدمة في اختبار IELTS", "duration": "25:30", "icon": "🎬"},
        {"title": "أساسيات قواعد اللغة الإنجليزية", "duration": "18:45", "icon": "📹"},
        {"title": "تقنيات التحدث للمبتدئين", "duration": "22:15", "icon": "🎥"},
        {"title": "كيفية كتابة المقالات", "duration": "20:00", "icon": "📽️"},
    ]
    
    for video in videos:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.1); border-radius:12px; padding:0.8rem 1rem; margin-bottom:0.8rem">
                <div style="display:flex; gap:1rem; align-items:center">
                    <div style="font-size:1.8rem">{video['icon']}</div>
                    <div>
                        <div style="font-weight:bold">{video['title']}</div>
                        <div style="font-size:0.75rem; opacity:0.6">⏱ {video['duration']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.button("▶ مشاهدة", key=f"watch_{video['title']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# CONTACT PAGE
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "contact":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.1); border-radius:20px; padding:2rem">
            <div style="text-align:center">
                <div style="font-size:3rem">📞</div>
                <div class="section-title">تواصل معنا</div>
                <div style="margin-top:1rem">
                    <p>📍 مصر - القاهرة</p>
                    <p>📧 info@malek-platform.com</p>
                    <p>📱 +20 123 456 789</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.1); border-radius:20px; padding:2rem">
            <div style="text-align:center">
                <div style="font-size:3rem">💬</div>
                <div class="section-title">راسلنا</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("contact_form"):
            name = st.text_input("الاسم")
            email = st.text_input("البريد الإلكتروني")
            message = st.text_area("الرسالة")
            submitted = st.form_submit_button("إرسال", use_container_width=True)
            if submitted:
                st.success("تم إرسال رسالتك بنجاح! سنتواصل معك قريباً")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Handle sidebar for mobile fallback
with st.sidebar:
    st.markdown("## 📚 منصة المَالِك")
    for pid, plabel in PAGES:
        if st.button(plabel, key=f"side_{pid}", use_container_width=True):
            st.session_state.page = pid
            st.query_params["page"] = pid
            st.rerun()
