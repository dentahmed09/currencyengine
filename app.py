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

# ──── Custom CSS for Professional Design ──────────────────────────────────
def inject_custom_css():
    st.markdown("""
    <style>
        /* Main container styling */
        .main-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 1.5rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            border: 1px solid rgba(241, 196, 15, 0.3);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .main-header h1 {
            color: #f1c40f;
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }
        
        .main-header p {
            color: #94a3b8;
            margin: 0.5rem 0 0 0;
            font-size: 0.9rem;
        }
        
        /* Currency Cards */
        .currency-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 15px;
            padding: 1rem;
            text-align: center;
            border: 1px solid #334155;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        .currency-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            border-color: #f1c40f;
        }
        
        .currency-symbol {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .currency-strength {
            font-size: 1.8rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .positive {
            color: #10b981;
        }
        
        .negative {
            color: #ef4444;
        }
        
        .neutral {
            color: #f1c40f;
        }
        
        .currency-change {
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        .currency-metrics {
            display: flex;
            justify-content: space-between;
            margin-top: 0.5rem;
            font-size: 0.7rem;
            color: #94a3b8;
        }
        
        /* Analytics Box */
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
        
        /* Pair Cards */
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
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: #0f172a;
            padding: 0.5rem;
            border-radius: 12px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        /* Form styling */
        .stForm {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid #334155;
        }
        
        /* Button styling */
        .stButton button {
            background: linear-gradient(135deg, #f1c40f, #e67e22);
            color: #0f172a;
            font-weight: bold;
            border: none;
            transition: all 0.2s;
        }
        
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(241, 196, 15, 0.3);
        }
        
        /* Metric styling */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 12px;
            padding: 0.8rem;
            border: 1px solid #334155;
        }
        
        hr {
            border-color: #334155;
        }
    </style>
    """, unsafe_allow_html=True)

## ==================== Sheet ID (من اللينك بتاعك) ====================
SHEET_ID = "1q_q9QGYHm0w7Z5nnO1Uq4NKLW1SoQCf5stbAMKoT3FE"

DAILY_WS   = "daily"
WEEKLY_WS  = "weekly"
MONTHLY_WS = "monthly"

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
    sheet = client.open_by_key(SHEET_ID)      # استخدام ID بدل الاسم
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

# ──── Display Currency Cards Function ──────────────────────────────────
def display_currency_cards(latest, prev=None):
    st.markdown("---")
    st.markdown('<p style="color: #f1c40f; font-size: 1.2rem; font-weight: bold;">💱 INSTITUTIONAL CURRENCY PULSES</p>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for idx, currency in enumerate(currencies):
        col_idx = idx % 4
        with cols[col_idx]:
            strength = latest[currency]
            strength_class = "positive" if strength > 0 else "negative" if strength < 0 else "neutral"
            strength_sign = "+" if strength > 0 else ""
            
            # Calculate daily change if prev exists
            change = None
            if prev is not None:
                change = latest[currency] - prev[currency]
                change_class = "positive" if change > 0 else "negative" if change < 0 else "neutral"
                change_sign = "+" if change > 0 else ""
                change_text = f'<span class="{change_class}">{change_sign}{change:.1f}</span>'
            else:
                change_text = "—"
            
            # Get weekly and monthly values
            weekly_val = None
            monthly_val = None
            if not db_weekly.empty:
                if currency in db_weekly.columns:
                    weekly_val = db_weekly.iloc[-1][currency]
            if not db_monthly.empty:
                if currency in db_monthly.columns:
                    monthly_val = db_monthly.iloc[-1][currency]
            
            weekly_text = f"{weekly_val:.0f}" if weekly_val is not None else "—"
            monthly_text = f"{monthly_val:.0f}" if monthly_val is not None else "—"
            
            st.markdown(f"""
            <div class="currency-card">
                <div class="currency-symbol">{currency}</div>
                <div class="currency-strength {strength_class}">{strength_sign}{strength:.1f}</div>
                <div class="currency-change">
                    {change_text}
                </div>
                <div class="currency-metrics">
                    <span>📊 {weekly_text}</span>
                    <span>📅 {monthly_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

def display_quick_analytics(latest, prev=None):
    st.markdown('<p style="color: #f1c40f; font-size: 1.2rem; font-weight: bold;">📊 QUICK ANALYTICS</p>', unsafe_allow_html=True)
    
    # Calculate rankings
    strength_df = pd.DataFrame({
        'Currency': currencies,
        'Strength': [latest[c] for c in currencies]
    }).sort_values('Strength', ascending=False)
    
    top_3 = strength_df.head(3)
    bottom_3 = strength_df.tail(3)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="analytics-box">
            <div class="analytics-title">🏆 TOP ASSETS</div>
        """, unsafe_allow_html=True)
        for _, row in top_3.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                <span style="font-weight: bold;">{row['Currency']}</span>
                <span class="positive">+{row['Strength']:.1f}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="analytics-box">
            <div class="analytics-title">📉 WEAK ASSETS</div>
        """, unsafe_allow_html=True)
        for _, row in bottom_3.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                <span style="font-weight: bold;">{row['Currency']}</span>
                <span class="negative">{row['Strength']:.1f}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        avg_strength = strength_df['Strength'].mean()
        std_strength = strength_df['Strength'].std()
        st.markdown(f"""
        <div class="analytics-box">
            <div class="analytics-title">📈 MARKET METRICS</div>
            <div style="margin: 0.5rem 0;">
                <div>Average Strength</div>
                <div class="{'positive' if avg_strength > 0 else 'negative'}" style="font-size: 1.2rem; font-weight: bold;">
                    {avg_strength:+.1f}
                </div>
            </div>
            <div style="margin: 0.5rem 0;">
                <div>Market Dispersion</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #f1c40f;">
                    {std_strength:.1f}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Inject custom CSS
inject_custom_css()

# ──── Main Header ────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏦 Institutional Currency Strength Engine</h1>
    <p>Multi-Timeframe Analysis | Institutional Flow | Smart Signals | High-Probability Setups</p>
</div>
""", unsafe_allow_html=True)

# ====================== تحميل البيانات ======================
db_daily   = load_data(DAILY_WS, "Date")
db_weekly  = load_data(WEEKLY_WS, "Week_Start")
db_monthly = load_data(MONTHLY_WS, "Month_Start")

tab_dashboard, tab_results = st.tabs([
    "📊 داش بورد يومي",
    "🔍 نتائج الأزواج",
])
# ──── تبويب داش بورد يومي ─────────────────────────────────
with tab_dashboard:
    if db_daily.empty:
        st.info("أدخل بيانات يومية أولاً")
    else:
        st.header("🌙 داش بورد يومي – آخر تحديث (دارك مود)")
        
        latest = db_daily.iloc[-1]
        prev = db_daily.iloc[-2] if len(db_daily) >= 2 else None
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1e2a3a 0%, #0f172a 100%); 
                        border-radius: 15px; padding: 20px; margin: 10px 0; 
                        border: 1px solid #334155;'>
                <h3 style='color: #f1c40f; text-align: center; margin-bottom: 20px;'>🥧 ترتيب العملات حسب القوة</h3>
            </div>
            """, unsafe_allow_html=True)
            
            strength_df = latest[currencies].to_frame('القوة').sort_values('القوة', ascending=False).reset_index(names='العملة')
            colors = ['#f39c12', '#e67e22', '#e74c3c', '#3498db', '#2ecc71', '#1abc9c', '#9b59b6', '#34495e']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=strength_df['العملة'],
                values=strength_df['القوة'].abs(),
                textinfo='label+percent',
                textposition='inside',
                hole=0.35,
                marker=dict(colors=colors, line=dict(color='#1e2a3a', width=3)),
                hovertemplate='<b>%{label}</b><br>القوة: %{customdata:.2f}<br><extra></extra>',
                customdata=strength_df['القوة'],
                textfont=dict(size=12, color='white')
            )])
            
            strongest = strength_df.iloc[0]['العملة']
            strongest_value = strength_df.iloc[0]['القوة']
            
            fig_pie.add_annotation(
                text=f"<b>{strongest}</b><br>{strongest_value:.1f}",
                x=0.5, y=0.5, font=dict(size=16, color='#f1c40f'), showarrow=False,
                bgcolor='rgba(15, 23, 42, 0.8)', bordercolor='#f1c40f', borderwidth=2
            )
            
            fig_pie.update_layout(
                title=dict(text="🏆 توزيع قوة العملات", font=dict(size=18, color='#f1c40f'), x=0.5),
                height=550, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05,
                           font=dict(size=11, color='#e2e8f0'), bgcolor='rgba(15, 23, 42, 0.7)')
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            
            with st.expander("📊 عرض تفاصيل الترتيب"):
                st.dataframe(strength_df.style.format({'القوة': '{:.2f}'}).bar(subset=['القوة'], color='#f39c12')
                            .set_properties(**{'background-color': '#1e2a3a', 'color': '#e2e8f0'}),
                            hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1e2a3a 0%, #0f172a 100%); 
                        border-radius: 15px; padding: 20px; margin: 10px 0; 
                        border: 1px solid #334155;'>
                <h3 style='color: #f1c40f; text-align: center; margin-bottom: 20px;'>📊 التغيرات اليومية</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if prev is not None:
                deltas = {c: latest[c] - prev[c] for c in currencies}
                sorted_currencies = sorted(currencies, key=lambda x: deltas[x])
                sorted_deltas = [deltas[c] for c in sorted_currencies]
                bar_colors = ['#ef4444' if x < 0 else '#10b981' if x > 0 else '#6b7280' for x in sorted_deltas]
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(x=sorted_currencies, y=sorted_deltas,
                    marker=dict(color=bar_colors), text=[f"{x:+.2f}" for x in sorted_deltas], textposition='outside'))
                fig_bar.add_hline(y=0, line_dash="solid", line_color="#f1c40f", line_width=2.5)
                
                max_delta = max(abs(min(sorted_deltas)), abs(max(sorted_deltas))) if sorted_deltas else 10
                y_range = max_delta * 1.3 if max_delta > 0 else 10
                
                fig_bar.update_layout(
                    title=dict(text="<b>التغيرات اليومية لكل عملة</b>", font=dict(size=16, color='#f1c40f'), x=0.5),
                    xaxis=dict(title=dict(text="<b>العملة</b>", font=dict(size=13, color='#e2e8f0')), tickangle=45),
                    yaxis=dict(title=dict(text="<b>قيمة التغير</b>", font=dict(size=13, color='#e2e8f0')), range=[-y_range, y_range]),
                    height=550, template="plotly_dark", plot_bgcolor='rgba(15, 23, 42, 0.8)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                with st.expander("📊 عرض تفاصيل التغيرات"):
                    changes_df = pd.DataFrame({'العملة': sorted_currencies, 'التغير اليومي': sorted_deltas})
                    st.dataframe(changes_df.style.format({'التغير اليومي': '{:+.2f}'})
                                .set_properties(**{'background-color': '#1e2a3a', 'color': '#e2e8f0'}),
                                hide_index=True, use_container_width=True)
            else:
                st.info("ℹ️ لا يوجد يوم سابق لحساب التغيرات")
        
        # الشارتات الـ 8
        st.markdown("---")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e2a3a 0%, #0f172a 100%); 
                    border-radius: 15px; padding: 20px; margin: 20px 0; 
                    border: 1px solid #334155;'>
            <h3 style='color: #f1c40f; text-align: center;'>📈 تحليل تطور قوة العملات (يومي - أسبوعي - شهري)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for i in range(0, len(currencies), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                currency = currencies[i]
                st.markdown(f"### 💱 {currency}")
                chart_data = pd.DataFrame()
                
                if not db_daily.empty:
                    daily_data = db_daily[['Date', currency]].copy().rename(columns={currency: 'يومي'})
                    chart_data = pd.concat([chart_data, daily_data], ignore_index=True)
                if not db_weekly.empty:
                    weekly_data = db_weekly[['Week_Start', currency]].copy().rename(columns={'Week_Start': 'Date', currency: 'أسبوعي'})
                    if not chart_data.empty:
                        chart_data = chart_data.merge(weekly_data[['Date', 'أسبوعي']], on='Date', how='outer')
                    else:
                        chart_data = weekly_data
                if not db_monthly.empty:
                    monthly_data = db_monthly[['Month_Start', currency]].copy().rename(columns={'Month_Start': 'Date', currency: 'شهري'})
                    if not chart_data.empty:
                        chart_data = chart_data.merge(monthly_data[['Date', 'شهري']], on='Date', how='outer')
                    else:
                        chart_data = monthly_data
                
                if not chart_data.empty:
                    chart_data = chart_data.sort_values('Date').reset_index(drop=True)
                    fig = go.Figure()
                    
                    if 'يومي' in chart_data.columns and not chart_data['يومي'].isna().all():
                        daily_plot = chart_data[chart_data['يومي'].notna()]
                        fig.add_trace(go.Scatter(x=daily_plot['Date'], y=daily_plot['يومي'], mode='lines+markers',
                                                  name='يومي', line=dict(color='#3498db', width=2.5)))
                    if 'أسبوعي' in chart_data.columns and not chart_data['أسبوعي'].isna().all():
                        weekly_plot = chart_data[chart_data['أسبوعي'].notna()]
                        fig.add_trace(go.Scatter(x=weekly_plot['Date'], y=weekly_plot['أسبوعي'], mode='lines+markers',
                                                  name='أسبوعي', line=dict(color='#f1c40f', width=2.5, dash='dash')))
                    if 'شهري' in chart_data.columns and not chart_data['شهري'].isna().all():
                        monthly_plot = chart_data[chart_data['شهري'].notna()]
                        fig.add_trace(go.Scatter(x=monthly_plot['Date'], y=monthly_plot['شهري'], mode='lines+markers',
                                                  name='شهري', line=dict(color='white', width=2.5, dash='dot')))
                    
                    fig.update_layout(
                        title=dict(text=f"<b>{currency}</b> - تطور القوة", font=dict(size=14, color='#f1c40f'), x=0.5),
                        xaxis=dict(title=dict(text="<b>التاريخ</b>", font=dict(size=10, color='#e2e8f0')), tickangle=45),
                        yaxis=dict(title=dict(text="<b>قوة العملة</b>", font=dict(size=10, color='#e2e8f0')),
                                  zeroline=True, zerolinecolor='#f1c40f'),
                        height=400, template="plotly_dark", hovermode='x unified',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        plot_bgcolor='rgba(15, 23, 42, 0.8)', paper_bgcolor='rgba(0,0,0,0)'
                    )
                    fig.add_hline(y=0, line_dash="solid", line_color="#e74c3c", line_width=1.5)
                    st.plotly_chart(fig, use_container_width=True, key=f"dashboard_chart_{currency}")
                else:
                    st.info(f"لا توجد بيانات للعملة {currency}")
            
            if i + 1 < len(currencies):
                with col2:
                    currency = currencies[i + 1]
                    st.markdown(f"### 💱 {currency}")
                    chart_data = pd.DataFrame()
                    
                    if not db_daily.empty:
                        daily_data = db_daily[['Date', currency]].copy().rename(columns={currency: 'يومي'})
                        chart_data = pd.concat([chart_data, daily_data], ignore_index=True)
                    if not db_weekly.empty:
                        weekly_data = db_weekly[['Week_Start', currency]].copy().rename(columns={'Week_Start': 'Date', currency: 'أسبوعي'})
                        if not chart_data.empty:
                            chart_data = chart_data.merge(weekly_data[['Date', 'أسبوعي']], on='Date', how='outer')
                        else:
                            chart_data = weekly_data
                    if not db_monthly.empty:
                        monthly_data = db_monthly[['Month_Start', currency]].copy().rename(columns={'Month_Start': 'Date', currency: 'شهري'})
                        if not chart_data.empty:
                            chart_data = chart_data.merge(monthly_data[['Date', 'شهري']], on='Date', how='outer')
                        else:
                            chart_data = monthly_data
                    
                    if not chart_data.empty:
                        chart_data = chart_data.sort_values('Date').reset_index(drop=True)
                        fig = go.Figure()
                        
                        if 'يومي' in chart_data.columns and not chart_data['يومي'].isna().all():
                            daily_plot = chart_data[chart_data['يومي'].notna()]
                            fig.add_trace(go.Scatter(x=daily_plot['Date'], y=daily_plot['يومي'], mode='lines+markers',
                                                      name='يومي', line=dict(color='#3498db', width=2.5)))
                        if 'أسبوعي' in chart_data.columns and not chart_data['أسبوعي'].isna().all():
                            weekly_plot = chart_data[chart_data['أسبوعي'].notna()]
                            fig.add_trace(go.Scatter(x=weekly_plot['Date'], y=weekly_plot['أسبوعي'], mode='lines+markers',
                                                      name='أسبوعي', line=dict(color='#f1c40f', width=2.5, dash='dash')))
                        if 'شهري' in chart_data.columns and not chart_data['شهري'].isna().all():
                            monthly_plot = chart_data[chart_data['شهري'].notna()]
                            fig.add_trace(go.Scatter(x=monthly_plot['Date'], y=monthly_plot['شهري'], mode='lines+markers',
                                                      name='شهري', line=dict(color='white', width=2.5, dash='dot')))
                        
                        fig.update_layout(
                            title=dict(text=f"<b>{currency}</b> - تطور القوة", font=dict(size=14, color='#f1c40f'), x=0.5),
                            xaxis=dict(title=dict(text="<b>التاريخ</b>", font=dict(size=10, color='#e2e8f0')), tickangle=45),
                            yaxis=dict(title=dict(text="<b>قوة العملة</b>", font=dict(size=10, color='#e2e8f0')),
                                      zeroline=True, zerolinecolor='#f1c40f'),
                            height=400, template="plotly_dark", hovermode='x unified',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                            plot_bgcolor='rgba(15, 23, 42, 0.8)', paper_bgcolor='rgba(0,0,0,0)'
                        )
                        fig.add_hline(y=0, line_dash="solid", line_color="#e74c3c", line_width=1.5)
                        st.plotly_chart(fig, use_container_width=True, key=f"dashboard_chart_{currency}")
                    else:
                        st.info(f"لا توجد بيانات للعملة {currency}")
            
            st.markdown("---")

# ──── تبويب نتائج الأزواج (28 كرت مرتب حسب قوة الزوج) ─────────────────────
with tab_results:
    if db_daily.empty or len(db_daily) < 2:
        st.info("📊 أدخل بيانات يومين على الأقل لعرض النتائج")
    else:
        st.header("🎯 نتائج الأزواج – 28 زوج")
        
        # ================== تهيئة Session State للشارتات ==================
        if 'show_chart' not in st.session_state:
            st.session_state.show_chart = {pair: False for pair in pairs}
        
        def toggle_chart(pair):
            st.session_state.show_chart[pair] = not st.session_state.show_chart[pair]
        
        # زر إغلاق جميع الشارتات
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🗑️ إخفاء كل الشارتات", use_container_width=True):
                for p in st.session_state.show_chart:
                    st.session_state.show_chart[p] = False
        
        st.markdown("---")
        
        # ================== حساب البيانات ==================
        latest = db_daily.iloc[-1]
        prev = db_daily.iloc[-2]
        delta = {c: latest[c] - prev[c] for c in currencies}
        
        results = []
        
        for pair in pairs:
            base, quote = pair[:3], pair[3:]
            
            # الإشارة الأساسية = قوة الزوج (Base - Quote)
            strength_today = latest[base] - latest[quote]
            
            # تحديد الإشارة بناءً على القوة
            if strength_today > 0:
                signal = "شراء"
                signal_color = "🟢"
            elif strength_today < 0:
                signal = "بيع"
                signal_color = "🔴"
            else:
                signal = "ثبات"
                signal_color = "🟡"
            
            # حساب قوة الإشارة (نسبة مئوية)
            max_strength = 5.0
            strength_percent = min(abs(strength_today) / max_strength * 100, 100)
            
            # حساب الدلتا
            health_delta = (latest[base] - latest[quote]) - (prev[base] - prev[quote])
            base_delta = delta[base]
            quote_delta = delta[quote]
            
            # ========== Confirmation (Up Trend / Down Trend / Range) ==========
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
            
            # حساب التقلب (Volatility)
            volatility = abs(base_delta - quote_delta)
            
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
        
        # ترتيب النتائج حسب قوة الزوج من الأكبر للأقل
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values("قوة الزوج", ascending=False).reset_index(drop=True)
        
        # ================== عرض 28 كرت ==================
        
        for i in range(0, len(df_results), 2):
            col1, col2 = st.columns(2, gap="large")
            
            # ================== الكرت الأول ==================
            with col1:
                row = df_results.iloc[i]
                pair = row["الزوج"]
                
                # تحديد الألوان حسب الإشارة
                if "شراء" in row["الإشارة"]:
                    bg_gradient = "linear-gradient(135deg, #0a2f1f, #051a0f)"
                    border_color = "#10b981"
                elif "بيع" in row["الإشارة"]:
                    bg_gradient = "linear-gradient(135deg, #2f1a1a, #1a0a0a)"
                    border_color = "#ef4444"
                else:
                    bg_gradient = "linear-gradient(135deg, #2d2a1a, #1f1c0f)"
                    border_color = "#f59e0b"
                
                # ألوان الدلتا
                base_delta_color = "#10b981" if row['Base Δ'] >= 0 else "#ef4444"
                quote_delta_color = "#10b981" if row['Quote Δ'] >= 0 else "#ef4444"
                health_delta_color = "#10b981" if row['Health Δ'] >= 0 else "#ef4444"
                
                # عرض الكرت باستخدام HTML
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
                
                # زر عرض الشارت
                st.button(
                    f"📈 عرض / إخفاء شارت {pair}",
                    key=f"btn_chart_{pair}_{i}",
                    on_click=toggle_chart,
                    args=(pair,),
                    use_container_width=True
                )
                
                # عرض الشارت إذا كان مفعلاً
                if st.session_state.show_chart.get(pair, False):
                    base, quote = pair[:3], pair[3:]
                    plot_df = db_daily.set_index('Date').copy()
                    
                    if base in plot_df.columns and quote in plot_df.columns:
                        plot_df['Strength'] = plot_df[base] - plot_df[quote]
                        plot_df[f'Δ {base}'] = plot_df[base].diff()
                        plot_df[f'Δ {quote}'] = plot_df[quote].diff()
                        plot_df = plot_df.dropna()
                        
                        if not plot_df.empty:
                            fig_pair = go.Figure()
                            
                            fig_pair.add_trace(go.Scatter(
                                x=plot_df.index, y=plot_df['Strength'],
                                name=f"قوة {pair}",
                                line=dict(color='#f1c40f', width=3),
                                mode='lines+markers',
                                fill='tozeroy',
                                fillcolor='rgba(241, 196, 15, 0.1)'
                            ))
                            
                            fig_pair.add_trace(go.Scatter(
                                x=plot_df.index, y=plot_df[f'Δ {base}'],
                                name=f"Δ {base}",
                                line=dict(color='#10b981', width=2, dash='dash'),
                                yaxis='y2'
                            ))
                            
                            fig_pair.add_trace(go.Scatter(
                                x=plot_df.index, y=plot_df[f'Δ {quote}'],
                                name=f"Δ {quote}",
                                line=dict(color='#ef4444', width=2, dash='dash'),
                                yaxis='y2'
                            ))
                            
                            fig_pair.add_hline(y=0, line_dash="solid", line_color="#6b7280")
                            
                            fig_pair.update_layout(
                                title=dict(text=f"<b>{pair}</b> – القوة والتغيرات", x=0.5),
                                height=450,
                                yaxis=dict(title="قوة الزوج (Base - Quote)"),
                                yaxis2=dict(title="التغير اليومي", overlaying='y', side='right'),
                                template="plotly_dark",
                                hovermode="x unified"
                            )
                            
                            st.plotly_chart(fig_pair, use_container_width=True)
                    else:
                        st.warning(f"⚠️ بيانات غير كاملة للزوج {pair}")
            
            # ================== الكرت الثاني ==================
            with col2:
                if i + 1 < len(df_results):
                    row = df_results.iloc[i + 1]
                    pair = row["الزوج"]
                    
                    # تحديد الألوان حسب الإشارة
                    if "شراء" in row["الإشارة"]:
                        bg_gradient = "linear-gradient(135deg, #0a2f1f, #051a0f)"
                        border_color = "#10b981"
                    elif "بيع" in row["الإشارة"]:
                        bg_gradient = "linear-gradient(135deg, #2f1a1a, #1a0a0a)"
                        border_color = "#ef4444"
                    else:
                        bg_gradient = "linear-gradient(135deg, #2d2a1a, #1f1c0f)"
                        border_color = "#f59e0b"
                    
                    # ألوان الدلتا
                    base_delta_color = "#10b981" if row['Base Δ'] >= 0 else "#ef4444"
                    quote_delta_color = "#10b981" if row['Quote Δ'] >= 0 else "#ef4444"
                    health_delta_color = "#10b981" if row['Health Δ'] >= 0 else "#ef4444"
                    
                    # عرض الكرت باستخدام HTML
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
                    
                    # زر عرض الشارت
                    st.button(
                        f"📈 عرض / إخفاء شارت {pair}",
                        key=f"btn_chart_{pair}_{i+1}",
                        on_click=toggle_chart,
                        args=(pair,),
                        use_container_width=True
                    )
                    
                    # عرض الشارت إذا كان مفعلاً
                    if st.session_state.show_chart.get(pair, False):
                        base, quote = pair[:3], pair[3:]
                        plot_df = db_daily.set_index('Date').copy()
                        
                        if base in plot_df.columns and quote in plot_df.columns:
                            plot_df['Strength'] = plot_df[base] - plot_df[quote]
                            plot_df[f'Δ {base}'] = plot_df[base].diff()
                            plot_df[f'Δ {quote}'] = plot_df[quote].diff()
                            plot_df = plot_df.dropna()
                            
                            if not plot_df.empty:
                                fig_pair = go.Figure()
                                
                                fig_pair.add_trace(go.Scatter(
                                    x=plot_df.index, y=plot_df['Strength'],
                                    name=f"قوة {pair}",
                                    line=dict(color='#f1c40f', width=3),
                                    mode='lines+markers',
                                    fill='tozeroy',
                                    fillcolor='rgba(241, 196, 15, 0.1)'
                                ))
                                
                                fig_pair.add_trace(go.Scatter(
                                    x=plot_df.index, y=plot_df[f'Δ {base}'],
                                    name=f"Δ {base}",
                                    line=dict(color='#10b981', width=2, dash='dash'),
                                    yaxis='y2'
                                ))
                                
                                fig_pair.add_trace(go.Scatter(
                                    x=plot_df.index, y=plot_df[f'Δ {quote}'],
                                    name=f"Δ {quote}",
                                    line=dict(color='#ef4444', width=2, dash='dash'),
                                    yaxis='y2'
                                ))
                                
                                fig_pair.add_hline(y=0, line_dash="solid", line_color="#6b7280")
                                
                                fig_pair.update_layout(
                                    title=dict(text=f"<b>{pair}</b> – القوة والتغيرات", x=0.5),
                                    height=450,
                                    yaxis=dict(title="قوة الزوج (Base - Quote)"),
                                    yaxis2=dict(title="التغير اليومي", overlaying='y', side='right'),
                                    template="plotly_dark",
                                    hovermode="x unified"
                                )
                                
                                st.plotly_chart(fig_pair, use_container_width=True)
                        else:
                            st.warning(f"⚠️ بيانات غير كاملة للزوج {pair}")
