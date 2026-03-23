import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(page_title="Institutional Currency Strength Engine", layout="wide", page_icon="🏦")

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

# ──── مسارات الملفات ──────────────────────────────────────────────────
BASE_DIR = r"C:\Users\ahmad\Downloads\Project\currency strength system v2"

DAILY_FILE   = os.path.join(BASE_DIR, "daily_scores.csv")
WEEKLY_FILE  = os.path.join(BASE_DIR, "weekly_scores.csv")
MONTHLY_FILE = os.path.join(BASE_DIR, "monthly_scores.csv")

currencies = ["USD", "CAD", "EUR", "GBP", "CHF", "AUD", "NZD", "JPY"]

pairs = [
    "EURUSD","EURGBP","EURAUD","EURNZD","EURCAD","EURCHF","EURJPY",
    "GBPUSD","GBPAUD","GBPNZD","GBPCAD","GBPCHF","GBPJPY",
    "AUDUSD","AUDNZD","AUDCAD","AUDCHF","AUDJPY",
    "NZDUSD","NZDCAD","NZDCHF","NZDJPY",
    "USDCAD","USDCHF","USDJPY",
    "CADCHF","CADJPY","CHFJPY"
]

def load_csv(file_path, date_col="Date"):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=[date_col] + currencies)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        return df
    df = pd.read_csv(file_path)
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date
    df = df.dropna(subset=[date_col])
    return df.sort_values(date_col).reset_index(drop=True)

def save_csv(df, file_path):
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

# Load data
db_daily   = load_csv(DAILY_FILE)
db_weekly  = load_csv(WEEKLY_FILE, "Week_Start")
db_monthly = load_csv(MONTHLY_FILE, "Month_Start")

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

# ──── Tabs ──────────────────────────────────────────────────────────
tab_input, tab_dashboard, tab_results = st.tabs([
    "📥 DATA ENTRY",
    "📊 INSTITUTIONAL DASHBOARD",
    "🔍 PAIR MATRIX",
])

# ──── تبويب الإدخال ────────────────────────────────────────────────────
with tab_input:
    st.header("📥 Data Entry")
    st.markdown('<p style="color: #94a3b8;">Input multi-timeframe currency strength scores</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="analytics-box" style="padding: 1rem;">', unsafe_allow_html=True)
        st.subheader("📅 Daily")
        with st.form("daily_form", clear_on_submit=True):
            d_date = st.date_input("Date", datetime.now().date(), key="d_date")
            d_scores = {c: st.number_input(f"{c}", -100., 100., 0., 0.1, format="%.2f", key=f"d_{c}") for c in currencies}
            if st.form_submit_button("💾 Save Daily", use_container_width=True):
                curr = load_csv(DAILY_FILE)
                new = pd.DataFrame([{"Date": d_date, **d_scores}])
                new['Date'] = pd.to_datetime(new['Date']).dt.date
                if not curr.empty:
                    curr = curr[curr['Date'] != d_date]
                final = pd.concat([curr, new]).sort_values('Date')
                save_csv(final, DAILY_FILE)
                st.success("✅ Daily data saved successfully!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="analytics-box" style="padding: 1rem;">', unsafe_allow_html=True)
        st.subheader("📆 Weekly")
        with st.form("weekly_form", clear_on_submit=True):
            w_date = st.date_input("Week Start", datetime.now().date(), key="w_date")
            w_scores = {c: st.number_input(f"{c}", -100., 100., 0., 0.1, format="%.2f", key=f"w_{c}") for c in currencies}
            if st.form_submit_button("💾 Save Weekly", use_container_width=True):
                curr = load_csv(WEEKLY_FILE, "Week_Start")
                new = pd.DataFrame([{"Week_Start": w_date, **w_scores}])
                new['Week_Start'] = pd.to_datetime(new['Week_Start']).dt.date
                if not curr.empty:
                    curr = curr[curr['Week_Start'] != w_date]
                final = pd.concat([curr, new]).sort_values('Week_Start')
                save_csv(final, WEEKLY_FILE)
                st.success("✅ Weekly data saved successfully!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="analytics-box" style="padding: 1rem;">', unsafe_allow_html=True)
        st.subheader("📅 Monthly")
        with st.form("monthly_form", clear_on_submit=True):
            m_date = st.date_input("Month Start", datetime.now().date(), key="m_date")
            m_scores = {c: st.number_input(f"{c}", -100., 100., 0., 0.1, format="%.2f", key=f"m_{c}") for c in currencies}
            if st.form_submit_button("💾 Save Monthly", use_container_width=True):
                curr = load_csv(MONTHLY_FILE, "Month_Start")
                new = pd.DataFrame([{"Month_Start": m_date, **m_scores}])
                new['Month_Start'] = pd.to_datetime(new['Month_Start']).dt.date
                if not curr.empty:
                    curr = curr[curr['Month_Start'] != m_date]
                final = pd.concat([curr, new]).sort_values('Month_Start')
                save_csv(final, MONTHLY_FILE)
                st.success("✅ Monthly data saved successfully!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ──── تبويب داش بورد يومي ─────────────────────────────────
with tab_dashboard:
    if db_daily.empty:
        st.info("ℹ️ Please enter daily data first to view the dashboard")
    else:
        st.header("🌙 Institutional Dashboard")
        
        latest = db_daily.iloc[-1]
        prev = db_daily.iloc[-2] if len(db_daily) >= 2 else None
        
        # Display Currency Cards
        display_currency_cards(latest, prev)
        
        # Display Quick Analytics
        display_quick_analytics(latest, prev)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="analytics-box">
                <div class="analytics-title">🏆 Currency Strength Distribution</div>
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
                title=dict(text="🏆 Currency Strength Distribution", font=dict(size=18, color='#f1c40f'), x=0.5),
                height=550, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05,
                           font=dict(size=11, color='#e2e8f0'), bgcolor='rgba(15, 23, 42, 0.7)')
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            
            with st.expander("📊 View Ranking Details"):
                st.dataframe(strength_df.style.format({'القوة': '{:.2f}'}).bar(subset=['القوة'], color='#f39c12')
                            .set_properties(**{'background-color': '#1e2a3a', 'color': '#e2e8f0'}),
                            hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="analytics-box">
                <div class="analytics-title">📊 Daily Changes</div>
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
                    title=dict(text="<b>Daily Changes by Currency</b>", font=dict(size=16, color='#f1c40f'), x=0.5),
                    xaxis=dict(title=dict(text="<b>Currency</b>", font=dict(size=13, color='#e2e8f0')), tickangle=45),
                    yaxis=dict(title=dict(text="<b>Change Value</b>", font=dict(size=13, color='#e2e8f0')), range=[-y_range, y_range]),
                    height=550, template="plotly_dark", plot_bgcolor='rgba(15, 23, 42, 0.8)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                with st.expander("📊 View Changes Details"):
                    changes_df = pd.DataFrame({'Currency': sorted_currencies, 'Daily Change': sorted_deltas})
                    st.dataframe(changes_df.style.format({'Daily Change': '{:+.2f}'})
                                .set_properties(**{'background-color': '#1e2a3a', 'color': '#e2e8f0'}),
                                hide_index=True, use_container_width=True)
            else:
                st.info("ℹ️ No previous day data available for calculating changes")
        
        # Time Series Charts
        st.markdown("---")
        st.markdown("""
        <div class="analytics-box">
            <div class="analytics-title">📈 Currency Strength Evolution (Daily - Weekly - Monthly)</div>
        </div>
        """, unsafe_allow_html=True)
        
        for i in range(0, len(currencies), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                currency = currencies[i]
                st.markdown(f"### 💱 {currency}")
                chart_data = pd.DataFrame()
                
                if not db_daily.empty:
                    daily_data = db_daily[['Date', currency]].copy().rename(columns={currency: 'Daily'})
                    chart_data = pd.concat([chart_data, daily_data], ignore_index=True)
                if not db_weekly.empty:
                    weekly_data = db_weekly[['Week_Start', currency]].copy().rename(columns={'Week_Start': 'Date', currency: 'Weekly'})
                    if not chart_data.empty:
                        chart_data = chart_data.merge(weekly_data[['Date', 'Weekly']], on='Date', how='outer')
                    else:
                        chart_data = weekly_data
                if not db_monthly.empty:
                    monthly_data = db_monthly[['Month_Start', currency]].copy().rename(columns={'Month_Start': 'Date', currency: 'Monthly'})
                    if not chart_data.empty:
                        chart_data = chart_data.merge(monthly_data[['Date', 'Monthly']], on='Date', how='outer')
                    else:
                        chart_data = monthly_data
                
                if not chart_data.empty:
                    chart_data = chart_data.sort_values('Date').reset_index(drop=True)
                    fig = go.Figure()
                    
                    if 'Daily' in chart_data.columns and not chart_data['Daily'].isna().all():
                        daily_plot = chart_data[chart_data['Daily'].notna()]
                        fig.add_trace(go.Scatter(x=daily_plot['Date'], y=daily_plot['Daily'], mode='lines+markers',
                                                  name='Daily', line=dict(color='#3498db', width=2.5)))
                    if 'Weekly' in chart_data.columns and not chart_data['Weekly'].isna().all():
                        weekly_plot = chart_data[chart_data['Weekly'].notna()]
                        fig.add_trace(go.Scatter(x=weekly_plot['Date'], y=weekly_plot['Weekly'], mode='lines+markers',
                                                  name='Weekly', line=dict(color='#f1c40f', width=2.5, dash='dash')))
                    if 'Monthly' in chart_data.columns and not chart_data['Monthly'].isna().all():
                        monthly_plot = chart_data[chart_data['Monthly'].notna()]
                        fig.add_trace(go.Scatter(x=monthly_plot['Date'], y=monthly_plot['Monthly'], mode='lines+markers',
                                                  name='Monthly', line=dict(color='white', width=2.5, dash='dot')))
                    
                    fig.update_layout(
                        title=dict(text=f"<b>{currency}</b> - Strength Evolution", font=dict(size=14, color='#f1c40f'), x=0.5),
                        xaxis=dict(title=dict(text="<b>Date</b>", font=dict(size=10, color='#e2e8f0')), tickangle=45),
                        yaxis=dict(title=dict(text="<b>Currency Strength</b>", font=dict(size=10, color='#e2e8f0')),
                                  zeroline=True, zerolinecolor='#f1c40f'),
                        height=400, template="plotly_dark", hovermode='x unified',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        plot_bgcolor='rgba(15, 23, 42, 0.8)', paper_bgcolor='rgba(0,0,0,0)'
                    )
                    fig.add_hline(y=0, line_dash="solid", line_color="#e74c3c", line_width=1.5)
                    st.plotly_chart(fig, use_container_width=True, key=f"dashboard_chart_{currency}")
                else:
                    st.info(f"No data available for {currency}")
            
            if i + 1 < len(currencies):
                with col2:
                    currency = currencies[i + 1]
                    st.markdown(f"### 💱 {currency}")
                    chart_data = pd.DataFrame()
                    
                    if not db_daily.empty:
                        daily_data = db_daily[['Date', currency]].copy().rename(columns={currency: 'Daily'})
                        chart_data = pd.concat([chart_data, daily_data], ignore_index=True)
                    if not db_weekly.empty:
                        weekly_data = db_weekly[['Week_Start', currency]].copy().rename(columns={'Week_Start': 'Date', currency: 'Weekly'})
                        if not chart_data.empty:
                            chart_data = chart_data.merge(weekly_data[['Date', 'Weekly']], on='Date', how='outer')
                        else:
                            chart_data = weekly_data
                    if not db_monthly.empty:
                        monthly_data = db_monthly[['Month_Start', currency]].copy().rename(columns={'Month_Start': 'Date', currency: 'Monthly'})
                        if not chart_data.empty:
                            chart_data = chart_data.merge(monthly_data[['Date', 'Monthly']], on='Date', how='outer')
                        else:
                            chart_data = monthly_data
                    
                    if not chart_data.empty:
                        chart_data = chart_data.sort_values('Date').reset_index(drop=True)
                        fig = go.Figure()
                        
                        if 'Daily' in chart_data.columns and not chart_data['Daily'].isna().all():
                            daily_plot = chart_data[chart_data['Daily'].notna()]
                            fig.add_trace(go.Scatter(x=daily_plot['Date'], y=daily_plot['Daily'], mode='lines+markers',
                                                      name='Daily', line=dict(color='#3498db', width=2.5)))
                        if 'Weekly' in chart_data.columns and not chart_data['Weekly'].isna().all():
                            weekly_plot = chart_data[chart_data['Weekly'].notna()]
                            fig.add_trace(go.Scatter(x=weekly_plot['Date'], y=weekly_plot['Weekly'], mode='lines+markers',
                                                      name='Weekly', line=dict(color='#f1c40f', width=2.5, dash='dash')))
                        if 'Monthly' in chart_data.columns and not chart_data['Monthly'].isna().all():
                            monthly_plot = chart_data[chart_data['Monthly'].notna()]
                            fig.add_trace(go.Scatter(x=monthly_plot['Date'], y=monthly_plot['Monthly'], mode='lines+markers',
                                                      name='Monthly', line=dict(color='white', width=2.5, dash='dot')))
                        
                        fig.update_layout(
                            title=dict(text=f"<b>{currency}</b> - Strength Evolution", font=dict(size=14, color='#f1c40f'), x=0.5),
                            xaxis=dict(title=dict(text="<b>Date</b>", font=dict(size=10, color='#e2e8f0')), tickangle=45),
                            yaxis=dict(title=dict(text="<b>Currency Strength</b>", font=dict(size=10, color='#e2e8f0')),
                                      zeroline=True, zerolinecolor='#f1c40f'),
                            height=400, template="plotly_dark", hovermode='x unified',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                            plot_bgcolor='rgba(15, 23, 42, 0.8)', paper_bgcolor='rgba(0,0,0,0)'
                        )
                        fig.add_hline(y=0, line_dash="solid", line_color="#e74c3c", line_width=1.5)
                        st.plotly_chart(fig, use_container_width=True, key=f"dashboard_chart_{currency}")
                    else:
                        st.info(f"No data available for {currency}")
            
            st.markdown("---")

# ──── تبويب نتائج الأزواج ─────────────────────────────────────
with tab_results:
    if db_daily.empty or len(db_daily) < 2:
        st.info("ℹ️ Please enter at least two days of data to view pair analysis")
    else:
        st.header("🔍 Institutional Pair Matrix")
        st.markdown('<p style="color: #94a3b8;">Deep-dive into currency pair dynamics with multi-timeframe strength analysis</p>', unsafe_allow_html=True)
        
        # Initialize session state for charts
        if 'show_chart' not in st.session_state:
            st.session_state.show_chart = {}
        
        latest = db_daily.iloc[-1]
        prev = db_daily.iloc[-2]
        delta = {c: latest[c] - prev[c] for c in currencies}
        
        results = []
        
        for pair in pairs:
            base, quote = pair[:3], pair[3:]
            health_today = latest[base] - latest[quote]
            health_yest  = prev[base] - prev[quote]
            health_delta = health_today - health_yest
            base_delta   = delta[base]
            quote_delta  = delta[quote]
            
            score_h = 1 if health_delta > 0 else -1 if health_delta < 0 else 0
            score_b = 1 if base_delta > 0 else -1 if base_delta < 0 else 0
            score_q = -1 if quote_delta > 0 else 1 if quote_delta < 0 else 0
            
            if base_delta > health_today and quote_delta > health_today:
                score_comp = 1
            elif base_delta < health_today and quote_delta < health_today:
                score_comp = -1
            else:
                score_comp = 0
            
            diff = base_delta - quote_delta
            score_diff = 1 if diff > 0 else -1 if diff < 0 else 0
            total_score = score_h + score_b + score_q + score_comp + score_diff
            
            if total_score > 0:
                signal = "BUY"
                color_class = "signal-buy"
                icon = "🟢"
                strength = min(total_score * 20, 100)
            elif total_score < 0:
                signal = "SELL"
                color_class = "signal-sell"
                icon = "🔴"
                strength = min(abs(total_score) * 20, 100)
            else:
                signal = "NEUTRAL"
                color_class = "signal-neutral"
                icon = "🟡"
                strength = 0
            
            results.append({
                "pair": pair,
                "health_delta": health_delta,
                "base_delta": base_delta,
                "quote_delta": quote_delta,
                "total_score": total_score,
                "signal": signal,
                "color_class": color_class,
                "icon": icon,
                "strength": strength,
                "base": base,
                "quote": quote
            })
        
        # Sort by total score
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Quick filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            signal_filter = st.selectbox("🔍 Filter by Signal", ["All", "BUY", "SELL", "NEUTRAL"])
        with col_filter2:
            min_strength = st.slider("⚡ Minimum Signal Strength", 0, 100, 0)
        with col_filter3:
            search_pair = st.text_input("🔎 Search Pair", placeholder="e.g., EURUSD")
        
        # Apply filters
        filtered_results = results.copy()
        if signal_filter != "All":
            filtered_results = [r for r in filtered_results if r['signal'] == signal_filter]
        filtered_results = [r for r in filtered_results if r['strength'] >= min_strength]
        if search_pair:
            filtered_results = [r for r in filtered_results if search_pair.upper() in r['pair']]
        
        st.markdown(f'<p style="color: #f1c40f; margin-bottom: 1rem;">📊 Showing {len(filtered_results)} of {len(results)} pairs</p>', unsafe_allow_html=True)
        
        # Display pairs as cards
        for idx, result in enumerate(filtered_results):
            strength_percent = result['strength']
            confidence_level = 60 + (strength_percent * 0.4) if strength_percent > 0 else 40
            
            st.markdown(f"""
            <div class="pair-card" style="border-left-color: {'#10b981' if result['signal'] == 'BUY' else '#ef4444' if result['signal'] == 'SELL' else '#f1c40f'}">
                <div class="pair-header">
                    <div class="pair-name">{result['pair']}</div>
                    <div class="pair-signal {result['color_class']}">{result['icon']} {result['signal']}</div>
                </div>
                <div class="pair-stats">
                    <div class="stat-item">
                        <div class="stat-label">HEALTH Δ</div>
                        <div class="stat-value {'positive' if result['health_delta'] > 0 else 'negative' if result['health_delta'] < 0 else 'neutral'}">
                            {result['health_delta']:+.2f}
                        </div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">BASE Δ ({result['base']})</div>
                        <div class="stat-value {'positive' if result['base_delta'] > 0 else 'negative' if result['base_delta'] < 0 else 'neutral'}">
                            {result['base_delta']:+.2f}
                        </div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">QUOTE Δ ({result['quote']})</div>
                        <div class="stat-value {'positive' if result['quote_delta'] > 0 else 'negative' if result['quote_delta'] < 0 else 'neutral'}">
                            {result['quote_delta']:+.2f}
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <div>
                        <span style="color: #94a3b8;">CONFIDENCE LEVEL:</span>
                        <span style="color: #f1c40f; font-weight: bold;"> {confidence_level:.0f}%</span>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">TOTAL SCORE:</span>
                        <span style="color: {'#10b981' if result['total_score'] > 0 else '#ef4444' if result['total_score'] < 0 else '#f1c40f'}; font-weight: bold;"> {result['total_score']:+.0f}</span>
                    </div>
                </div>
                <div class="score-bar">
                    <div class="score-fill" style="width: {strength_percent}%;"></div>
                </div>
                <div style="margin-top: 0.5rem; text-align: center; color: #f1c40f;">
                    Signal Strength: {strength_percent:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to show chart
            col_btn, col_empty = st.columns([1, 3])
            with col_btn:
                if st.button(f"📈 View Chart", key=f"btn_chart_{result['pair']}_{idx}"):
                    st.session_state.show_chart[result['pair']] = not st.session_state.show_chart.get(result['pair'], False)
            
            # Show chart if button is clicked
            if st.session_state.show_chart.get(result['pair'], False):
                st.markdown(f"#### 📊 {result['pair']} - Strength Analysis")
                
                base, quote = result['pair'][:3], result['pair'][3:]
                plot_df = db_daily.set_index('Date')
                
                if base not in plot_df.columns or quote not in plot_df.columns:
                    st.warning(f"⚠️ Incomplete data for {result['pair']}")
                else:
                    plot_df['Strength'] = plot_df[base] - plot_df[quote]
                    plot_df['Δ ' + base] = plot_df[base].diff()
                    plot_df['Δ ' + quote] = plot_df[quote].diff()
                    plot_df = plot_df.dropna(subset=['Δ ' + base, 'Δ ' + quote])
                    
                    if plot_df.empty:
                        st.warning("⚠️ Insufficient data for chart")
                    else:
                        fig_pair = go.Figure()
                        
                        fig_pair.add_trace(go.Scatter(
                            x=plot_df.index, y=plot_df['Strength'],
                            name=f"✨ {result['pair']} Strength",
                            line=dict(color='#f1c40f', width=3.5),
                            mode='lines+markers',
                            fill='tozeroy',
                            fillcolor='rgba(241, 196, 15, 0.1)'
                        ))
                        
                        fig_pair.add_trace(go.Scatter(
                            x=plot_df.index, y=plot_df['Δ ' + base],
                            name=f"📈 {base} Change",
                            line=dict(color='#10b981', width=2.5, dash='dash'),
                            yaxis='y2'
                        ))
                        
                        fig_pair.add_trace(go.Scatter(
                            x=plot_df.index, y=plot_df['Δ ' + quote],
                            name=f"📉 {quote} Change",
                            line=dict(color='#ef4444', width=2.5, dash='dash'),
                            yaxis='y2'
                        ))
                        
                        fig_pair.add_hline(y=0, line_dash="solid", line_color="#6b7280", line_width=1.5)
                        
                        fig_pair.update_layout(
                            title=dict(text=f"<b>{result['pair']}</b> – Pair Strength & Daily Changes",
                                      font=dict(size=18, color='#f1c40f'), x=0.5),
                            height=500,
                            yaxis=dict(title=dict(text=f"<b>Pair Strength</b><br>({base} - {quote})", font=dict(size=12))),
                            yaxis2=dict(title=dict(text="<b>Daily Change</b>", font=dict(size=12)),
                                       overlaying='y', side='right', showgrid=False),
                            template="plotly_dark",
                            hovermode="x unified",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                            plot_bgcolor='rgba(15, 23, 42, 0.8)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(t=80, b=50, l=60, r=80)
                        )
                        
                        st.plotly_chart(fig_pair, use_container_width=True)
                        
                        # Show latest values
                        last = plot_df.iloc[-1]
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Pair Strength", f"{last['Strength']:.2f}")
                        col2.metric(f"Δ {base}", f"{last['Δ ' + base]:+.2f}")
                        col3.metric(f"Δ {quote}", f"{last['Δ ' + quote]:+.2f}")
            
            st.markdown("---")
        
        # Summary section
        with st.expander("📊 Signal Summary", expanded=False):
            summary_data = []
            for r in results:
                summary_data.append({
                    "Pair": r['pair'],
                    "Signal": f"{r['icon']} {r['signal']}",
                    "Total Score": f"{r['total_score']:+.0f}",
                    "Strength": f"{r['strength']:.0f}%"
                })
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, hide_index=True, use_container_width=True)

# ──── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📁 Data Files")
    st.caption(f"📅 Daily: `{os.path.basename(DAILY_FILE)}`")
    st.caption(f"📆 Weekly: `{os.path.basename(WEEKLY_FILE)}`")
    st.caption(f"📅 Monthly: `{os.path.basename(MONTHLY_FILE)}`")
    st.markdown("---")
    
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for f in [DAILY_FILE, WEEKLY_FILE, MONTHLY_FILE]:
            if os.path.exists(f):
                os.remove(f)
        st.success("✅ All data cleared! Please restart the app.")
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.8rem;">
        <p>🏦 Institutional Currency Strength Engine v2</p>
        <p>Multi-Timeframe Analysis</p>
    </div>
    """, unsafe_allow_html=True)

        # streamlit run "C:\Users\ahmad\Downloads\Project\eng\app.py"