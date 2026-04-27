import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
# أضفه في أعلى الكود بعد imports
import time
st_autorefresh = st.empty()
if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = time.time()
if time.time() - st.session_state['last_refresh'] > 3600:
    st.session_state['last_refresh'] = time.time()
    st.cache_data.clear()
    st.rerun()
    
st.set_page_config(page_title="Institutional Currency Strength Engine", layout="wide", page_icon="🏦")

# ====================== Google Sheets Configuration ======================
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
        .main-header p { color: #64748b; margin: 0.4rem 0 0; font-size: 0.8rem; text-transform: uppercase; }
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
MONTHLY_WS = "monthly"
ECONOMY_WS = "ECONOMY"
YIELD_WS   = "YIELD"
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

CURRENCY_COLORS = {
    'USD': '#3b82f6', 'EUR': '#f1c40f', 'GBP': '#a78bfa',
    'JPY': '#f43f5e', 'CHF': '#e2e8f0', 'CAD': '#fb923c',
    'AUD': '#34d399', 'NZD': '#22d3ee',
}

currency_flags = {
    "USD":"🇺🇸","EUR":"🇪🇺","GBP":"🇬🇧","JPY":"🇯🇵",
    "CHF":"🇨🇭","CAD":"🇨🇦","AUD":"🇦🇺","NZD":"🇳🇿"
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
        st.warning(f"Could not load News worksheet: {e}")
        return pd.DataFrame()

# ====================== Helper Functions ======================
def get_row_for_date(df, date_col, sel_date):
    """يجيب الصف الحالي والسابق لتاريخ معين"""
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
    """يجيب أقرب أسبوع قبل أو يساوي التاريخ المختار"""
    db_weekly = db_weekly.copy()
    db_weekly['Week_Start'] = pd.to_datetime(db_weekly['Week_Start']).dt.date
    available = db_weekly[db_weekly['Week_Start'] <= selected_date]
    if available.empty:
        return None, None
    curr = available.iloc[-1]
    prev = available.iloc[-2] if len(available) >= 2 else None
    return curr, prev

def get_monthly_row(db_monthly, selected_date):
    """يجيب أقرب شهر قبل أو يساوي التاريخ المختار"""
    db_monthly = db_monthly.copy()
    db_monthly['Month_Start'] = pd.to_datetime(db_monthly['Month_Start']).dt.date
    available = db_monthly[db_monthly['Month_Start'] <= selected_date]
    if available.empty:
        return None, None
    curr = available.iloc[-1]
    prev = available.iloc[-2] if len(available) >= 2 else None
    return curr, prev

def get_direction(curr_row, prev_row, col):
    """يحدد اتجاه العملة مقارنة بالسابق"""
    if curr_row is None or prev_row is None:
        return None
    if col not in curr_row.index or col not in prev_row.index:
        return None
    c, p = curr_row[col], prev_row[col]
    if pd.isna(c) or pd.isna(p):
        return None
    if c > p: return 'up'
    elif c < p: return 'down'
    else: return 'flat'

def signal_color(signal):
    if signal == 'BUY':  return '#10b981', 'rgba(16,185,129,0.15)'
    if signal == 'SELL': return '#ef4444', 'rgba(239,68,68,0.15)'
    return '#f1c40f', 'rgba(241,196,15,0.15)'

def summary_cards(buy_count, sell_count, extra_label="", extra_count=0):
    """ملخص BUY/SELL في أعلى كل تبويب"""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style='background:rgba(16,185,129,0.15);border:1px solid #10b981;
                    border-radius:12px;padding:16px;text-align:center;'>
            <div style='font-size:12px;color:#94a3b8;'>BUY Signals</div>
            <div style='font-size:36px;font-weight:bold;color:#10b981;'>{buy_count}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='background:rgba(239,68,68,0.15);border:1px solid #ef4444;
                    border-radius:12px;padding:16px;text-align:center;'>
            <div style='font-size:12px;color:#94a3b8;'>SELL Signals</div>
            <div style='font-size:36px;font-weight:bold;color:#ef4444;'>{sell_count}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style='background:rgba(241,196,15,0.15);border:1px solid #f1c40f;
                    border-radius:12px;padding:16px;text-align:center;'>
            <div style='font-size:12px;color:#94a3b8;'>{extra_label if extra_label else "Total Active"}</div>
            <div style='font-size:36px;font-weight:bold;color:#f1c40f;'>
                {extra_count if extra_label else buy_count + sell_count}
            </div>
        </div>""", unsafe_allow_html=True)

def html_table(headers, rows_html, height=400):
    """جدول HTML موحد الشكل"""
    headers_html = "".join([f"<th>{h}</th>" for h in headers])
    table = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <style>
        body {{ margin:0;padding:0;background:transparent;
               font-family:-apple-system,BlinkMacSystemFont,sans-serif; }}
        table {{ width:100%;border-collapse:collapse;
                background:linear-gradient(135deg,#0f172a,#1e293b);
                border-radius:12px;overflow:hidden; }}
        th {{ background:#1e293b;color:#f1c40f;padding:12px 10px;
             text-align:left;font-size:12px;font-weight:600;
             border-bottom:2px solid #f1c40f;white-space:nowrap; }}
        tr:hover {{ background:rgba(241,196,15,0.04); }}
        td {{ padding:12px 10px; }}
    </style></head><body>
    <table>
        <thead><tr>{headers_html}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table></body></html>"""
    st.components.v1.html(table, height=height, scrolling=True)

# ====================== Date Selector ======================
def render_date_selector(db_daily):
    db_daily = db_daily.copy()
    db_daily['Date'] = pd.to_datetime(db_daily['Date']).dt.date
    all_dates = db_daily['Date'].sort_values(ascending=False).tolist()

    date_options, date_map = [], {}
    for d in all_dates:
        ds    = d.strftime("%Y-%m-%d")
        label = f"📅 {ds}  ·  Latest" if d == all_dates[0] else f"📅 {ds}"
        date_options.append(label)
        date_map[label] = d

    st.markdown("""
    <div style='background:#0f172a;border:1px solid rgba(241,196,15,0.25);
                border-radius:10px;padding:10px 16px;margin-bottom:1.2rem;'>
        <span style='color:#f1c40f;font-size:13px;font-weight:600;'>DATE</span>
        <span style='color:#334155;font-size:11px;'> | </span>
        <span style='color:#64748b;font-size:11px;'>Choose The Date</span>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_label = st.selectbox(
            "", options=date_options, index=0,
            key="global_date_selector", label_visibility="collapsed"
        )
    selected_date = date_map[selected_label]
    st.session_state['selected_date'] = selected_date
    return selected_date

# ══════════════════════════════════════════════════════════════
# TAB 1 — Daily Signals
# ══════════════════════════════════════════════════════════════
def render_daily_signals(db_daily, db_economy, db_yield, db_weekly, db_monthly, selected_date):

    if db_daily.empty or db_economy.empty:
        st.info("📊 يرجى إدخال بيانات Daily و ECONOMY أولاً")
        return

    daily_curr, daily_prev     = get_row_for_date(db_daily,   'Date', selected_date)
    eco_curr,   eco_prev       = get_row_for_date(db_economy,  'Date', selected_date)
    yield_curr, yield_prev     = get_row_for_date(db_yield,    'Date', selected_date) if not db_yield.empty else (None, None)
    weekly_curr, weekly_prev   = get_weekly_row(db_weekly,   selected_date)
    monthly_curr, monthly_prev = get_monthly_row(db_monthly, selected_date)

    if daily_curr is None or eco_curr is None:
        st.error(f"❌ لا توجد بيانات للتاريخ {selected_date}")
        return

    def get_pair_signal(base, quote):
        eco_base  = get_direction(eco_curr,   eco_prev,   base)
        eco_quote = get_direction(eco_curr,   eco_prev,   quote)
        yld_base  = get_direction(yield_curr, yield_prev, base)  if yield_curr is not None else None
        yld_quote = get_direction(yield_curr, yield_prev, quote) if yield_curr is not None else None

        daily_val = None
        b = daily_curr.get(base, 0)
        q = daily_curr.get(quote, 0)
        if pd.notna(b) and pd.notna(q):
            diff      = b - q
            daily_val = 'up' if diff > 0 else 'down' if diff < 0 else 'flat'

        if eco_base == 'up' and eco_quote == 'down':
            signal     = 'BUY'
            confidence = 80 if daily_val == 'up' else 75
        elif eco_base == 'down' and eco_quote == 'up':
            signal     = 'SELL'
            confidence = 80 if daily_val == 'down' else 75
        elif (eco_base == 'up' and eco_quote != 'down') or (eco_quote == 'down' and eco_base != 'up'):
            signal     = 'BUY'
            confidence = 70 if daily_val == 'up' else 65
        elif (eco_base == 'down' and eco_quote != 'up') or (eco_quote == 'up' and eco_base != 'down'):
            signal     = 'SELL'
            confidence = 70 if daily_val == 'down' else 65
        elif eco_base in ('flat', None) or eco_quote in ('flat', None):
            yld_signal = None
            if yld_base is not None and yld_quote is not None:
                if (yld_base == 'up' and yld_quote != 'up') or (yld_quote == 'down' and yld_base != 'down'):
                    yld_signal = 'BUY'
                elif (yld_base == 'down' and yld_quote != 'down') or (yld_quote == 'up' and yld_base != 'up'):
                    yld_signal = 'SELL'
            if yld_signal == 'BUY' and daily_val == 'up':
                signal, confidence = 'BUY', 60
            elif yld_signal == 'SELL' and daily_val == 'down':
                signal, confidence = 'SELL', 60
            else:
                signal, confidence = 'WAIT', 0
        else:
            signal, confidence = 'WAIT', 0

        # Scores
        daily_score  = (daily_curr.get(base, 0)   - daily_curr.get(quote, 0))   if daily_curr  is not None else None
        weekly_score = (weekly_curr.get(base, 0)   - weekly_curr.get(quote, 0))  if weekly_curr is not None else None
        monthly_score= (monthly_curr.get(base, 0)  - monthly_curr.get(quote, 0)) if monthly_curr is not None else None

        return {
            'signal': signal, 'confidence': confidence,
            'daily_score': daily_score,
            'weekly_score': weekly_score,
            'monthly_score': monthly_score,
        }

    results = []
    for pair in pairs:
        base, quote = pair[:3], pair[3:]
        r = get_pair_signal(base, quote)
        r['pair'] = pair
        results.append(r)

    df = pd.DataFrame(results)
    df = df[df['signal'] != 'WAIT'].sort_values('confidence', ascending=False)

    # ── ملخص ──
    buy_count  = len(df[df['signal'] == 'BUY'])
    sell_count = len(df[df['signal'] == 'SELL'])

    count_80 = len(df[df['confidence'] == 80])
    count_75 = len(df[df['confidence'] == 75])
    count_70 = len(df[df['confidence'] == 70])
    count_65 = len(df[df['confidence'] == 65])
    count_60 = len(df[df['confidence'] == 60])

    summary_cards(buy_count, sell_count)
    st.markdown("---")

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, count, color, desc in [
        (c1, "80%", count_80, '#059669', 'Cross + Daily'),
        (c2, "75%", count_75, '#10b981', 'Cross Only'),
        (c3, "70%", count_70, '#f1c40f', 'One-Side + Daily'),
        (c4, "65%", count_65, '#f97316', 'One-Side Only'),
        (c5, "60%", count_60, '#8b5cf6', 'Yield + Daily'),
    ]:
        with col:
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.2);border:1px solid {color};
                        border-radius:12px;padding:14px;text-align:center;'>
                <div style='font-size:20px;font-weight:bold;color:{color};'>{count}</div>
                <div style='font-size:13px;font-weight:bold;color:{color};'>{label}</div>
                <div style='font-size:10px;color:#64748b;'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── جدول الإشارات ──
    def build_rows(df):
        rows = ""
        for _, row in df.iterrows():
            sc, sbg = signal_color(row['signal'])
            conf    = row['confidence']

            conf_colors = {80:'#059669', 75:'#10b981', 70:'#f1c40f', 65:'#f97316', 60:'#8b5cf6'}
            cc = conf_colors.get(conf, '#64748b')

            def fmt_score(val):
                if val is None or pd.isna(val): return '<span style="color:#64748b;">—</span>'
                c = '#10b981' if val > 0 else '#ef4444'
                t = 'Target High' if val > 0 else 'Target Low'
                return f'<span style="color:{c};font-weight:600;">{abs(val):.1f}% ({t})</span>'

            rows += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="font-weight:700;color:#e2e8f0;font-size:14px;">{row['pair']}</td>
                <td><span style="background:{sbg};color:{sc};border:1px solid {sc};
                             padding:5px 14px;border-radius:20px;font-weight:700;">{row['signal']}</span></td>
                <td>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="background:#1e293b;border-radius:4px;height:6px;width:60px;overflow:hidden;">
                            <div style="background:{cc};height:100%;width:{conf}%;border-radius:4px;"></div>
                        </div>
                        <span style="color:{cc};font-weight:700;">{conf}%</span>
                    </div>
                </td>
                <td>{fmt_score(row['daily_score'])}</td>
                <td>{fmt_score(row['weekly_score'])}</td>
                <td>{fmt_score(row['monthly_score'])}</td>
            </tr>"""
        return rows

    html_table(
        ["Pair", "Signal", "Confidence", "🎯 Daily", "📆 Weekly", "🗓️ Monthly"],
        build_rows(df),
        height=max(200, len(df) * 52 + 60)
    )

# ══════════════════════════════════════════════════════════════
# TAB 2 — Scalping Signals
# ══════════════════════════════════════════════════════════════
def render_scalping_signals(db_daily, db_weekly, db_monthly, selected_date):

    if db_daily.empty or db_weekly.empty or db_monthly.empty:
        st.info("📊 يرجى إدخال بيانات Daily و Weekly و Monthly أولاً")
        return

    daily_curr, _          = get_row_for_date(db_daily, 'Date', selected_date)
    weekly_curr, weekly_prev = get_weekly_row(db_weekly, selected_date)
    monthly_curr, monthly_prev = get_monthly_row(db_monthly, selected_date)

    if daily_curr is None:
        st.error(f"❌ لا توجد بيانات يومية للتاريخ {selected_date}")
        return
    if weekly_curr is None:
        st.error("❌ لا توجد بيانات أسبوعية")
        return
    if monthly_curr is None:
        st.error("❌ لا توجد بيانات شهرية")
        return

    # ========== القسم الأول: اليومي vs الأسبوعي ==========
    results_daily_vs_weekly = []
    for pair in pairs:
        base, quote = pair[:3], pair[3:]

        b_d = daily_curr.get(base, None)
        q_d = daily_curr.get(quote, None)
        b_w = weekly_curr.get(base, None)
        q_w = weekly_curr.get(quote, None)

        if any(x is None or pd.isna(x) for x in [b_d, q_d, b_w, q_w]):
            continue

        daily_score  = b_d - q_d
        weekly_score = b_w - q_w
        acceleration = daily_score - weekly_score
        weekly_bias  = "Bullish" if weekly_score > 0 else "Bearish"

        if acceleration > 0 and weekly_score > 0:
            signal = "BUY"
        elif acceleration < 0 and weekly_score < 0:
            signal = "SELL"
        else:
            signal = "WAIT"

        results_daily_vs_weekly.append({
            "pair":         pair,
            "signal":       signal,
            "daily_score":  round(daily_score,  2),
            "weekly_score": round(weekly_score, 2),
            "acceleration": round(acceleration, 2),
            "weekly_bias":  weekly_bias,
        })

    df_daily_vs_weekly = pd.DataFrame(results_daily_vs_weekly)
    df_daily_vs_weekly = df_daily_vs_weekly[df_daily_vs_weekly['signal'] != 'WAIT']
    df_daily_vs_weekly = df_daily_vs_weekly.reindex(df_daily_vs_weekly['acceleration'].abs().sort_values(ascending=False).index)

    # عرض الجدول الأول
    buy_count_1  = len(df_daily_vs_weekly[df_daily_vs_weekly['signal'] == 'BUY'])
    sell_count_1 = len(df_daily_vs_weekly[df_daily_vs_weekly['signal'] == 'SELL'])
    st.markdown("### 📈 Daily vs Weekly")
    summary_cards(buy_count_1, sell_count_1)
    st.markdown("---")

    def build_rows_daily_vs_weekly(df):
        rows = ""
        for _, row in df.iterrows():
            sc, sbg    = signal_color(row['signal'])
            acc_color  = '#10b981' if row['acceleration'] > 0 else '#ef4444'
            bias_color = '#10b981' if row['weekly_bias'] == 'Bullish' else '#ef4444'
            bias_icon  = '📈' if row['weekly_bias'] == 'Bullish' else '📉'

            rows += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="font-weight:700;color:#e2e8f0;font-size:15px;">{row['pair']}</td>
                <td><span style="background:{sbg};color:{sc};border:1px solid {sc};
                             padding:5px 14px;border-radius:20px;font-weight:700;">{row['signal']}</span></td>
                <td style="color:{acc_color};font-weight:700;font-size:15px;">{row['acceleration']:+.2f}</td>
                <td style="color:#e2e8f0;">{row['daily_score']:+.2f}</td>
                <td style="color:#e2e8f0;">{row['weekly_score']:+.2f}</td>
                <td style="color:{bias_color};font-weight:600;">{bias_icon} {row['weekly_bias']}</td>
            </tr>"""
        return rows

    html_table(
        ["Pair", "Signal", "⚡ Acceleration (Daily - Weekly)", "📅 Daily Score", "📆 Weekly Score", "Weekly Bias"],
        build_rows_daily_vs_weekly(df_daily_vs_weekly),
        height=max(200, len(df_daily_vs_weekly) * 52 + 60)
    )

    st.markdown("---")
    st.markdown("### 🗓️ Weekly vs Monthly")

    # ========== القسم الثاني: الأسبوعي vs الشهري (الجديد) ==========
    results_weekly_vs_monthly = []
    for pair in pairs:
        base, quote = pair[:3], pair[3:]

        b_w = weekly_curr.get(base, None)
        q_w = weekly_curr.get(quote, None)
        b_m = monthly_curr.get(base, None)
        q_m = monthly_curr.get(quote, None)

        if any(x is None or pd.isna(x) for x in [b_w, q_w, b_m, q_m]):
            continue

        weekly_score  = b_w - q_w
        monthly_score = b_m - q_m
        acceleration_monthly = weekly_score - monthly_score
        monthly_bias  = "Bullish" if monthly_score > 0 else "Bearish"

        if acceleration_monthly > 0 and monthly_score > 0:
            signal = "BUY"
        elif acceleration_monthly < 0 and monthly_score < 0:
            signal = "SELL"
        else:
            signal = "WAIT"

        results_weekly_vs_monthly.append({
            "pair":                 pair,
            "signal":               signal,
            "weekly_score":         round(weekly_score, 2),
            "monthly_score":        round(monthly_score, 2),
            "acceleration_monthly": round(acceleration_monthly, 2),
            "monthly_bias":         monthly_bias,
        })

    df_weekly_vs_monthly = pd.DataFrame(results_weekly_vs_monthly)
    df_weekly_vs_monthly = df_weekly_vs_monthly[df_weekly_vs_monthly['signal'] != 'WAIT']
    df_weekly_vs_monthly = df_weekly_vs_monthly.reindex(df_weekly_vs_monthly['acceleration_monthly'].abs().sort_values(ascending=False).index)

    # عرض الجدول الثاني
    buy_count_2  = len(df_weekly_vs_monthly[df_weekly_vs_monthly['signal'] == 'BUY'])
    sell_count_2 = len(df_weekly_vs_monthly[df_weekly_vs_monthly['signal'] == 'SELL'])
    summary_cards(buy_count_2, sell_count_2, extra_label="Total Signals", extra_count=buy_count_2 + sell_count_2)
    st.markdown("---")

    def build_rows_weekly_vs_monthly(df):
        rows = ""
        for _, row in df.iterrows():
            sc, sbg    = signal_color(row['signal'])
            acc_color  = '#10b981' if row['acceleration_monthly'] > 0 else '#ef4444'
            bias_color = '#10b981' if row['monthly_bias'] == 'Bullish' else '#ef4444'
            bias_icon  = '📈' if row['monthly_bias'] == 'Bullish' else '📉'

            rows += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="font-weight:700;color:#e2e8f0;font-size:15px;">{row['pair']}</td>
                <td><span style="background:{sbg};color:{sc};border:1px solid {sc};
                             padding:5px 14px;border-radius:20px;font-weight:700;">{row['signal']}</span></td>
                <td style="color:{acc_color};font-weight:700;font-size:15px;">{row['acceleration_monthly']:+.2f}</td>
                <td style="color:#e2e8f0;">{row['weekly_score']:+.2f}</td>
                <td style="color:#e2e8f0;">{row['monthly_score']:+.2f}</td>
                <td style="color:{bias_color};font-weight:600;">{bias_icon} {row['monthly_bias']}</td>
            </tr>"""
        return rows

    html_table(
        ["Pair", "Signal", "⚡ Acceleration (Weekly - Monthly)", "📆 Weekly Score", "🗓️ Monthly Score", "Monthly Bias"],
        build_rows_weekly_vs_monthly(df_weekly_vs_monthly),
        height=max(200, len(df_weekly_vs_monthly) * 52 + 60)
    )
    
# ══════════════════════════════════════════════════════════════
# TAB 3 — Ultra Scalping Signals (FULL WORKING VERSION)
# ══════════════════════════════════════════════════════════════

import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

PAIRS_YF = {
    "EURUSD": "EURUSD=X", "EURGBP": "EURGBP=X", "EURAUD": "EURAUD=X",
    "EURNZD": "EURNZD=X", "EURCAD": "EURCAD=X", "EURCHF": "EURCHF=X",
    "EURJPY": "EURJPY=X", "GBPUSD": "GBPUSD=X", "GBPAUD": "GBPAUD=X",
    "GBPNZD": "GBPNZD=X", "GBPCAD": "GBPCAD=X", "GBPCHF": "GBPCHF=X",
    "GBPJPY": "GBPJPY=X", "AUDUSD": "AUDUSD=X", "AUDNZD": "AUDNZD=X",
    "AUDCAD": "AUDCAD=X", "AUDCHF": "AUDCHF=X", "AUDJPY": "AUDJPY=X",
    "NZDUSD": "NZDUSD=X", "NZDCAD": "NZDCAD=X", "NZDCHF": "NZDCHF=X",
    "NZDJPY": "NZDJPY=X", "USDCAD": "USDCAD=X", "USDCHF": "USDCHF=X",
    "USDJPY": "USDJPY=X", "CADCHF": "CADCHF=X", "CADJPY": "CADJPY=X",
    "CHFJPY": "CHFJPY=X"
}

# ============================================================
# جلب البيانات
# ============================================================
@st.cache_data(ttl=300, show_spinner=False)  # cache 5 دقائق
def fetch_h1_h4_data():
    end = datetime.utcnow()
    start = end - timedelta(days=10)
    
    h1_data, h4_data = {}, {}
    
    for pair, ticker in PAIRS_YF.items():
        try:
            # H1 data
            df1 = yf.download(ticker, start=start, end=end,
                            interval='1h', progress=False, auto_adjust=True)
            
            if not df1.empty:
                if isinstance(df1.columns, pd.MultiIndex):
                    df1.columns = df1.columns.get_level_values(0)
                df1.index = pd.to_datetime(df1.index)
                if df1.index.tz is not None:
                    df1.index = df1.index.tz_localize(None)
                
                h1_data[pair] = {
                    dt: {
                        'open': float(r['Open']),
                        'high': float(r['High']),
                        'low': float(r['Low']),
                        'close': float(r['Close'])
                    }
                    for dt, r in df1.iterrows()
                }
            else:
                h1_data[pair] = {}
            
            # H4 data (aggregate from 1h)
            df4 = yf.download(ticker, start=start, end=end,
                            interval='1h', progress=False, auto_adjust=True)
            
            if not df4.empty:
                if isinstance(df4.columns, pd.MultiIndex):
                    df4.columns = df4.columns.get_level_values(0)
                df4.index = pd.to_datetime(df4.index)
                if df4.index.tz is not None:
                    df4.index = df4.index.tz_localize(None)
                
                df4_agg = df4.resample('4h').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last'
                }).dropna()
                
                h4_data[pair] = {
                    dt: {
                        'open': float(r['Open']),
                        'high': float(r['High']),
                        'low': float(r['Low']),
                        'close': float(r['Close'])
                    }
                    for dt, r in df4_agg.iterrows()
                }
            else:
                h4_data[pair] = {}
                
        except Exception as e:
            h1_data[pair] = {}
            h4_data[pair] = {}
    
    return h1_data, h4_data


# ============================================================
# حساب القوة
# ============================================================
def calc_strength_live(pair_closes):
    CURRENCIES_LOCAL = ["USD","CAD","EUR","GBP","CHF","AUD","NZD","JPY"]
    scores = {c: 0 for c in CURRENCIES_LOCAL}
    pair_dir = {}
    
    for p in PAIRS_YF:
        if p in pair_closes:
            pair_dir[p] = 1 if pair_closes[p]['close'] > pair_closes[p]['open'] else -1
        else:
            pair_dir[p] = 0
    
    def add(curr, p, d):
        if p in pair_dir and pair_dir[p] != 0:
            scores[curr] += 1 if pair_dir[p] == d else 0
    
    add('EUR','EURUSD', 1); add('EUR','EURGBP', 1); add('EUR','EURCAD', 1)
    add('EUR','EURAUD', 1); add('EUR','EURNZD', 1); add('EUR','EURCHF', 1); add('EUR','EURJPY', 1)
    add('GBP','EURGBP',-1); add('GBP','GBPUSD', 1); add('GBP','GBPCAD', 1)
    add('GBP','GBPAUD', 1); add('GBP','GBPNZD', 1); add('GBP','GBPCHF', 1); add('GBP','GBPJPY', 1)
    add('AUD','EURAUD',-1); add('AUD','GBPAUD',-1); add('AUD','AUDUSD', 1)
    add('AUD','AUDNZD', 1); add('AUD','AUDCAD', 1); add('AUD','AUDCHF', 1); add('AUD','AUDJPY', 1)
    add('NZD','EURNZD',-1); add('NZD','GBPNZD',-1); add('NZD','AUDNZD',-1)
    add('NZD','NZDUSD', 1); add('NZD','NZDCAD', 1); add('NZD','NZDCHF', 1); add('NZD','NZDJPY', 1)
    add('USD','EURUSD',-1); add('USD','GBPUSD',-1); add('USD','AUDUSD',-1)
    add('USD','NZDUSD',-1); add('USD','USDCAD', 1); add('USD','USDCHF', 1); add('USD','USDJPY', 1)
    add('CAD','EURCAD',-1); add('CAD','GBPCAD',-1); add('CAD','AUDCAD',-1)
    add('CAD','NZDCAD',-1); add('CAD','USDCAD',-1); add('CAD','CADCHF', 1); add('CAD','CADJPY', 1)
    add('CHF','EURCHF',-1); add('CHF','GBPCHF',-1); add('CHF','AUDCHF',-1)
    add('CHF','NZDCHF',-1); add('CHF','USDCHF',-1); add('CHF','CADCHF',-1); add('CHF','CHFJPY', 1)
    add('JPY','EURJPY',-1); add('JPY','GBPJPY',-1); add('JPY','AUDJPY',-1)
    add('JPY','NZDJPY',-1); add('JPY','USDJPY',-1); add('JPY','CADJPY',-1); add('JPY','CHFJPY',-1)
    
    return {c: round((scores[c] / 7) * 100) for c in CURRENCIES_LOCAL}


# ============================================================
# حساب الإشارات
# ============================================================
def get_live_signals(h1_data, h4_data):
    h4_times_all = sorted({dt for p in PAIRS_YF for dt in h4_data.get(p, {})})
    h1_times_all = sorted({dt for p in PAIRS_YF for dt in h1_data.get(p, {})})
    
    if not h4_times_all or not h1_times_all:
        return pd.DataFrame(), None, None, 0
    
    now = datetime.utcnow()
    
    # آخر H4 مغلقة
    closed_h4 = [t for t in h4_times_all if t < now]
    if not closed_h4:
        return pd.DataFrame(), None, None, 0
    
    last_h4_time = closed_h4[-1]
    
    # حساب رقم الشمعة
    hours_passed = (now - last_h4_time).total_seconds() / 3600
    current_candle = min(int(hours_passed) + 1, 4)
    
    cycle_end = last_h4_time + timedelta(hours=4)
    
    # الشموع المغلقة في الدورة
    cycle_h1s = [
        t for t in h1_times_all
        if last_h4_time <= t < cycle_end and t < now - timedelta(minutes=1)
    ]
    
    if not cycle_h1s:
        return pd.DataFrame(), last_h4_time, cycle_end, current_candle
    
    signals = []
    
    for pair in PAIRS_YF:
        base, quote = pair[:3], pair[3:]
        
        h4_bar = h4_data.get(pair, {}).get(last_h4_time)
        if not h4_bar:
            continue
        
        # H4 Score
        h4_closes = {}
        for p in PAIRS_YF:
            if last_h4_time in h4_data.get(p, {}):
                h4_closes[p] = h4_data[p][last_h4_time]
        
        if len(h4_closes) < 20:
            continue
        
        h4_strength = calc_strength_live(h4_closes)
        b_h4 = h4_strength.get(base)
        q_h4 = h4_strength.get(quote)
        
        if any(x is None for x in [b_h4, q_h4]):
            continue
        
        h4_score = b_h4 - q_h4
        if h4_score == 0:
            continue
        
        liquidity_taken = False
        
        for idx, h1_time in enumerate(cycle_h1s):
            h1_bar = h1_data.get(pair, {}).get(h1_time)
            if not h1_bar:
                continue
            
            # فحص السيولة مع تسامح 5%
            h4_range = abs(h4_bar['high'] - h4_bar['low'])
            tolerance = h4_range * 0.05
            
            if h4_score > 0 and h1_bar['high'] >= (h4_bar['high'] - tolerance):
                liquidity_taken = True
                break
            
            if h4_score < 0 and h1_bar['low'] <= (h4_bar['low'] + tolerance):
                liquidity_taken = True
                break
            
            # H1 Score
            h1_closes = {}
            for p in PAIRS_YF:
                if h1_time in h1_data.get(p, {}):
                    h1_closes[p] = h1_data[p][h1_time]
            
            if len(h1_closes) < 20:
                continue
            
            h1_strength = calc_strength_live(h1_closes)
            b_h1 = h1_strength.get(base)
            q_h1 = h1_strength.get(quote)
            
            if any(x is None for x in [b_h1, q_h1]):
                continue
            
            h1_score = b_h1 - q_h1
            
            # BUY Signal
            if h4_score > 0 and h1_score > h4_score:
                if h1_bar['high'] >= h4_bar['high']:
                    continue
                
                signals.append({
                    'pair': pair,
                    'signal': 'BUY',
                    'h1_score': h1_score,
                    'h4_score': h4_score,
                    'acceleration': round(h1_score - h4_score, 2),
                    'entry': round(h1_bar['close'], 5),
                    'target': round(h4_bar['high'], 5),
                    'space': round(h4_bar['high'] - h1_bar['close'], 5),
                    'cycle_candle': idx + 1,
                    'h4_time': last_h4_time,
                    'h1_time': h1_time,
                    'cycle_end': cycle_end,
                })
            
            # SELL Signal
            elif h4_score < 0 and h1_score < h4_score:
                if h1_bar['low'] <= h4_bar['low']:
                    continue
                
                signals.append({
                    'pair': pair,
                    'signal': 'SELL',
                    'h1_score': h1_score,
                    'h4_score': h4_score,
                    'acceleration': round(h4_score - h1_score, 2),
                    'entry': round(h1_bar['close'], 5),
                    'target': round(h4_bar['low'], 5),
                    'space': round(h1_bar['close'] - h4_bar['low'], 5),
                    'cycle_candle': idx + 1,
                    'h4_time': last_h4_time,
                    'h1_time': h1_time,
                    'cycle_end': cycle_end,
                })
    
    df = pd.DataFrame(signals)
    if not df.empty:
        df = df.sort_values('acceleration', ascending=False)
    
    return df, last_h4_time, cycle_end, current_candle


# ============================================================
# واجهة Streamlit
# ============================================================
def render_h1_h4_signals():
    st.markdown("## ⚡ H1 vs H4 — Live Signals")
    
    # ── جلب البيانات ──
    with st.spinner("⏳ جاري تحميل البيانات..."):
        h1_data, h4_data = fetch_h1_h4_data()
    
    df, last_h4_time, cycle_end, current_candle = get_live_signals(h1_data, h4_data)
    
    now = datetime.utcnow()
    
    # ── معلومات الدورة ──
    if last_h4_time:
        h4_str = last_h4_time.strftime('%H:%M UTC')
        cycle_str = cycle_end.strftime('%H:%M UTC') if cycle_end else '—'
        
        elapsed = int((now - last_h4_time).total_seconds() / 60)
        remaining = max(0, 240 - elapsed)
        
        candle_color = ['#10b981', '#f1c40f', '#f97316', '#ef4444'][current_candle - 1]
        
        # Header Card
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    border: 1px solid #334155; border-radius: 16px;
                    padding: 20px; margin-bottom: 20px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h3 style='color: #f1c40f; margin: 0; font-size: 18px;'>
                        ⚡ إشارات H1 vs H4
                    </h3>
                    <p style='color: #94a3b8; margin: 5px 0 0 0; font-size: 13px;'>
                        🕐 بداية: {h4_str} → ⏰ نهاية: {cycle_str}
                    </p>
                </div>
                <div style='text-align: center;'>
                    <div style='color: #64748b; font-size: 11px; margin-bottom: 4px;'>
                        رقم الشمعة
                    </div>
                    <div style='color: {candle_color}; font-size: 40px; font-weight: 900;
                                line-height: 1;'>
                        H1[{current_candle}]
                    </div>
                </div>
            </div>
            <div style='margin-top: 15px;'>
                <div style='background: #1e293b; border-radius: 10px; height: 8px;'>
                    <div style='background: {candle_color}; width: {min(100, (elapsed/240)*100)}%;
                                height: 100%; border-radius: 10px; transition: width 1s;'>
                    </div>
                </div>
                <p style='color: #64748b; font-size: 11px; margin: 5px 0 0 0;'>
                    ⏱️ متبقي: {remaining} دقيقة | 📊 تقدم: {min(100, int((elapsed/240)*100))}%
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ── عرض الإشارات ──
    if df.empty:
        st.warning("📭 لا توجد إشارات حالية")
        
        with st.expander("💡 الأسباب المحتملة", expanded=True):
            st.markdown("""
            - ⏳ لم تكتمل شروط الإشارة بعد (انتظر إغلاق الشمعة)
            - 🚫 السيولة تم أخذها مبكراً في الدورة
            - 📉 السوق في حالة تشبع أو تذبذب
            - 🔄 الأزواج لم تصل للحد الأدنى (20 زوج)
            
            **جرب التحديث بعد 5-10 دقائق**
            """)
        
        if st.button("🔄 تحديث الآن", key="refresh_empty", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        return
    
    # ── إحصائيات سريعة ──
    buy_count = len(df[df['signal'] == 'BUY'])
    sell_count = len(df[df['signal'] == 'SELL'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 إجمالي", len(df))
    with col2:
        st.metric("🟢 شراء", buy_count)
    with col3:
        st.metric("🔴 بيع", sell_count)
    with col4:
        st.metric("⚡ أفضل تسارع", f"{df['acceleration'].max():.0f}")
    
    st.markdown("---")
    
    # ── كروت الإشارات ──
    for idx, (_, row) in enumerate(df.iterrows()):
        signal_color = '#10b981' if row['signal'] == 'BUY' else '#ef4444'
        signal_bg = 'rgba(16, 185, 129, 0.1)' if row['signal'] == 'BUY' else 'rgba(239, 68, 68, 0.1)'
        acc_color = '#10b981' if row['signal'] == 'BUY' else '#ef4444'
        
        candle_colors = {1: '#10b981', 2: '#f1c40f', 3: '#f97316', 4: '#ef4444'}
        c_color = candle_colors.get(row['cycle_candle'], '#64748b')
        
        h1_time_str = row['h1_time'].strftime('%H:%M')
        cycle_end_str = row['cycle_end'].strftime('%H:%M')
        
        # بناء كرت الإشارة
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    border: 1px solid {signal_color}40; border-radius: 12px;
                    padding: 16px; margin-bottom: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            
            <!-- الصف الأول: الزوج والإشارة -->
            <div style='display: flex; justify-content: space-between; align-items: center;
                        margin-bottom: 12px;'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='color: #f1f5f9; font-size: 18px; font-weight: 700;'>
                        {row['pair']}
                    </span>
                    <span style='background: {signal_bg}; color: {signal_color};
                                border: 1px solid {signal_color}; padding: 4px 14px;
                                border-radius: 20px; font-weight: 700; font-size: 13px;'>
                        {row['signal']}
                    </span>
                </div>
                <span style='color: {c_color}; font-weight: 700; font-size: 13px;
                            background: rgba(0,0,0,0.3); padding: 4px 10px;
                            border-radius: 8px;'>
                    شمعة H1[{row['cycle_candle']}]
                </span>
            </div>
            
            <!-- الصف الثاني: التسارع والسكورات -->
            <div style='display: flex; justify-content: space-between; align-items: center;
                        margin-bottom: 10px; padding: 8px 12px;
                        background: rgba(0,0,0,0.2); border-radius: 8px;'>
                <div style='display: flex; align-items: center; gap: 6px;'>
                    <span style='color: #94a3b8; font-size: 13px;'>⚡ التسارع:</span>
                    <span style='color: {acc_color}; font-weight: 700; font-size: 15px;'>
                        +{row['acceleration']}
                    </span>
                </div>
                <div style='color: #94a3b8; font-size: 13px;'>
                    H1 Score: <span style='color: #e2e8f0; font-weight: 600;'>
                        {row['h1_score']:+.0f}</span>
                    &nbsp;|&nbsp;
                    H4 Score: <span style='color: #94a3b8; font-weight: 600;'>
                        {row['h4_score']:+.0f}</span>
                </div>
            </div>
            
            <!-- الصف الثالث: الأسعار -->
            <div style='display: flex; justify-content: space-between; align-items: center;
                        padding: 8px 12px; background: rgba(0,0,0,0.2); border-radius: 8px;
                        font-family: monospace; font-size: 13px;'>
                <div>
                    <span style='color: #94a3b8;'>🎯 الدخول:</span>
                    <span style='color: #e2e8f0; font-weight: 600; margin-left: 4px;'>
                        {row['entry']}
                    </span>
                </div>
                <div>
                    <span style='color: #94a3b8;'>🏁 الهدف:</span>
                    <span style='color: {signal_color}; font-weight: 700; margin-left: 4px;'>
                        {row['target']}
                    </span>
                </div>
                <div>
                    <span style='color: #94a3b8;'>📏 المساحة:</span>
                    <span style='color: #cbd5e1; font-weight: 600; margin-left: 4px;'>
                        {row['space']}
                    </span>
                </div>
            </div>
            
            <!-- الصف الرابع: التوقيت -->
            <div style='margin-top: 10px; display: flex; justify-content: space-between;
                        color: #64748b; font-size: 11px;'>
                <span>🕐 الشمعة: {h1_time_str} UTC</span>
                <span>⏰ تنتهي: {cycle_end_str} UTC</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ── أزرار التحكم ──
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 تحديث الإشارات", key="refresh_signals", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col2:
        st.caption(f"🕐 آخر تحديث: {now.strftime('%H:%M:%S UTC')}")


# ============================================================
# تشغيل التبويب
# ============================================================
if __name__ == "__main__":
    st.set_page_config(
        page_title="H1 vs H4 Signals",
        page_icon="⚡",
        layout="wide"
    )
    render_h1_h4_signals()

# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════
inject_custom_css()

st.markdown("""
<div class="main-header">
    <h1>🏦 Institutional Currency Strength Engine</h1>
    <p>Pro Trader Mindsite</p>
</div>""", unsafe_allow_html=True)

# ── تحميل البيانات ──
db_daily   = load_data(DAILY_WS,   "Date")
db_weekly  = load_data(WEEKLY_WS,  "Week_Start")
db_monthly = load_data(MONTHLY_WS, "Month_Start")
db_economy = load_data(ECONOMY_WS, "Date")
db_yield   = load_data(YIELD_WS,   "Date")
db_news    = load_news_data()

# ── Date Selector ──
if db_daily.empty:
    st.warning("⚠️ لا توجد بيانات يومية")
    st.stop()

selected_date = render_date_selector(db_daily)

# ── التبويبات ──
tab1, tab2, tab3, = st.tabs([
    "📅 Daily Signals",
    "⚡ Scalping Signals",
    "🔴 Ultra Scalping Signals",
])

with tab1:
    render_daily_signals(db_daily, db_economy, db_yield, db_weekly, db_monthly, selected_date)

with tab2:
    render_scalping_signals(db_daily, db_weekly, db_monthly, selected_date)

with tab3:
    render_h1_h4_signals()
