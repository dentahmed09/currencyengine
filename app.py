import streamlit as st
from datetime import datetime
import random
import time

# ── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="منصة المَالِك التعليمية",
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
        "quiz_scores": {"IELTS": 0, "STEP": 0, "GENERAL": 0},
        "dark_mode": False,
        "notifications": [],
        "points": 0,
        "badges": [],
        "completed_lessons": [],
        "favorite_downloads": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ── Global CSS with Dark Mode Support & Yellow Cards ──────────────────────
def load_css():
    dark_mode = st.session_state.get("dark_mode", False)
    
    # Colors based on mode
    if dark_mode:
        bg_gradient = "linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%)"
        card_bg = "rgba(30,30,45,0.95)"
        text_color = "#ffffff"
        text_secondary = "#aaaaaa"
        card_yellow = "#2a2a1a"
        yellow_text = "#FFD700"
    else:
        bg_gradient = "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)"
        card_bg = "rgba(255,255,255,0.95)"
        text_color = "#1a1a2e"
        text_secondary = "#666666"
        card_yellow = "#FFD700"
        yellow_text = "#1a1a2e"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap');
    
    * {{
        direction: rtl;
        font-family: 'Tajawal', sans-serif !important;
    }}
    
    /* Hide default Streamlit elements */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; max-width: 100% !important; padding-bottom: 0 !important; }}
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
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #FFD700;
        border-radius: 10px;
    }}
    
    /* Navbar */
    .navbar {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 3rem;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(14px);
        border-bottom: 1px solid rgba(255,255,255,0.2);
        position: sticky; top: 0; z-index: 999;
    }}
    .nav-logo {{ font-size: 1.5rem; font-weight: 900; color: #fff; }}
    .nav-logo span {{ color: #FFD700; }}
    .nav-links {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
    .nav-btn {{
        border: none; border-radius: 50px; padding: 0.5rem 1.2rem;
        font-size: 0.9rem; font-family: 'Tajawal', sans-serif;
        cursor: pointer; transition: all 0.3s;
        background: rgba(255,255,255,0.15); color: #fff;
    }}
    .nav-btn:hover {{ background: rgba(255,215,0,0.3); transform: translateY(-2px); }}
    .nav-btn.active {{ background: #FFD700; color: #1a1a2e; font-weight: 700; }}
    
    /* Hero Section */
    .hero {{
        text-align: center;
        padding: 3rem 2rem 2rem 2rem;
        color: #fff;
    }}
    .hero h1 {{
        font-size: clamp(1.8rem, 5vw, 2.8rem);
        font-weight: 900;
        margin-bottom: 0.5rem;
    }}
    .hero h1 span {{ color: #FFD700; }}
    .hero p {{
        font-size: 1rem;
        opacity: 0.85;
        max-width: 650px;
        margin: 0 auto 1.5rem auto;
        line-height: 1.8;
    }}
    .hero-buttons {{
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }}
    .btn-primary {{
        background: #FFD700;
        color: #1a1a2e;
        border: none;
        border-radius: 50px;
        padding: 0.7rem 1.8rem;
        font-size: 0.9rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s;
    }}
    .btn-primary:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255,215,0,0.4);
    }}
    .btn-outline {{
        background: transparent;
        color: #fff;
        border: 2px solid #FFD700;
        border-radius: 50px;
        padding: 0.65rem 1.8rem;
        font-size: 0.9rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s;
    }}
    .btn-outline:hover {{
        background: rgba(255,215,0,0.2);
        transform: translateY(-2px);
    }}
    
    /* Section */
    .section {{
        padding: 2rem 3rem;
    }}
    .section-title {{
        font-size: 1.6rem;
        font-weight: 800;
        color: #fff;
        margin-bottom: 0.5rem;
        text-align: center;
    }}
    .section-subtitle {{
        font-size: 0.9rem;
        color: rgba(255,255,255,0.7);
        margin-bottom: 2rem;
        text-align: center;
    }}
    
    /* Features Grid - Yellow Cards */
    .features-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        max-width: 1200px;
        margin: 0 auto;
    }}
    
    .feature-card {{
        background: {card_yellow};
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
    }}
    .feature-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }}
    
    .feature-icon {{
        width: 65px;
        height: 65px;
        background: rgba(26, 26, 46, 0.15);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto 1rem auto;
        color: {yellow_text};
    }}
    
    .feature-title {{
        font-size: 1.1rem;
        font-weight: 800;
        color: {yellow_text};
        margin-bottom: 0.5rem;
        white-space: pre-line;
    }}
    .feature-desc {{
        font-size: 0.8rem;
        color: {yellow_text if dark_mode else '#3a3a5e'};
        line-height: 1.5;
        white-space: pre-line;
    }}
    
    /* Stats Row */
    .stats-row {{
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
        justify-content: center;
        margin: 2rem 0;
    }}
    .stat-card {{
        flex: 1;
        min-width: 180px;
        max-width: 220px;
        background: {card_bg};
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }}
    .stat-card:hover {{
        transform: translateY(-5px);
    }}
    .stat-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    .stat-num {{ font-size: 1.8rem; font-weight: 900; color: #FFD700; }}
    .stat-lbl {{ font-size: 0.85rem; color: {text_secondary}; }}
    
    /* Course Cards */
    .courses-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 1rem;
    }}
    .course-card {{
        background: {card_bg};
        border-radius: 18px;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }}
    .course-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }}
    .course-header {{
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1rem;
        text-align: center;
        font-size: 2rem;
    }}
    .course-body {{ padding: 1.2rem; }}
    .course-title {{ font-size: 1.1rem; font-weight: 800; color: {text_color}; margin-bottom: 0.3rem; }}
    .course-desc {{ font-size: 0.85rem; color: {text_secondary}; line-height: 1.5; }}
    .course-meta {{
        display: flex;
        gap: 1rem;
        margin-top: 0.8rem;
        font-size: 0.75rem;
        color: {text_secondary};
    }}
    .course-footer {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.2rem;
        border-top: 1px solid rgba(0,0,0,0.05);
        background: rgba(0,0,0,0.02);
    }}
    .course-price {{ font-weight: 700; color: #FFD700; }}
    
    /* Quiz Card */
    .quiz-card {{
        background: {card_bg};
        border-radius: 20px;
        padding: 2rem;
        max-width: 700px;
        margin: 0 auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    .quiz-q {{ font-size: 1.1rem; font-weight: 700; color: {text_color}; margin-bottom: 1.5rem; line-height: 1.6; }}
    
    .progress-bar-bg {{
        height: 8px;
        background: rgba(255,255,255,0.2);
        border-radius: 50px;
        margin-bottom: 1.5rem;
        overflow: hidden;
    }}
    .progress-bar-fill {{
        height: 100%;
        background: #FFD700;
        border-radius: 50px;
        transition: width 0.3s ease;
    }}
    
    /* Study Plan */
    .study-plan {{
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 2rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }}
    .study-plan-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFD700;
        margin-bottom: 0.5rem;
    }}
    .study-plan-text {{
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
    }}
    
    /* Download Cards */
    .dl-card {{
        display: flex;
        align-items: center;
        gap: 1rem;
        background: {card_bg};
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }}
    .dl-card:hover {{ transform: translateX(-5px); }}
    .dl-icon {{ font-size: 2rem; }}
    .dl-info {{ flex: 1; }}
    .dl-name {{ font-weight: 700; color: {text_color}; }}
    .dl-size {{ font-size: 0.75rem; color: {text_secondary}; }}
    
    /* Profile */
    .profile-card {{
        background: {card_bg};
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
    }}
    .avatar {{
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin: 0 auto 1rem auto;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 1.5rem;
        color: rgba(255,255,255,0.5);
        font-size: 0.8rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin-top: 3rem;
    }}
    
    /* Notifications */
    .notification {{
        position: fixed;
        top: 80px;
        right: 20px;
        background: {card_bg};
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        border-right: 4px solid #FFD700;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    /* Badges */
    .badge-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin-top: 1rem;
    }}
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 0.3rem 0.8rem;
        border-radius: 50px;
        color: #1a1a2e;
        font-size: 0.75rem;
        font-weight: 700;
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .features-grid {{
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }}
        .section {{
            padding: 1.5rem;
        }}
        .navbar {{
            padding: 0.8rem 1rem;
            flex-direction: column;
            gap: 0.5rem;
        }}
        .stats-row {{
            gap: 1rem;
        }}
    }}
    
    @media (max-width: 480px) {{
        .features-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

load_css()

# ── Data ──────────────────────────────────────────────────────────────────
COURSES = [
    {"icon": "🎓", "title": "IELTS Master", "desc": "دورة متكاملة لتحضير اختبار IELTS", "badge": "IELTS", "lessons": 24, "level": "متقدم", "price": "مجاني"},
    {"icon": "📝", "title": "STEP Preparation", "desc": "تحضير مكثف لاختبار STEP", "badge": "STEP", "lessons": 18, "level": "متوسط", "price": "مجاني"},
    {"icon": "🗣️", "title": "English Speaking", "desc": "طور مهارات المحادثة بطلاقة", "badge": "Speaking", "lessons": 20, "level": "جميع المستويات", "price": "مجاني"},
    {"icon": "✍️", "title": "Academic Writing", "desc": "تعلم كتابة المقالات الأكاديمية", "badge": "Writing", "lessons": 15, "level": "متقدم", "price": "مجاني"},
    {"icon": "👂", "title": "Listening Skills", "desc": "تقنيات متقدمة للاستماع", "badge": "Listening", "lessons": 12, "level": "متوسط", "price": "مجاني"},
    {"icon": "📖", "title": "Reading Comprehension", "desc": "استراتيجيات القراءة السريعة", "badge": "Reading", "lessons": 14, "level": "متوسط", "price": "مجاني"},
    {"icon": "🎯", "title": "Grammar Master", "desc": "قواعد اللغة الإنجليزية من الصفر", "badge": "Grammar", "lessons": 30, "level": "مبتدئ", "price": "مجاني"},
    {"icon": "💼", "title": "Business English", "desc": "الإنجليزية للأعمال والمقابلات", "badge": "Business", "lessons": 16, "level": "متقدم", "price": "مجاني"},
]

VIDEOS = [
    {"thumb": "🎬", "title": "مقدمة اختبار IELTS", "dur": "25:30", "views": "15,234", "cat": "IELTS", "level": "مبتدئ"},
    {"thumb": "🎥", "title": "أسرار قسم الكتابة Writing", "dur": "32:15", "views": "12,456", "cat": "Writing", "level": "متقدم"},
    {"thumb": "📹", "title": "تقنيات التحدث Band 7+", "dur": "28:40", "views": "18,789", "cat": "Speaking", "level": "متقدم"},
    {"thumb": "🎞️", "title": "نصائح اختبار STEP", "dur": "22:30", "views": "8,901", "cat": "STEP", "level": "متوسط"},
    {"thumb": "📽️", "title": "استراتيجيات القراءة الفعالة", "dur": "35:20", "views": "10,567", "cat": "Reading", "level": "متوسط"},
    {"thumb": "🎦", "title": "حيل الاستماع للمبتدئين", "dur": "18:45", "views": "14,321", "cat": "Listening", "level": "مبتدئ"},
]

QUIZ_IELTS = [
    {"q": "ما هو الحد الأقصى لدرجة اختبار IELTS؟", "opts": ["7", "8", "9", "10"], "ans": 2, "explanation": "درجة IELTS تتراوح من 0 إلى 9"},
    {"q": "كم عدد أقسام اختبار IELTS؟", "opts": ["3", "4", "5", "6"], "ans": 1, "explanation": "IELTS له 4 أقسام: Listening, Reading, Writing, Speaking"},
    {"q": "ما مدة اختبار الاستماع في IELTS؟", "opts": ["20 دقيقة", "30 دقيقة", "40 دقيقة", "50 دقيقة"], "ans": 1, "explanation": "مدة الاستماع 30 دقيقة مع 10 دقائق إضافية لنقل الإجابات"},
    {"q": "أي من هذه ليس قسم في IELTS؟", "opts": ["Listening", "Reading", "Grammar", "Writing"], "ans": 2, "explanation": "IELTS لا يحتوي على قسم منفصل للقواعد"},
]

QUIZ_STEP = [
    {"q": "ما هي الدرجة النهائية لاختبار STEP؟", "opts": ["100", "200", "300", "400"], "ans": 1, "explanation": "اختبار STEP من 200 درجة"},
    {"q": "كم عدد أقسام اختبار STEP؟", "opts": ["2", "3", "4", "5"], "ans": 2, "explanation": "STEP يتكون من 3 أقسام رئيسية"},
    {"q": "الحد الأدنى لاجتياز STEP في معظم الجامعات؟", "opts": ["50%", "60%", "70%", "80%"], "ans": 2, "explanation": "معظم الجامعات تتطلب 70% أو أكثر"},
]

QUIZ_GENERAL = [
    {"q": "اختر الجملة الصحيحة نحوياً:", "opts": ["She go to school", "She goes to school", "She going to school", "She gone to school"], "ans": 1, "explanation": "مع she/he/it نضيف s للفعل"},
    {"q": "معنى كلمة 'Significant' هو:", "opts": ["صغير", "مهم", "سريع", "بطيء"], "ans": 1, "explanation": "Significant تعني مهم أو بارز"},
    {"q": "أي حرف جر صحيح: 'She is good ___ English.'", "opts": ["in", "on", "at", "for"], "ans": 2, "explanation": "نقول good at لمهارة معينة"},
    {"q": "المضاد المناسب لكلمة 'Ancient' هو:", "opts": ["قديم", "حديث", "جميل", "قبيح"], "ans": 1, "explanation": "Ancient = قديم، عكسه Modern = حديث"},
]

DOWNLOADS = [
    {"icon": "📄", "name": "كتيب IELTS - القواعد الأساسية", "size": "2.5 MB", "type": "PDF"},
    {"icon": "📋", "name": "قاموس المفردات المصور", "size": "4.8 MB", "type": "PDF"},
    {"icon": "🗂️", "name": "نماذج امتحانات STEP محلولة", "size": "6.2 MB", "type": "PDF"},
    {"icon": "📊", "name": "خطة دراسة 30 يوم", "size": "1.5 MB", "type": "PDF"},
    {"icon": "🎧", "name": "تمارين الاستماع الصوتية", "size": "35.7 MB", "type": "ZIP"},
    {"icon": "✏️", "name": "كراسة تمارين الكتابة", "size": "3.2 MB", "type": "PDF"},
]

# ── Helper Functions ──────────────────────────────────────────────────────
def add_notification(message, type="success"):
    st.session_state.notifications.append({"message": message, "type": type, "time": datetime.now()})
    if len(st.session_state.notifications) > 3:
        st.session_state.notifications.pop(0)

def add_points(points, reason=""):
    st.session_state.points += points
    add_notification(f"🎉 +{points} نقطة {reason}!")
    check_badges()

def check_badges():
    badges_to_check = [
        (st.session_state.points >= 100, "نقاطي", "🏅 أنت الآن في مستوى 'نقاطي'"),
        (st.session_state.points >= 500, "خبير", "🏆 مذهل! حصلت على لقب 'خبير'"),
        (len(st.session_state.enrolled_courses) >= 3, "متعلم نشط", "📚 تهانينا! أصبحت 'متعلم نشط'"),
        (len(st.session_state.completed_lessons) >= 10, "مجتهد", "⭐ أحسنت! حصلت على وسام 'مجتهد'"),
        (len(st.session_state.quiz_scores) > 0 and max(st.session_state.quiz_scores.values()) >= 3, "متفوق", "🎯 حصلت على وسام 'متفوق'")
    ]
    
    for condition, badge_name, message in badges_to_check:
        if condition and badge_name not in st.session_state.badges:
            st.session_state.badges.append(badge_name)
            add_notification(message)

def enroll_course(course_title):
    if st.session_state.logged_in:
        if course_title not in st.session_state.enrolled_courses:
            st.session_state.enrolled_courses.append(course_title)
            add_points(30, f"للتسجيل في كورس {course_title}")
            check_badges()
            add_notification(f"✅ تم تسجيلك في كورس {course_title} بنجاح")
            return True
        else:
            add_notification(f"ℹ️ أنت مسجل بالفعل في {course_title}", "info")
            return False
    else:
        add_notification("⚠️ يرجى تسجيل الدخول أولاً", "warning")
        return False

def watch_video(video_title):
    if video_title not in st.session_state.watched_videos:
        st.session_state.watched_videos.append(video_title)
        add_points(10, f"لمشاهدة {video_title}")
        add_notification(f"🎬 شاهدت: {video_title}")
        check_badges()

def render_navbar():
    pages = [
        ("home", "🏠 الرئيسية"),
        ("courses", "📚 الكورسات"),
        ("videos", "🎬 الفيديوهات"),
        ("quiz", "📝 الاختبارات"),
        ("downloads", "📥 التحميلات"),
        ("profile", "👤 ملفي")
    ]
    
    col1, col2, col3 = st.columns([2, 6, 1.5])
    with col1:
        st.markdown("<div class='nav-logo'>📚 <span>منصة المَالِك</span></div>", unsafe_allow_html=True)
    
    with col2:
        nav_cols = st.columns(len(pages))
        for idx, (pid, plabel) in enumerate(pages):
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
        if st.button(dark_icon, key="dark_mode_toggle", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

# ── Pages ─────────────────────────────────────────────────────────────────
def home_page():
    # Hero Section
    st.markdown("""
    <div class="hero">
        <h1>📚 <span>منصة المَالِك</span> التعليمية</h1>
        <p>نقدم دورات في اللغة الإنجليزية مصممة خصيصاً لتتناسب مع جميع المستويات<br>
        ونوفر لك جميع خدمات تعليمية استثنائية لتحقيق أهدافك</p>
        <div class="hero-buttons">
            <button class="btn-primary" onclick="window.location.href='?page=courses'">📖 تصفح جميع دوراتنا</button>
            <button class="btn-outline" onclick="window.location.href='?page=videos'">🎯 تعلم طريقة الاستشراف</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics
    st.markdown("""
    <div class="stats-row">
        <div class="stat-card"><div class="stat-icon">👨‍🎓</div><div class="stat-num">+10,000</div><div class="stat-lbl">طالب مسجل</div></div>
        <div class="stat-card"><div class="stat-icon">📚</div><div class="stat-num">+50</div><div class="stat-lbl">دورة تعليمية</div></div>
        <div class="stat-card"><div class="stat-icon">🎬</div><div class="stat-num">+200</div><div class="stat-lbl">فيديو تعليمي</div></div>
        <div class="stat-card"><div class="stat-icon">⭐</div><div class="stat-num">4.9</div><div class="stat-lbl">تقييم الطلاب</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section - 4 Yellow Cards
    st.markdown('<div class="section">', unsafe_allow_html=True)
    
    features = [
        {"icon": "📅", "title": "جدول دراسية\nخطة وصول دراسية", "desc": "مخصصة تناسب وقتك\nوأهدافك التعليمية"},
        {"icon": "⚡", "title": "تدريب فوري", "desc": "تمارين واختبارات بعد كل درس\nلتطبيق ما تعلمته"},
        {"icon": "👨‍🏫", "title": "مدربون خبراء", "desc": "شرح سلس من مدربين\nمختصين في شرح التقنيات\nاللازمة"},
        {"icon": "🎯", "title": "دورات مختلفة", "desc": "دورات مختلفة لتحقيق نتائج\nسريعة في وقت قصير"}
    ]
    
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
    
    # Featured Courses
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📘 أفضل كورساتنا</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">اختر المسار المناسب لك وابدأ رحلة التعلم</div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for idx, course in enumerate(COURSES[:4]):
        with cols[idx]:
            st.markdown(f"""
            <div class="course-card">
                <div class="course-header">{course['icon']}</div>
                <div class="course-body">
                    <div class="course-title">{course['title']}</div>
                    <div class="course-desc">{course['desc']}</div>
                    <div class="course-meta">
                        <span>📊 {course['lessons']} درس</span>
                        <span>📖 {course['level']}</span>
                    </div>
                </div>
                <div class="course-footer">
                    <span class="course-price">🎁 {course['price']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"انضم الآن", key=f"home_enroll_{idx}", use_container_width=True):
                if enroll_course(course['title']):
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Study Plan
    st.markdown("""
    <div class="section">
        <div class="study-plan">
            <div class="study-plan-title">📋 جدول دراسي مخصص</div>
            <div class="study-plan-text">خطط دراسية مرنة تناسب وقتك وتساعدك على تحقيق أهدافك التعليمية بفعالية</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def courses_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📚 جميع الكورسات التعليمية</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">اختر الكورس المناسب لمستواك وابدأ التعلم</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        categories = ["الكل", "IELTS", "STEP", "Speaking", "Writing", "Grammar", "Business"]
        selected_cat = st.selectbox("🔍 تصفية حسب المجال", categories, key="course_filter")
    with col2:
        levels = ["الكل", "مبتدئ", "متوسط", "متقدم"]
        selected_level = st.selectbox("📊 تصفية حسب المستوى", levels, key="level_filter")
    with col3:
        search = st.text_input("🔎 بحث", placeholder="اسم الكورس...", key="course_search")
    
    filtered = COURSES
    if selected_cat != "الكل":
        filtered = [c for c in filtered if c['badge'] == selected_cat]
    if selected_level != "الكل":
        filtered = [c for c in filtered if c['level'] == selected_level]
    if search:
        filtered = [c for c in filtered if search.lower() in c['title'].lower()]
    
    st.markdown(f'<p style="color: rgba(255,255,255,0.7); margin-bottom: 1rem;">📊 显示 {len(filtered)} 个课程</p>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, course in enumerate(filtered):
        with cols[idx % 3]:
            enrolled = course['title'] in st.session_state.enrolled_courses
            st.markdown(f"""
            <div class="course-card">
                <div class="course-header">{course['icon']}</div>
                <div class="course-body">
                    <div class="course-title">{course['title']}</div>
                    <div class="course-desc">{course['desc']}</div>
                    <div class="course-meta">
                        <span>🎖️ {course['badge']}</span>
                        <span>📊 {course['lessons']} درس</span>
                        <span>📖 {course['level']}</span>
                    </div>
                </div>
                <div class="course-footer">
                    <span class="course-price">🎁 {course['price']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            btn_text = "✅ مسجل" if enrolled else "📝 انضم الآن"
            if st.button(btn_text, key=f"course_{course['title']}", use_container_width=True, disabled=enrolled):
                if enroll_course(course['title']):
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def videos_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 مكتبة الفيديوهات التعليمية</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">أكثر من 200 فيديو تعليمي لمساعدتك في رحلة التعلم</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        categories = ["الكل", "IELTS", "STEP", "Speaking", "Writing", "Reading", "Listening"]
        selected_cat = st.selectbox("🔍 التصنيف", categories, key="video_cat")
    with col2:
        levels = ["الكل", "مبتدئ", "متوسط", "متقدم"]
        selected_level = st.selectbox("📊 المستوى", levels, key="video_level")
    
    filtered = VIDEOS
    if selected_cat != "الكل":
        filtered = [v for v in filtered if v['cat'] == selected_cat]
    if selected_level != "الكل":
        filtered = [v for v in filtered if v['level'] == selected_level]
    
    for video in filtered:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.08); border-radius:12px; padding:0.8rem 1rem; margin-bottom:0.8rem">
                <div style="display:flex; gap:1rem; align-items:center">
                    <div style="font-size:2rem">{video['thumb']}</div>
                    <div style="flex:1">
                        <div style="font-weight:bold; color:#FFD700">{video['title']}</div>
                        <div style="font-size:0.7rem; opacity:0.6">
                            ⏱ {video['dur']} | 👁 {video['views']} | {video['cat']} | مستوى {video['level']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            watched = video['title'] in st.session_state.watched_videos
            btn_text = "✅ تم" if watched else "▶ شاهد"
            if st.button(btn_text, key=f"watch_{video['title']}", use_container_width=True, disabled=watched):
                watch_video(video['title'])
                st.rerun()
        with col3:
            st.markdown(f'<div style="padding:0.5rem; text-align:center">{video["dur"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def quiz_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 اختبر معلوماتك</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">اختر نوع الاختبار وابدأ التحدي</div>', unsafe_allow_html=True)
    
    # Quiz type selector
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎓 IELTS Quiz", use_container_width=True, type="primary" if st.session_state.q_type == "IELTS" else "secondary"):
            st.session_state.q_type = "IELTS"
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.quiz_done = False
            st.rerun()
    with col2:
        if st.button("📋 STEP Quiz", use_container_width=True, type="primary" if st.session_state.q_type == "STEP" else "secondary"):
            st.session_state.q_type = "STEP"
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.quiz_done = False
            st.rerun()
    with col3:
        if st.button("💡 General Quiz", use_container_width=True, type="primary" if st.session_state.q_type == "GENERAL" else "secondary"):
            st.session_state.q_type = "GENERAL"
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.quiz_done = False
            st.rerun()
    
    st.markdown("---")
    
    # Load questions based on type
    if st.session_state.q_type == "IELTS":
        questions = QUIZ_IELTS
    elif st.session_state.q_type == "STEP":
        questions = QUIZ_STEP
    else:
        questions = QUIZ_GENERAL
    
    total = len(questions)
    
    if st.session_state.quiz_done:
        percentage = int((st.session_state.score / total) * 100)
        
        # Save best score
        if st.session_state.score > st.session_state.quiz_scores.get(st.session_state.q_type, 0):
            st.session_state.quiz_scores[st.session_state.q_type] = st.session_state.score
            points_earned = st.session_state.score * 15
            add_points(points_earned, f"في اختبار {st.session_state.q_type}")
            check_badges()
        
        # Determine emoji and message
        if percentage >= 80:
            emoji = "🏆"
            message = "ممتاز! أنت متميز حقاً"
        elif percentage >= 60:
            emoji = "🎉"
            message = "جيد جداً! واصل التقدم"
        elif percentage >= 40:
            emoji = "👍"
            message = "جيد، لكن يمكنك التحسن"
        else:
            emoji = "📚"
            message = "تحتاج إلى مراجعة المواد"
        
        st.markdown(f"""
        <div class="quiz-card" style="text-align:center">
            <div style="font-size:3rem">{emoji}</div>
            <div style="font-size:1.5rem; font-weight:bold; margin:1rem 0">
                نتيجتك: {st.session_state.score}/{total}
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width:{percentage}%"></div>
            </div>
            <div style="font-size:1rem; margin:1rem 0">{message}</div>
            <div style="font-size:0.85rem; opacity:0.7">أفضل نتيجة: {st.session_state.quiz_scores.get(st.session_state.q_type, 0)}/{total}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 إعادة الاختبار", use_container_width=True):
                st.session_state.q_idx = 0
                st.session_state.score = 0
                st.session_state.quiz_done = False
                st.rerun()
        with col2:
            if st.button("🏠 العودة للرئيسية", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
    else:
        idx = st.session_state.q_idx
        q = questions[idx]
        progress = ((idx) / total) * 100
        
        st.markdown(f"""
        <div class="quiz-card">
            <div style="display:flex; justify-content:space-between; margin-bottom:1rem">
                <span style="color:#FFD700; font-weight:bold">اختبار {st.session_state.q_type}</span>
                <span>📋 سؤال {idx + 1} من {total}</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width:{progress}%"></div>
            </div>
            <div class="quiz-q">{q['q']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        for i, opt in enumerate(q["opts"]):
            # Style based on answer state
            if st.session_state.answered:
                if i == q["ans"]:
                    btn_text = f"✅ {opt}"
                    btn_style = "background: rgba(46, 204, 113, 0.2); border-color: #2ecc71;"
                elif i == st.session_state.chosen:
                    btn_text = f"❌ {opt}"
                    btn_style = "background: rgba(231, 76, 60, 0.2); border-color: #e74c3c;"
                else:
                    btn_text = f"🔘 {opt}"
                    btn_style = ""
            else:
                btn_text = f"🔘 {opt}"
                btn_style = ""
            
            if st.button(btn_text, key=f"quiz_opt_{idx}_{i}", use_container_width=True, disabled=st.session_state.answered):
                st.session_state.chosen = i
                st.session_state.answered = True
                if i == q["ans"]:
                    st.session_state.score += 1
                    st.success("✅ إجابة صحيحة!")
                else:
                    st.error(f"❌ إجابة خاطئة! الإجابة الصحيحة: {q['opts'][q['ans']]}")
                if 'explanation' in q:
                    st.info(f"💡 {q['explanation']}")
                st.rerun()
        
        if st.session_state.answered:
            col1, col2 = st.columns([3, 1])
            with col1:
                if idx + 1 < total:
                    if st.button("➡️ السؤال التالي", type="primary", use_container_width=False):
                        st.session_state.q_idx += 1
                        st.session_state.answered = False
                        st.session_state.chosen = None
                        st.rerun()
                else:
                    if st.button("🏁 إنهاء الاختبار", type="primary", use_container_width=False):
                        st.session_state.quiz_done = True
                        st.rerun()
            with col2:
                st.markdown(f'<div style="text-align:left; color:#FFD700">🎯 النقاط: {st.session_state.score}</div>', unsafe_allow_html=True)

def downloads_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📥 ملفات التحميل</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">موارد مجانية لمساعدتك في رحلة التعلم</div>', unsafe_allow_html=True)
    
    # Search and filter
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔍 بحث", placeholder="اسم الملف...", key="download_search")
    with col2:
        file_types = ["الكل", "PDF", "ZIP"]
        selected_type = st.selectbox("📄 نوع الملف", file_types, key="download_type")
    
    filtered = DOWNLOADS
    if search:
        filtered = [d for d in filtered if search.lower() in d['name'].lower()]
    if selected_type != "الكل":
        filtered = [d for d in filtered if d['type'] == selected_type]
    
    for file in filtered:
        col1, col2, col3, col4 = st.columns([4, 1, 1, 0.5])
        with col1:
            st.markdown(f"""
            <div class="dl-card">
                <div class="dl-icon">{file['icon']}</div>
                <div class="dl-info">
                    <div class="dl-name">{file['name']}</div>
                    <div class="dl-size">📦 {file['size']} | 📄 {file['type']}</div>
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
                st.info("🔐 سجل دخولك")
        with col3:
            fav = file['name'] in st.session_state.favorite_downloads
            fav_icon = "⭐" if fav else "☆"
            if st.button(fav_icon, key=f"fav_{file['name']}"):
                if fav:
                    st.session_state.favorite_downloads.remove(file['name'])
                    add_notification(f"📌 تمت إزالة {file['name']} من المفضلة", "info")
                else:
                    st.session_state.favorite_downloads.append(file['name'])
                    add_points(5, f"لإضافة {file['name'][:20]} إلى المفضلة")
                    add_notification(f"⭐ تمت إضافة {file['name']} إلى المفضلة")
                st.rerun()
        with col4:
            st.markdown(f'<div style="font-size:0.7rem; opacity:0.5">{file["size"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.favorite_downloads:
        st.markdown("---")
        st.markdown("### ⭐ ملفاتك المفضلة")
        for fav in st.session_state.favorite_downloads:
            st.markdown(f"- 📄 {fav}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def profile_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # Login Form
        st.markdown("""
        <div style="max-width:450px; margin:2rem auto">
            <div class="quiz-card">
                <div style="text-align:center">
                    <div style="font-size:3rem">🔐</div>
                    <h2 style="color:#FFD700">تسجيل الدخول</h2>
                    <p style="font-size:0.85rem; opacity:0.7">سجل دخولك للوصول إلى جميع الميزات</p>
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
                    st.session_state.user_email = email if email else f"{username}@example.com"
                    add_points(50, "للتسجيل في المنصة")
                    add_notification(f"✨ مرحباً {username}! أهلاً بك في منصة المالك التعليمية")
                    check_badges()
                    st.rerun()
                else:
                    st.error("❌ الرجاء إدخال اسم المستخدم وكلمة المرور")
            
            if register_btn:
                st.info("📧 سيتم إرسال رابط التأكيد إلى بريدك الإلكتروني")
    else:
        # Profile Info
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="profile-card">
                <div class="avatar">👤</div>
                <h3 style="color:#FFD700">{st.session_state.username}</h3>
                <p style="font-size:0.8rem; opacity:0.7">{st.session_state.user_email}</p>
                <hr>
                <div class="stat-num" style="font-size:2rem">{st.session_state.points}</div>
                <div>🏆 النقاط</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Logout button
            if st.button("🚪 تسجيل الخروج", use_container_width=True, type="secondary"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.user_email = ""
                st.rerun()
        
        with col2:
            # Stats
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("📚 كورسات مسجل بها", len(st.session_state.enrolled_courses))
            with col_b:
                st.metric("🎬 فيديوهات شاهدتها", len(st.session_state.watched_videos))
            with col_c:
                best_score = max(st.session_state.quiz_scores.values()) if st.session_state.quiz_scores else 0
                st.metric("🏆 أفضل درجة", f"{best_score}")
            
            # Progress
            st.markdown("---")
            st.markdown("#### 📊 تقدمك التعليمي")
            
            total_courses = max(len(COURSES), 1)
            course_progress = int((len(st.session_state.enrolled_courses) / total_courses) * 100)
            st.progress(course_progress, text=f"تقدم الكورسات: {course_progress}%")
            
            total_videos = max(len(VIDEOS), 1)
            video_progress = int((len(st.session_state.watched_videos) / total_videos) * 100)
            st.progress(video_progress, text=f"تقدم الفيديوهات: {video_progress}%")
            
            # Badges
            if st.session_state.badges:
                st.markdown("---")
                st.markdown("#### 🏅 الأوسمة التي حصلت عليها")
                badges_html = '<div class="badge-container">'
                for badge in st.session_state.badges:
                    badges_html += f'<span class="badge">🏅 {badge}</span>'
                badges_html += '</div>'
                st.markdown(badges_html, unsafe_allow_html=True)
            
            # Enrolled Courses
            if st.session_state.enrolled_courses:
                st.markdown("---")
                st.markdown("#### ✅ الكورسات المسجل بها")
                for course in st.session_state.enrolled_courses:
                    st.markdown(f"- 📖 {course}")

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
        © 2025 منصة المَالِك التعليمية — جميع الحقوق محفوظة
        <br>
        <small>🌟 {st.session_state.points} نقطة | {len(st.session_state.badges)} وسام | {len(st.session_state.enrolled_courses)} كورس</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
