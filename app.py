import streamlit as st

st.set_page_config(
    page_title="منصة الريحاني التعليمية",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&family=Poppins:wght@400;600;700&display=swap');

:root {
  --primary:   #6C63FF;
  --secondary: #FF6584;
  --accent:    #F5A623;
  --grad1:     #667eea;
  --grad2:     #764ba2;
  --grad3:     #f093fb;
  --dark:      #1a1a2e;
  --card-bg:   rgba(255,255,255,0.95);
  --text:      #2d2d2d;
}

html, body, [class*="css"] {
  font-family: 'Tajawal', sans-serif !important;
  direction: rtl;
}

/* ── hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] { background: transparent; }

/* ── page background ── */
[data-testid="stAppViewContainer"]::before {
  content: '';
  position: fixed; inset: 0; z-index: -1;
  background: linear-gradient(135deg, var(--grad1) 0%, var(--grad2) 50%, var(--grad3) 100%);
}

/* ── nav bar ── */
.navbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 3rem;
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(255,255,255,0.2);
  position: sticky; top: 0; z-index: 999;
}
.nav-logo { font-size: 1.6rem; font-weight: 900; color: #fff; letter-spacing: -0.5px; }
.nav-logo span { color: var(--accent); }
.nav-links { display: flex; gap: 0.4rem; }
.nav-btn {
  border: none; border-radius: 50px; padding: 0.45rem 1.2rem;
  font-size: 0.9rem; font-family: 'Tajawal', sans-serif;
  cursor: pointer; transition: all .25s;
}
.nav-btn.active { background: var(--accent); color: #fff; font-weight: 700; }
.nav-btn:not(.active) { background: rgba(255,255,255,0.15); color: #fff; }
.nav-btn:not(.active):hover { background: rgba(255,255,255,0.3); }

/* ── section containers ── */
.section { padding: 2.5rem 3rem; }

/* ── hero ── */
.hero {
  min-height: 70vh; display: flex; flex-direction: column;
  justify-content: center; padding: 4rem 3rem;
  color: #fff;
}
.hero h1 { font-size: clamp(2.2rem,5vw,3.8rem); font-weight: 900; line-height: 1.2; margin-bottom: 1rem; }
.hero p  { font-size: 1.15rem; opacity: .85; max-width: 520px; margin-bottom: 2rem; }
.hero-btn {
  display: inline-block; background: var(--accent);
  color: #fff; font-family: 'Tajawal',sans-serif; font-size: 1.05rem; font-weight: 700;
  padding: 0.85rem 2.4rem; border-radius: 50px; border: none; cursor: pointer;
  box-shadow: 0 8px 30px rgba(245,166,35,.45); transition: transform .2s, box-shadow .2s;
}
.hero-btn:hover { transform: translateY(-3px); box-shadow: 0 14px 40px rgba(245,166,35,.55); }

/* ── stat cards ── */
.stats-row { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.stat-card {
  flex: 1; min-width: 200px;
  background: var(--card-bg); border-radius: 18px;
  padding: 1.6rem; text-align: center;
  box-shadow: 0 10px 40px rgba(0,0,0,.12);
  transition: transform .25s;
}
.stat-card:hover { transform: translateY(-6px); }
.stat-icon { font-size: 2.2rem; margin-bottom: .5rem; }
.stat-num  { font-size: 1.9rem; font-weight: 900; color: var(--primary); }
.stat-lbl  { font-size: 0.95rem; color: #666; margin-top: .2rem; }

/* ── section heading ── */
.sec-title {
  font-size: 1.8rem; font-weight: 900; color: #fff;
  margin-bottom: .5rem;
}
.sec-sub { color: rgba(255,255,255,.75); font-size: 1rem; margin-bottom: 2rem; }

/* ── course / video cards ── */
.cards-grid { display: flex; gap: 1.4rem; flex-wrap: wrap; }
.course-card {
  flex: 1; min-width: 240px; max-width: 320px;
  background: var(--card-bg); border-radius: 18px;
  overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,.13);
  transition: transform .25s, box-shadow .25s;
}
.course-card:hover { transform: translateY(-8px); box-shadow: 0 18px 50px rgba(0,0,0,.2); }
.card-thumb {
  height: 140px; display: flex; align-items: center; justify-content: center;
  font-size: 3.5rem;
}
.card-body { padding: 1.1rem 1.3rem; }
.card-badge {
  display: inline-block; font-size: .72rem; font-weight: 700;
  padding: .25rem .7rem; border-radius: 50px; margin-bottom: .6rem;
  background: rgba(108,99,255,.15); color: var(--primary);
}
.card-title  { font-size: 1.05rem; font-weight: 700; color: var(--dark); margin-bottom: .4rem; }
.card-desc   { font-size: .88rem; color: #666; line-height: 1.5; }
.card-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding: .8rem 1.3rem; border-top: 1px solid #f0f0f0;
}
.card-price  { font-weight: 700; color: var(--accent); font-size: 1rem; }
.card-enroll {
  background: var(--primary); color: #fff;
  border: none; border-radius: 50px; padding: .38rem 1rem;
  font-family: 'Tajawal',sans-serif; font-size: .88rem; cursor: pointer;
  transition: background .2s;
}
.card-enroll:hover { background: var(--grad2); }

/* ── play button overlay ── */
.play-overlay {
  position: relative; cursor: pointer;
}
.play-btn {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,.25); transition: background .2s;
}
.play-btn:hover { background: rgba(0,0,0,.4); }
.play-circle {
  width: 52px; height: 52px; border-radius: 50%;
  background: rgba(255,255,255,.9);
  display: flex; align-items: center; justify-content: center; font-size: 1.4rem;
}

/* ── login form ── */
.login-wrap {
  max-width: 460px; margin: 2rem auto;
  background: var(--card-bg); border-radius: 24px;
  padding: 2.5rem; box-shadow: 0 20px 60px rgba(0,0,0,.18);
}
.login-title { font-size: 1.6rem; font-weight: 900; color: var(--dark); text-align: center; margin-bottom: 1.5rem; }

/* ── quiz ── */
.quiz-card {
  background: var(--card-bg); border-radius: 20px;
  padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,.12); max-width: 700px; margin: auto;
}
.quiz-q { font-size: 1.15rem; font-weight: 700; color: var(--dark); margin-bottom: 1.2rem; }
.opt-btn {
  display: block; width: 100%;
  background: rgba(108,99,255,.07); border: 2px solid rgba(108,99,255,.2);
  border-radius: 12px; padding: .75rem 1.2rem;
  font-family: 'Tajawal',sans-serif; font-size: .98rem; color: var(--dark);
  text-align: right; cursor: pointer; margin-bottom: .65rem;
  transition: all .2s;
}
.opt-btn:hover { background: rgba(108,99,255,.15); border-color: var(--primary); }
.opt-btn.correct { background: rgba(39,174,96,.15); border-color: #27ae60; color: #27ae60; }
.opt-btn.wrong   { background: rgba(231,76,60,.12); border-color: #e74c3c;  color: #e74c3c;  }
.progress-bar-bg {
  height: 8px; background: rgba(255,255,255,.3); border-radius: 50px; margin-bottom: 1.5rem;
}
.progress-bar-fill {
  height: 100%; background: var(--accent); border-radius: 50px; transition: width .4s;
}

/* ── downloads ── */
.dl-card {
  display: flex; align-items: center; gap: 1.2rem;
  background: var(--card-bg); border-radius: 16px;
  padding: 1.2rem 1.5rem; margin-bottom: 1rem;
  box-shadow: 0 6px 25px rgba(0,0,0,.09);
  transition: transform .2s;
}
.dl-card:hover { transform: translateX(-4px); }
.dl-icon { font-size: 2.2rem; }
.dl-info { flex: 1; }
.dl-name { font-weight: 700; color: var(--dark); font-size: 1rem; }
.dl-size { font-size: .82rem; color: #888; margin-top: .15rem; }
.dl-btn {
  background: var(--primary); color: #fff; border: none;
  border-radius: 50px; padding: .45rem 1.2rem;
  font-family: 'Tajawal',sans-serif; font-size: .88rem; cursor: pointer;
  transition: background .2s;
}
.dl-btn:hover { background: var(--grad2); }

/* ── footer ── */
.footer {
  text-align: center; padding: 1.5rem; color: rgba(255,255,255,.55); font-size: .85rem;
  border-top: 1px solid rgba(255,255,255,.1); margin-top: 3rem;
}

/* ── streamlit override ── */
.stButton > button { display: none; }  /* we use HTML buttons; hide ST defaults where unused */
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────
if "page"       not in st.session_state: st.session_state.page = "home"
if "logged_in"  not in st.session_state: st.session_state.logged_in = False
if "username"   not in st.session_state: st.session_state.username = ""
if "q_idx"      not in st.session_state: st.session_state.q_idx = 0
if "score"      not in st.session_state: st.session_state.score = 0
if "answered"   not in st.session_state: st.session_state.answered = False
if "chosen"     not in st.session_state: st.session_state.chosen = None
if "quiz_done"  not in st.session_state: st.session_state.quiz_done = False
if "q_type"     not in st.session_state: st.session_state.q_type = "IELTS"

# ── Data ──────────────────────────────────────────────────────────────────
COURSES = [
    {"icon":"🎓","color":"linear-gradient(135deg,#667eea,#764ba2)","badge":"IELTS","title":"IELTS من الصفر للاحتراف","desc":"استعد لامتحان IELTS مع أفضل المدربين وحقق الدرجة التي تحلم بها","price":"مجاني","lessons":24},
    {"icon":"📝","color":"linear-gradient(135deg,#f093fb,#f5576c)","badge":"STEP","title":"اختبار STEP المتكامل","desc":"دورة شاملة لاختبار STEP تغطي جميع المهارات اللغوية بأسلوب احترافي","price":"مجاني","lessons":18},
    {"icon":"🗣️","color":"linear-gradient(135deg,#4facfe,#00f2fe)","badge":"Speaking","title":"مهارات المحادثة","desc":"طوّر مهارة التحدث والمحادثة بالإنجليزية مع متحدثين أصليين","price":"مجاني","lessons":12},
    {"icon":"✍️","color":"linear-gradient(135deg,#43e97b,#38f9d7)","badge":"Writing","title":"الكتابة الأكاديمية","desc":"تعلم كتابة المقالات والتقارير الأكاديمية بمستوى عالمي","price":"مجاني","lessons":15},
    {"icon":"👂","color":"linear-gradient(135deg,#fa709a,#fee140)","badge":"Listening","title":"مهارة الاستماع","desc":"تمارين استماع مكثفة لرفع درجتك في قسم Listening","price":"مجاني","lessons":10},
    {"icon":"📖","color":"linear-gradient(135deg,#a18cd1,#fbc2eb)","badge":"Reading","title":"الفهم القرائي","desc":"استراتيجيات متقدمة للفهم القرائي وزيادة سرعة القراءة","price":"مجاني","lessons":14},
]

VIDEOS = [
    {"thumb":"🎬","color":"linear-gradient(135deg,#667eea,#764ba2)","title":"مقدمة اختبار IELTS - الجزء الأول","dur":"18:32","views":"12,450","cat":"IELTS"},
    {"thumb":"🎥","color":"linear-gradient(135deg,#f5576c,#f093fb)","title":"أسرار قسم Writing Task 2","dur":"24:15","views":"9,820","cat":"Writing"},
    {"thumb":"📹","color":"linear-gradient(135deg,#4facfe,#00f2fe)","title":"تقنيات Speaking Band 7+","dur":"21:40","views":"15,300","cat":"Speaking"},
    {"thumb":"🎞️","color":"linear-gradient(135deg,#43e97b,#38f9d7)","title":"STEP اختبار - نصائح ذهبية","dur":"16:55","views":"7,650","cat":"STEP"},
    {"thumb":"📽️","color":"linear-gradient(135deg,#fa709a,#fee140)","title":"Reading Strategies للمستوى المتقدم","dur":"19:20","views":"11,200","cat":"Reading"},
    {"thumb":"🎦","color":"linear-gradient(135deg,#a18cd1,#fbc2eb)","title":"Listening Tips & Tricks","dur":"22:10","views":"8,900","cat":"Listening"},
]

QUIZ_IELTS = [
    {"q":"Which section of IELTS tests your ability to write essays and reports?","opts":["Listening","Reading","Writing","Speaking"],"ans":2},
    {"q":"What is the maximum band score in IELTS?","opts":["9","10","8","7"],"ans":0},
    {"q":"Choose the correct sentence:","opts":["She go to school","She goes to school","She going to school","She gone to school"],"ans":1},
    {"q":"IELTS Academic is required for:","opts":["Work visa","University admission","Tourist visa","Driving licence"],"ans":1},
    {"q":"Which word is a synonym for 'significant'?","opts":["tiny","important","boring","quick"],"ans":1},
    {"q":"Choose the correct preposition: 'She is good ___ English.'","opts":["in","on","at","for"],"ans":2},
    {"q":"How long is the IELTS Listening section?","opts":["40 minutes","30 minutes","60 minutes","20 minutes"],"ans":1},
    {"q":"Which of these is NOT a section in IELTS?","opts":["Listening","Reading","Grammar","Writing"],"ans":2},
]

QUIZ_STEP = [
    {"q":"Choose the correct verb form: 'He ___ to school every day.'","opts":["go","goes","going","gone"],"ans":1},
    {"q":"What does 'ubiquitous' mean?","opts":["rare","present everywhere","expensive","dangerous"],"ans":1},
    {"q":"STEP test is required in:","opts":["Egypt","Saudi Arabia","UAE","UK"],"ans":1},
    {"q":"Choose the correct sentence:","opts":["I am agree","I agrees","I agree","I agreeing"],"ans":2},
    {"q":"The opposite of 'ancient' is:","opts":["old","modern","large","fast"],"ans":1},
    {"q":"Which tense: 'She has been studying for 3 hours.'","opts":["Simple past","Present perfect continuous","Future simple","Past perfect"],"ans":1},
    {"q":"The STEP test total score is out of:","opts":["100","200","900","50"],"ans":1},
    {"q":"Choose the correct article: '___ apple a day keeps the doctor away.'","opts":["A","An","The","No article"],"ans":1},
]

DOWNLOADS = [
    {"icon":"📄","name":"كتاب IELTS - Cambridge 18","size":"15.2 MB","type":"PDF"},
    {"icon":"📋","name":"قاموس مفردات IELTS الأساسية","size":"3.8 MB","type":"PDF"},
    {"icon":"🗂️","name":"نماذج امتحانات STEP مع الحلول","size":"8.5 MB","type":"PDF"},
    {"icon":"📊","name":"خطة المذاكرة 30 يوم","size":"1.2 MB","type":"PDF"},
    {"icon":"🎧","name":"تسجيلات Listening للتدريب","size":"45.7 MB","type":"ZIP"},
    {"icon":"✏️","name":"نماذج Writing مصححة","size":"5.3 MB","type":"PDF"},
    {"icon":"📝","name":"اختبارات Reading كاملة","size":"6.9 MB","type":"PDF"},
    {"icon":"🔤","name":"قائمة Academic Word List","size":"0.9 MB","type":"PDF"},
]

# ── Navigation bar ─────────────────────────────────────────────────────────
PAGES = [("home","🏠 الرئيسية"),("videos","🎬 الفيديوات"),("login","🔐 تسجيل الدخول"),("quiz","📝 الاختبار"),("downloads","📥 التحميلات")]

nav_html = '<div class="navbar"><div class="nav-logo">📚 <span>الريحاني</span> التعليمية</div><div class="nav-links">'
for pid, plabel in PAGES:
    cls = "nav-btn active" if st.session_state.page == pid else "nav-btn"
    nav_html += f'<button class="{cls}" onclick="window.location.href=\'?page={pid}\'">{plabel}</button>'
nav_html += '</div></div>'
st.markdown(nav_html, unsafe_allow_html=True)

# read URL param for navigation (Streamlit query params)
params = st.query_params
if "page" in params:
    st.session_state.page = params["page"]

# ── Sidebar nav (mobile fallback) ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 منصة الريحاني")
    for pid, plabel in PAGES:
        if st.button(plabel, key=f"side_{pid}", use_container_width=True):
            st.session_state.page = pid
            st.query_params["page"] = pid
            st.rerun()
    if st.session_state.logged_in:
        st.success(f"مرحباً، {st.session_state.username} 👋")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

page = st.session_state.page

# ═══════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════
if page == "home":
    # Hero
    st.markdown("""
    <div class="hero">
      <h1>منصة الريحاني<br>التعليمية 🎓</h1>
      <p>طوّر مهاراتك في اللغة الإنجليزية واستعد لامتحانات IELTS و STEP مع أفضل المدربين المتخصصين</p>
      <button class="hero-btn">ابدأ التعلم مجاناً ←</button>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">🏆 إنجازاتنا</p><p class="sec-sub">أرقام تتحدث عن نفسها</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="stats-row">
      <div class="stat-card"><div class="stat-icon">👨‍🎓</div><div class="stat-num">+5,000</div><div class="stat-lbl">طالب مسجل</div></div>
      <div class="stat-card"><div class="stat-icon">📚</div><div class="stat-num">60+</div><div class="stat-lbl">دورة تعليمية</div></div>
      <div class="stat-card"><div class="stat-icon">🎬</div><div class="stat-num">200+</div><div class="stat-lbl">فيديو تعليمي</div></div>
      <div class="stat-card"><div class="stat-icon">⭐</div><div class="stat-num">4.9</div><div class="stat-lbl">تقييم الطلاب</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Courses
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">📘 دوراتنا التعليمية</p><p class="sec-sub">محتوى احترافي مصمم خصيصاً لنجاحك</p>', unsafe_allow_html=True)
    cards_html = '<div class="cards-grid">'
    for c in COURSES:
        cards_html += f"""
        <div class="course-card">
          <div class="card-thumb" style="background:{c['color']}">{c['icon']}</div>
          <div class="card-body">
            <span class="card-badge">{c['badge']}</span>
            <div class="card-title">{c['title']}</div>
            <div class="card-desc">{c['desc']}</div>
          </div>
          <div class="card-footer">
            <span class="card-price">🎁 {c['price']} | {c['lessons']} درس</span>
            <button class="card-enroll">انضم الآن</button>
          </div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer">© 2025 منصة الريحاني التعليمية — جميع الحقوق محفوظة</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# VIDEOS PAGE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "videos":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">🎬 مكتبة الفيديوات</p><p class="sec-sub">أكثر من 200 فيديو تعليمي متخصص</p>', unsafe_allow_html=True)

    cards_html = '<div class="cards-grid">'
    for v in VIDEOS:
        cards_html += f"""
        <div class="course-card">
          <div class="card-thumb play-overlay" style="background:{v['color']}">
            {v['thumb']}
            <div class="play-btn"><div class="play-circle">▶</div></div>
          </div>
          <div class="card-body">
            <span class="card-badge">{v['cat']}</span>
            <div class="card-title">{v['title']}</div>
            <div class="card-desc">⏱ {v['dur']} &nbsp;|&nbsp; 👁 {v['views']} مشاهدة</div>
          </div>
          <div class="card-footer">
            <span class="card-price">🆓 مجاني</span>
            <button class="card-enroll">▶ شاهد الآن</button>
          </div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "login":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    if st.session_state.logged_in:
        st.markdown(f"""
        <div class="login-wrap" style="text-align:center">
          <div style="font-size:3rem;margin-bottom:1rem">🎉</div>
          <div class="login-title">مرحباً، {st.session_state.username}!</div>
          <p style="color:#666">أنت مسجل الدخول بنجاح في منصة الريحاني التعليمية</p>
        </div>""", unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", use_container_width=False):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    else:
        st.markdown('<div class="login-wrap"><div class="login-title">🔐 تسجيل الدخول</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
            password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ دخول", use_container_width=True, type="primary")
            with col2:
                register = st.form_submit_button("📝 إنشاء حساب", use_container_width=True)

            if submitted:
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"✅ مرحباً {username}! تم تسجيل الدخول بنجاح")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ الرجاء إدخال اسم المستخدم وكلمة المرور")
            if register:
                st.info("📧 سيتم توجيهك لصفحة التسجيل قريباً")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# QUIZ PAGE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "quiz":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">📝 اختبر معلوماتك</p><p class="sec-sub">اختر نوع الاختبار وابدأ التحدي</p>', unsafe_allow_html=True)

    # Quiz type selector
    col_a, col_b, col_c = st.columns([1,1,2])
    with col_a:
        if st.button("🎓 IELTS Quiz", use_container_width=True):
            st.session_state.q_type = "IELTS"
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.chosen = None
            st.session_state.quiz_done = False
            st.rerun()
    with col_b:
        if st.button("📋 STEP Quiz", use_container_width=True):
            st.session_state.q_type = "STEP"
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.chosen = None
            st.session_state.quiz_done = False
            st.rerun()

    questions = QUIZ_IELTS if st.session_state.q_type == "IELTS" else QUIZ_STEP
    total = len(questions)

    if st.session_state.quiz_done:
        pct = int(st.session_state.score / total * 100)
        emoji = "🏆" if pct >= 80 else ("👍" if pct >= 50 else "📚")
        st.markdown(f"""
        <div class="quiz-card" style="text-align:center">
          <div style="font-size:4rem;margin-bottom:1rem">{emoji}</div>
          <div style="font-size:1.8rem;font-weight:900;color:#2d2d2d;margin-bottom:.5rem">
            نتيجتك: {st.session_state.score}/{total}
          </div>
          <div style="font-size:1.1rem;color:#666">نسبة النجاح: {pct}%</div>
          <div style="height:12px;background:#eee;border-radius:50px;margin:1.5rem 0">
            <div style="height:100%;width:{pct}%;background:{'#27ae60' if pct>=60 else '#e74c3c'};border-radius:50px;transition:width .5s"></div>
          </div>
          <p style="color:#555">{'ممتاز! أنت مستعد للامتحان 🎉' if pct>=80 else ('جيد، استمر في التدريب 💪' if pct>=50 else 'راجع المادة وحاول مرة أخرى 📖')}</p>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 إعادة الاختبار", use_container_width=False):
            st.session_state.q_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.chosen = None
            st.session_state.quiz_done = False
            st.rerun()
    else:
        idx = st.session_state.q_idx
        q = questions[idx]
        progress = (idx / total) * 100

        st.markdown(f"""
        <div class="quiz-card">
          <div style="display:flex;justify-content:space-between;margin-bottom:.8rem">
            <span style="font-weight:700;color:#6C63FF">سؤال {idx+1} من {total}</span>
            <span style="color:#666">نوع الاختبار: {st.session_state.q_type}</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{progress}%"></div></div>
          <div class="quiz-q">{q['q']}</div>
        </div>""", unsafe_allow_html=True)

        for i, opt in enumerate(q["opts"]):
            btn_label = f"{'✅' if (st.session_state.answered and i==q['ans']) else ('❌' if (st.session_state.answered and i==st.session_state.chosen and i!=q['ans']) else '🔵')} {opt}"
            if st.button(btn_label, key=f"opt_{idx}_{i}", use_container_width=True, disabled=st.session_state.answered):
                st.session_state.chosen = i
                st.session_state.answered = True
                if i == q["ans"]:
                    st.session_state.score += 1
                    st.success("✅ إجابة صحيحة!")
                else:
                    st.error(f"❌ إجابة خاطئة! الصحيح: {q['opts'][q['ans']]}")
                st.rerun()

        if st.session_state.answered:
            if idx + 1 < total:
                if st.button("السؤال التالي ←", type="primary", use_container_width=False):
                    st.session_state.q_idx += 1
                    st.session_state.answered = False
                    st.session_state.chosen = None
                    st.rerun()
            else:
                if st.button("🏁 إنهاء الاختبار", type="primary", use_container_width=False):
                    st.session_state.quiz_done = True
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# DOWNLOADS PAGE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "downloads":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">📥 ملفات التحميل</p><p class="sec-sub">موارد مجانية لمساعدتك في رحلتك التعليمية</p>', unsafe_allow_html=True)

    search = st.text_input("🔍 ابحث عن ملف...", placeholder="اكتب اسم الملف")
    filtered = [d for d in DOWNLOADS if search.lower() in d["name"].lower()] if search else DOWNLOADS

    for d in filtered:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="dl-card">
              <div class="dl-icon">{d['icon']}</div>
              <div class="dl-info">
                <div class="dl-name">{d['name']}</div>
                <div class="dl-size">📦 {d['size']} &nbsp;|&nbsp; 📄 {d['type']}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.button("⬇️ تحميل", key=f"dl_{d['name']}", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">© 2025 منصة الريحاني التعليمية — جميع الحقوق محفوظة</div>', unsafe_allow_html=True)
