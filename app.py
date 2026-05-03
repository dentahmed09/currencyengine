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
# TAB 1 — Daily Signals  (ECONOMY ONLY — 4 categories)
# ══════════════════════════════════════════════════════════════
def render_daily_signals(db_daily, db_economy, db_yield, db_weekly, db_monthly, selected_date):

    if db_daily.empty or db_economy.empty:
        st.info("📊 يرجى إدخال بيانات Daily و ECONOMY أولاً")
        return

    eco_curr, eco_prev = get_row_for_date(db_economy, 'Date', selected_date)

    if eco_curr is None or eco_prev is None:
        st.error(f"❌ لا توجد بيانات اقتصادية كافية للتاريخ {selected_date}")
        return

    # ── بناء قائمة الأزواج مع تصنيفها ──
    crossover   = []   # تقاطع  : base صاعد + quote هابط (أو عكس)
    alignment   = []   # توافق  : الاثنين صاعدين أو الاثنين هابطين
    single_move = []   # قوة وحده: واحدة تتحرك والثانية flat
    stagnation  = []   # ثبات   : الاثنين flat / null

    for pair in pairs:
        base  = pair[:3]
        quote = pair[3:]

        dir_base  = get_direction(eco_curr, eco_prev, base)
        dir_quote = get_direction(eco_curr, eco_prev, quote)

        # فرق السكور الاقتصادي اليومي
        try:
            score_base  = float(eco_curr.get(base,  0) or 0)
            score_quote = float(eco_curr.get(quote, 0) or 0)
            eco_diff    = round(score_base - score_quote, 2)
        except Exception:
            eco_diff = None

        row = {
            "pair":        pair,
            "dir_base":    dir_base,
            "dir_quote":   dir_quote,
            "eco_diff":    eco_diff,
        }

        # التصنيف
        if dir_base == 'up'   and dir_quote == 'down':
            row["signal"] = "BUY"
            crossover.append(row)
        elif dir_base == 'down' and dir_quote == 'up':
            row["signal"] = "SELL"
            crossover.append(row)
        elif dir_base == 'up'   and dir_quote == 'up':
            row["signal"] = "ALIGN↑"
            alignment.append(row)
        elif dir_base == 'down' and dir_quote == 'down':
            row["signal"] = "ALIGN↓"
            alignment.append(row)
        elif (dir_base in ('up', 'down') and dir_quote == 'flat') or \
             (dir_quote in ('up', 'down') and dir_base == 'flat'):
            row["signal"] = "BUY" if (
                (dir_base == 'up'   and dir_quote == 'flat') or
                (dir_quote == 'down' and dir_base == 'flat')
            ) else "SELL"
            single_move.append(row)
        else:
            row["signal"] = "FLAT"
            stagnation.append(row)

    # ═══════════════════════════════════
    # دالة بناء جدول HTML موحد
    # ═══════════════════════════════════
    def fmt_dir(d):
        if d == 'up':   return '<span style="color:#10b981;font-weight:700;">▲ UP</span>'
        if d == 'down': return '<span style="color:#ef4444;font-weight:700;">▼ DOWN</span>'
        if d == 'flat': return '<span style="color:#64748b;">— FLAT</span>'
        return '<span style="color:#334155;">N/A</span>'

    def fmt_diff(val):
        if val is None: return '<span style="color:#334155;">—</span>'
        color = '#10b981' if val > 0 else '#ef4444' if val < 0 else '#64748b'
        sign  = '+' if val > 0 else ''
        return f'<span style="color:{color};font-weight:700;">{sign}{val}</span>'

    def build_rows(data_list):
        rows = ""
        for row in data_list:
            sc, sbg = signal_color(row['signal'])
            rows += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="font-weight:700;color:#e2e8f0;font-size:14px;">{row['pair']}</td>
                <td>{fmt_dir(row['dir_base'])}</td>
                <td>{fmt_dir(row['dir_quote'])}</td>
                <td>{fmt_diff(row['eco_diff'])}</td>
                <td>
                    <span style="background:{sbg};color:{sc};border:1px solid {sc};
                                 padding:4px 14px;border-radius:20px;font-weight:700;font-size:12px;">
                        {row['signal']}
                    </span>
                </td>
            </tr>"""
        return rows

    HEADERS = ["Pair", "Base Dir", "Quote Dir", "Eco Diff (Base − Quote)", "Signal"]

    # ═══════════════════════════════════
    # ملخص أعلى الصفحة
    # ═══════════════════════════════════
    c1, c2, c3, c4 = st.columns(4)
    for col, label, count, color, icon in [
        (c1, "تقاطع",    len(crossover),   '#10b981', '🔀'),
        (c2, "توافق",    len(alignment),   '#3b82f6', '🤝'),
        (c3, "قوة وحده", len(single_move), '#f1c40f', '⚡'),
        (c4, "ثبات",     len(stagnation),  '#64748b', '➖'),
    ]:
        with col:
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.2);border:1px solid {color};
                        border-radius:12px;padding:16px;text-align:center;'>
                <div style='font-size:20px;'>{icon}</div>
                <div style='font-size:24px;font-weight:bold;color:{color};'>{count}</div>
                <div style='font-size:13px;color:{color};font-weight:600;'>{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ═══════════════════════════════════
    # 1 — تقاطع
    # ═══════════════════════════════════
    st.markdown("""
    <div style='background:#0f172a;border-right:3px solid #10b981;
                border-radius:8px;padding:10px 16px;margin-bottom:0.75rem;'>
        <span style='color:#10b981;font-size:14px;font-weight:700;'>🔀 تقاطع</span>
        <span style='color:#64748b;font-size:12px;margin-right:12px;'>
            اقتصاد Base صاعد + Quote هابط (أو العكس)
        </span>
    </div>""", unsafe_allow_html=True)

    if crossover:
        html_table(HEADERS, build_rows(crossover), height=max(150, len(crossover) * 50 + 56))
    else:
        st.info("لا توجد أزواج في هذا التصنيف")

    st.markdown("---")

    # ═══════════════════════════════════
    # 2 — توافق
    # ═══════════════════════════════════
    st.markdown("""
    <div style='background:#0f172a;border-right:3px solid #3b82f6;
                border-radius:8px;padding:10px 16px;margin-bottom:0.75rem;'>
        <span style='color:#3b82f6;font-size:14px;font-weight:700;'>🤝 توافق</span>
        <span style='color:#64748b;font-size:12px;margin-right:12px;'>
            الاقتصادين في نفس الاتجاه (كلاهما صاعد أو هابط)
        </span>
    </div>""", unsafe_allow_html=True)

    if alignment:
        html_table(HEADERS, build_rows(alignment), height=max(150, len(alignment) * 50 + 56))
    else:
        st.info("لا توجد أزواج في هذا التصنيف")

    st.markdown("---")

    # ═══════════════════════════════════
    # 3 — قوة وحده
    # ═══════════════════════════════════
    st.markdown("""
    <div style='background:#0f172a;border-right:3px solid #f1c40f;
                border-radius:8px;padding:10px 16px;margin-bottom:0.75rem;'>
        <span style='color:#f1c40f;font-size:14px;font-weight:700;'>⚡ قوة وحده</span>
        <span style='color:#64748b;font-size:12px;margin-right:12px;'>
            عملة واحدة متحركة والأخرى ثابتة
        </span>
    </div>""", unsafe_allow_html=True)

    if single_move:
        html_table(HEADERS, build_rows(single_move), height=max(150, len(single_move) * 50 + 56))
    else:
        st.info("لا توجد أزواج في هذا التصنيف")

    st.markdown("---")

    # ═══════════════════════════════════
    # 4 — ثبات
    # ═══════════════════════════════════
    st.markdown("""
    <div style='background:#0f172a;border-right:3px solid #475569;
                border-radius:8px;padding:10px 16px;margin-bottom:0.75rem;'>
        <span style='color:#94a3b8;font-size:14px;font-weight:700;'>➖ ثبات</span>
        <span style='color:#64748b;font-size:12px;margin-right:12px;'>
            لا حركة في كلا الاقتصادين
        </span>
    </div>""", unsafe_allow_html=True)

    if stagnation:
        html_table(HEADERS, build_rows(stagnation), height=max(150, len(stagnation) * 50 + 56))
    else:
        st.info("لا توجد أزواج في هذا التصنيف")
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
# TAB — Multi-Timeframe Acceleration Signals
# ══════════════════════════════════════════════════════════════

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

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

CURRENCIES = ["USD", "CAD", "EUR", "GBP", "CHF", "AUD", "NZD", "JPY"]

# ============================================================
# 1. جلب البيانات
# ============================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_mtf_data():
    """
    يجلب أحدث إغلاق مكتمل لكل TF
    ttl=60 → كل دقيقة يتحقق هل في إغلاق جديد
    """
    now   = datetime.utcnow()
    end   = now + timedelta(days=1)
    start = now - timedelta(days=60)  # شهرين للـ Monthly

    data = {tf: {} for tf in ['MN', 'W', 'D', 'H4', 'H1']}

    for pair, ticker in PAIRS_YF.items():
        try:
            # ── H1 و H4 ──
            df1h = yf.download(ticker, start=now - timedelta(days=7),
                               end=end, interval='1h',
                               progress=False, auto_adjust=True)
            if not df1h.empty:
                if isinstance(df1h.columns, pd.MultiIndex):
                    df1h.columns = df1h.columns.get_level_values(0)
                df1h.index = pd.to_datetime(df1h.index).tz_localize(None)

                # H1 — آخر شمعة مغلقة
                h1_closed = df1h[df1h.index < now]
                if not h1_closed.empty:
                    data['H1'][pair] = h1_closed.iloc[-1]

                # H4 — تجميع من H1
                df4h = df1h.resample('4h').agg(
                    Open=('Open','first'), High=('High','max'),
                    Low=('Low','min'),   Close=('Close','last')
                ).dropna()
                h4_closed = df4h[df4h.index < now]
                if not h4_closed.empty:
                    data['H4'][pair] = h4_closed.iloc[-1]

            # ── Daily ──
            df1d = yf.download(ticker, start=now - timedelta(days=10),
                               end=end, interval='1d',
                               progress=False, auto_adjust=True)
            if not df1d.empty:
                if isinstance(df1d.columns, pd.MultiIndex):
                    df1d.columns = df1d.columns.get_level_values(0)
                df1d.index = pd.to_datetime(df1d.index).tz_localize(None)
                d_closed = df1d[df1d.index < now]
                if not d_closed.empty:
                    data['D'][pair] = d_closed.iloc[-1]

            # ── Weekly ──
            df1w = yf.download(ticker, start=now - timedelta(days=30),
                               end=end, interval='1wk',
                               progress=False, auto_adjust=True)
            if not df1w.empty:
                if isinstance(df1w.columns, pd.MultiIndex):
                    df1w.columns = df1w.columns.get_level_values(0)
                df1w.index = pd.to_datetime(df1w.index).tz_localize(None)
                w_closed = df1w[df1w.index < now]
                if not w_closed.empty:
                    data['W'][pair] = w_closed.iloc[-1]

            # ── Monthly ──
            df1mo = yf.download(ticker, start=start,
                                end=end, interval='1mo',
                                progress=False, auto_adjust=True)
            if not df1mo.empty:
                if isinstance(df1mo.columns, pd.MultiIndex):
                    df1mo.columns = df1mo.columns.get_level_values(0)
                df1mo.index = pd.to_datetime(df1mo.index).tz_localize(None)
                mo_closed = df1mo[df1mo.index < now]
                if not mo_closed.empty:
                    data['MN'][pair] = mo_closed.iloc[-1]

        except:
            pass

    return data

# ============================================================
# 2. حساب قوة العملات
# ============================================================
def calc_strength(tf_data):
    """
    tf_data: dict {pair: row} حيث row فيها Open و Close
    يرجع: dict {currency: score%}
    """
    scores   = {c: 0 for c in CURRENCIES}
    pair_dir = {}

    for pair in PAIRS_YF:
        if pair in tf_data:
            row = tf_data[pair]
            try:
                o = float(row['Open']); c = float(row['Close'])
                pair_dir[pair] = 1 if c > o else -1
            except:
                pair_dir[pair] = 0
        else:
            pair_dir[pair] = 0

    def add(curr, pair, d):
        if pair in pair_dir and pair_dir[pair] != 0:
            scores[curr] += 1 if pair_dir[pair] == d else 0

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

    return {c: round((scores[c] / 7) * 100) for c in CURRENCIES}

# ============================================================
# 3. حساب إشارات زوج واحد
# ============================================================
def get_pair_signals(pair, strengths, data):
    base, quote = pair[:3], pair[3:]
    results = []

    comparisons = [
        ('W',  'MN', 'W vs M'),
        ('D',  'W',  'D vs W'),
        ('H4', 'D',  'H4 vs D'),
        ('H1', 'H4', 'H1 vs H4'),
    ]

    for tf_small, tf_big, label in comparisons:
        s_small = strengths.get(tf_small, {})
        s_big   = strengths.get(tf_big,   {})

        if not s_small or not s_big:
            continue

        b_small = s_small.get(base);  q_small = s_small.get(quote)
        b_big   = s_big.get(base);    q_big   = s_big.get(quote)

        if any(x is None for x in [b_small, q_small, b_big, q_big]):
            continue

        score_small = b_small - q_small
        score_big   = b_big   - q_big

        if score_small == 0 or score_big == 0:
            continue

        acceleration = score_small - score_big

        # شرط السعر (مساحة)
        bar_small = data.get(tf_small, {}).get(pair)
        bar_big   = data.get(tf_big,   {}).get(pair)

        if bar_small is None or bar_big is None:
            continue

        try:
            high_small = float(bar_small['High']); low_small = float(bar_small['Low'])
            high_big   = float(bar_big['High']);   low_big   = float(bar_big['Low'])
            close_small= float(bar_small['Close'])
        except:
            continue

        # BUY
        if score_small > 0 and score_big > 0 and score_small > score_big:
            if high_small >= high_big:
                continue
            results.append({
                'pair':        pair,
                'comparison':  label,
                'signal':      'BUY',
                'score_small': score_small,
                'score_big':   score_big,
                'acceleration':round(acceleration, 2),
                'entry':       round(close_small, 5),
                'target':      round(high_big, 5),
            })

        # SELL
        elif score_small < 0 and score_big < 0 and score_small < score_big:
            if low_small <= low_big:
                continue
            results.append({
                'pair':        pair,
                'comparison':  label,
                'signal':      'SELL',
                'score_small': score_small,
                'score_big':   score_big,
                'acceleration':round(abs(acceleration), 2),
                'entry':       round(close_small, 5),
                'target':      round(low_big, 5),
            })

    return results

# ============================================================
# 4. حساب كل الإشارات
# ============================================================
def get_all_signals(data):
    # حساب الـ Strength لكل TF
    strengths = {tf: calc_strength(data[tf]) for tf in ['MN','W','D','H4','H1']}

    all_signals = []
    for pair in PAIRS_YF:
        all_signals.extend(get_pair_signals(pair, strengths, data))

    df = pd.DataFrame(all_signals)
    if not df.empty:
        df = df.sort_values('acceleration', ascending=False)
    return df, strengths

# ============================================================
# 5. عرض جدول
# ============================================================
def build_mtf_table(df_filtered, label):
    if df_filtered.empty:
        return f"<p style='color:#475569;'>لا توجد إشارات — {label}</p>"

    rows = ""
    for _, row in df_filtered.iterrows():
        sc, sbg   = signal_color(row['signal'])
        acc_color = '#10b981' if row['signal'] == 'BUY' else '#ef4444'
        tgt_color = '#10b981' if row['signal'] == 'BUY' else '#ef4444'

        rows += f"""
        <tr style="border-bottom:1px solid #1e293b;">
            <td style="font-weight:700;color:#e2e8f0;font-size:14px;">{row['pair']}</td>
            <td><span style="background:{sbg};color:{sc};border:1px solid {sc};
                         padding:4px 12px;border-radius:20px;font-weight:700;font-size:13px;">
                         {row['signal']}</span></td>
            <td style="color:{acc_color};font-weight:700;">+{row['acceleration']}</td>
            <td style="color:#94a3b8;">{row['score_small']:+.0f}</td>
            <td style="color:#64748b;">{row['score_big']:+.0f}</td>
            <td style="color:#e2e8f0;font-family:monospace;font-size:13px;">{row['entry']}</td>
            <td style="color:{tgt_color};font-family:monospace;font-size:13px;">{row['target']}</td>
        </tr>"""

    headers = ["Pair","Signal","⚡ Acc","Score Small","Score Big","Entry","🎯 Target"]
    h_html  = "".join([f"<th>{h}</th>" for h in headers])

    return f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <style>
        body{{margin:0;padding:0;background:transparent;
             font-family:-apple-system,BlinkMacSystemFont,sans-serif;}}
        table{{width:100%;border-collapse:collapse;
               background:linear-gradient(135deg,#0f172a,#1e293b);
               border-radius:12px;overflow:hidden;}}
        th{{background:#1e293b;color:#f1c40f;padding:10px 8px;
           text-align:left;font-size:12px;font-weight:600;
           border-bottom:2px solid #f1c40f;white-space:nowrap;}}
        tr:hover{{background:rgba(241,196,15,0.04);}}
        td{{padding:10px 8px;}}
    </style></head><body>
    <table><thead><tr>{h_html}</tr></thead>
    <tbody>{rows}</tbody></table></body></html>"""

# ============================================================
# 6. الـ Render الرئيسي
# ============================================================
def render_mtf_signals():
    now = datetime.utcnow()

    # ── هيدر ──
    col_t, col_r = st.columns([3, 1])
    with col_t:
        st.markdown("""
        <div style='background:#0f172a;border:1px solid rgba(241,196,15,0.2);
                    border-radius:12px;padding:14px 20px;margin-bottom:1rem;'>
            <span style='color:#f1c40f;font-size:15px;font-weight:700;'>
                📊 Multi-Timeframe Acceleration Signals
            </span><br>
            <span style='color:#64748b;font-size:11px;'>
                W vs M | D vs W | H4 vs D | H1 vs H4
            </span>
        </div>""", unsafe_allow_html=True)
    with col_r:
        st.markdown(f"""
        <div style='background:#0f172a;border:1px solid #1e293b;
                    border-radius:12px;padding:12px;text-align:center;'>
            <div style='color:#64748b;font-size:11px;'>UTC Now</div>
            <div style='color:#f1c40f;font-size:16px;font-weight:700;'>
                {now.strftime('%H:%M')}
            </div>
            <div style='color:#475569;font-size:10px;'>
                {now.strftime('%Y-%m-%d')}
            </div>
        </div>""", unsafe_allow_html=True)

    # ── جلب البيانات ──
    with st.spinner("⏳ جاري جلب البيانات..."):
        data = fetch_mtf_data()

    # ── حساب الإشارات ──
    df_all, strengths = get_all_signals(data)

    if df_all.empty:
        st.info("📭 لا توجد إشارات حالياً")
        if st.button("🔄 تحديث", key="refresh_mtf"):
            st.cache_data.clear()
            st.rerun()
        return

    # ── ملخص عام ──
    buy_total  = len(df_all[df_all['signal'] == 'BUY'])
    sell_total = len(df_all[df_all['signal'] == 'SELL'])
    summary_cards(buy_total, sell_total)
    st.markdown("---")

    # ── عرض Strength Table ──
    with st.expander("💪 Currency Strength by Timeframe", expanded=False):
        tf_labels = {'MN':'Monthly','W':'Weekly','D':'Daily','H4':'H4','H1':'H1'}
        strength_rows = ""
        for curr in CURRENCIES:
            flag = {"USD":"🇺🇸","EUR":"🇪🇺","GBP":"🇬🇧","JPY":"🇯🇵",
                    "CHF":"🇨🇭","CAD":"🇨🇦","AUD":"🇦🇺","NZD":"🇳🇿"}.get(curr,"")
            cells = f"<td style='font-weight:700;color:#e2e8f0;'>{flag} {curr}</td>"
            for tf in ['MN','W','D','H4','H1']:
                val = strengths.get(tf, {}).get(curr, 0)
                color = '#10b981' if val >= 57 else '#ef4444' if val <= 43 else '#94a3b8'
                cells += f"<td style='color:{color};font-weight:600;'>{val}%</td>"
            strength_rows += f"<tr style='border-bottom:1px solid #1e293b;'>{cells}</tr>"

        tf_heads = "".join([f"<th>{tf_labels[t]}</th>" for t in ['MN','W','D','H4','H1']])
        st.components.v1.html(f"""
        <!DOCTYPE html><html><head><meta charset="UTF-8">
        <style>
            body{{margin:0;padding:0;font-family:sans-serif;background:transparent;}}
            table{{width:100%;border-collapse:collapse;
                   background:#0f172a;border-radius:10px;overflow:hidden;}}
            th{{background:#1e293b;color:#f1c40f;padding:8px;font-size:12px;
               border-bottom:2px solid #f1c40f;}}
            td{{padding:8px;text-align:center;}}
        </style></head><body>
        <table><thead><tr><th>Currency</th>{tf_heads}</tr></thead>
        <tbody>{strength_rows}</tbody></table></body></html>
        """, height=280)

    st.markdown("---")

    # ── 4 جداول الإشارات ──
    comparisons = [
        ('W vs M',  '📅 Weekly vs Monthly',  'أكبر إطار'),
        ('D vs W',  '📆 Daily vs Weekly',    'إطار متوسط'),
        ('H4 vs D', '⏰ H4 vs Daily',        'إطار قصير'),
        ('H1 vs H4','⚡ H1 vs H4',           'أصغر إطار'),
    ]

    for comp_key, comp_label, comp_desc in comparisons:
        df_comp = df_all[df_all['comparison'] == comp_key]
        buy_c   = len(df_comp[df_comp['signal'] == 'BUY'])
        sell_c  = len(df_comp[df_comp['signal'] == 'SELL'])

        st.markdown(f"""
        <div style='background:#0f172a;border:1px solid #1e293b;
                    border-radius:10px;padding:10px 16px;margin:1rem 0 0.5rem;
                    display:flex;justify-content:space-between;align-items:center;'>
            <span style='color:#f1c40f;font-size:14px;font-weight:700;'>{comp_label}</span>
            <span style='color:#64748b;font-size:11px;'>{comp_desc}</span>
            <span>
                <span style='color:#10b981;font-weight:700;margin-left:12px;'>
                    ▲ {buy_c} BUY</span>
                <span style='color:#ef4444;font-weight:700;margin-left:12px;'>
                    ▼ {sell_c} SELL</span>
            </span>
        </div>""", unsafe_allow_html=True)

        if df_comp.empty:
            st.info(f"📭 لا توجد إشارات — {comp_label}")
        else:
            st.components.v1.html(
                build_mtf_table(df_comp, comp_label),
                height=max(150, len(df_comp) * 46 + 60),
                scrolling=True
            )

    # ── زر تحديث ──
    st.markdown("---")
    if st.button("🔄 تحديث يدوي", key="refresh_mtf"):
        st.cache_data.clear()
        st.rerun()

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
     "📊 MTF Acceleration",
])

with tab1:
    render_daily_signals(db_daily, db_economy, db_yield, db_weekly, db_monthly, selected_date)

with tab2:
    render_scalping_signals(db_daily, db_weekly, db_monthly, selected_date)

with tab3:
   render_mtf_signals()
