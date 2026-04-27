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
# TAB — Ultra Scalping Signals (Hybrid Version V3)
# ══════════════════════════════════════════════════════════════

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

PAIRS_YF = {
    "EURUSD": "EURUSD=X","GBPUSD": "GBPUSD=X","USDJPY": "USDJPY=X",
    "USDCHF": "USDCHF=X","USDCAD": "USDCAD=X","AUDUSD": "AUDUSD=X",
    "NZDUSD": "NZDUSD=X","EURJPY": "EURJPY=X","GBPJPY": "GBPJPY=X"
}

# ============================================================
# DATA
# ============================================================
def fetch_data():
    end = datetime.utcnow()
    start = end - timedelta(days=5)

    h1_data, h4_data = {}, {}

    for pair, ticker in PAIRS_YF.items():
        try:
            df1 = yf.download(ticker, start=start, end=end, interval='1h', progress=False)
            df4 = yf.download(ticker, start=start, end=end, interval='4h', progress=False)

            if not df1.empty:
                df1.index = df1.index.tz_localize(None)
                h1_data[pair] = {dt: row for dt, row in df1.iterrows()}
            else:
                h1_data[pair] = {}

            if not df4.empty:
                df4.index = df4.index.tz_localize(None)
                h4_data[pair] = {dt: row for dt, row in df4.iterrows()}
            else:
                h4_data[pair] = {}

        except:
            h1_data[pair], h4_data[pair] = {}, {}

    return h1_data, h4_data

# ============================================================
# STRENGTH
# ============================================================
def calc_strength(pair_closes):
    currencies = ["USD","EUR","GBP","JPY","CHF","CAD","AUD","NZD"]
    scores = {c: 0 for c in currencies}

    for p, v in pair_closes.items():
        if v['Close'] > v['Open']:
            base, quote = p[:3], p[3:]
            scores[base] += 1
        else:
            base, quote = p[:3], p[3:]
            scores[quote] += 1

    return scores

# ============================================================
# SIGNAL ENGINE
# ============================================================
def get_signals(h1_data, h4_data):

    now = datetime.utcnow()

    h4_times = sorted({t for p in h4_data for t in h4_data[p]})
    last_h4 = [t for t in h4_times if t < now][-1]

    cycle_end = last_h4 + timedelta(hours=4)

    signals = []

    for pair in PAIRS_YF:

        base, quote = pair[:3], pair[3:]

        h4_bar = h4_data[pair].get(last_h4)
        if not h4_bar:
            continue

        # ===== H4 SCORE =====
        h4_closes = {p: h4_data[p][last_h4] for p in h4_data if last_h4 in h4_data[p]}
        if len(h4_closes) < 5:
            continue

        h4_strength = calc_strength(h4_closes)
        h4_score = h4_strength.get(base,0) - h4_strength.get(quote,0)

        # ===== H1 CYCLE =====
        h1_times = sorted(h1_data[pair].keys())

        for idx, t in enumerate(h1_times):

            if not (last_h4 <= t < cycle_end):
                continue

            h1_bar = h1_data[pair][t]

            # ===== H1 SCORE =====
            h1_closes = {p: h1_data[p][t] for p in h1_data if t in h1_data[p]}
            if len(h1_closes) < 5:
                continue

            h1_strength = calc_strength(h1_closes)
            h1_score = h1_strength.get(base,0) - h1_strength.get(quote,0)

            signal = None

            if h4_score > 0 and h1_score > h4_score:
                signal = "BUY"
                target = h4_bar['High']

            elif h4_score < 0 and h1_score < h4_score:
                signal = "SELL"
                target = h4_bar['Low']

            if not signal:
                continue

            # ===== LIQUIDITY TRACKING =====
            liquidity_taken = False

            future_candles = [x for x in h1_times if x >= t and x < cycle_end]

            for ft in future_candles:
                f_bar = h1_data[pair][ft]

                if signal == "BUY" and f_bar['High'] >= target:
                    liquidity_taken = True
                    break

                if signal == "SELL" and f_bar['Low'] <= target:
                    liquidity_taken = True
                    break

            # ✅ فقط الإشارات اللي السيولة متاخدتش
            if not liquidity_taken:
                signals.append({
                    "pair": pair,
                    "signal": signal,
                    "entry": round(h1_bar['Close'],5),
                    "target": round(target,5),
                    "h1_score": h1_score,
                    "h4_score": h4_score,
                    "candle": idx+1
                })

    df = pd.DataFrame(signals)
    if not df.empty:
        df = df.sort_values("candle")

    return df, last_h4

# ============================================================
# UI
# ============================================================
def render_ultra_scalping():

    st.subheader("⚡ Ultra Scalping V3")

    h1_data, h4_data = fetch_data()
    df, last_h4 = get_signals(h1_data, h4_data)

    if df.empty:
        st.warning("📭 No Active Signals")
        return

    for _, row in df.iterrows():
        color = "green" if row['signal']=="BUY" else "red"

        st.markdown(f"""
        **{row['pair']}** | {row['signal']}  
        Entry: {row['entry']}  
        Target: {row['target']}  
        H1: {row['h1_score']} | H4: {row['h4_score']}  
        Candle: {row['candle']}
        """)

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
