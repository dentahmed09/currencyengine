import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Institutional Currency Strength Engine", layout="wide", page_icon="🏦")

# ====================== Google Sheets ======================
@st.cache_resource(show_spinner=False)
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)

# ====================== CSS ======================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .main-header {
            background: #0f172a;
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(241,196,15,0.2);
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, #f1c40f, #e67e22, #f1c40f);
        }
        .main-header h1 { color: #f1c40f; margin: 0; font-size: 1.6rem; font-weight: 700; }
        .main-header p  { color: #64748b; margin: 0.4rem 0 0; font-size: 0.8rem; text-transform: uppercase; }
        .section-header {
            font-size: 11px; font-weight: 600; color: #475569;
            letter-spacing: 0.1em; text-transform: uppercase;
            margin: 1.5rem 0 0.75rem;
            padding-bottom: 6px; border-bottom: 1px solid #1e293b;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0; background: #0f172a; padding: 4px;
            border-radius: 10px; border: 1px solid #1e293b;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px; padding: 0.5rem 1.2rem;
            font-size: 13px; font-weight: 500; color: #64748b; border: none;
        }
        .stTabs [aria-selected="true"] { background: #1e293b !important; color: #f1c40f !important; }
        .stButton button {
            background: #f1c40f; color: #0f172a; font-weight: 600;
            border: none; border-radius: 8px; transition: all 0.15s;
        }
        .stButton button:hover { background: #e67e22; transform: translateY(-1px); }
        hr { border-color: #1e293b; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)

# ====================== Constants ======================
SHEET_ID   = "1q_q9QGYHm0w7Z5nnO1Uq4NKLW1SoQCf5stbAMKoT3FE"
DAILY_WS   = "daily"
WEEKLY_WS  = "weekly"
ECONOMY_WS = "ECONOMY"
NEWS_WS    = "News"

currencies = ["USD", "CAD", "EUR", "GBP", "CHF", "AUD", "NZD", "JPY"]

pairs = [
    "EURUSD","EURGBP","EURAUD","EURNZD","EURCAD","EURCHF","EURJPY",
    "GBPUSD","GBPAUD","GBPNZD","GBPCAD","GBPCHF","GBPJPY",
    "AUDUSD","AUDNZD","AUDCAD","AUDCHF","AUDJPY",
    "NZDUSD","NZDCAD","NZDCHF","NZDJPY",
    "USDCAD","USDCHF","USDJPY",
    "CADCHF","CADJPY","CHFJPY"
]

currency_flags = {
    "USD":"🇺🇸","EUR":"🇪🇺","GBP":"🇬🇧","JPY":"🇯🇵",
    "CHF":"🇨🇭","CAD":"🇨🇦","AUD":"🇦🇺","NZD":"🇳🇿"
}

# حالات العملة وخصائصها
STATE_CONFIG = {
    "STRONG TREND": {"icon":"💥","color":"#059669","priority":5},
    "TREND":        {"icon":"📈","color":"#10b981","priority":4},
    "WEAK TREND":   {"icon":"⚠️","color":"#f97316","priority":3},
    "RANGE":        {"icon":"🔄","color":"#64748b","priority":2},
    "REVERSAL":     {"icon":"💣","color":"#ef4444","priority":1},
}

# أولوية السيناريوهات
SCENARIO_CONFIG = {
    ("STRONG TREND","STRONG TREND","opposite"): {"label":"💥 Strong vs Strong","confidence":80,"trade":True},
    ("STRONG TREND","REVERSAL",    "opposite"): {"label":"🚀 Strong vs Reversal","confidence":75,"trade":True},
    ("TREND",       "REVERSAL",    "opposite"): {"label":"⚡ Trend vs Reversal","confidence":70,"trade":True},
    ("STRONG TREND","WEAK TREND",  "opposite"): {"label":"📊 Strong vs Weak","confidence":65,"trade":True},
    ("TREND",       "WEAK TREND",  "opposite"): {"label":"📊 Trend vs Weak","confidence":60,"trade":True},
    ("STRONG TREND","STRONG TREND","same"):     {"label":"❌ Strong vs Strong (Same)","confidence":0,"trade":False},
    ("WEAK TREND",  "WEAK TREND",  "any"):      {"label":"❌ Weak vs Weak","confidence":0,"trade":False},
    ("REVERSAL",    "REVERSAL",    "any"):      {"label":"❌ Reversal vs Reversal","confidence":0,"trade":False},
}

# ====================== Load Functions ======================
def load_data(worksheet_name: str, date_col: str = "Date"):
    client = get_gspread_client()
    sheet  = client.open_by_key(SHEET_ID)
    ws     = sheet.worksheet(worksheet_name)
    data   = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=[date_col] + currencies)
    df = pd.DataFrame(data)
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date
    df = df.dropna(subset=[date_col])
    return df.sort_values(date_col).reset_index(drop=True)

def load_news_data():
    client = get_gspread_client()
    sheet  = client.open_by_key(SHEET_ID)
    try:
        ws   = sheet.worksheet(NEWS_WS)
        data = ws.get_all_records()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        if 'Shock' in df.columns:
            df['Shock'] = pd.to_numeric(df['Shock'], errors='coerce')
        return df
    except Exception as e:
        st.warning(f"Could not load News: {e}")
        return pd.DataFrame()

# ====================== Helpers ======================
def get_row_for_date(df, date_col, sel_date):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.date
    row = df[df[date_col] == sel_date]
    if row.empty:
        return None, None
    idx  = row.index[0]
    curr = row.iloc[0]
    prev = df.iloc[idx - 1] if idx > 0 else None
    return curr, prev

def get_weekly_row(db_weekly, selected_date):
    db = db_weekly.copy()
    db['Week_Start'] = pd.to_datetime(db['Week_Start']).dt.date
    available = db[db['Week_Start'] <= selected_date]
    if available.empty:
        return None, None
    curr = available.iloc[-1]
    prev = available.iloc[-2] if len(available) >= 2 else None
    return curr, prev

def safe_float(val):
    try:
        if val is None or str(val).strip() == '':
            return None
        return float(val)
    except:
        return None

def html_table(headers, rows_html, height=400):
    h = "".join([f"<th>{x}</th>" for x in headers])
    t = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
    <style>
        body{{margin:0;padding:0;background:transparent;
             font-family:-apple-system,BlinkMacSystemFont,sans-serif;}}
        table{{width:100%;border-collapse:collapse;
               background:linear-gradient(135deg,#0f172a,#1e293b);
               border-radius:12px;overflow:hidden;}}
        th{{background:#1e293b;color:#f1c40f;padding:12px 10px;
            text-align:left;font-size:12px;font-weight:600;
            border-bottom:2px solid #f1c40f;white-space:nowrap;}}
        tr:hover{{background:rgba(241,196,15,0.04);}}
        td{{padding:11px 10px;}}
    </style></head><body>
    <table><thead><tr>{h}</tr></thead>
    <tbody>{rows_html}</tbody></table></body></html>"""
    st.components.v1.html(t, height=height, scrolling=True)

def summary_cards(buy, sell, mid_label="Total", mid_val=None):
    mid = mid_val if mid_val is not None else buy + sell
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div style='background:rgba(16,185,129,0.15);border:1px solid #10b981;
            border-radius:12px;padding:16px;text-align:center;'>
            <div style='font-size:12px;color:#94a3b8;'>Bullish / BUY</div>
            <div style='font-size:36px;font-weight:bold;color:#10b981;'>{buy}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style='background:rgba(239,68,68,0.15);border:1px solid #ef4444;
            border-radius:12px;padding:16px;text-align:center;'>
            <div style='font-size:12px;color:#94a3b8;'>Bearish / SELL</div>
            <div style='font-size:36px;font-weight:bold;color:#ef4444;'>{sell}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div style='background:rgba(241,196,15,0.15);border:1px solid #f1c40f;
            border-radius:12px;padding:16px;text-align:center;'>
            <div style='font-size:12px;color:#94a3b8;'>{mid_label}</div>
            <div style='font-size:36px;font-weight:bold;color:#f1c40f;'>{mid}</div>
        </div>""", unsafe_allow_html=True)

# ====================== Date Selector ======================
def render_date_selector(db_daily):
    db = db_daily.copy()
    db['Date'] = pd.to_datetime(db['Date']).dt.date
    all_dates = db['Date'].sort_values(ascending=False).tolist()
    options, date_map = [], {}
    for d in all_dates:
        ds    = d.strftime("%Y-%m-%d")
        label = f"📅 {ds}  ·  Latest" if d == all_dates[0] else f"📅 {ds}"
        options.append(label)
        date_map[label] = d
    st.markdown("""<div style='background:#0f172a;border:1px solid rgba(241,196,15,0.25);
        border-radius:10px;padding:10px 16px;margin-bottom:1.2rem;'>
        <span style='color:#f1c40f;font-size:13px;font-weight:600;'>DATE</span>
        <span style='color:#334155;font-size:11px;'> | </span>
        <span style='color:#64748b;font-size:11px;'>Choose The Date</span>
    </div>""", unsafe_allow_html=True)
    _,c2,_ = st.columns([1,2,1])
    with c2:
        sel = st.selectbox("", options=options, index=0,
                           key="global_date_selector", label_visibility="collapsed")
    selected = date_map[sel]
    st.session_state['selected_date'] = selected
    return selected

# ══════════════════════════════════════════════════════════════
# ENGINE 1 — Economic Direction per Currency
# ══════════════════════════════════════════════════════════════
def calc_eco_direction(currency, db_economy, selected_date, lookback=12):
    """
    يحسب الاتجاه الاقتصادي للعملة
    Returns: direction (+/-/=), current_val, prev_val, range_high, range_low
    """
    if db_economy.empty or currency not in db_economy.columns:
        return "=", None, None, None, None

    db = db_economy.copy()
    db['Date'] = pd.to_datetime(db['Date']).dt.date
    history = db[db['Date'] <= selected_date].sort_values('Date').reset_index(drop=True)

    if len(history) < 2:
        return "=", None, None, None, None

    curr_val = safe_float(history.iloc[-1][currency])
    prev_val = safe_float(history.iloc[-2][currency])

    lookback_data = history.iloc[-(lookback+1):-1]
    range_high = lookback_data[currency].max() if not lookback_data.empty else None
    range_low  = lookback_data[currency].min() if not lookback_data.empty else None

    if curr_val is None or prev_val is None:
        return "=", curr_val, prev_val, range_high, range_low

    if curr_val > prev_val:
        return "+", curr_val, prev_val, range_high, range_low
    elif curr_val < prev_val:
        return "-", curr_val, prev_val, range_high, range_low
    else:
        return "=", curr_val, prev_val, range_high, range_low

# ══════════════════════════════════════════════════════════════
# ENGINE 2 — Event Direction per Currency
# ══════════════════════════════════════════════════════════════
def calc_event_directions(currency, db_news, selected_date):
    """
    يحسب اتجاه التوقعات واتجاه النتيجة بالأوزان
    Returns:
        forecast_dir: + / = / -
        actual_dir:   + / = / -
        has_events:   bool
        details:      list
    """
    if db_news.empty:
        return "=", "=", False, []

    db = db_news.copy()
    db['Date'] = pd.to_datetime(db['Date']).dt.date
    today = db[(db['Date'] == selected_date) & (db['Currency'] == currency)]

    if today.empty:
        return "=", "=", False, []

    weights     = {'High': 0.5, 'Moderate': 0.3, 'Low': 0.2}
    fore_score  = 0.0
    actual_score = 0.0
    details     = []

    for _, evt in today.iterrows():
        w        = weights.get(evt.get('Importance','Low'), 0.2)
        forecast = safe_float(evt.get('Forecast'))
        previous = safe_float(evt.get('Previous'))
        actual   = safe_float(evt.get('Actual'))

        # Forecast vs Previous
        f_dir = "="
        if forecast is not None and previous is not None:
            if forecast > previous:
                fore_score += w
                f_dir = "+"
            elif forecast < previous:
                fore_score -= w
                f_dir = "-"

        # Actual vs Forecast
        a_dir = "="
        if actual is not None and forecast is not None:
            if actual > forecast:
                actual_score += w
                a_dir = "+"
            elif actual < forecast:
                actual_score -= w
                a_dir = "-"

        details.append({
            'time':       evt.get('TimeOnly','—'),
            'importance': evt.get('Importance','Low'),
            'f_dir':      f_dir,
            'a_dir':      a_dir,
            'forecast':   forecast,
            'previous':   previous,
            'actual':     actual,
        })

    forecast_dir = "+" if fore_score > 0 else "-" if fore_score < 0 else "="
    actual_dir   = "+" if actual_score > 0 else "-" if actual_score < 0 else "="

    return forecast_dir, actual_dir, True, details

# ══════════════════════════════════════════════════════════════
# ENGINE 3 — Currency State
# ══════════════════════════════════════════════════════════════
def calc_currency_state(currency, db_economy, db_news, selected_date, lookback=12):
    """
    يجمع الـ 3 مدخلات ويحدد الحالة النهائية للعملة

    Returns dict:
        state:        STRONG TREND / TREND / WEAK TREND / RANGE / REVERSAL
        direction:    UP / DOWN / NEUTRAL
        eco_dir:      + / - / =
        fore_dir:     + / - / =
        actual_dir:   + / - / =
        pattern:      (eco, fore, actual)
        has_events:   bool
        details:      event details
        eco_val / eco_high / eco_low
    """
    eco_dir, eco_val, eco_prev, eco_high, eco_low = calc_eco_direction(
        currency, db_economy, selected_date, lookback
    )
    fore_dir, actual_dir, has_events, details = calc_event_directions(
        currency, db_news, selected_date
    )

    pattern = (eco_dir, fore_dir, actual_dir)

    # تحديد الحالة بناءً على الـ pattern
    STRONG_PATTERNS = {
        ("+","+","+"),("+","=","+"),("+","+","="),
        ("-","-","-"),("-","=","-"),("-","-","="),
    }
    TREND_PATTERNS = {
        ("+","+","="),("+","=","+"),("+","=","="),
        ("-","-","="),("-","=","-"),("-","=","="),
    }
    WEAK_PATTERNS = {
        ("+","+","-"),("+","=","-"),
        ("-","-","+"),(("-","=","+")),
    }
    RANGE_PATTERNS = {
        ("+","=","="),("+","-","="),
        ("-","=","="),("-","+","="),
        ("=","=","="),("=","+","="),("=","-","="),
        ("=","=","+"),(("=","=","-")),
    }
    REVERSAL_PATTERNS = {
        ("+","-","-"),("+","-","+"),
        ("-","+","+"),(("-","+","-")),
    }

    if pattern in STRONG_PATTERNS:
        state = "STRONG TREND"
    elif pattern in TREND_PATTERNS:
        state = "TREND"
    elif pattern in WEAK_PATTERNS:
        state = "WEAK TREND"
    elif pattern in REVERSAL_PATTERNS:
        state = "REVERSAL"
    else:
        state = "RANGE"

    # الاتجاه العام
    if eco_dir == "+":
        direction = "UP"
    elif eco_dir == "-":
        direction = "DOWN"
    else:
        direction = "NEUTRAL"

    return {
        'currency':   currency,
        'state':      state,
        'direction':  direction,
        'eco_dir':    eco_dir,
        'fore_dir':   fore_dir,
        'actual_dir': actual_dir,
        'pattern':    pattern,
        'has_events': has_events,
        'details':    details,
        'eco_val':    eco_val,
        'eco_high':   eco_high,
        'eco_low':    eco_low,
    }

# ══════════════════════════════════════════════════════════════
# ENGINE 4 — Pair Opportunity
# ══════════════════════════════════════════════════════════════
def calc_pair_opportunity(base_state, quote_state):
    """
    يقارن حالة العملتين ويحدد نوع الفرصة والأولوية

    Returns:
        scenario_label: وصف السيناريو
        confidence:     نسبة الثقة (0 = تجنب)
        direction:      BUY / SELL / AVOID
        priority:       رقم للترتيب
    """
    b_state = base_state['state']
    q_state = quote_state['state']
    b_dir   = base_state['direction']
    q_dir   = quote_state['direction']

    # هل الاتجاهين عكس بعض؟
    if b_dir == "UP" and q_dir == "DOWN":
        rel = "opposite"
        trade_dir = "BUY"
    elif b_dir == "DOWN" and q_dir == "UP":
        rel = "opposite"
        trade_dir = "SELL"
    elif b_dir == "UP" and q_dir in ("NEUTRAL","UP"):
        rel = "same"
        trade_dir = "BUY" if b_dir == "UP" else "SELL"
    elif b_dir == "DOWN" and q_dir in ("NEUTRAL","DOWN"):
        rel = "same"
        trade_dir = "SELL"
    else:
        rel = "any"
        trade_dir = "AVOID"

    # ترتيب الحالات للمقارنة (الأقوى أولاً)
    state_order = ["STRONG TREND","REVERSAL","TREND","WEAK TREND","RANGE"]

    def sort_states(s1, s2):
        """يرتب الحالتين بحيث الأقوى أولاً"""
        i1 = state_order.index(s1) if s1 in state_order else 99
        i2 = state_order.index(s2) if s2 in state_order else 99
        if i1 <= i2:
            return s1, s2, False
        return s2, s1, True  # True = تم العكس

    s1, s2, swapped = sort_states(b_state, q_state)

    # البحث في SCENARIO_CONFIG
    key1 = (s1, s2, rel)
    key2 = (s1, s2, "any")
    key3 = (s2, s1, rel)
    key4 = (s2, s1, "any")

    scenario = None
    for key in [key1, key2, key3, key4]:
        if key in SCENARIO_CONFIG:
            scenario = SCENARIO_CONFIG[key]
            break

    if scenario is None:
        # حكم عام بناءً على الأولوية
        b_priority = STATE_CONFIG.get(b_state, {}).get('priority', 0)
        q_priority = STATE_CONFIG.get(q_state, {}).get('priority', 0)
        total_priority = b_priority + q_priority

        if rel == "opposite" and total_priority >= 8:
            scenario = {"label": f"📊 {b_state} vs {q_state}", "confidence": 60, "trade": True}
        elif rel == "opposite" and total_priority >= 5:
            scenario = {"label": f"📊 {b_state} vs {q_state}", "confidence": 55, "trade": True}
        else:
            scenario = {"label": f"🔄 {b_state} vs {q_state}", "confidence": 0, "trade": False}

    if not scenario['trade']:
        trade_dir = "AVOID"

    return {
        'scenario':   scenario['label'],
        'confidence': scenario['confidence'],
        'direction':  trade_dir,
        'rel':        rel,
    }

# ══════════════════════════════════════════════════════════════
# ENGINE 5 — Scalp Signal
# ══════════════════════════════════════════════════════════════
def calc_scalp_signal(pair, daily_curr, weekly_curr):
    """
    يحسب حالة السكالب والتسارع

    Returns:
        scalp_state: STRONG TREND / WEAK TREND / RANGE / REVERSAL SETUP
        direction:   UP / DOWN / NEUTRAL
        acceleration
        daily_score
        weekly_score
    """
    base, quote = pair[:3], pair[3:]

    b_d = safe_float(daily_curr.get(base))  if daily_curr  is not None else None
    q_d = safe_float(daily_curr.get(quote)) if daily_curr  is not None else None
    b_w = safe_float(weekly_curr.get(base)) if weekly_curr is not None else None
    q_w = safe_float(weekly_curr.get(quote))if weekly_curr is not None else None

    if any(x is None for x in [b_d, q_d, b_w, q_w]):
        return "RANGE", "NEUTRAL", 0, 0, 0

    daily_score  = b_d - q_d
    weekly_score = b_w - q_w
    acceleration = daily_score - weekly_score

    weekly_up   = weekly_score > 0
    weekly_down = weekly_score < 0
    acc_pos     = acceleration > 0
    acc_neg     = acceleration < 0

    if weekly_up and acc_pos:
        return "STRONG TREND", "UP",      round(acceleration,2), round(daily_score,2), round(weekly_score,2)
    elif weekly_up and acc_neg:
        return "WEAK TREND",   "UP",      round(acceleration,2), round(daily_score,2), round(weekly_score,2)
    elif weekly_down and acc_neg:
        return "STRONG TREND", "DOWN",    round(acceleration,2), round(daily_score,2), round(weekly_score,2)
    elif weekly_down and acc_pos:
        return "REVERSAL SETUP","DOWN",   round(acceleration,2), round(daily_score,2), round(weekly_score,2)
    else:
        return "RANGE",        "NEUTRAL", round(acceleration,2), round(daily_score,2), round(weekly_score,2)

# ══════════════════════════════════════════════════════════════
# ENGINE 6 — Final Decision
# ══════════════════════════════════════════════════════════════
def calc_final_decision(pair_opportunity, scalp_state, scalp_direction, eco_direction):
    """
    يربط فرصة الزوج بحالة السكالب

    منطق القرار:
    - Scalp STRONG TREND يوافق eco_direction → تأكيد كامل
    - Scalp WEAK TREND → تخفيض الثقة
    - Scalp REVERSAL SETUP → تحذير
    - Scalp RANGE → تجنب

    Returns:
        final_signal:     BUY / SELL / AVOID
        final_confidence: نسبة الثقة النهائية
        scalp_note:       ملاحظة السكالب
    """
    base_conf  = pair_opportunity['confidence']
    base_dir   = pair_opportunity['direction']

    if base_dir == "AVOID" or base_conf == 0:
        return "AVOID", 0, "❌ No opportunity"

    if scalp_state == "RANGE":
        return "AVOID", 0, "❌ Scalp: Range — No Entry"

    # توافق اتجاه السكالب مع الـ eco
    scalp_confirms = (
        (base_dir == "BUY"  and scalp_direction == "UP") or
        (base_dir == "SELL" and scalp_direction == "DOWN")
    )

    if scalp_state == "STRONG TREND" and scalp_confirms:
        final_conf = base_conf
        note       = "✅ Scalp: Strong Confirm"
    elif scalp_state == "TREND" and scalp_confirms:
        final_conf = max(base_conf - 5, 60)
        note       = "✅ Scalp: Confirm"
    elif scalp_state == "WEAK TREND" and scalp_confirms:
        final_conf = max(base_conf - 10, 55)
        note       = "⚠️ Scalp: Weak Confirm"
    elif scalp_state == "REVERSAL SETUP":
        final_conf = max(base_conf - 15, 50)
        note       = "💣 Scalp: Reversal Warning"
    else:
        # السكالب مخالف
        final_conf = max(base_conf - 20, 50)
        note       = "⚠️ Scalp: Against Direction"

    return base_dir, final_conf, note

# ══════════════════════════════════════════════════════════════
# TAB 1 — Currency States
# ══════════════════════════════════════════════════════════════
def render_states_tab(db_economy, db_news, selected_date):
    if db_economy.empty:
        st.info("📊 يرجى إدخال بيانات ECONOMY أولاً")
        return

    states = {}
    for curr in currencies:
        states[curr] = calc_currency_state(curr, db_economy, db_news, selected_date)

    # ملخص
    up_count   = sum(1 for s in states.values() if s['direction'] == "UP")
    down_count = sum(1 for s in states.values() if s['direction'] == "DOWN")
    summary_cards(up_count, down_count, "Neutral",
                  sum(1 for s in states.values() if s['direction'] == "NEUTRAL"))
    st.markdown("---")

    # كروت العملات
    st.markdown('<div class="section-header">💱 Currency State Analysis</div>', unsafe_allow_html=True)

    sorted_states = sorted(states.values(),
                           key=lambda x: STATE_CONFIG.get(x['state'],{}).get('priority',0),
                           reverse=True)

    cols = st.columns(4)
    for idx, s in enumerate(sorted_states):
        with cols[idx % 4]:
            cfg      = STATE_CONFIG.get(s['state'], {"icon":"❓","color":"#64748b"})
            flag     = currency_flags.get(s['currency'], "")
            dir_icon = "📈" if s['direction']=="UP" else "📉" if s['direction']=="DOWN" else "➖"
            dir_col  = "#10b981" if s['direction']=="UP" else "#ef4444" if s['direction']=="DOWN" else "#64748b"

            # pattern display
            p = s['pattern']
            def dir_badge(d):
                if d == "+": return f'<span style="color:#10b981;font-weight:700;">+</span>'
                if d == "-": return f'<span style="color:#ef4444;font-weight:700;">-</span>'
                return f'<span style="color:#64748b;font-weight:700;">=</span>'

            pattern_html = f"Eco:{dir_badge(p[0])} | News:{dir_badge(p[1])} | Result:{dir_badge(p[2])}"

            st.markdown(f"""
            <div style="background:#0f172a;border:2px solid {cfg['color']}40;
                        border-top:3px solid {cfg['color']};
                        border-radius:14px;padding:16px;margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:22px;">{flag}</span>
                        <span style="font-size:17px;font-weight:700;color:#e2e8f0;">{s['currency']}</span>
                    </div>
                    <span style="font-size:20px;">{cfg['icon']}</span>
                </div>
                <div style="font-size:13px;font-weight:700;color:{cfg['color']};margin-bottom:8px;">
                    {s['state']}
                </div>
                <div style="font-size:12px;color:{dir_col};margin-bottom:8px;">
                    {dir_icon} {s['direction']}
                </div>
                <div style="font-size:11px;color:#64748b;">{pattern_html}</div>
                {'<div style="font-size:10px;color:#334155;margin-top:6px;">No events today</div>' if not s['has_events'] else ''}
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # جدول تفصيلي
    st.markdown('<div class="section-header">📋 Detailed State Table</div>', unsafe_allow_html=True)

    def build_state_rows():
        rows = ""
        for s in sorted_states:
            cfg     = STATE_CONFIG.get(s['state'], {"icon":"❓","color":"#64748b"})
            flag    = currency_flags.get(s['currency'], "")
            dir_col = "#10b981" if s['direction']=="UP" else "#ef4444" if s['direction']=="DOWN" else "#64748b"

            eco_html  = f'<span style="color:{"#10b981" if s["eco_dir"]=="+" else "#ef4444" if s["eco_dir"]=="-" else "#64748b"};">{s["eco_dir"]}</span>'
            fore_html = f'<span style="color:{"#10b981" if s["fore_dir"]=="+" else "#ef4444" if s["fore_dir"]=="-" else "#64748b"};">{s["fore_dir"]}</span>'
            act_html  = f'<span style="color:{"#10b981" if s["actual_dir"]=="+" else "#ef4444" if s["actual_dir"]=="-" else "#64748b"};">{s["actual_dir"]}</span>'

            eco_val_str = f"{s['eco_val']:.2f}" if s['eco_val'] is not None else "—"

            rows += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="font-weight:700;color:#e2e8f0;">{flag} {s['currency']}</td>
                <td style="color:{cfg['color']};font-weight:600;">{cfg['icon']} {s['state']}</td>
                <td style="color:{dir_col};font-weight:600;">{s['direction']}</td>
                <td style="text-align:center;">{eco_html}</td>
                <td style="text-align:center;">{fore_html}</td>
                <td style="text-align:center;">{act_html}</td>
                <td style="color:#64748b;font-size:12px;">{eco_val_str}</td>
                <td style="color:#475569;font-size:11px;">{'✅' if s['has_events'] else '—'}</td>
            </tr>"""
        return rows

    html_table(
        ["Currency","State","Direction","Eco","Forecast","Actual","Eco Val","Events"],
        build_state_rows(),
        height=max(250, len(currencies)*52+60)
    )

# ══════════════════════════════════════════════════════════════
# TAB 2 — Scalping Signals
# ══════════════════════════════════════════════════════════════
def render_scalping_tab(db_daily, db_weekly, selected_date):
    if db_daily.empty or db_weekly.empty:
        st.info("📊 يرجى إدخال بيانات Daily و Weekly أولاً")
        return

    daily_curr,  _ = get_row_for_date(db_daily,  'Date', selected_date)
    weekly_curr, _ = get_weekly_row(db_weekly, selected_date)

    if daily_curr is None:
        st.error(f"❌ لا توجد بيانات يومية للتاريخ {selected_date}")
        return
    if weekly_curr is None:
        st.error("❌ لا توجد بيانات أسبوعية")
        return

    results = []
    for pair in pairs:
        scalp_state, scalp_dir, acc, d_score, w_score = calc_scalp_signal(
            pair, daily_curr, weekly_curr
        )
        if scalp_state == "RANGE":
            continue
        results.append({
            'pair':        pair,
            'scalp_state': scalp_state,
            'direction':   scalp_dir,
            'acceleration':acc,
            'daily_score': d_score,
            'weekly_score':w_score,
        })

    df = pd.DataFrame(results)
    if df.empty:
        st.info("لا توجد إشارات سكالب للتاريخ المختار")
        return

    df = df.reindex(df['acceleration'].abs().sort_values(ascending=False).index)

    up_count   = len(df[df['direction']=="UP"])
    down_count = len(df[df['direction']=="DOWN"])
    summary_cards(up_count, down_count, "Total", len(df))
    st.markdown("---")

    state_colors = {
        "STRONG TREND":  "#059669",
        "WEAK TREND":    "#f97316",
        "REVERSAL SETUP":"#ef4444",
        "RANGE":         "#64748b",
    }
    state_icons = {
        "STRONG TREND":  "💥",
        "WEAK TREND":    "⚠️",
        "REVERSAL SETUP":"💣",
        "RANGE":         "🔄",
    }

    def build_scalp_rows(df):
        rows = ""
        for _, row in df.iterrows():
            sc      = state_colors.get(row['scalp_state'],"#64748b")
            icon    = state_icons.get(row['scalp_state'],"")
            dir_col = "#10b981" if row['direction']=="UP" else "#ef4444" if row['direction']=="DOWN" else "#64748b"
            dir_ico = "📈" if row['direction']=="UP" else "📉" if row['direction']=="DOWN" else "➖"
            acc_col = "#10b981" if row['acceleration']>0 else "#ef4444"

            rows += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="font-weight:700;color:#e2e8f0;font-size:15px;">{row['pair']}</td>
                <td style="color:{sc};font-weight:700;">{icon} {row['scalp_state']}</td>
                <td style="color:{dir_col};font-weight:600;">{dir_ico} {row['direction']}</td>
                <td style="color:{acc_col};font-weight:700;">{row['acceleration']:+.2f}</td>
                <td style="color:#e2e8f0;">{row['daily_score']:+.2f}</td>
                <td style="color:#e2e8f0;">{row['weekly_score']:+.2f}</td>
            </tr>"""
        return rows

    html_table(
        ["Pair","Scalp State","Direction","⚡ Acceleration","📅 Daily","📆 Weekly"],
        build_scalp_rows(df),
        height=max(200, len(df)*52+60)
    )

# ══════════════════════════════════════════════════════════════
# TAB 3 — Market Events
# ══════════════════════════════════════════════════════════════
def render_events_tab(db_news, selected_date):
    if db_news.empty:
        st.info("📊 لا توجد بيانات أحداث")
        return

    db = db_news.copy()
    db['Date'] = pd.to_datetime(db['Date']).dt.date
    today = db[db['Date'] == selected_date]

    if today.empty:
        st.info(f"📭 لا توجد أحداث للتاريخ {selected_date}")
        return

    active_currencies = today['Currency'].unique()

    # حساب اتجاه كل عملة
    currency_data = []
    for curr in active_currencies:
        f_dir, a_dir, _, details = calc_event_directions(curr, db_news, selected_date)
        currency_data.append({
            'currency': curr,
            'fore_dir': f_dir,
            'actual_dir': a_dir,
            'details': details,
        })

    bull = sum(1 for c in currency_data if c['fore_dir']=="+")
    bear = sum(1 for c in currency_data if c['fore_dir']=="-")
    summary_cards(bull, bear, "Total Events", len(today))
    st.markdown("---")

    # كروت العملات
    st.markdown('<div class="section-header">🎯 Active Currencies</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(currency_data),4))
    for idx, cd in enumerate(currency_data):
        with cols[idx%4]:
            flag     = currency_flags.get(cd['currency'],"")
            fc       = "#10b981" if cd['fore_dir']=="+" else "#ef4444" if cd['fore_dir']=="-" else "#64748b"
            ac       = "#10b981" if cd['actual_dir']=="+" else "#ef4444" if cd['actual_dir']=="-" else "#64748b"
            f_label  = "Bullish" if cd['fore_dir']=="+" else "Bearish" if cd['fore_dir']=="-" else "Neutral"
            a_label  = "Positive" if cd['actual_dir']=="+" else "Negative" if cd['actual_dir']=="-" else "Awaiting"
            st.markdown(f"""
            <div style="background:#0f172a;border:2px solid {fc};border-radius:14px;
                        padding:16px;text-align:center;margin-bottom:10px;">
                <div style="font-size:26px;">{flag}</div>
                <div style="font-size:17px;font-weight:700;color:#e2e8f0;">{cd['currency']}</div>
                <div style="margin-top:8px;font-size:12px;color:#94a3b8;">
                    Forecast: <span style="color:{fc};font-weight:700;">{f_label}</span>
                </div>
                <div style="font-size:12px;color:#94a3b8;">
                    Result: <span style="color:{ac};font-weight:700;">{a_label}</span>
                </div>
                <div style="font-size:11px;color:#475569;margin-top:4px;">{len(cd['details'])} events</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # جدول الأحداث
    st.markdown('<div class="section-header">📋 Events Timeline</div>', unsafe_allow_html=True)
    sorted_today = today.sort_values('TimeOnly') if 'TimeOnly' in today.columns else today

    def build_event_rows(df):
        rows = ""
        for _, evt in df.iterrows():
            imp      = evt.get('Importance','Low')
            imp_icon = {"High":"🔴","Moderate":"🟡","Low":"🟢"}.get(imp,"⚪")
            fc  = safe_float(evt.get('Forecast'))
            prv = safe_float(evt.get('Previous'))
            act = safe_float(evt.get('Actual'))

            fc_col,fc_ico   = '#e2e8f0',''
            act_col,act_ico = '#e2e8f0',''

            if fc is not None and prv is not None:
                if fc>prv:  fc_col,fc_ico  = '#10b981','📈'
                elif fc<prv:fc_col,fc_ico  = '#ef4444','📉'

            if act is not None and fc is not None:
                if act>fc:  act_col,act_ico = '#10b981','✅'
                elif act<fc:act_col,act_ico = '#ef4444','❌'

            fc_s  = str(evt['Forecast']) if pd.notna(evt.get('Forecast')) and str(evt.get('Forecast')).strip()!='' else '—'
            prv_s = str(evt['Previous']) if pd.notna(evt.get('Previous')) and str(evt.get('Previous')).strip()!='' else '—'
            act_s = str(evt['Actual'])   if pd.notna(evt.get('Actual'))   and str(evt.get('Actual')).strip()!=''   else '—'

            rows += f"""
            <tr style="border-bottom:1px solid #334155;">
                <td style="color:white;">{imp_icon} {evt.get('TimeOnly','—')}</td>
                <td style="font-weight:bold;color:white;">{evt.get('Currency','—')}</td>
                <td style="color:#94a3b8;font-size:12px;">{str(evt.get('EventName','—'))[:45]}</td>
                <td style="color:{fc_col};font-weight:bold;">{fc_ico} {fc_s}</td>
                <td style="color:#64748b;">{prv_s}</td>
                <td style="color:{act_col};font-weight:bold;">{act_ico} {act_s}</td>
            </tr>"""
        return rows

    html_table(
        ["Time","Curr","Event","Forecast","Previous","Actual"],
        build_event_rows(sorted_today),
        height=min(500, len(sorted_today)*45+60)
    )

# ══════════════════════════════════════════════════════════════
# TAB 4 — Confluence (القرار النهائي)
# ══════════════════════════════════════════════════════════════
def render_confluence_tab(db_daily, db_economy, db_news, db_weekly, selected_date):
    if db_daily.empty or db_economy.empty:
        st.info("📊 يرجى إدخال بيانات أولاً")
        return

    daily_curr,  _ = get_row_for_date(db_daily,  'Date', selected_date)
    weekly_curr, _ = get_weekly_row(db_weekly, selected_date)

    if daily_curr is None:
        st.error(f"❌ لا توجد بيانات للتاريخ {selected_date}")
        return

    # حساب حالة كل عملة
    states = {}
    for curr in currencies:
        states[curr] = calc_currency_state(curr, db_economy, db_news, selected_date)

    results = []
    for pair in pairs:
        base, quote = pair[:3], pair[3:]
        base_state  = states[base]
        quote_state = states[quote]

        # فرصة الزوج
        opportunity = calc_pair_opportunity(base_state, quote_state)
        if opportunity['confidence'] == 0:
            continue

        # حالة السكالب
        scalp_state, scalp_dir, acc, d_score, w_score = calc_scalp_signal(
            pair, daily_curr, weekly_curr
        )

        # القرار النهائي
        final_sig, final_conf, scalp_note = calc_final_decision(
            opportunity, scalp_state, scalp_dir, base_state['direction']
        )

        if final_sig == "AVOID":
            continue

        results.append({
            'pair':         pair,
            'signal':       final_sig,
            'confidence':   final_conf,
            'scenario':     opportunity['scenario'],
            'scalp_state':  scalp_state,
            'scalp_note':   scalp_note,
            'acceleration': acc,
            'base_state':   base_state['state'],
            'quote_state':  quote_state['state'],
            'base_dir':     base_state['direction'],
            'quote_dir':    quote_state['direction'],
            'base_pattern': base_state['pattern'],
            'quote_pattern':quote_state['pattern'],
        })

    df = pd.DataFrame(results)
    if df.empty:
        st.info("لا توجد إشارات نهائية للتاريخ المختار")
        return

    df = df.sort_values(['confidence'], ascending=False).reset_index(drop=True)

    buy_count  = len(df[df['signal']=="BUY"])
    sell_count = len(df[df['signal']=="SELL"])

    # نسب الثقة
    conf_bands = {80:0, 75:0, 70:0, 65:0, 60:0}
    for c in df['confidence']:
        if c >= 80:   conf_bands[80] += 1
        elif c >= 75: conf_bands[75] += 1
        elif c >= 70: conf_bands[70] += 1
        elif c >= 65: conf_bands[65] += 1
        else:         conf_bands[60] += 1

    summary_cards(buy_count, sell_count)
    st.markdown("---")

    cols = st.columns(5)
    for col, (pct, count), color in zip(cols, conf_bands.items(),
        ['#059669','#10b981','#f1c40f','#f97316','#8b5cf6']):
        with col:
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.2);border:1px solid {color};
                        border-radius:12px;padding:14px;text-align:center;'>
                <div style='font-size:24px;font-weight:bold;color:{color};'>{count}</div>
                <div style='font-size:13px;font-weight:bold;color:{color};'>{pct}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # الجدول النهائي
    conf_colors = {80:'#059669',75:'#10b981',70:'#f1c40f',65:'#f97316',60:'#8b5cf6'}
    state_icons_map = {
        "STRONG TREND":"💥","TREND":"📈","WEAK TREND":"⚠️",
        "RANGE":"🔄","REVERSAL":"💣","REVERSAL SETUP":"💣"
    }

    def build_confluence_rows(df):
        rows = ""
        for _, row in df.iterrows():
            sig_col  = "#10b981" if row['signal']=="BUY" else "#ef4444"
            sig_bg   = "rgba(16,185,129,0.15)" if row['signal']=="BUY" else "rgba(239,68,68,0.15)"
            cc       = conf_colors.get(row['confidence'],'#64748b')

            b_cfg    = STATE_CONFIG.get(row['base_state'],  {"color":"#64748b"})
            q_cfg    = STATE_CONFIG.get(row['quote_state'], {"color":"#64748b"})
            b_icon   = state_icons_map.get(row['base_state'],  "")
            q_icon   = state_icons_map.get(row['quote_state'], "")

            def pattern_str(p):
                icons = {"+":"<span style='color:#10b981'>+</span>",
                         "-":"<span style='color:#ef4444'>-</span>",
                         "=":"<span style='color:#64748b'>=</span>"}
                return f"{icons.get(p[0],'?')}{icons.get(p[1],'?')}{icons.get(p[2],'?')}"

            acc_col = "#10b981" if row['acceleration']>0 else "#ef4444"

            rows += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="font-weight:700;color:#e2e8f0;font-size:14px;">{row['pair']}</td>
                <td>
                    <span style="background:{sig_bg};color:{sig_col};border:1px solid {sig_col};
                                 padding:5px 12px;border-radius:20px;font-weight:700;">
                        {row['signal']}
                    </span>
                </td>
                <td>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <div style="background:#1e293b;border-radius:4px;height:6px;width:50px;overflow:hidden;">
                            <div style="background:{cc};height:100%;width:{row['confidence']}%;border-radius:4px;"></div>
                        </div>
                        <span style="color:{cc};font-weight:700;font-size:13px;">{row['confidence']}%</span>
                    </div>
                </td>
                <td style="font-size:12px;color:#94a3b8;">{row['scenario']}</td>
                <td style="font-size:12px;">
                    <span style="color:{b_cfg['color']};">{b_icon} {row['base_state']}</span>
                    {pattern_str(row['base_pattern'])}
                </td>
                <td style="font-size:12px;">
                    <span style="color:{q_cfg['color']};">{q_icon} {row['quote_state']}</span>
                    {pattern_str(row['quote_pattern'])}
                </td>
                <td style="font-size:12px;color:#94a3b8;">{row['scalp_note']}</td>
                <td style="color:{acc_col};font-weight:700;">{row['acceleration']:+.2f}</td>
            </tr>"""
        return rows

    html_table(
        ["Pair","Signal","Confidence","Scenario",
         "Base State","Quote State","Scalp","⚡ Acc"],
        build_confluence_rows(df),
        height=max(300, len(df)*55+60)
    )

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
inject_custom_css()

st.markdown("""
<div class="main-header">
    <h1>🏦 Institutional Currency Strength Engine</h1>
    <p>Currency States • Scalping • Market Events • Confluence</p>
</div>""", unsafe_allow_html=True)

# تحميل البيانات
db_daily   = load_data(DAILY_WS,  "Date")
db_weekly  = load_data(WEEKLY_WS, "Week_Start")
db_economy = load_data(ECONOMY_WS,"Date")
db_news    = load_news_data()

if db_daily.empty:
    st.warning("⚠️ لا توجد بيانات يومية")
    st.stop()

selected_date = render_date_selector(db_daily)

tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 Currency States",
    "⚡ Scalping Signals",
    "📰 Market Events",
    "🎯 Confluence",
])

with tab1:
    render_states_tab(db_economy, db_news, selected_date)

with tab2:
    render_scalping_tab(db_daily, db_weekly, selected_date)

with tab3:
    render_events_tab(db_news, selected_date)

with tab4:
    render_confluence_tab(db_daily, db_economy, db_news, db_weekly, selected_date)
