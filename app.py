import streamlit as st
import time
from datetime import datetime
import random

# ── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="منصة الريحاني التعليمية",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Initialize Session State ───────────────────────────────────────────────
def init_session_state():
    defaults = {
        "page": "home",
        "logged_in": False,
        "username": "",
        "user_email": "",
        "q_idx": 0,
        "score": 0,
        "answered": False,
        "chosen": None,
        "quiz_done": False,
        "q_type": "IELTS",
        "enrolled_courses": [],
        "watched_videos": [],
        "quiz_scores": {"IELTS": 0, "STEP": 0},
        "dark_mode": False,
        "notifications": [],
        "points": 0,
        "badges": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ── Global CSS with Dark Mode Support ──────────────────────────────────────
def load_css():
    dark_mode = st.session_state.get("dark_mode", False)
    
    bg_gradient = "linear-gradient(160deg, #0a1172 0%, #1a2aad 40%, #2d3fc7 65%, #6C63FF 100%)" if not dark_mode else "linear-gradient(160deg, #0a0a1a 0%, #1a1a2e 40%, #16213e 65%, #0f3460 100%)"
    card_bg = "rgba(255,255,255,0.95)" if not dark_mode else "rgba(30,30,45,0.95)"
    text_color = "#2d2d2d" if not dark_mode else "#ffffff"
    text_secondary = "#666666" if not dark_mode else "#aaaaaa"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&family=Poppins:wght@400;600;700&display=swap');
    
    * {{
        direction: rtl;
        font-family: 'Tajawal', sans-serif !important;
    }}
    
    /* Hide default Streamlit elements */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; max-width: 100% !important; }}
    [data-testid="stAppViewContainer"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    
    /* Background */
    [data-testid="stAppViewContainer"]::before {{
        content: '';
        position: fixed; inset: 0; z-index: -1;
        background: {bg_gradient};
        transition: all 0.3s ease;
    }}
    
    /* Cards and containers */
    .wave-divider {{
        width: 100%; overflow: hidden; line-height: 0;
        margin-bottom: -2px;
    }}
    .wave-divider svg {{ display: block; width: 100%; }}
    
    .navbar {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 3rem;
        background: rgba(255,255,255,0.12);
        backdrop-filter: blur(14px);
        border-bottom: 1px solid rgba(255,255,255,0.2);
        position: sticky; top: 0; z-index: 999;
    }}
    
    .nav-logo {{ font-size: 1.6rem; font-weight: 900; color: #fff; }}
    .nav-logo span {{ color: #F5A623; }}
    .nav-links {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
    
    .section {{ padding: 2rem 3rem; }}
    
    .hero {{
        min-height: 60vh; display: flex; flex-direction: column;
        justify-content: center; padding: 3rem 3rem;
        color: #fff;
    }}
    .hero h1 {{ font-size: clamp(2rem,5vw,3.5rem); font-weight: 900; line-height: 1.2; margin-bottom: 1rem; }}
    .hero p {{ font-size: 1.1rem; opacity: .85; max-width: 520px; margin-bottom: 2rem; }}
    
    .hero-btn, .primary-btn {{
        display: inline-block; background: #F5A623;
        color: #fff; font-size: 1rem; font-weight: 700;
        padding: 0.8rem 2rem; border-radius: 50px; border: none;
        cursor: pointer; transition: all 0.3s ease;
        text-decoration: none;
    }}
    .hero-btn:hover, .primary-btn:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(245,166,35,0.4);
    }}
    
    .stats-row {{ display: flex; gap: 1.5rem; flex-wrap: wrap; margin: 2rem 0; }}
    .stat-card {{
        flex: 1; min-width: 180px;
        background: {card_bg}; border-radius: 18px;
        padding: 1.5rem; text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }}
    .stat-card:hover {{ transform: translateY(-5px); }}
    .stat-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    .stat-num {{ font-size: 1.8rem; font-weight: 900; color: #6C63FF; }}
    .stat-lbl {{ font-size: 0.9rem; color: {text_secondary}; }}
    
    .sec-title {{ font-size: 1.8rem; font-weight: 900; color: #fff; margin-bottom: 0.5rem; }}
    .sec-sub {{ color: rgba(255,255,255,0.8); font-size: 1rem; margin-bottom: 2rem; }}
    
    .cards-grid {{ display: flex; gap: 1.5rem; flex-wrap: wrap; }}
    .course-card {{
        flex: 1; min-width: 250px; max-width: 320px;
        background: {card_bg}; border-radius: 18px;
        overflow: hidden; transition: all 0.3s ease;
        cursor: pointer;
    }}
    .course-card:hover {{ transform: translateY(-8px); box-shadow: 0 15px 40px rgba(0,0,0,0.2); }}
    
    .card-thumb {{
        height: 140px; display: flex; align-items: center; justify-content: center;
        font-size: 3rem; position: relative;
    }}
    .card-body {{ padding: 1rem 1.2rem; }}
    .card-badge {{
        display: inline-block; font-size: 0.7rem; font-weight: 700;
        padding: 0.2rem 0.7rem; border-radius: 50px; margin-bottom: 0.5rem;
        background: rgba(108,99,255,0.15); color: #6C63FF;
    }}
    .card-title {{ font-size: 1rem; font-weight: 700; color: {text_color}; margin-bottom: 0.3rem; }}
    .card-desc {{ font-size: 0.85rem; color: {text_secondary}; line-height: 1.5; }}
    .card-footer {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.8rem 1.2rem; border-top: 1px solid rgba(0,0,0,0.05);
    }}
    .card-price {{ font-weight: 700; color: #F5A623; }}
    
    .quiz-card {{
        background: {card_bg}; border-radius: 20px;
        padding: 2rem; max-width: 700px; margin: 0 auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    .quiz-q {{ font-size: 1.1rem; font-weight: 700; color: {text_color}; margin-bottom: 1.5rem; }}
    
    .progress-bar-bg {{
        height: 8px; background: rgba(0,0,0,0.1); border-radius: 50px;
        margin-bottom: 1.5rem; overflow: hidden;
    }}
    .progress-bar-fill {{
        height: 100%; background: #F5A623; border-radius: 50px;
        transition: width 0.3s ease;
    }}
    
    .dl-card {{
        display: flex; align-items: center; gap: 1rem;
        background: {card_bg}; border-radius: 16px;
        padding: 1rem 1.5rem; margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }}
    .dl-card:hover {{ transform: translateX(-5px); }}
    .dl-icon {{ font-size: 2rem; }}
    .dl-info {{ flex: 1; }}
    .dl-name {{ font-weight: 700; color: {text_color}; }}
    .dl-size {{ font-size: 0.8rem; color: {text_secondary}; }}
    
    .footer {{
        text-align: center; padding: 1.5rem;
        color: rgba(255,255,255,0.6); font-size: 0.85rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin-top: 3rem;
    }}
    
    .notification {{
        position: fixed; top: 80px; right: 20px;
        background: {card_bg}; padding: 1rem 1.5rem;
        border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        z-index: 1000; animation: slideIn 0.3s ease;
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    .badge {{
        display: inline-flex; align-items: center; gap: 0.5rem;
        background: linear-gradient(135deg, #f5af19, #f12711);
        padding: 0.3rem 0.8rem; border-radius: 50px;
        color: white; font-size: 0.8rem; margin: 0.2rem;
    }}
    </style>
    """, unsafe_allow_html=True)

load_css()

# ── Data ──────────────────────────────────────────────────────────────────
COURSES = [
    {"icon":"🎓","color":"linear-gradient(135deg,#667eea,#764ba2)","badge":"IELTS","title":"IELTS من الصفر للاحتراف","desc":"استعد لامتحان IELTS مع أفضل المدربين","price":"مجاني","lessons":24},
    {"icon":"📝","color":"linear-gradient(135deg,#f093fb,#f5576c)","badge":"STEP","title":"اختبار STEP المتكامل","desc":"دورة شاملة لاختبار STEP","price":"مجاني","lessons":18},
    {"icon":"🗣️","color":"linear-gradient(135deg,#4facfe,#00f2fe)","badge":"Speaking","title":"مهارات المحادثة","desc":"طوّر مهارة التحدث بالإنجليزية","price":"مجاني","lessons":12},
    {"icon":"✍️","color":"linear-gradient(135deg,#43e97b,#38f9d7)","badge":"Writing","title":"الكتابة الأكاديمية","desc":"تعلم كتابة المقالات والتقارير","price":"مجاني","lessons":15},
]

VIDEOS = [
    {"thumb":"🎬","title":"مقدمة اختبار IELTS - الجزء الأول","dur":"18:32","views":"12,450","cat":"IELTS","url":"https://youtu.be/example1"},
    {"thumb":"🎥","title":"أسرار قسم Writing Task 2","dur":"24:15","views":"9,820","cat":"Writing","url":"https://youtu.be/example2"},
    {"thumb":"📹","title":"تقنيات Speaking Band 7+","dur":"21:40","views":"15,300","cat":"Speaking","url":"https://youtu.be/example3"},
    {"thumb":"🎞️","title":"STEP اختبار - نصائح ذهبية","dur":"16:55","views":"7,650","cat":"STEP","url":"https://youtu.be/example4"},
]

QUIZ_IELTS = [
    {"q":"ما هو الحد الأقصى لدرجة IELTS؟","opts":["9","10","8","7"],"ans":0,"explanation":"درجة IELTS تتراوح من 0 إلى 9"},
    {"q":"أي قسم من IELTS يختبر مهارة الكتابة؟","opts":["Listening","Reading","Writing","Speaking"],"ans":2,"explanation":"قسم الكتابة هو Writing Task 1 & 2"},
    {"q":"كم مدة قسم الاستماع في IELTS؟","opts":["40 دقيقة","30 دقيقة","60 دقيقة","20 دقيقة"],"ans":1,"explanation":"مدة الاستماع 30 دقيقة مع 10 د额外"},
]

QUIZ_STEP = [
    {"q":"ما هي الدرجة النهائية لاختبار STEP؟","opts":["100","200","900","50"],"ans":1,"explanation":"درجة STEP من 200"},
    {"q":"أي جملة صحيحة نحوياً؟","opts":["I am agree","I agrees","I agree","I agreeing"],"ans":2,"explanation":"I agree هي الصحيحة"},
]

DOWNLOADS = [
    {"icon":"📄","name":"كتاب IELTS - Cambridge 18","size":"15.2 MB","type":"PDF","url":"#"},
    {"icon":"📋","name":"قاموس مفردات IELTS","size":"3.8 MB","type":"PDF","url":"#"},
    {"icon":"🗂️","name":"نماذج STEP مع الحلول","size":"8.5 MB","type":"PDF","url":"#"},
]

# ── Helper Functions ──────────────────────────────────────────────────────
def add_notification(message, type="success"):
    st.session_state.notifications.append({"message": message, "type": type, "time": datetime.now()})
    if len(st.session_state.notifications) > 5:
        st.session_state.notifications.pop(0)

def add_points(points, reason=""):
    st.session_state.points += points
    add_notification(f"🎉 +{points} نقطة {reason}!")

def check_badges():
    if st.session_state.points >= 100 and "نقاطي" not in st.session_state.badges:
        st.session_state.badges.append("نقاطي")
        add_notification("🏅 حصلت على وسام 'نقاطي'!")
    if len(st.session_state.enrolled_courses) >= 3 and "متعلم" not in st.session_state.badges:
        st.session_state.badges.append("متعلم")
        add_notification("🏅 حصلت على وسام 'متعلم'!")

def render_navbar():
    PAGES = [
        ("home", "🏠 الرئيسية"),
        ("courses", "📚 الكورسات"),
        ("videos", "🎬 الفيديوهات"),
        ("quiz", "📝 الاختبارات"),
        ("downloads", "📥 التحميلات"),
        ("profile", "👤 ملفي")
    ]
    
    # Dark mode toggle in navbar
    col1, col2, col3 = st.columns([2, 6, 1])
    with col1:
        st.markdown("<div class='nav-logo'>📚 <span>الريحاني</span></div>", unsafe_allow_html=True)
    
    with col2:
        nav_cols = st.columns(len(PAGES))
        for idx, (pid, plabel) in enumerate(PAGES):
            with nav_cols[idx]:
                is_active = st.session_state.page == pid
                if st.button(plabel, key=f"nav_{pid}", 
                           type="primary" if is_active else "secondary",
                           use_container_width=True):
                    st.session_state.page = pid
                    st.query_params["page"] = pid
                    st.rerun()
    
    with col3:
        dark_icon = "🌙" if not st.session_state.dark_mode else "☀️"
        if st.button(dark_icon, key="dark_mode_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

def enroll_course(course_title):
    if st.session_state.logged_in:
        if course_title not in st.session_state.enrolled_courses:
            st.session_state.enrolled_courses.append(course_title)
            add_points(50, f"للتسجيل في كورس {course_title}")
            check_badges()
            add_notification(f"✅ تم تسجيلك في كورس {course_title} بنجاح!")
            return True
        else:
            add_notification(f"ℹ️ أنت مسجل بالفعل في كورس {course_title}", "info")
            return False
    else:
        add_notification("⚠️ يرجى تسجيل الدخول أولاً للتسجيل في الكورسات", "warning")
        return False

# ── Pages ─────────────────────────────────────────────────────────────────
def home_page():
    st.markdown("""
    <div class="hero">
        <h1>منصة الريحاني<br>التعليمية 🎓</h1>
        <p>طوّر مهاراتك في اللغة الإنجليزية واستعد لامتحانات IELTS و STEP مع أفضل المدربين</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    st.markdown('<div class="stats-row">', unsafe_allow_html=True)
    stats = [
        ("👨‍🎓", "+5,000", "طالب مسجل"),
        ("📚", "60+", "دورة تعليمية"),
        ("🎬", "200+", "فيديو تعليمي"),
        ("⭐", "4.9", "تقييم الطلاب")
    ]
    for icon, num, label in stats:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">{icon}</div>
            <div class="stat-num">{num}</div>
            <div class="stat-lbl">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Featured Courses
    st.markdown('<p class="sec-title">📘 أشهر كورساتنا</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, course in enumerate(COURSES[:4]):
        with cols[idx]:
            with st.container():
                st.markdown(f"""
                <div class="course-card">
                    <div class="card-thumb" style="background:{course['color']}">{course['icon']}</div>
                    <div class="card-body">
                        <span class="card-badge">{course['badge']}</span>
                        <div class="card-title">{course['title']}</div>
                        <div class="card-desc">{course['desc']}</div>
                    </div>
                    <div class="card-footer">
                        <span class="card-price">🎁 {course['price']} | {course['lessons']} درس</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"انضم الآن", key=f"enroll_home_{idx}", use_container_width=True):
                    if enroll_course(course['title']):
                        st.rerun()

def courses_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">📚 جميع الكورسات التعليمية</p>', unsafe_allow_html=True)
    
    # Filter by category
    categories = ["الكل", "IELTS", "STEP", "Speaking", "Writing"]
    selected_cat = st.selectbox("🔍 تصفية حسب:", categories, key="course_filter")
    
    filtered = COURSES if selected_cat == "الكل" else [c for c in COURSES if c['badge'] == selected_cat]
    
    for course in filtered:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.1); border-radius:12px; padding:1rem; margin-bottom:1rem">
                <div style="font-size:1.2rem; font-weight:bold">{course['icon']} {course['title']}</div>
                <div style="font-size:0.85rem; opacity:0.8">{course['desc']}</div>
                <div style="margin-top:0.5rem">
                    <span class="card-badge">{course['badge']}</span>
                    <span style="margin-right:1rem">📊 {course['lessons']} درس</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='padding:1rem'><span class='card-price'>🎁 {course['price']}</span></div>", unsafe_allow_html=True)
        with col3:
            enrolled = course['title'] in st.session_state.enrolled_courses
            btn_text = "✅ مسجل" if enrolled else "📝 انضم الآن"
            if st.button(btn_text, key=f"enroll_{course['title']}", use_container_width=True, disabled=enrolled):
                if enroll_course(course['title']):
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def videos_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">🎬 مكتبة الفيديوهات</p>', unsafe_allow_html=True)
    
    # Search
    search = st.text_input("🔍 ابحث عن فيديو...", placeholder="اكتب عنوان الفيديو", key="video_search")
    
    filtered = [v for v in VIDEOS if search.lower() in v['title'].lower()] if search else VIDEOS
    
    for video in filtered:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.1); border-radius:12px; padding:1rem; margin-bottom:1rem">
                    <div style="display:flex; gap:1rem; align-items:center">
                        <div style="font-size:2.5rem">{video['thumb']}</div>
                        <div>
                            <div style="font-weight:bold">{video['title']}</div>
                            <div style="font-size:0.8rem; opacity:0.7">
                                ⏱ {video['dur']} | 👁 {video['views']} مشاهدة | {video['cat']}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("▶ شاهد الآن", key=f"watch_{video['title']}", use_container_width=True):
                    add_points(10, f"لمشاهدة فيديو {video['title'][:20]}")
                    if video['title'] not in st.session_state.watched_videos:
                        st.session_state.watched_videos.append(video['title'])
                    add_notification(f"🎬 جارٍ تشغيل: {video['title']}")
                    st.video(video['url'] if 'url' in video else "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    st.markdown('</div>', unsafe_allow_html=True)

def quiz_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">📝 اختبر معلوماتك</p>', unsafe_allow_html=True)
    
    # Quiz type selector
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎓 اختبار IELTS", use_container_width=True, type="primary" if st.session_state.q_type == "IELTS" else "secondary"):
            st.session_state.q_type = "IELTS"
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.quiz_done = False
            st.rerun()
    with col2:
        if st.button("📋 اختبار STEP", use_container_width=True, type="primary" if st.session_state.q_type == "STEP" else "secondary"):
            st.session_state.q_type = "STEP"
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.quiz_done = False
            st.rerun()
    
    st.markdown("---")
    
    questions = QUIZ_IELTS if st.session_state.q_type == "IELTS" else QUIZ_STEP
    total = len(questions)
    
    if st.session_state.quiz_done:
        percentage = int((st.session_state.score / total) * 100)
        emoji = "🏆" if percentage >= 80 else ("👍" if percentage >= 50 else "📚")
        
        st.markdown(f"""
        <div class="quiz-card" style="text-align:center">
            <div style="font-size:3rem">{emoji}</div>
            <div style="font-size:1.5rem; font-weight:bold; margin:1rem 0">
                نتيجتك: {st.session_state.score}/{total}
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width:{percentage}%"></div>
            </div>
            <div style="font-size:1rem; color:#666">{'ممتاز! 🎉' if percentage >= 80 else ('جيد، استمر 💪' if percentage >= 50 else 'راجع المادة وحاول مرة أخرى 📖')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 إعادة الاختبار", use_container_width=False):
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.quiz_done = False
            st.rerun()
        
        # Save score
        if st.session_state.score > st.session_state.quiz_scores.get(st.session_state.q_type, 0):
            st.session_state.quiz_scores[st.session_state.q_type] = st.session_state.score
            points_earned = st.session_state.score * 10
            add_points(points_earned, f"في اختبار {st.session_state.q_type}")
            check_badges()
    else:
        idx = st.session_state.q_idx
        q = questions[idx]
        progress = (idx / total) * 100
        
        st.markdown(f"""
        <div class="quiz-card">
            <div style="display:flex; justify-content:space-between; margin-bottom:1rem">
                <span>📋 سؤال {idx+1} من {total}</span>
                <span>🎯 {st.session_state.q_type}</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width:{progress}%"></div>
            </div>
            <div class="quiz-q">{q['q']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        for i, opt in enumerate(q["opts"]):
            btn_text = opt
            if st.session_state.answered:
                if i == q["ans"]:
                    btn_text = f"✅ {opt}"
                elif i == st.session_state.chosen:
                    btn_text = f"❌ {opt}"
            
            if st.button(btn_text, key=f"quiz_opt_{idx}_{i}", use_container_width=True, disabled=st.session_state.answered):
                st.session_state.chosen = i
                st.session_state.answered = True
                if i == q["ans"]:
                    st.session_state.score += 1
                    st.success("✅ إجابة صحيحة!")
                else:
                    st.error(f"❌ إجابة خاطئة! الصحيح: {q['opts'][q['ans']]}")
                if 'explanation' in q:
                    st.info(f"💡 {q['explanation']}")
                st.rerun()
        
        if st.session_state.answered:
            if idx + 1 < total:
                if st.button("➡️ السؤال التالي", type="primary", use_container_width=True):
                    st.session_state.q_idx += 1
                    st.session_state.answered = False
                    st.session_state.chosen = None
                    st.rerun()
            else:
                if st.button("🏁 إنهاء الاختبار وعرض النتيجة", type="primary", use_container_width=True):
                    st.session_state.quiz_done = True
                    st.rerun()

def downloads_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">📥 ملفات التحميل</p>', unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        file_type = st.selectbox("📄 نوع الملف", ["الكل", "PDF", "ZIP"])
    with col2:
        search = st.text_input("🔍 بحث", placeholder="اسم الملف...")
    
    filtered = DOWNLOADS
    if search:
        filtered = [d for d in filtered if search.lower() in d['name'].lower()]
    if file_type != "الكل":
        filtered = [d for d in filtered if d['type'] == file_type]
    
    for file in filtered:
        col1, col2, col3 = st.columns([5, 2, 1])
        with col1:
            st.markdown(f"""
            <div class="dl-card">
                <div class="dl-icon">{file['icon']}</div>
                <div class="dl-info">
                    <div class="dl-name">{file['name']}</div>
                    <div class="dl-size">📦 {file['size']} | {file['type']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.session_state.logged_in:
                st.download_button(
                    label="⬇️ تحميل",
                    data=f"محاكاة لملف {file['name']}",
                    file_name=file['name'].replace(" ", "_") + ".pdf",
                    mime="application/pdf",
                    key=f"dl_{file['name']}"
                )
            else:
                st.info("🔐 سجل دخولك للتحميل")
        with col3:
            if st.button("⭐", key=f"fav_{file['name']}"):
                add_points(5, "لإضافة ملف للمفضلة")
                add_notification(f"📌 تمت إضافة {file['name']} إلى المفضلة")

def profile_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # Login Form
        st.markdown("""
        <div style="max-width:400px; margin:2rem auto">
            <div class="quiz-card">
                <div style="text-align:center">
                    <div style="font-size:3rem">🔐</div>
                    <h2>تسجيل الدخول</h2>
                </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
            email = st.text_input("📧 البريد الإلكتروني", placeholder="example@email.com")
            password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
            
            col1, col2 = st.columns(2)
            with col1:
                login_btn = st.form_submit_button("✅ دخول", use_container_width=True, type="primary")
            with col2:
                register_btn = st.form_submit_button("📝 إنشاء حساب", use_container_width=True)
            
            if login_btn:
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_email = email
                    add_points(100, "للتسجيل في المنصة")
                    add_notification(f"✨ مرحباً {username}! أهلاً بك في منصة الريحاني")
                    check_badges()
                    st.rerun()
                else:
                    st.error("❌ الرجاء إدخال جميع البيانات")
            
            if register_btn:
                st.info("📧 سيتم إرسال رابط التأكيد إلى بريدك الإلكتروني")
    else:
        # Profile Info
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="quiz-card" style="text-align:center">
                <div style="font-size:4rem">👤</div>
                <h3>{st.session_state.username}</h3>
                <p>{st.session_state.user_email}</p>
                <hr>
                <div class="stat-num">{st.session_state.points}</div>
                <div>🏆 النقاط</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📊 إحصائياتي")
            
            # Stats
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("📚 كورسات مسجل بها", len(st.session_state.enrolled_courses))
            with col_b:
                st.metric("🎬 فيديوهات شاهدتها", len(st.session_state.watched_videos))
            with col_c:
                best_score = max(st.session_state.quiz_scores.values()) if st.session_state.quiz_scores else 0
                st.metric("🏆 أفضل درجة", f"{best_score}")
            
            # Badges
            if st.session_state.badges:
                st.markdown("### 🏅 الأوسمة")
                badges_html = ""
                for badge in st.session_state.badges:
                    badges_html += f'<span class="badge">🏅 {badge}</span>'
                st.markdown(badges_html, unsafe_allow_html=True)
            
            # Enrolled Courses
            if st.session_state.enrolled_courses:
                st.markdown("### ✅ الكورسات المسجل بها")
                for course in st.session_state.enrolled_courses:
                    st.markdown(f"- 📖 {course}")
            
            # Logout button
            if st.button("🚪 تسجيل الخروج", use_container_width=True, type="secondary"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.user_email = ""
                st.session_state.enrolled_courses = []
                st.rerun()

# ── Main App ──────────────────────────────────────────────────────────────
def main():
    # Handle query params
    params = st.query_params
    if "page" in params:
        st.session_state.page = params["page"]
    
    # Render navbar
    render_navbar()
    
    # Show notifications
    if st.session_state.notifications:
        latest = st.session_state.notifications[-1]
        st.toast(latest['message'], icon="✅" if latest['type'] == "success" else "ℹ️")
    
    # Page routing
    pages = {
        "home": home_page,
        "courses": courses_page,
        "videos": videos_page,
        "quiz": quiz_page,
        "downloads": downloads_page,
        "profile": profile_page
    }
    
    current_page = pages.get(st.session_state.page, home_page)
    current_page()
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        © 2025 منصة الريحاني التعليمية — جميع الحقوق محفوظة
        <br>
        <small>🌟 لديك {st.session_state.points} نقطة | {len(st.session_state.badges)} وسام</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
