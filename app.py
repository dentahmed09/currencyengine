import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

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

# ══════════════════════════════════════════════════════════════
# ✅ CSS جديد تماماً - شكل احترافي وألوان محسّنة
# ══════════════════════════════════════════════════════════════
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
        
        /* ── Global ── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* ── Main Header ── */
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
        .main-header h1 {
            color: #f1c40f;
            margin: 0;
            font-size: 1.6rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .main-header p {
            color: #64748b;
            margin: 0.4rem 0 0;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        /* ── Date Selector Banner ── */
        .date-banner {
            background: #0f172a;
            border: 1px solid rgba(241,196,15,0.3);
            border-radius: 12px;
            padding: 0.8rem 1.2rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background: #0f172a;
            padding: 4px;
            border-radius: 10px;
            border: 1px solid #1e293b;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            font-size: 13px;
            font-weight: 500;
            color: #64748b;
            border: none;
        }
        .stTabs [aria-selected="true"] {
            background: #1e293b !important;
            color: #f1c40f !important;
        }

        /* ── Metric Cards ── */
        .metric-card {
            background: #0f172a;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            border: 1px solid #1e293b;
            transition: border-color 0.2s;
        }
        .metric-card:hover {
            border-color: rgba(241,196,15,0.3);
        }

        /* ── Section Headers ── */
        .section-header {
            font-size: 11px;
            font-weight: 600;
            color: #475569;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin: 1.5rem 0 0.75rem;
            padding-bottom: 6px;
            border-bottom: 1px solid #1e293b;
        }

        /* ── Tables ── */
        [data-testid="stMetric"] {
            background: #0f172a;
            border-radius: 10px;
            padding: 0.8rem;
            border: 1px solid #1e293b;
        }

        /* ── Buttons ── */
        .stButton button {
            background: #f1c40f;
            color: #0f172a;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            transition: all 0.15s;
        }
        .stButton button:hover {
            background: #e67e22;
            transform: translateY(-1px);
        }

        /* ── Selectbox ── */
        .stSelectbox > div > div {
            background: #0f172a;
            border-color: #1e293b;
            border-radius: 8px;
        }

        /* ── Dividers ── */
        hr { border-color: #1e293b; }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }
        
        /* ── Pair Cards ── */
        .pair-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 15px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border-left: 4px solid;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .pair-card:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .pair-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .pair-name {
            font-size: 1.3rem;
            font-weight: bold;
        }
        
        .pair-signal {
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.8rem;
        }
        
        .signal-buy {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid #10b981;
        }
        
        .signal-sell {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid #ef4444;
        }
        
        .signal-neutral {
            background: rgba(241, 196, 15, 0.2);
            color: #f1c40f;
            border: 1px solid #f1c40f;
        }
        
        .pair-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.8rem;
            margin: 1rem 0;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-label {
            font-size: 0.7rem;
            color: #94a3b8;
            margin-bottom: 0.3rem;
        }
        
        .stat-value {
            font-size: 1rem;
            font-weight: bold;
        }
        
        .score-bar {
            background: #334155;
            border-radius: 10px;
            height: 6px;
            overflow: hidden;
            margin-top: 0.5rem;
        }
        
        .score-fill {
            background: linear-gradient(90deg, #f1c40f, #e67e22);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s;
        }
        
        /* ── Form styling ── */
        .stForm {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid #334155;
        }
        
        /* ── Analytics Box ── */
        .analytics-box {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 15px;
            padding: 1.2rem;
            border: 1px solid #334155;
            margin-bottom: 1rem;
        }
        
        .analytics-title {
            color: #f1c40f;
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 1rem;
            border-bottom: 2px solid #f1c40f;
            display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)

## ==================== Sheet ID ====================
SHEET_ID = "1q_q9QGYHm0w7Z5nnO1Uq4NKLW1SoQCf5stbAMKoT3FE"

DAILY_WS   = "daily"
WEEKLY_WS  = "weekly"
MONTHLY_WS = "monthly"
ECONOMY_WS = "ECONOMY"    
YIELD_WS   = "YIELD"       

currencies = ["USD", "CAD", "EUR", "GBP", "CHF", "AUD", "NZD", "JPY"]

pairs = [
    "EURUSD","EURGBP","EURAUD","EURNZD","EURCAD","EURCHF","EURJPY",
    "GBPUSD","GBPAUD","GBPNZD","GBPCAD","GBPCHF","GBPJPY",
    "AUDUSD","AUDNZD","AUDCAD","AUDCHF","AUDJPY",
    "NZDUSD","NZDCAD","NZDCHF","NZDJPY",
    "USDCAD","USDCHF","USDJPY",
    "CADCHF","CADJPY","CHFJPY"
]

# ====================== Load & Save Functions ======================
def load_data(worksheet_name: str, date_col: str = "Date"):
    client = get_gspread_client()
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet(worksheet_name)
    data = ws.get_all_records()
    
    if not data:
        return pd.DataFrame(columns=[date_col] + currencies)
    
    df = pd.DataFrame(data)
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date
    df = df.dropna(subset=[date_col])
    return df.sort_values(date_col).reset_index(drop=True)

def save_data(df: pd.DataFrame, worksheet_name: str):
    client = get_gspread_client()
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet(worksheet_name)
    ws.clear()
    ws.update([df.columns.tolist()] + df.values.tolist())

# Inject custom CSS
inject_custom_css()

# ──── Main Header ────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏦 Institutional Currency Strength Engine</h1>
    <p>Multi-Timeframe Analysis | Economic Strength | Yield Data | Institutional Flow</p>
</div>
""", unsafe_allow_html=True)

# ====================== تحميل البيانات ======================
db_daily   = load_data(DAILY_WS, "Date")
db_weekly  = load_data(WEEKLY_WS, "Week_Start")
db_monthly = load_data(MONTHLY_WS, "Month_Start")
db_yield   = load_data(YIELD_WS, "Date")
db_economy = load_data(ECONOMY_WS, "Date")

# ══════════════════════════════════════════════════════════════
# ✅ 1. Date Selector موحد في أعلى الصفحة (قبل التبويبات)
# ══════════════════════════════════════════════════════════════
def render_unified_date_selector(db_daily):
    """
    يرجع التاريخ المختار ويخزنه في session_state['selected_date']
    استخدمه في كل التبويبات بدل ما كل تبويب يعمل selector منفصل
    """
    if db_daily.empty:
        return None

    db_daily['Date'] = pd.to_datetime(db_daily['Date']).dt.date
    all_dates = db_daily['Date'].sort_values(ascending=False).tolist()

    date_options = []
    date_map = {}
    for d in all_dates:
        ds = d.strftime("%Y-%m-%d")
        label = f"📅 {ds}  ·  Latest" if d == all_dates[0] else f"📅 {ds}"
        date_options.append(label)
        date_map[label] = d

    st.markdown("""
    <div style='background:#0f172a; border:1px solid rgba(241,196,15,0.25);
                border-radius:10px; padding:10px 16px; margin-bottom:1.2rem;
                display:flex; align-items:center; gap:8px;'>
        <span style='color:#f1c40f; font-size:13px; font-weight:600;'>DATE</span>
        <span style='color:#334155; font-size:11px;'>|</span>
        <span style='color:#64748b; font-size:11px;'>اختر التاريخ لعرض التحليل في جميع التبويبات</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_label = st.selectbox(
            "",
            options=date_options,
            index=0,
            key="global_date_selector",
            label_visibility="collapsed"
        )

    selected_date = date_map[selected_label]
    st.session_state['selected_date'] = selected_date
    return selected_date

# استدعاء الـ Unified Date Selector
selected_date = render_unified_date_selector(db_daily)
if selected_date is None:
    st.stop()

# ══════════════════════════════════════════════════════════════
# ✅ 3 & 4. ألوان جديدة للشارتات + عرض الشارتات فوق بعض
# ══════════════════════════════════════════════════════════════
CURRENCY_COLORS = {
    'USD': '#3b82f6',   # أزرق
    'EUR': '#f1c40f',   # ذهبي
    'GBP': '#a78bfa',   # بنفسجي فاتح
    'JPY': '#f43f5e',   # وردي أحمر
    'CHF': '#e2e8f0',   # أبيض فضي
    'CAD': '#fb923c',   # برتقالي
    'AUD': '#34d399',   # أخضر زمردي
    'NZD': '#22d3ee',   # سماوي
}

currencies_list = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']

def render_stacked_charts(db_economy, db_yield):
    """
    يرسم شارت الاقتصاد وشارت العوائد فوق بعض
    بعرض كامل للصفحة وبألوان مختلفة تماماً
    """

    # ── شارت الاقتصاد ──
    st.markdown('<div class="section-header">🏭 Economic Strength — All Currencies</div>',
                unsafe_allow_html=True)

    if not db_economy.empty:
        econ_data = db_economy.copy()
        econ_data['Date'] = pd.to_datetime(econ_data['Date'])
        econ_data = econ_data.sort_values('Date')

        fig_econ = go.Figure()

        for currency in currencies_list:
            if currency in econ_data.columns:
                cd = econ_data[['Date', currency]].dropna()
                if not cd.empty:
                    fig_econ.add_trace(go.Scatter(
                        x=cd['Date'],
                        y=cd[currency],
                        mode='lines',
                        name=currency,
                        line=dict(
                            color=CURRENCY_COLORS.get(currency, '#94a3b8'),
                            width=2
                        ),
                        hovertemplate=f'<b>{currency}</b>: %{{y:.2f}}<extra></extra>'
                    ))

        fig_econ.update_layout(
            height=380,
            template="plotly_dark",
            hovermode='x unified',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15,23,42,0.8)',
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.01,
                xanchor="center", x=0.5,
                font=dict(size=11),
                bgcolor='rgba(0,0,0,0)'
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(30,41,59,0.8)',
                tickfont=dict(size=10),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(30,41,59,0.8)',
                tickfont=dict(size=10),
                zeroline=True,
                zerolinecolor='rgba(241,196,15,0.4)',
                zerolinewidth=1.5,
            ),
        )
        fig_econ.add_hline(y=0, line_dash="dot",
                           line_color="rgba(241,196,15,0.3)",
                           line_width=1)

        st.plotly_chart(fig_econ, use_container_width=True, key="econ_chart_full")
    else:
        st.info("📊 لا توجد بيانات اقتصادية")

    # ── مسافة ──
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── شارت العوائد ──
    st.markdown('<div class="section-header">📈 Real Yield — All Currencies</div>',
                unsafe_allow_html=True)

    if not db_yield.empty:
        yield_data = db_yield.copy()
        yield_data['Date'] = pd.to_datetime(yield_data['Date'])
        yield_data = yield_data.sort_values('Date')

        fig_yield = go.Figure()

        for currency in currencies_list:
            if currency in yield_data.columns:
                cd = yield_data[['Date', currency]].dropna()
                if not cd.empty:
                    fig_yield.add_trace(go.Scatter(
                        x=cd['Date'],
                        y=cd[currency],
                        mode='lines',
                        name=currency,
                        line=dict(
                            color=CURRENCY_COLORS.get(currency, '#94a3b8'),
                            width=2
                        ),
                        hovertemplate=f'<b>{currency}</b>: %{{y:.2f}}%<extra></extra>'
                    ))

        fig_yield.update_layout(
            height=380,
            template="plotly_dark",
            hovermode='x unified',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15,23,42,0.8)',
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.01,
                xanchor="center", x=0.5,
                font=dict(size=11),
                bgcolor='rgba(0,0,0,0)'
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(30,41,59,0.8)',
                tickfont=dict(size=10),
            ),
            yaxis=dict(
                title=dict(text="Yield %", font=dict(size=10)),
                showgrid=True,
                gridcolor='rgba(30,41,59,0.8)',
                tickfont=dict(size=10),
                zeroline=True,
                zerolinecolor='rgba(241,196,15,0.4)',
                zerolinewidth=1.5,
            ),
        )
        fig_yield.add_hline(y=0, line_dash="dot",
                            line_color="rgba(241,196,15,0.3)",
                            line_width=1)

        st.plotly_chart(fig_yield, use_container_width=True, key="yield_chart_full")
    else:
        st.info("📊 لا توجد بيانات عوائد")

# ══════════════════════════════════════════════════════════════
# ✅ 2. Daily Dashboard الجديد (بدون Currency Cards)
# ══════════════════════════════════════════════════════════════
def render_dashboard_tab(db_daily, db_economy, db_yield, db_weekly, db_monthly, selected_date):

    if db_daily.empty:
        st.info("📊 Please enter daily data first")
        return

    db_daily['Date'] = pd.to_datetime(db_daily['Date']).dt.date
    selected_row = db_daily[db_daily['Date'] == selected_date]
    if selected_row.empty:
        st.error(f"❌ No data for {selected_date}")
        return

    current_data = selected_row.iloc[0]
    date_index = selected_row.index[0]
    prev_data = db_daily.iloc[date_index - 1] if date_index > 0 else None

    # Economy & Yield للتاريخ المختار
    economy_data_today = None
    yield_data_today = None
    if not db_economy.empty:
        db_economy['Date'] = pd.to_datetime(db_economy['Date']).dt.date
        eco_row = db_economy[db_economy['Date'] == selected_date]
        if not eco_row.empty:
            economy_data_today = eco_row.iloc[0]
    if not db_yield.empty:
        db_yield['Date'] = pd.to_datetime(db_yield['Date']).dt.date
        yld_row = db_yield[db_yield['Date'] == selected_date]
        if not yld_row.empty:
            yield_data_today = yld_row.iloc[0]

    def get_color(value):
        if value > 0: return "#10b981"
        elif value < 0: return "#ef4444"
        return "#475569"

    currency_flags = {
        "USD":"🇺🇸","EUR":"🇪🇺","GBP":"🇬🇧","JPY":"🇯🇵",
        "CHF":"🇨🇭","CAD":"🇨🇦","AUD":"🇦🇺","NZD":"🇳🇿"
    }
    currency_full_names = {
        "USD":"US Dollar","EUR":"Euro","GBP":"British Pound",
        "JPY":"Japanese Yen","CHF":"Swiss Franc","CAD":"Canadian Dollar",
        "AUD":"Australian Dollar","NZD":"New Zealand Dollar"
    }

    # ── Regional Power ──
    st.markdown('<div class="section-header">🌍 Regional Power</div>', unsafe_allow_html=True)

    us_power  = current_data[['USD','CAD']].mean()
    eu_power  = current_data[['GBP','EUR','CHF']].mean()
    asi_power = current_data[['AUD','NZD','JPY']].mean()

    r1, r2, r3 = st.columns(3)
    for col, label, emoji, power, members in [
        (r1, "Americas", "🇺🇸", us_power,  "USD · CAD"),
        (r2, "Europe",   "🇪🇺", eu_power,  "GBP · EUR · CHF"),
        (r3, "Asia-Pac", "🇯🇵", asi_power, "AUD · NZD · JPY"),
    ]:
        c = get_color(power)
        with col:
            st.markdown(f"""
            <div style='background:#0f172a; border:1px solid {c}40;
                        border-radius:14px; padding:20px; text-align:center;
                        border-top:2px solid {c};'>
                <div style='font-size:36px; margin-bottom:8px;'>{emoji}</div>
                <div style='font-size:13px; font-weight:600; color:#94a3b8;
                            letter-spacing:0.08em; text-transform:uppercase;'>{label}</div>
                <div style='font-size:30px; font-weight:700; color:{c};
                            margin:8px 0; font-family:"JetBrains Mono",monospace;'>{power:+.2f}</div>
                <div style='font-size:11px; color:#475569;'>{members}</div>
            </div>""", unsafe_allow_html=True)

    # Strongest Region
    powers = {'Americas': us_power, 'Europe': eu_power, 'Asia-Pac': asi_power}
    strongest = max(powers, key=powers.get)
    st.markdown(f"""
    <div style='background:#0f172a; border:1px solid #1e293b; border-radius:8px;
                padding:8px 16px; text-align:center; margin:12px 0;'>
        <span style='color:#475569; font-size:12px;'>Strongest Region</span>
        <span style='color:#f1c40f; font-weight:700; font-size:13px; margin-left:8px;'>
            {strongest} · {powers[strongest]:+.2f}
        </span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Currency Rankings ──
    st.markdown('<div class="section-header">📊 Currency Rankings</div>', unsafe_allow_html=True)

    col_eco, col_yld = st.columns(2)

    def render_ranking(col, title, icon, data_today, unit=""):
        with col:
            st.markdown(f"""
            <div style='background:#0f172a; border:1px solid #1e293b; border-radius:14px; padding:16px;'>
                <div style='text-align:center; margin-bottom:12px;'>
                    <span style='font-size:18px;'>{icon}</span>
                    <span style='color:#f1c40f; font-size:13px; font-weight:600;
                                 margin-left:6px; text-transform:uppercase;
                                 letter-spacing:0.06em;'>{title}</span>
                </div>""", unsafe_allow_html=True)

            if data_today is not None:
                ranking = []
                for curr in currencies_list:
                    if curr in data_today.index:
                        v = data_today[curr]
                        if pd.notna(v):
                            ranking.append({'curr': curr, 'val': v})
                ranking.sort(key=lambda x: x['val'], reverse=True)

                for idx, item in enumerate(ranking, 1):
                    medal = ["🥇","🥈","🥉"][idx-1] if idx <= 3 else f"{idx}."
                    vc = "#10b981" if item['val'] > 0 else "#ef4444"
                    flag = currency_flags.get(item['curr'], "")
                    st.markdown(f"""
                    <div style='display:flex; align-items:center; justify-content:space-between;
                                padding:8px 10px; margin:4px 0;
                                background:rgba(0,0,0,0.3); border-radius:8px;
                                border-left:2px solid {vc};'>
                        <div style='display:flex; align-items:center; gap:10px;'>
                            <span style='font-size:15px; min-width:28px;'>{medal}</span>
                            <span style='font-size:20px;'>{flag}</span>
                            <span style='font-weight:600; font-size:13px;'>{item['curr']}</span>
                        </div>
                        <span style='font-weight:700; font-size:14px; color:{vc};
                                     font-family:"JetBrains Mono",monospace;'>
                            {item['val']:+.2f}{unit}
                        </span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No data")

            st.markdown("</div>", unsafe_allow_html=True)

    render_ranking(col_eco, "Economic Power", "🏭", economy_data_today)
    render_ranking(col_yld, "Real Yield",     "📈", yield_data_today, unit="%")

    st.markdown("---")

    # ── Charts (فوق بعض) ──
    render_stacked_charts(db_economy, db_yield)

    st.markdown("---")

    # ── HTF Charts ──
    st.markdown('<div class="section-header">📈 Higher Time Frame — Currency Strength</div>',
                unsafe_allow_html=True)

    for i in range(0, len(currencies_list), 2):
        col1, col2 = st.columns(2)
        for col, currency in [(col1, currencies_list[i]),
                               (col2, currencies_list[i+1] if i+1 < len(currencies_list) else None)]:
            if currency is None:
                continue
            with col:
                full_name = currency_full_names.get(currency, currency)
                flag      = currency_flags.get(currency, "")
                st.markdown(f"**{flag} {currency}** — {full_name}")

                chart_data = pd.DataFrame()
                if not db_daily.empty:
                    d = db_daily[['Date', currency]].copy().rename(columns={currency:'Daily'})
                    chart_data = d
                if not db_weekly.empty:
                    db_weekly['Week_Start'] = pd.to_datetime(db_weekly['Week_Start']).dt.date
                    w = db_weekly[['Week_Start', currency]].copy().rename(
                        columns={'Week_Start':'Date', currency:'Weekly'})
                    chart_data = chart_data.merge(w, on='Date', how='outer') if not chart_data.empty else w
                if not db_monthly.empty:
                    db_monthly['Month_Start'] = pd.to_datetime(db_monthly['Month_Start']).dt.date
                    m = db_monthly[['Month_Start', currency]].copy().rename(
                        columns={'Month_Start':'Date', currency:'Monthly'})
                    chart_data = chart_data.merge(m, on='Date', how='outer') if not chart_data.empty else m

                if not chart_data.empty:
                    chart_data = chart_data.sort_values('Date').reset_index(drop=True)
                    fig = go.Figure()

                    trace_cfg = [
                        ('Daily',   CURRENCY_COLORS.get(currency,'#94a3b8'), 'solid',  2.5),
                        ('Weekly',  '#f1c40f',                                'dash',   2),
                        ('Monthly', '#e2e8f0',                                'dot',    2),
                    ]
                    for col_name, color, dash, width in trace_cfg:
                        if col_name in chart_data.columns:
                            cd = chart_data[chart_data[col_name].notna()]
                            if not cd.empty:
                                fig.add_trace(go.Scatter(
                                    x=cd['Date'], y=cd[col_name],
                                    mode='lines', name=col_name,
                                    line=dict(color=color, width=width, dash=dash),
                                ))

                    fig.update_layout(
                        height=280,
                        template="plotly_dark",
                        hovermode='x unified',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(15,23,42,0.8)',
                        margin=dict(l=0, r=0, t=4, b=0),
                        legend=dict(
                            orientation="h", yanchor="bottom", y=1.01,
                            xanchor="center", x=0.5, font=dict(size=10),
                            bgcolor='rgba(0,0,0,0)'
                        ),
                        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(30,41,59,0.6)',
                            zeroline=True,
                            zerolinecolor='rgba(241,196,15,0.3)',
                            tickfont=dict(size=9)
                        ),
                    )
                    fig.add_hline(y=0, line_dash="dot",
                                  line_color="rgba(241,196,15,0.25)", line_width=1)
                    st.plotly_chart(fig, use_container_width=True,
                                    key=f"htf_{currency}")
                else:
                    st.info(f"No data for {currency}")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# إنشاء التبويبات
# ══════════════════════════════════════════════════════════════
tab_dashboard, tab_results, tab_signal, tab_signal_engine = st.tabs([
    "🌍 Market Overview",
    "⚡ Scalping Signals", 
    "📊 Signal Matrix",
    "📅 Daily Signals",
])

# ──── Daily Dashboard Tab (باستخدام الدالة الجديدة) ─────────────────────────────────
with tab_dashboard:
    render_dashboard_tab(db_daily, db_economy, db_yield, db_weekly, db_monthly, selected_date)

# ──── تبويب Pair Matrix (باستخدام التاريخ الموحد) ─────────────────────
with tab_results:
    if db_daily.empty or len(db_daily) < 2:
        st.info("📊 أدخل بيانات يومين على الأقل لعرض النتائج")
    else:
        st.header("🎯 28 Pairs Results")
        
        # استخدام التاريخ الموحد من session_state
        selected_date = st.session_state.get('selected_date', db_daily['Date'].max())
        
        st.markdown(f"""
        <div style="text-align: center; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                    border-radius: 10px; padding: 8px; margin: 10px 0; border: 1px solid #f1c40f;">
            <span style="color: #f1c40f; font-weight: bold;">📅 التاريخ المختار: {selected_date.strftime('%Y-%m-%d')}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ================== حساب البيانات للتاريخ المختار ==================
        selected_row = db_daily[db_daily['Date'] == selected_date]
        
        if selected_row.empty:
            st.error(f"❌ لا توجد بيانات للتاريخ {selected_date}")
        else:
            latest = selected_row.iloc[0]
            
            date_index = db_daily[db_daily['Date'] == selected_date].index[0]
            if date_index > 0:
                prev_row = db_daily.iloc[date_index - 1]
                prev = prev_row
            else:
                prev = None
                st.warning("⚠️ هذا هو أول يوم في البيانات، لا توجد بيانات سابقة لحساب التغيرات")
            
            delta = {}
            if prev is not None:
                delta = {c: latest[c] - prev[c] for c in currencies}
            
            results = []
            
            for pair in pairs:
                base, quote = pair[:3], pair[3:]
                
                strength_today = latest[base] - latest[quote]
                
                if strength_today > 0:
                    signal = "BUY"
                    signal_color = "🟢"
                elif strength_today < 0:
                    signal = "SELL"
                    signal_color = "🔴"
                else:
                    signal = "WAIT"
                    signal_color = "🟡"
                
                max_strength = 5.0
                strength_percent = min(abs(strength_today) / max_strength * 100, 100)
                
                if prev is not None:
                    health_delta = (latest[base] - latest[quote]) - (prev[base] - prev[quote])
                    base_delta = delta[base]
                    quote_delta = delta[quote]
                    
                    if base_delta > health_delta and quote_delta > health_delta:
                        confirmation = "Up Trend"
                        conf_icon = "📈"
                        conf_color = "#10b981"
                    elif base_delta < health_delta and quote_delta < health_delta:
                        confirmation = "Down Trend"
                        conf_icon = "📉"
                        conf_color = "#ef4444"
                    else:
                        confirmation = "Range"
                        conf_icon = "🔄"
                        conf_color = "#f59e0b"
                    
                    volatility = abs(base_delta - quote_delta)
                else:
                    health_delta = 0
                    base_delta = 0
                    quote_delta = 0
                    confirmation = "No Data"
                    conf_icon = "❓"
                    conf_color = "#6b7280"
                    volatility = 0
                
                results.append({
                    "الزوج": pair,
                    "قوة الزوج": round(strength_today, 2),
                    "الإشارة": f"{signal_color} {signal}",
                    "القوة %": round(strength_percent, 0),
                    "Base Δ": round(base_delta, 2),
                    "Quote Δ": round(quote_delta, 2),
                    "Health Δ": round(health_delta, 2),
                    "Confirmation": confirmation,
                    "conf_icon": conf_icon,
                    "conf_color": conf_color,
                    "Volatility": round(volatility, 2),
                })
            
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values("قوة الزوج", ascending=False).reset_index(drop=True)
            
            # ================== عرض 28 كرت ==================
            for i in range(0, len(df_results), 2):
                col1, col2 = st.columns(2, gap="large")
                
                # ================== الكرت الأول ==================
                with col1:
                    row = df_results.iloc[i]
                    pair = row["الزوج"]
                    
                    if "BUY" in row["الإشارة"]:
                        bg_gradient = "linear-gradient(135deg, #0a2f1f, #051a0f)"
                        border_color = "#10b981"
                    elif "SELL" in row["الإشارة"]:
                        bg_gradient = "linear-gradient(135deg, #2f1a1a, #1a0a0a)"
                        border_color = "#ef4444"
                    else:
                        bg_gradient = "linear-gradient(135deg, #2d2a1a, #1f1c0f)"
                        border_color = "#f59e0b"
                    
                    base_delta_color = "#10b981" if row['Base Δ'] >= 0 else "#ef4444"
                    quote_delta_color = "#10b981" if row['Quote Δ'] >= 0 else "#ef4444"
                    health_delta_color = "#10b981" if row['Health Δ'] >= 0 else "#ef4444"
                    
                    card_html = f'''
                    <div style="background: {bg_gradient}; padding: 20px; border-radius: 20px; margin: 10px 0; border: 2px solid {border_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h2 style="margin:0; color: {border_color}; font-size: 28px;">{pair}</h2>
                            <h1 style="margin:0; font-size: 42px;">{row['الإشارة']}</h1>
                        </div>
                        <div style="background: rgba(0,0,0,0.5); border-radius: 12px; padding: 15px; margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="font-size: 18px;">📊 قوة الزوج:</span>
                                <span style="font-size: 24px; font-weight: bold; color: {border_color};">{row['قوة الزوج']:+.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-size: 18px;">⚡ قوة الإشارة:</span>
                                <span style="font-size: 20px; font-weight: bold;">{row['القوة %']:.0f}%</span>
                            </div>
                        </div>
                        <div style="background: rgba(0,0,0,0.4); border-radius: 12px; padding: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 14px; color: #9ca3af;">📈 BASE Δ</div>
                                    <div style="font-size: 20px; font-weight: bold; color: {base_delta_color};">{row['Base Δ']:+.2f}</div>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 14px; color: #9ca3af;">📉 QUOTE Δ</div>
                                    <div style="font-size: 20px; font-weight: bold; color: {quote_delta_color};">{row['Quote Δ']:+.2f}</div>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 14px; color: #9ca3af;">💚 HEALTH Δ</div>
                                    <div style="font-size: 20px; font-weight: bold; color: {health_delta_color};">{row['Health Δ']:+.2f}</div>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 14px; color: #9ca3af;">📊 VOLATILITY</div>
                                    <div style="font-size: 20px; font-weight: bold; color: #f59e0b;">{row['Volatility']:.2f}</div>
                                </div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: {row['conf_color']}20; border-radius: 10px; border: 1px solid {row['conf_color']};">
                                <span style="font-size: 18px;">{row['conf_icon']}</span>
                                <span style="font-size: 16px; font-weight: bold; color: {row['conf_color']};"> {row['Confirmation']}</span>
                            </div>
                        </div>
                    </div>
                    '''
                    st.markdown(card_html, unsafe_allow_html=True)
                
                # ================== الكرت الثاني ==================
                with col2:
                    if i + 1 < len(df_results):
                        row = df_results.iloc[i + 1]
                        pair = row["الزوج"]
                        
                        if "BUY" in row["الإشارة"]:
                            bg_gradient = "linear-gradient(135deg, #0a2f1f, #051a0f)"
                            border_color = "#10b981"
                        elif "SELL" in row["الإشارة"]:
                            bg_gradient = "linear-gradient(135deg, #2f1a1a, #1a0a0a)"
                            border_color = "#ef4444"
                        else:
                            bg_gradient = "linear-gradient(135deg, #2d2a1a, #1f1c0f)"
                            border_color = "#f59e0b"
                        
                        base_delta_color = "#10b981" if row['Base Δ'] >= 0 else "#ef4444"
                        quote_delta_color = "#10b981" if row['Quote Δ'] >= 0 else "#ef4444"
                        health_delta_color = "#10b981" if row['Health Δ'] >= 0 else "#ef4444"
                        
                        card_html = f'''
                        <div style="background: {bg_gradient}; padding: 20px; border-radius: 20px; margin: 10px 0; border: 2px solid {border_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                                <h2 style="margin:0; color: {border_color}; font-size: 28px;">{pair}</h2>
                                <h1 style="margin:0; font-size: 42px;">{row['الإشارة']}</h1>
                            </div>
                            <div style="background: rgba(0,0,0,0.5); border-radius: 12px; padding: 15px; margin-bottom: 15px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                    <span style="font-size: 18px;">📊 قوة الزوج:</span>
                                    <span style="font-size: 24px; font-weight: bold; color: {border_color};">{row['قوة الزوج']:+.2f}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="font-size: 18px;">⚡ قوة الإشارة:</span>
                                    <span style="font-size: 20px; font-weight: bold;">{row['القوة %']:.0f}%</span>
                                </div>
                            </div>
                            <div style="background: rgba(0,0,0,0.4); border-radius: 12px; padding: 15px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                    <div style="flex: 1; text-align: center;">
                                        <div style="font-size: 14px; color: #9ca3af;">📈 BASE Δ</div>
                                        <div style="font-size: 20px; font-weight: bold; color: {base_delta_color};">{row['Base Δ']:+.2f}</div>
                                    </div>
                                    <div style="flex: 1; text-align: center;">
                                        <div style="font-size: 14px; color: #9ca3af;">📉 QUOTE Δ</div>
                                        <div style="font-size: 20px; font-weight: bold; color: {quote_delta_color};">{row['Quote Δ']:+.2f}</div>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                    <div style="flex: 1; text-align: center;">
                                        <div style="font-size: 14px; color: #9ca3af;">💚 HEALTH Δ</div>
                                        <div style="font-size: 20px; font-weight: bold; color: {health_delta_color};">{row['Health Δ']:+.2f}</div>
                                    </div>
                                    <div style="flex: 1; text-align: center;">
                                        <div style="font-size: 14px; color: #9ca3af;">📊 VOLATILITY</div>
                                        <div style="font-size: 20px; font-weight: bold; color: #f59e0b;">{row['Volatility']:.2f}</div>
                                    </div>
                                </div>
                                <div style="text-align: center; padding: 8px; background: {row['conf_color']}20; border-radius: 10px; border: 1px solid {row['conf_color']};">
                                    <span style="font-size: 18px;">{row['conf_icon']}</span>
                                    <span style="font-size: 16px; font-weight: bold; color: {row['conf_color']};"> {row['Confirmation']}</span>
                                </div>
                            </div>
                        </div>
                        '''
                        st.markdown(card_html, unsafe_allow_html=True)

# ──── Signal Matrix Tab (باستخدام التاريخ الموحد) ─────────────────────
with tab_signal:
    st.header("📊 Signal Matrix - Multi-Timeframe Currency Strength")
    st.caption("Economic • Yield • Monthly • Weekly • Daily — White = Current Value, Arrow = Change vs Previous")
    
    if db_daily.empty:
        st.info("📊 Please enter daily data first")
    else:
        # استخدام التاريخ الموحد من session_state
        selected_date = st.session_state.get('selected_date', db_daily['Date'].max())
        
        st.markdown(f"""
        <div style="text-align: center; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                    border-radius: 10px; padding: 8px; margin: 10px 0; border: 1px solid #f1c40f;">
            <span style="color: #f1c40f; font-weight: bold;">📅 Selected Date: {selected_date.strftime('%Y-%m-%d')}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ================== Calculate Data for Selected Date ==================
        if isinstance(selected_date, pd.Timestamp):
            selected_date = selected_date.date()
        
        selected_row = db_daily[db_daily['Date'] == selected_date]
        
        if selected_row.empty:
            st.error(f"❌ No data found for {selected_date}")
        else:
            latest = selected_row.iloc[0]
            
            date_index = db_daily[db_daily['Date'] == selected_date].index[0]
            if date_index > 0:
                prev_row = db_daily.iloc[date_index - 1]
                prev = prev_row
            else:
                prev = None
            
            # ================== Get Economy data ==================
            economy_today = None
            economy_prev = None
            if not db_economy.empty:
                db_economy['Date'] = pd.to_datetime(db_economy['Date']).dt.date
                eco_today_row = db_economy[db_economy['Date'] == selected_date]
                if not eco_today_row.empty:
                    economy_today = eco_today_row.iloc[0]
                    eco_idx = db_economy[db_economy['Date'] == selected_date].index[0]
                    if eco_idx > 0:
                        economy_prev = db_economy.iloc[eco_idx - 1]
            
            # ================== Get Yield data ==================
            yield_today = None
            yield_prev = None
            if not db_yield.empty:
                db_yield['Date'] = pd.to_datetime(db_yield['Date']).dt.date
                yld_today_row = db_yield[db_yield['Date'] == selected_date]
                if not yld_today_row.empty:
                    yield_today = yld_today_row.iloc[0]
                    yld_idx = db_yield[db_yield['Date'] == selected_date].index[0]
                    if yld_idx > 0:
                        yield_prev = db_yield.iloc[yld_idx - 1]
            
            # Get Weekly data
            selected_date_obj = pd.to_datetime(selected_date)
            week_start = (selected_date_obj - pd.Timedelta(days=selected_date_obj.weekday())).date()
            
            weekly_current = {}
            weekly_prev_val = {}
            
            if not db_weekly.empty:
                db_weekly['Week_Start'] = pd.to_datetime(db_weekly['Week_Start']).dt.date
                weekly_sorted = db_weekly.sort_values('Week_Start')
                weekly_current_row = db_weekly[db_weekly['Week_Start'] == week_start]
                
                if not weekly_current_row.empty:
                    weekly_idx = db_weekly[db_weekly['Week_Start'] == week_start].index[0]
                    for curr in currencies:
                        if curr in weekly_current_row.columns and pd.notna(weekly_current_row.iloc[0][curr]):
                            weekly_current[curr] = weekly_current_row.iloc[0][curr]
                            if weekly_idx > 0:
                                prev_week_val = db_weekly.iloc[weekly_idx - 1][curr]
                                weekly_prev_val[curr] = prev_week_val if pd.notna(prev_week_val) else weekly_current[curr]
                            else:
                                weekly_prev_val[curr] = weekly_current[curr]
                        else:
                            weekly_current[curr] = latest[curr] if curr in latest.index else 0
                            weekly_prev_val[curr] = weekly_current[curr]
                else:
                    for curr in currencies:
                        weekly_current[curr] = latest[curr] if curr in latest.index else 0
                        weekly_prev_val[curr] = weekly_current[curr]
            else:
                for curr in currencies:
                    weekly_current[curr] = latest[curr] if curr in latest.index else 0
                    weekly_prev_val[curr] = weekly_current[curr]
            
            # Get Monthly data
            month_start = selected_date_obj.replace(day=1).date()
            
            monthly_current = {}
            monthly_prev_val = {}
            
            if not db_monthly.empty:
                db_monthly['Month_Start'] = pd.to_datetime(db_monthly['Month_Start']).dt.date
                monthly_sorted = db_monthly.sort_values('Month_Start')
                monthly_current_row = db_monthly[db_monthly['Month_Start'] == month_start]
                
                if not monthly_current_row.empty:
                    monthly_idx = db_monthly[db_monthly['Month_Start'] == month_start].index[0]
                    for curr in currencies:
                        if curr in monthly_current_row.columns and pd.notna(monthly_current_row.iloc[0][curr]):
                            monthly_current[curr] = monthly_current_row.iloc[0][curr]
                            if monthly_idx > 0:
                                prev_month_val = db_monthly.iloc[monthly_idx - 1][curr]
                                monthly_prev_val[curr] = prev_month_val if pd.notna(prev_month_val) else monthly_current[curr]
                            else:
                                monthly_prev_val[curr] = monthly_current[curr]
                        else:
                            monthly_current[curr] = latest[curr] if curr in latest.index else 0
                            monthly_prev_val[curr] = monthly_current[curr]
                else:
                    for curr in currencies:
                        monthly_current[curr] = latest[curr] if curr in latest.index else 0
                        monthly_prev_val[curr] = monthly_current[curr]
            else:
                for curr in currencies:
                    monthly_current[curr] = latest[curr] if curr in latest.index else 0
                    monthly_prev_val[curr] = monthly_current[curr]
            
            # Helper functions
            def get_arrow_color(current_val, prev_val):
                if current_val is None or prev_val is None or pd.isna(current_val) or pd.isna(prev_val):
                    return "#f1c40f"
                if current_val > prev_val:
                    return "#10b981"
                elif current_val < prev_val:
                    return "#ef4444"
                else:
                    return "#f1c40f"
            
            def get_arrow_symbol(current_val, prev_val):
                if current_val is None or prev_val is None or pd.isna(current_val) or pd.isna(prev_val):
                    return "●"
                if current_val > prev_val:
                    return "▲"
                elif current_val < prev_val:
                    return "▼"
                else:
                    return "●"
            
            # Currency names and flags
            currency_full_names = {
                "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound",
                "JPY": "Japanese Yen", "CHF": "Swiss Franc", "CAD": "Canadian Dollar",
                "AUD": "Australian Dollar", "NZD": "New Zealand Dollar"
            }
            
            currency_flags = {
                "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
                "CHF": "🇨🇭", "CAD": "🇨🇦", "AUD": "🇦🇺", "NZD": "🇳🇿"
            }
            
            currencies_list = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]
            
            # ================== 1. Currency Snapshot Cards ==================
            st.subheader("💱 Currency Snapshot")
            
            cols_row1 = st.columns(4)
            for idx, curr in enumerate(currencies_list[:4]):
                with cols_row1[idx]:
                    curr_val = latest[curr] if curr in latest.index else 0
                    curr_prev = prev[curr] if prev is not None and curr in prev.index else curr_val
                    
                    eco_val = economy_today[curr] if economy_today is not None and curr in economy_today.index and pd.notna(economy_today[curr]) else None
                    eco_prev = economy_prev[curr] if economy_prev is not None and curr in economy_prev.index and pd.notna(economy_prev[curr]) else eco_val
                    
                    yld_val = yield_today[curr] if yield_today is not None and curr in yield_today.index and pd.notna(yield_today[curr]) else None
                    yld_prev = yield_prev[curr] if yield_prev is not None and curr in yield_prev.index and pd.notna(yield_prev[curr]) else yld_val
                    
                    if eco_val is not None and eco_prev is not None:
                        eco_delta = eco_val - eco_prev
                        eco_str = f"{eco_delta:+.2f}"
                    else:
                        eco_str = "N/A"
                        
                    if yld_val is not None and yld_prev is not None:
                        yld_delta = yld_val - yld_prev
                        yld_str = f"{yld_delta:+.2f}%"
                    else:
                        yld_str = "N/A"
                    
                    daily_delta = curr_val - curr_prev if prev is not None else 0
                    daily_arrow = get_arrow_symbol(daily_delta, 0)
                    daily_arrow_color = get_arrow_color(daily_delta, 0)
                    
                    weekly_curr = weekly_current.get(curr, curr_val)
                    weekly_prev_v = weekly_prev_val.get(curr, weekly_curr)
                    weekly_delta = weekly_curr - weekly_prev_v
                    weekly_arrow = get_arrow_symbol(weekly_delta, 0)
                    weekly_arrow_color = get_arrow_color(weekly_delta, 0)
                    
                    monthly_curr = monthly_current.get(curr, curr_val)
                    monthly_prev_v = monthly_prev_val.get(curr, monthly_curr)
                    monthly_delta = monthly_curr - monthly_prev_v
                    monthly_arrow = get_arrow_symbol(monthly_delta, 0)
                    monthly_arrow_color = get_arrow_color(monthly_delta, 0)
                    
                    eco_arrow = get_arrow_symbol(eco_val, eco_prev)
                    eco_arrow_color = get_arrow_color(eco_val, eco_prev)
                    
                    yld_arrow = get_arrow_symbol(yld_val, yld_prev)
                    yld_arrow_color = get_arrow_color(yld_val, yld_prev)
                    
                    flag = currency_flags.get(curr, "💰")
                    full_name = currency_full_names.get(curr, curr)
                    
                    card_html = f'''
                    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                                border-radius: 12px; padding: 14px; margin: 5px 0; 
                                border: 1px solid #334155; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px; border-bottom: 1px solid #334155; padding-bottom: 6px;">
                            <span style="font-size: 24px;">{flag}</span>
                            <div>
                                <div style="font-weight: bold; color: #f1c40f; font-size: 16px;">{curr}</div>
                                <div style="font-size: 9px; color: #64748b;">{full_name}</div>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 5px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">🏭 Economic Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {eco_arrow_color};">{eco_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{eco_str}</span></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📈 Yield Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {yld_arrow_color};">{yld_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{yld_str}</span></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📅 Daily Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {daily_arrow_color};">{daily_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{daily_delta:+.2f}</span></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📆 Weekly Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {weekly_arrow_color};">{weekly_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{weekly_delta:+.2f}</span></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">🗓️ Monthly Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {monthly_arrow_color};">{monthly_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{monthly_delta:+.2f}</span></span>
                            </div>
                        </div>
                    </div>
                    '''
                    st.markdown(card_html, unsafe_allow_html=True)
            
            cols_row2 = st.columns(4)
            for idx, curr in enumerate(currencies_list[4:]):
                with cols_row2[idx]:
                    curr_val = latest[curr] if curr in latest.index else 0
                    curr_prev = prev[curr] if prev is not None and curr in prev.index else curr_val
                    
                    eco_val = economy_today[curr] if economy_today is not None and curr in economy_today.index and pd.notna(economy_today[curr]) else None
                    eco_prev = economy_prev[curr] if economy_prev is not None and curr in economy_prev.index and pd.notna(economy_prev[curr]) else eco_val
                    
                    yld_val = yield_today[curr] if yield_today is not None and curr in yield_today.index and pd.notna(yield_today[curr]) else None
                    yld_prev = yield_prev[curr] if yield_prev is not None and curr in yield_prev.index and pd.notna(yield_prev[curr]) else yld_val
                    
                    if eco_val is not None and eco_prev is not None:
                        eco_delta = eco_val - eco_prev
                        eco_str = f"{eco_delta:+.2f}"
                    else:
                        eco_str = "N/A"
                        
                    if yld_val is not None and yld_prev is not None:
                        yld_delta = yld_val - yld_prev
                        yld_str = f"{yld_delta:+.2f}%"
                    else:
                        yld_str = "N/A"
                    
                    daily_delta = curr_val - curr_prev if prev is not None else 0
                    daily_arrow = get_arrow_symbol(daily_delta, 0)
                    daily_arrow_color = get_arrow_color(daily_delta, 0)
                    
                    weekly_curr = weekly_current.get(curr, curr_val)
                    weekly_prev_v = weekly_prev_val.get(curr, weekly_curr)
                    weekly_delta = weekly_curr - weekly_prev_v
                    weekly_arrow = get_arrow_symbol(weekly_delta, 0)
                    weekly_arrow_color = get_arrow_color(weekly_delta, 0)
                    
                    monthly_curr = monthly_current.get(curr, curr_val)
                    monthly_prev_v = monthly_prev_val.get(curr, monthly_curr)
                    monthly_delta = monthly_curr - monthly_prev_v
                    monthly_arrow = get_arrow_symbol(monthly_delta, 0)
                    monthly_arrow_color = get_arrow_color(monthly_delta, 0)
                    
                    eco_arrow = get_arrow_symbol(eco_val, eco_prev)
                    eco_arrow_color = get_arrow_color(eco_val, eco_prev)
                    
                    yld_arrow = get_arrow_symbol(yld_val, yld_prev)
                    yld_arrow_color = get_arrow_color(yld_val, yld_prev)
                    
                    flag = currency_flags.get(curr, "💰")
                    full_name = currency_full_names.get(curr, curr)
                    
                    card_html = f'''
                    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                                border-radius: 12px; padding: 14px; margin: 5px 0; 
                                border: 1px solid #334155; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px; border-bottom: 1px solid #334155; padding-bottom: 6px;">
                            <span style="font-size: 24px;">{flag}</span>
                            <div>
                                <div style="font-weight: bold; color: #f1c40f; font-size: 16px;">{curr}</div>
                                <div style="font-size: 9px; color: #64748b;">{full_name}</div>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 5px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">🏭 Economic Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {eco_arrow_color};">{eco_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{eco_str}</span></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📈 Yield Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {yld_arrow_color};">{yld_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{yld_str}</span></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📅 Daily Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {daily_arrow_color};">{daily_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{daily_delta:+.2f}</span></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📆 Weekly Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {weekly_arrow_color};">{weekly_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{weekly_delta:+.2f}</span></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">🗓️ Monthly Δ:</span>
                                <span><span style="font-weight: bold; font-size: 12px; color: {monthly_arrow_color};">{monthly_arrow}</span> <span style="font-weight: bold; font-size: 12px; color: white;">{monthly_delta:+.2f}</span></span>
                            </div>
                        </div>
                    </div>
                    '''
                    st.markdown(card_html, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ================== Pairs Signal Matrix ==================
            st.subheader("📈 Pairs Signal Matrix")
            st.caption("Economic • Yield • Monthly • Weekly • Daily — White = Current Value, Arrow = Change vs Previous")
            
            pairs_ordered = [
                "EURUSD", "EURGBP", "EURAUD", "EURNZD", "EURCAD", "EURCHF", "EURJPY",
                "GBPUSD", "GBPAUD", "GBPNZD", "GBPCAD", "GBPCHF", "GBPJPY",
                "AUDUSD", "AUDNZD", "AUDCAD", "AUDCHF", "AUDJPY",
                "NZDUSD", "NZDCAD", "NZDCHF", "NZDJPY",
                "USDCAD", "USDCHF", "USDJPY",
                "CADCHF", "CADJPY", "CHFJPY"
            ]
            
            table_data = []
            
            for pair in pairs_ordered:
                base, quote = pair[:3], pair[3:]
                
                # Economic
                eco_current = None
                eco_prev = None
                if economy_today is not None and economy_prev is not None:
                    if base in economy_today.index and quote in economy_today.index and base in economy_prev.index and quote in economy_prev.index:
                        if pd.notna(economy_today[base]) and pd.notna(economy_today[quote]):
                            eco_current = economy_today[base] - economy_today[quote]
                            eco_prev = economy_prev[base] - economy_prev[quote]
                
                eco_arrow = get_arrow_symbol(eco_current, eco_prev)
                eco_arrow_color = get_arrow_color(eco_current, eco_prev)
                eco_display = f"{eco_current:+.2f}" if eco_current is not None else "N/A"
                
                # Yield
                yld_current = None
                yld_prev = None
                if yield_today is not None and yield_prev is not None:
                    if base in yield_today.index and quote in yield_today.index and base in yield_prev.index and quote in yield_prev.index:
                        if pd.notna(yield_today[base]) and pd.notna(yield_today[quote]):
                            yld_current = yield_today[base] - yield_today[quote]
                            yld_prev = yield_prev[base] - yield_prev[quote]
                
                yld_arrow = get_arrow_symbol(yld_current, yld_prev)
                yld_arrow_color = get_arrow_color(yld_current, yld_prev)
                yld_display = f"{yld_current:+.2f}" if yld_current is not None else "N/A"
                
                # Monthly
                m_base = monthly_current.get(base, 0)
                m_quote = monthly_current.get(quote, 0)
                m_base_prev = monthly_prev_val.get(base, m_base)
                m_quote_prev = monthly_prev_val.get(quote, m_quote)
                monthly_pair_current = m_base - m_quote
                monthly_pair_prev = m_base_prev - m_quote_prev
                
                monthly_arrow = get_arrow_symbol(monthly_pair_current, monthly_pair_prev)
                monthly_arrow_color = get_arrow_color(monthly_pair_current, monthly_pair_prev)
                monthly_display = f"{monthly_pair_current:+.2f}"
                
                # Weekly
                w_base = weekly_current.get(base, 0)
                w_quote = weekly_current.get(quote, 0)
                w_base_prev = weekly_prev_val.get(base, w_base)
                w_quote_prev = weekly_prev_val.get(quote, w_quote)
                weekly_pair_current = w_base - w_quote
                weekly_pair_prev = w_base_prev - w_quote_prev
                
                weekly_arrow = get_arrow_symbol(weekly_pair_current, weekly_pair_prev)
                weekly_arrow_color = get_arrow_color(weekly_pair_current, weekly_pair_prev)
                weekly_display = f"{weekly_pair_current:+.2f}"
                
                # Daily
                daily_current = latest.get(base, 0) - latest.get(quote, 0)
                daily_prev = (prev.get(base, 0) - prev.get(quote, 0)) if prev is not None else daily_current
                
                daily_arrow = get_arrow_symbol(daily_current, daily_prev)
                daily_arrow_color = get_arrow_color(daily_current, daily_prev)
                daily_display = f"{daily_current:+.2f}"
                
                table_data.append({
                    "Pair": pair,
                    "Economic": eco_display, "Economic_Arrow": eco_arrow, "Economic_Arrow_Color": eco_arrow_color,
                    "Yield": yld_display, "Yield_Arrow": yld_arrow, "Yield_Arrow_Color": yld_arrow_color,
                    "Monthly": monthly_display, "Monthly_Arrow": monthly_arrow, "Monthly_Arrow_Color": monthly_arrow_color,
                    "Weekly": weekly_display, "Weekly_Arrow": weekly_arrow, "Weekly_Arrow_Color": weekly_arrow_color,
                    "Daily": daily_display, "Daily_Arrow": daily_arrow, "Daily_Arrow_Color": daily_arrow_color,
                })
            
            # ================== HTML Table كامل ==================
            table_html = """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background: transparent;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                }
                .signal-table {
                    width: 100%;
                    border-collapse: collapse;
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    border-radius: 12px;
                    overflow: hidden;
                }
                .signal-table th {
                    background: #1e293b;
                    color: #f1c40f;
                    padding: 14px 8px;
                    text-align: center;
                    font-weight: 600;
                    font-size: 13px;
                    border-bottom: 2px solid #f1c40f;
                }
                .signal-table td {
                    padding: 11px 8px;
                    text-align: center;
                    border-bottom: 1px solid #334155;
                    font-size: 13.5px;
                    font-weight: 500;
                }
                .signal-table tr:hover {
                    background: rgba(241, 196, 15, 0.06);
                }
                .pair-cell {
                    font-weight: 700;
                    color: #e2e8f0;
                }
            </style>
            </head>
            <body>
            <table class="signal-table">
                <thead>
                    <tr>
                        <th>Pair</th>
                        <th>🏭 Economic</th>
                        <th>📈 Yield</th>
                        <th>🗓️ Monthly</th>
                        <th>📆 Weekly</th>
                        <th>📅 Daily</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for row in table_data:
                table_html += f"""
                    <tr>
                        <td class="pair-cell">{row['Pair']}</td>
                        <td><span style="font-weight: bold; color: {row['Economic_Arrow_Color']};">{row['Economic_Arrow']}</span> <span style="font-weight: bold; color: white;">{row['Economic']}</span></td>
                        <td><span style="font-weight: bold; color: {row['Yield_Arrow_Color']};">{row['Yield_Arrow']}</span> <span style="font-weight: bold; color: white;">{row['Yield']}</span></td>
                        <td><span style="font-weight: bold; color: {row['Monthly_Arrow_Color']};">{row['Monthly_Arrow']}</span> <span style="font-weight: bold; color: white;">{row['Monthly']}</span></td>
                        <td><span style="font-weight: bold; color: {row['Weekly_Arrow_Color']};">{row['Weekly_Arrow']}</span> <span style="font-weight: bold; color: white;">{row['Weekly']}</span></td>
                        <td><span style="font-weight: bold; color: {row['Daily_Arrow_Color']};">{row['Daily_Arrow']}</span> <span style="font-weight: bold; color: white;">{row['Daily']}</span></td>
                    </tr>
                """
            
            table_html += """
                </tbody>
            </table>
            </body>
            </html>
            """
            
            st.components.v1.html(table_html, height=680, scrolling=True)
            
            # Legend
            st.markdown("---")
            st.markdown("""
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; padding: 10px;">
                <div style="display: flex; align-items: center; gap: 8px;"><span style="color: #10b981; font-size: 20px;">▲</span> <span style="color: #94a3b8;">Increasing (Up Arrow)</span></div>
                <div style="display: flex; align-items: center; gap: 8px;"><span style="color: #ef4444; font-size: 20px;">▼</span> <span style="color: #94a3b8;">Decreasing (Down Arrow)</span></div>
                <div style="display: flex; align-items: center; gap: 8px;"><span style="color: #f1c40f; font-size: 20px;">●</span> <span style="color: #94a3b8;">Unchanged / No Change</span></div>
                <div style="display: flex; align-items: center; gap: 8px;"><span style="color: white; font-size: 16px; font-weight: bold;">+2.45</span> <span style="color: #94a3b8;">Value (always white)</span></div>
            </div>
            """, unsafe_allow_html=True)

# ──── Signal Engine Tab (باستخدام التاريخ الموحد) ─────────────────────
with tab_signal_engine:
    st.header("📡 Signal Engine")
    st.caption("نظام الإشارات المبني على الأولوية: Economic → Yield → Daily")

    if db_daily.empty or db_economy.empty:
        st.info("📊 يرجى إدخال بيانات Daily و ECONOMY أولاً")
    else:
        # استخدام التاريخ الموحد من session_state
        sel_date_se = st.session_state.get('selected_date', db_daily['Date'].max())

        # ══════════════════════════════════════════
        # 2. جلب بيانات اليوم والأمس
        # ══════════════════════════════════════════
        def get_row_and_prev(df, date_col, sel_date):
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
            row = df[df[date_col] == sel_date]
            if row.empty:
                return None, None
            idx = row.index[0]
            curr = row.iloc[0]
            prev = df.iloc[idx - 1] if idx > 0 else None
            return curr, prev

        daily_curr, daily_prev   = get_row_and_prev(db_daily,   'Date', sel_date_se)
        eco_curr,   eco_prev     = get_row_and_prev(db_economy,  'Date', sel_date_se)
        yield_curr, yield_prev   = get_row_and_prev(db_yield,    'Date', sel_date_se) if not db_yield.empty else (None, None)

        if daily_curr is None or eco_curr is None:
            st.error("❌ لا توجد بيانات كافية للتاريخ المختار")
            st.stop()

        # ══════════════════════════════════════════
        # 3. دوال الاتجاه
        # ══════════════════════════════════════════
        def get_direction(curr_row, prev_row, col):
            if curr_row is None or prev_row is None:
                return None
            if col not in curr_row.index or col not in prev_row.index:
                return None
            c = curr_row[col]
            p = prev_row[col]
            if pd.isna(c) or pd.isna(p):
                return None
            if c > p:
                return 'up'
            elif c < p:
                return 'down'
            else:
                return 'flat'

        # ══════════════════════════════════════════
        # 4. منطق الإشارة لكل زوج (النظام الخماسي الجديد)
        # ══════════════════════════════════════════
        def get_pair_signal(base, quote):
            eco_base  = get_direction(eco_curr,   eco_prev,   base)
            eco_quote = get_direction(eco_curr,   eco_prev,   quote)
            yld_base  = get_direction(yield_curr, yield_prev, base)  if yield_curr is not None else None
            yld_quote = get_direction(yield_curr, yield_prev, quote) if yield_curr is not None else None
            
            # Daily alignment
            daily_val = None
            if daily_curr is not None:
                b = daily_curr.get(base,  0)
                q = daily_curr.get(quote, 0)
                if pd.notna(b) and pd.notna(q):
                    diff = b - q
                    daily_val = 'up' if diff > 0 else 'down' if diff < 0 else 'flat'

            signal     = None
            confidence = None

            # ── 1️⃣ تقاطع اقتصادي كامل (80% مع Daily - 75% بدون Daily) ──
            if eco_base == 'up' and eco_quote == 'down':
                signal = 'BUY'
                confidence = 80 if daily_val == 'up' else 75

            elif eco_base == 'down' and eco_quote == 'up':
                signal = 'SELL'
                confidence = 80 if daily_val == 'down' else 75

            # ── 2️⃣ حركة من طرف واحد (70% مع Daily - 65% بدون Daily) ──
            elif (eco_base == 'up' and eco_quote != 'down') or \
                 (eco_quote == 'down' and eco_base != 'up'):
                signal = 'BUY'
                confidence = 70 if daily_val == 'up' else 65

            elif (eco_base == 'down' and eco_quote != 'up') or \
                 (eco_quote == 'up' and eco_base != 'down'):
                signal = 'SELL'
                confidence = 70 if daily_val == 'down' else 65

            # ── 3️⃣ اقتصاد ثابت + Yield + Daily متوافق (60% SCALP) ──
            elif (eco_base == 'flat' or eco_quote == 'flat') or (eco_base is None):
                yld_signal = None
                if yld_base is not None and yld_quote is not None:
                    if (yld_base == 'up' and yld_quote != 'up') or (yld_quote == 'down' and yld_base != 'down'):
                        yld_signal = 'BUY'
                    elif (yld_base == 'down' and yld_quote != 'down') or (yld_quote == 'up' and yld_base != 'up'):
                        yld_signal = 'SELL'
                
                # لازم Yield + Daily متوافقين
                if yld_signal == 'BUY' and daily_val == 'up':
                    signal = 'BUY'
                    confidence = 60
                elif yld_signal == 'SELL' and daily_val == 'down':
                    signal = 'SELL'
                    confidence = 60
                else:
                    signal = 'WAIT'
                    confidence = 0

            # ── 4️⃣ لا توجد إشارة ──
            else:
                signal = 'WAIT'
                confidence = 0

            return {
                'signal':     signal,
                'confidence': confidence,
            }

        # ══════════════════════════════════════════
        # 5. حساب الإشارات لـ 28 زوج
        # ══════════════════════════════════════════
        pairs_ordered = [
            "EURUSD","EURGBP","EURAUD","EURNZD","EURCAD","EURCHF","EURJPY",
            "GBPUSD","GBPAUD","GBPNZD","GBPCAD","GBPCHF","GBPJPY",
            "AUDUSD","AUDNZD","AUDCAD","AUDCHF","AUDJPY",
            "NZDUSD","NZDCAD","NZDCHF","NZDJPY",
            "USDCAD","USDCHF","USDJPY",
            "CADCHF","CADJPY","CHFJPY"
        ]

        results_se = []
        for pair in pairs_ordered:
            base, quote = pair[:3], pair[3:]
            r = get_pair_signal(base, quote)
            r['pair'] = pair
            results_se.append(r)

        df_se = pd.DataFrame(results_se)

        # ══════════════════════════════════════════
        # 6. ملخص الإشارات (5 metric cards)
        # ══════════════════════════════════════════
        count_80 = len(df_se[df_se['confidence'] == 80])
        count_75 = len(df_se[df_se['confidence'] == 75])
        count_70 = len(df_se[df_se['confidence'] == 70])
        count_65 = len(df_se[df_se['confidence'] == 65])
        count_60 = len(df_se[df_se['confidence'] == 60])

        st.markdown("---")
        st.subheader("📊 Daily Signals")

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(f"""
            <div style='background:rgba(5,150,105,0.15); border:1px solid #059669;
                        border-radius:12px; padding:16px; text-align:center;'>
                <div style='font-size:12px;color:#94a3b8;'>STRONG+</div>
                <div style='font-size:32px;font-weight:bold;color:#059669;'>{count_80}</div>
                <div style='font-size:11px;color:#059669;font-weight:bold;'>80%</div>
                <div style='font-size:10px;color:#64748b;'>Cross + Daily</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style='background:rgba(16,185,129,0.15); border:1px solid #10b981;
                        border-radius:12px; padding:16px; text-align:center;'>
                <div style='font-size:12px;color:#94a3b8;'>STRONG</div>
                <div style='font-size:32px;font-weight:bold;color:#10b981;'>{count_75}</div>
                <div style='font-size:11px;color:#10b981;font-weight:bold;'>75%</div>
                <div style='font-size:10px;color:#64748b;'>Cross Only</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div style='background:rgba(241,196,15,0.15); border:1px solid #f1c40f;
                        border-radius:12px; padding:16px; text-align:center;'>
                <div style='font-size:12px;color:#94a3b8;'>MODERATE</div>
                <div style='font-size:32px;font-weight:bold;color:#f1c40f;'>{count_70}</div>
                <div style='font-size:11px;color:#f1c40f;font-weight:bold;'>70%</div>
                <div style='font-size:10px;color:#64748b;'>One-Side + Daily</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div style='background:rgba(249,115,22,0.15); border:1px solid #f97316;
                        border-radius:12px; padding:16px; text-align:center;'>
                <div style='font-size:12px;color:#94a3b8;'>WEAK</div>
                <div style='font-size:32px;font-weight:bold;color:#f97316;'>{count_65}</div>
                <div style='font-size:11px;color:#f97316;font-weight:bold;'>65%</div>
                <div style='font-size:10px;color:#64748b;'>One-Side Only</div>
            </div>""", unsafe_allow_html=True)
        with c5:
            st.markdown(f"""
            <div style='background:rgba(139,92,246,0.15); border:1px solid #8b5cf6;
                        border-radius:12px; padding:16px; text-align:center;'>
                <div style='font-size:12px;color:#94a3b8;'>SCALP</div>
                <div style='font-size:32px;font-weight:bold;color:#8b5cf6;'>{count_60}</div>
                <div style='font-size:11px;color:#8b5cf6;font-weight:bold;'>60%</div>
                <div style='font-size:10px;color:#64748b;'>Flat + Yield + Daily</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ══════════════════════════════════════════
        # 7. ترتيب الجدول حسب النسبة + حذف WAIT
        # ══════════════════════════════════════════
        df_se['_sort'] = df_se['confidence'].replace(0, -1)
        df_filtered = df_se.sort_values('_sort', ascending=False).drop('_sort', axis=1)
        
        # حذف صفوف WAIT من الجدول
        df_filtered = df_filtered[df_filtered['signal'] != 'WAIT']

        # ══════════════════════════════════════════
        # 8. الجدول الرئيسي (3 أعمدة فقط)
        # ══════════════════════════════════════════
        def build_signal_table(df):
            rows_html = ""
            for _, row in df.iterrows():
                pair      = row['pair']
                signal    = row['signal']
                conf      = row['confidence']

                # لون الإشارة ثابت: BUY = أخضر / SELL = أحمر / WAIT = رمادي
                if signal == 'BUY':
                    sig_color = '#10b981'
                    sig_bg    = 'rgba(16,185,129,0.2)'
                    border_c  = '#10b981'
                elif signal == 'SELL':
                    sig_color = '#ef4444'
                    sig_bg    = 'rgba(239,68,68,0.2)'
                    border_c  = '#ef4444'
                else:  # WAIT
                    sig_color = '#64748b'
                    sig_bg    = 'rgba(100,116,139,0.1)'
                    border_c  = '#475569'

                # لون شريط الثقة يتغير حسب النسبة
                if conf > 0:
                    if conf == 80:
                        bar_color = '#059669'
                        conf_color = '#059669'
                    elif conf == 75:
                        bar_color = '#10b981'
                        conf_color = '#10b981'
                    elif conf == 70:
                        bar_color = '#f1c40f'
                        conf_color = '#f1c40f'
                    elif conf == 65:
                        bar_color = '#f97316'
                        conf_color = '#f97316'
                    elif conf == 60:
                        bar_color = '#8b5cf6'
                        conf_color = '#8b5cf6'
                    else:
                        bar_color = '#64748b'
                        conf_color = '#64748b'
                    
                    conf_display = f"""
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="background:#1e293b;border-radius:4px;height:6px;width:50px;overflow:hidden;">
                            <div style="background:{bar_color};height:100%;width:{conf}%;border-radius:4px;"></div>
                        </div>
                        <span style="font-size:13px;color:{conf_color};font-weight:700;">{conf}%</span>
                    </div>
                    """
                else:
                    conf_display = '<span style="font-size:13px;color:#64748b;">—</span>'

                rows_html += f"""
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:12px 10px;font-weight:700;color:#e2e8f0;font-size:14px;">{pair}</td>
                    <td style="padding:12px 10px;">
                        <span style="background:{sig_bg};color:{sig_color};border:1px solid {border_c};
                                     padding:5px 14px;border-radius:20px;font-weight:700;font-size:13px;">
                            {signal}
                        </span>
                    </td>
                    <td style="padding:12px 10px;">{conf_display}</td>
                </tr>"""
            return rows_html

        table_html = f"""
        <!DOCTYPE html><html><head><meta charset="UTF-8">
        <style>
            body {{ margin:0; padding:0; background:transparent;
                   font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
            table {{ width:100%; border-collapse:collapse;
                    background:linear-gradient(135deg,#0f172a,#1e293b);
                    border-radius:12px; overflow:hidden; }}
            th {{ background:#1e293b; color:#f1c40f; padding:12px 10px;
                 text-align:left; font-size:12px; font-weight:600;
                 border-bottom:2px solid #f1c40f; white-space:nowrap; }}
            tr:hover {{ background:rgba(241,196,15,0.04); }}
        </style></head><body>
        <table>
            <thead><tr>
                <th>Pair</th>
                <th>Signal</th>
                <th>Confidence</th>
            </tr></thead>
            <tbody>{build_signal_table(df_filtered)}</tbody>
        </table></body></html>"""

        row_count   = len(df_filtered)
        table_height = max(200, row_count * 52 + 60)
        st.components.v1.html(table_html, height=table_height, scrolling=True)
