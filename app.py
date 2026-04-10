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

tab_dashboard, tab_results, tab_signal = st.tabs([
    "📊 Daily Dashboard",
    "🔍 Pair Matrix",
    "📊 Signal Matrix",
])

# ──── Daily Dashboard Tab ─────────────────────────────────
with tab_dashboard:
    if db_daily.empty:
        st.info("📊 Please enter daily data first")
    else:
        st.header("🌙 Daily Dashboard")
        
        # ========== Date Dropdown ==========
        if 'Date' not in db_daily.columns:
            st.error("Date column not found in data")
        else:
            # Convert dates properly
            db_daily['Date'] = pd.to_datetime(db_daily['Date']).dt.date
            date_options = db_daily['Date'].tolist()
            date_options_str = [d.strftime('%Y-%m-%d') for d in date_options]
            
            selected_date_str = st.selectbox(
                "📅 Select Date to View Analysis:",
                options=date_options_str,
                index=len(date_options_str)-1
            )
            
            # Get selected date
            selected_date = pd.to_datetime(selected_date_str).date()
            selected_row = db_daily[db_daily['Date'] == selected_date]
            
            if selected_row.empty:
                st.error(f"❌ No data found for {selected_date_str}")
                current_data = db_daily.iloc[-1]
                selected_date = current_data['Date']
            else:
                current_data = selected_row.iloc[0]
            
            # Get previous data if available
            date_index = db_daily[db_daily['Date'] == selected_date].index[0]
            if date_index > 0:
                prev_data = db_daily.iloc[date_index - 1]
            else:
                prev_data = None
            
            st.markdown("---")
            
            # ========== Regional Power (3 separate boxes) ==========
            st.subheader("🌍 Regional Power")
            
            # Define currencies by region
            us_currencies_codes = ['USD', 'CAD']
            europe_currencies_codes = ['GBP', 'EUR', 'CHF']
            asia_currencies_codes = ['AUD', 'NZD', 'JPY']
            
            # Calculate averages based on selected date
            us_power = current_data[us_currencies_codes].mean() if all(c in current_data.index for c in us_currencies_codes) else 0
            europe_power = current_data[europe_currencies_codes].mean() if all(c in current_data.index for c in europe_currencies_codes) else 0
            asia_power = current_data[asia_currencies_codes].mean() if all(c in current_data.index for c in asia_currencies_codes) else 0
            
            # Function to determine color
            def get_color(value):
                if value > 0:
                    return "#10b981"
                elif value < 0:
                    return "#ef4444"
                else:
                    return "#6b7280"
            
            # Display three boxes in a row
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); 
                            border-radius: 15px; padding: 20px; text-align: center;
                            border: 2px solid {get_color(us_power)};'>
                    <div style='font-size: 40px; margin-bottom: 10px;'>🇺🇸</div>
                    <div style='font-size: 20px; font-weight: bold; margin-bottom: 10px;'>America</div>
                    <div style='font-size: 32px; font-weight: bold; color: {get_color(us_power)};'>{us_power:+.2f}</div>
                    <div style='font-size: 12px; color: #94a3b8; margin-top: 10px;'>
                        USD, CAD
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_r2:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); 
                            border-radius: 15px; padding: 20px; text-align: center;
                            border: 2px solid {get_color(europe_power)};'>
                    <div style='font-size: 40px; margin-bottom: 10px;'>🇪🇺</div>
                    <div style='font-size: 20px; font-weight: bold; margin-bottom: 10px;'>Europe</div>
                    <div style='font-size: 32px; font-weight: bold; color: {get_color(europe_power)};'>{europe_power:+.2f}</div>
                    <div style='font-size: 12px; color: #94a3b8; margin-top: 10px;'>
                        GBP, EUR, CHF
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_r3:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); 
                            border-radius: 15px; padding: 20px; text-align: center;
                            border: 2px solid {get_color(asia_power)};'>
                    <div style='font-size: 40px; margin-bottom: 10px;'>🇯🇵</div>
                    <div style='font-size: 20px; font-weight: bold; margin-bottom: 10px;'>Asia</div>
                    <div style='font-size: 32px; font-weight: bold; color: {get_color(asia_power)};'>{asia_power:+.2f}</div>
                    <div style='font-size: 12px; color: #94a3b8; margin-top: 10px;'>
                        AUD, NZD, JPY
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Strongest region
            powers = {'Americas': us_power, 'Europe': europe_power, 'Asia': asia_power}
            strongest_region = max(powers, key=powers.get)
            strongest_value_region = powers[strongest_region]
            
            st.markdown(f"""
            <div style='background: #1e2a3a; border-radius: 10px; padding: 10px; text-align: center; margin: 20px 0;'>
                <span style='color: #f1c40f;'>🏆 Strongest Region Currently:</span>
                <span style='font-weight: bold; color: #10b981;'>{strongest_region}</span>
                <span style='color: #f1c40f;'> ({strongest_value_region:+.2f})</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ========== Currency Rankings (Economic Power & Yield) ==========
            st.subheader("📊 Currency Rankings")
            
            # Full names for display
            currency_full_names = {
                "USD": "US Dollar",
                "EUR": "Euro",
                "GBP": "British Pound",
                "JPY": "Japanese Yen",
                "CHF": "Swiss Franc",
                "CAD": "Canadian Dollar",
                "AUD": "Australian Dollar",
                "NZD": "New Zealand Dollar"
            }
            
            currency_flags = {
                "USD": "🇺🇸",
                "EUR": "🇪🇺",
                "GBP": "🇬🇧",
                "JPY": "🇯🇵",
                "CHF": "🇨🇭",
                "CAD": "🇨🇦",
                "AUD": "🇦🇺",
                "NZD": "🇳🇿"
            }
            
            # جلب بيانات الاقتصاد والعوائد لليوم المختار
            economy_data_today = None
            yield_data_today = None
            
            if not db_economy.empty:
                economy_row = db_economy[db_economy['Date'] == selected_date]
                if not economy_row.empty:
                    economy_data_today = economy_row.iloc[0]
            
            if not db_yield.empty:
                yield_row = db_yield[db_yield['Date'] == selected_date]
                if not yield_row.empty:
                    yield_data_today = yield_row.iloc[0]
            
            # Create two columns for side-by-side rankings
            col_rank1, col_rank2 = st.columns(2)
            
            # ===== Column 1: Economic Power Ranking =====
            with col_rank1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); 
                            border-radius: 15px; padding: 15px; 
                            border: 1px solid #334155;'>
                    <div style='text-align: center; margin-bottom: 15px;'>
                        <span style='font-size: 24px;'>🏭</span>
                        <h4 style='color: #f1c40f; margin: 0;'>Economic Power Ranking</h4>
                        <span style='font-size: 12px; color: #94a3b8;'>Strongest → Weakest</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Collect economic strength data for all currencies
                economic_ranking = []
                currencies_list = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']
                
                if economy_data_today is not None:
                    for currency_code in currencies_list:
                        if currency_code in economy_data_today.index:
                            eco_val = economy_data_today[currency_code]
                            if pd.notna(eco_val):
                                full_name = currency_full_names.get(currency_code, currency_code)
                                flag = currency_flags.get(currency_code, "💰")
                                economic_ranking.append({
                                    'currency': currency_code,
                                    'name': full_name,
                                    'flag': flag,
                                    'value': eco_val
                                })
                
                # Sort from largest to smallest
                economic_ranking.sort(key=lambda x: x['value'], reverse=True)
                
                if economic_ranking:
                    for idx, item in enumerate(economic_ranking, 1):
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                        value_color = "#10b981" if item['value'] >= 0 else "#ef4444"
                        
                        st.markdown(f"""
                        <div style='display: flex; align-items: center; justify-content: space-between; 
                                    padding: 10px 12px; margin: 8px 0; 
                                    background: rgba(0,0,0,0.3); border-radius: 10px;
                                    border-left: 3px solid {value_color};'>
                            <div style='display: flex; align-items: center; gap: 12px;'>
                                <span style='font-size: 18px; font-weight: bold; width: 35px;'>{medal}</span>
                                <span style='font-size: 28px;'>{item['flag']}</span>
                                <div>
                                    <span style='font-weight: bold;'>{item['currency']}</span>
                                    <span style='font-size: 11px; color: #94a3b8; margin-left: 5px;'>{item['name']}</span>
                                </div>
                            </div>
                            <span style='font-weight: bold; font-size: 18px; color: {value_color};'>{item['value']:+.2f}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("📊 No economic data available")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # ===== Column 2: Yield Ranking =====
            with col_rank2:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); 
                            border-radius: 15px; padding: 15px; 
                            border: 1px solid #334155;'>
                    <div style='text-align: center; margin-bottom: 15px;'>
                        <span style='font-size: 24px;'>📈</span>
                        <h4 style='color: #f1c40f; margin: 0;'>Yield Ranking</h4>
                        <span style='font-size: 12px; color: #94a3b8;'>Highest → Lowest</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Collect yield data for all currencies
                yield_ranking = []
                
                if yield_data_today is not None:
                    for currency_code in currencies_list:
                        if currency_code in yield_data_today.index:
                            y_val = yield_data_today[currency_code]
                            if pd.notna(y_val):
                                full_name = currency_full_names.get(currency_code, currency_code)
                                flag = currency_flags.get(currency_code, "💰")
                                yield_ranking.append({
                                    'currency': currency_code,
                                    'name': full_name,
                                    'flag': flag,
                                    'value': y_val
                                })
                
                # Sort from largest to smallest
                yield_ranking.sort(key=lambda x: x['value'], reverse=True)
                
                if yield_ranking:
                    for idx, item in enumerate(yield_ranking, 1):
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                        # Yield color: green for positive, red for negative, yellow for near zero
                        if item['value'] > 0.5:
                            value_color = "#10b981"
                        elif item['value'] < 0:
                            value_color = "#ef4444"
                        else:
                            value_color = "#f1c40f"
                        
                        st.markdown(f"""
                        <div style='display: flex; align-items: center; justify-content: space-between; 
                                    padding: 10px 12px; margin: 8px 0; 
                                    background: rgba(0,0,0,0.3); border-radius: 10px;
                                    border-left: 3px solid {value_color};'>
                            <div style='display: flex; align-items: center; gap: 12px;'>
                                <span style='font-size: 18px; font-weight: bold; width: 35px;'>{medal}</span>
                                <span style='font-size: 28px;'>{item['flag']}</span>
                                <div>
                                    <span style='font-weight: bold;'>{item['currency']}</span>
                                    <span style='font-size: 11px; color: #94a3b8; margin-left: 5px;'>{item['name']}</span>
                                </div>
                            </div>
                            <span style='font-weight: bold; font-size: 18px; color: {value_color};'>{item['value']:.2f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("📊 No yield data available")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
                        # ========== Economic & Yield Charts ==========
            st.markdown("---")
            
            # Create two columns for charts
            col_chart1, col_chart2 = st.columns(2)
            
            # ===== Chart 1: Economic Strength Timeline =====
            with col_chart1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); 
                            border-radius: 15px; padding: 15px; 
                            border: 1px solid #334155;'>
                    <div style='text-align: center; margin-bottom: 15px;'>
                        <span style='font-size: 24px;'>🏭</span>
                        <h4 style='color: #f1c40f; margin: 0;'>Economic Strength Timeline</h4>
                        <span style='font-size: 12px; color: #94a3b8;'>All Currencies - Historical Data</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Prepare economic data for chart
                if not db_economy.empty:
                    # Get all economic data
                    econ_chart_data = db_economy.copy()
                    econ_chart_data['Date'] = pd.to_datetime(econ_chart_data['Date'])
                    econ_chart_data = econ_chart_data.sort_values('Date')
                    
                    # Create figure
                    fig_econ = go.Figure()
                    
                    # Colors for each currency
                    econ_colors = {
                        'USD': '#3498db', 'EUR': '#2ecc71', 'GBP': '#e74c3c', 'JPY': '#f39c12',
                        'CHF': '#9b59b6', 'CAD': '#1abc9c', 'AUD': '#e67e22', 'NZD': '#e84393'
                    }
                    
                    # Add line for each currency
                    for currency in currencies_list:
                        if currency in econ_chart_data.columns:
                            currency_data = econ_chart_data[['Date', currency]].dropna()
                            if not currency_data.empty:
                                fig_econ.add_trace(go.Scatter(
                                    x=currency_data['Date'],
                                    y=currency_data[currency],
                                    mode='lines+markers',
                                    name=currency,
                                    line=dict(color=econ_colors.get(currency, '#95a5a6'), width=2),
                                    marker=dict(size=4)
                                ))
                    
                    # Update layout
                    fig_econ.update_layout(
                        title=dict(
                            text="<b>Economic Strength Over Time</b>",
                            font=dict(size=14, color='#f1c40f'),
                            x=0.5
                        ),
                        xaxis=dict(
                            title=dict(text="<b>Date</b>", font=dict(size=10, color='#e2e8f0')),
                            tickangle=45,
                            tickfont=dict(size=9)
                        ),
                        yaxis=dict(
                            title=dict(text="<b>Economic Strength</b>", font=dict(size=10, color='#e2e8f0')),
                            zeroline=True,
                            zerolinecolor='#f1c40f',
                            zerolinewidth=1.5
                        ),
                        height=400,
                        template="plotly_dark",
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=10)
                        ),
                        plot_bgcolor='rgba(15, 23, 42, 0.8)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Add zero line
                    fig_econ.add_hline(y=0, line_dash="solid", line_color="#e74c3c", line_width=1.5, opacity=0.5)
                    
                    st.plotly_chart(fig_econ, use_container_width=True, key="econ_timeline_chart")
                else:
                    st.info("📊 No economic data available for chart")
            
            # ===== Chart 2: Yield Timeline =====
            with col_chart2:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); 
                            border-radius: 15px; padding: 15px; 
                            border: 1px solid #334155;'>
                    <div style='text-align: center; margin-bottom: 15px;'>
                        <span style='font-size: 24px;'>📈</span>
                        <h4 style='color: #f1c40f; margin: 0;'>Yield Timeline</h4>
                        <span style='font-size: 12px; color: #94a3b8;'>All Currencies - Historical Data</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Prepare yield data for chart
                if not db_yield.empty:
                    # Get all yield data
                    yield_chart_data = db_yield.copy()
                    yield_chart_data['Date'] = pd.to_datetime(yield_chart_data['Date'])
                    yield_chart_data = yield_chart_data.sort_values('Date')
                    
                    # Create figure
                    fig_yield = go.Figure()
                    
                    # Colors for each currency (same as economic)
                    yield_colors = {
                        'USD': '#3498db', 'EUR': '#2ecc71', 'GBP': '#e74c3c', 'JPY': '#f39c12',
                        'CHF': '#9b59b6', 'CAD': '#1abc9c', 'AUD': '#e67e22', 'NZD': '#e84393'
                    }
                    
                    # Add line for each currency
                    for currency in currencies_list:
                        if currency in yield_chart_data.columns:
                            currency_data = yield_chart_data[['Date', currency]].dropna()
                            if not currency_data.empty:
                                fig_yield.add_trace(go.Scatter(
                                    x=currency_data['Date'],
                                    y=currency_data[currency],
                                    mode='lines+markers',
                                    name=currency,
                                    line=dict(color=yield_colors.get(currency, '#95a5a6'), width=2),
                                    marker=dict(size=4)
                                ))
                    
                    # Update layout
                    fig_yield.update_layout(
                        title=dict(
                            text="<b>Yield Rates Over Time</b>",
                            font=dict(size=14, color='#f1c40f'),
                            x=0.5
                        ),
                        xaxis=dict(
                            title=dict(text="<b>Date</b>", font=dict(size=10, color='#e2e8f0')),
                            tickangle=45,
                            tickfont=dict(size=9)
                        ),
                        yaxis=dict(
                            title=dict(text="<b>Yield (%)</b>", font=dict(size=10, color='#e2e8f0')),
                            zeroline=True,
                            zerolinecolor='#f1c40f',
                            zerolinewidth=1.5
                        ),
                        height=400,
                        template="plotly_dark",
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=10)
                        ),
                        plot_bgcolor='rgba(15, 23, 42, 0.8)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Add zero line
                    fig_yield.add_hline(y=0, line_dash="solid", line_color="#e74c3c", line_width=1.5, opacity=0.5)
                    
                    st.plotly_chart(fig_yield, use_container_width=True, key="yield_timeline_chart")
                else:
                    st.info("📊 No yield data available for chart")
            
            st.markdown("---")
            
            # ========== Currency Cards ==========
            st.subheader("💱 Currency Cards")
            
            # Central bank data
            currency_central_banks = {
                "USD": "Federal Reserve",
                "EUR": "European Central Bank",
                "GBP": "Bank of England",
                "JPY": "Bank of Japan",
                "CHF": "Swiss National Bank",
                "CAD": "Bank of Canada",
                "AUD": "Reserve Bank of Australia",
                "NZD": "Reserve Bank of New Zealand"
            }
            
            # Function to display currency pairs as a table
            def show_currency_pairs_table(currency_code, current_data, prev_data, pairs):
                """Display table for pairs related to a specific currency"""
                related_pairs = [pair for pair in pairs if currency_code in pair]
                currency_full = currency_full_names.get(currency_code, currency_code)
                
                st.markdown(f"##### 🔍 {currency_full} Pairs")
                
                table_data = []
                for pair in related_pairs:
                    base, quote = pair[:3], pair[3:]
                    strength_today = current_data[base] - current_data[quote]
                    
                    if strength_today > 0:
                        signal_display = "🟢 BUY"
                    elif strength_today < 0:
                        signal_display = "🔴 SELL"
                    else:
                        signal_display = "🟡 WAIT"
                    
                    if prev_data is not None:
                        delta = {c: current_data[c] - prev_data[c] for c in currencies_list}
                        base_delta = delta[base]
                        quote_delta = delta[quote]
                        volatility = abs(base_delta - quote_delta)
                        delta_power = strength_today - (prev_data[base] - prev_data[quote])
                        
                        if current_data[base] > current_data[quote]:
                            base_vs_quote = f"{base} > {quote}"
                        elif current_data[base] < current_data[quote]:
                            base_vs_quote = f"{base} < {quote}"
                        else:
                            base_vs_quote = f"{base} = {quote}"
                    else:
                        delta_power = 0
                        volatility = 0
                        base_vs_quote = "N/A"
                    
                    table_data.append({
                        "Pair": pair,
                        "Signal": signal_display,
                        "Power": f"{strength_today:+.0f}",
                        "Δ Power": f"{delta_power:+.0f}",
                        "Base vs Quote": base_vs_quote,
                        "Volatility": f"{volatility:.0f}"
                    })
                
                df_table = pd.DataFrame(table_data)
                df_table['Power_Num'] = df_table['Power'].str.replace('+', '').astype(float)
                df_table = df_table.sort_values('Power_Num', ascending=False).drop('Power_Num', axis=1)
                
                st.dataframe(
                    df_table,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Pair": st.column_config.TextColumn("Pair", width="small"),
                        "Signal": st.column_config.TextColumn("Signal", width="small"),
                        "Power": st.column_config.TextColumn("Power", width="small"),
                        "Δ Power": st.column_config.TextColumn("Δ Power", width="small"),
                        "Base vs Quote": st.column_config.TextColumn("Base vs Quote", width="medium"),
                        "Volatility": st.column_config.TextColumn("Volatility", width="small")
                    }
                )
                st.caption("📌 **Note:** 🟢 BUY = Positive Power | 🔴 SELL = Negative Power | 🟡 WAIT = Zero Power")
                st.markdown("---")
            
            # ==================== Display Cards + Tables Directly ====================
            for i in range(0, len(currencies_list), 2):
                col1, col2 = st.columns(2)
                
                # ==================== العملة الأولى ====================
                with col1:
                    currency_code = currencies_list[i]
                    currency_strength = current_data[currency_code]
                    strength_color = "#10b981" if currency_strength >= 0 else "#ef4444"
                    full_name = currency_full_names.get(currency_code, currency_code)
                    flag = currency_flags.get(currency_code, "💰")
                    central_bank = currency_central_banks.get(currency_code, "")
                    
                    # Economic Strength
                    economic_strength = None
                    if economy_data_today is not None and currency_code in economy_data_today.index:
                        eco_val = economy_data_today[currency_code]
                        if pd.notna(eco_val):
                            economic_strength = eco_val
                    
                    economic_strength_text = f"{economic_strength:+.2f}" if economic_strength is not None else "N/A"
                    economic_color = "#10b981" if (economic_strength is not None and economic_strength >= 0) else "#ef4444" if (economic_strength is not None and economic_strength < 0) else "#6b7280"
                    
                    # Yield
                    yield_value = None
                    if yield_data_today is not None and currency_code in yield_data_today.index:
                        y_val = yield_data_today[currency_code]
                        if pd.notna(y_val):
                            yield_value = y_val
                    
                    yield_text = f"{yield_value:.2f}%" if yield_value is not None else "N/A"
                    yield_color = "#10b981" if (yield_value is not None and yield_value > 0) else "#ef4444" if (yield_value is not None and yield_value < 0) else "#f1c40f"
                    
                    # عرض الكارت
                    card_html = f'''
                    <div style="background: linear-gradient(135deg, #1e2a3a 0%, #0f172a 100%); 
                                border-radius: 15px; padding: 20px; margin: 10px 0;
                                border: 1px solid #334155;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <div style="font-size: 48px;">{flag}</div>
                            <div>
                                <h2 style="margin:0; color: #f1c40f;">{full_name}</h2>
                                <div style="font-size: 12px; color: #94a3b8;">{central_bank}</div>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                            <span>💪 Currency Strength (Daily):</span>
                            <span style="font-weight: bold; color: {strength_color};">{currency_strength:+.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                            <span>🏭 Economic Strength (ECONOMY):</span>
                            <span style="font-weight: bold; color: {economic_color};">{economic_strength_text}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                            <span>📈 Yield (YIELD):</span>
                            <span style="font-weight: bold; color: {yield_color};">{yield_text}</span>
                        </div>
                    </div>
                    '''
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # الجدول يظهر مباشرة تحت الكارت
                    show_currency_pairs_table(currency_code, current_data, prev_data, pairs)
                
                # ==================== العملة الثانية ====================
                if i + 1 < len(currencies_list):
                    with col2:
                        currency_code = currencies_list[i + 1]
                        currency_strength = current_data[currency_code]
                        strength_color = "#10b981" if currency_strength >= 0 else "#ef4444"
                        full_name = currency_full_names.get(currency_code, currency_code)
                        flag = currency_flags.get(currency_code, "💰")
                        central_bank = currency_central_banks.get(currency_code, "")
                        
                        # Economic Strength
                        economic_strength = None
                        if economy_data_today is not None and currency_code in economy_data_today.index:
                            eco_val = economy_data_today[currency_code]
                            if pd.notna(eco_val):
                                economic_strength = eco_val
                        
                        economic_strength_text = f"{economic_strength:+.2f}" if economic_strength is not None else "N/A"
                        economic_color = "#10b981" if (economic_strength is not None and economic_strength >= 0) else "#ef4444" if (economic_strength is not None and economic_strength < 0) else "#6b7280"
                        
                        # Yield
                        yield_value = None
                        if yield_data_today is not None and currency_code in yield_data_today.index:
                            y_val = yield_data_today[currency_code]
                            if pd.notna(y_val):
                                yield_value = y_val
                        
                        yield_text = f"{yield_value:.2f}%" if yield_value is not None else "N/A"
                        yield_color = "#10b981" if (yield_value is not None and yield_value > 0) else "#ef4444" if (yield_value is not None and yield_value < 0) else "#f1c40f"
                        
                        # عرض الكارت
                        card_html = f'''
                        <div style="background: linear-gradient(135deg, #1e2a3a 0%, #0f172a 100%); 
                                    border-radius: 15px; padding: 20px; margin: 10px 0;
                                    border: 1px solid #334155;">
                            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                                <div style="font-size: 48px;">{flag}</div>
                                <div>
                                    <h2 style="margin:0; color: #f1c40f;">{full_name}</h2>
                                    <div style="font-size: 12px; color: #94a3b8;">{central_bank}</div>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                                <span>💪 Currency Strength (Daily):</span>
                                <span style="font-weight: bold; color: {strength_color};">{currency_strength:+.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                                <span>🏭 Economic Strength (ECONOMY):</span>
                                <span style="font-weight: bold; color: {economic_color};">{economic_strength_text}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                                <span>📈 Yield (YIELD):</span>
                                <span style="font-weight: bold; color: {yield_color};">{yield_text}</span>
                            </div>
                        </div>
                        '''
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # الجدول يظهر مباشرة تحت الكارت
                        show_currency_pairs_table(currency_code, current_data, prev_data, pairs)
        
        # ========== Higher Time Frame Analyses ==========
        st.markdown("---")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e2a3a 0%, #0f172a 100%); 
                    border-radius: 15px; padding: 20px; margin: 20px 0; 
                    border: 1px solid #334155;'>
            <h3 style='color: #f1c40f; text-align: center;'>📈 Higher Time Frame Analyses</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Display charts for all currencies (2 per row)
        for i in range(0, len(currencies_list), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                currency = currencies_list[i]
                currency_full = currency_full_names.get(currency, currency)
                st.markdown(f"### 💱 {currency_full} ({currency})")
                
                # Prepare chart data from all three timeframes
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
                    
                    # Daily line (blue)
                    if 'Daily' in chart_data.columns and not chart_data['Daily'].isna().all():
                        daily_plot = chart_data[chart_data['Daily'].notna()]
                        fig.add_trace(go.Scatter(
                            x=daily_plot['Date'], 
                            y=daily_plot['Daily'], 
                            mode='lines+markers',
                            name='Daily', 
                            line=dict(color='#3498db', width=2.5),
                            marker=dict(size=6)
                        ))
                    
                    # Weekly line (yellow, dashed)
                    if 'Weekly' in chart_data.columns and not chart_data['Weekly'].isna().all():
                        weekly_plot = chart_data[chart_data['Weekly'].notna()]
                        fig.add_trace(go.Scatter(
                            x=weekly_plot['Date'], 
                            y=weekly_plot['Weekly'], 
                            mode='lines+markers',
                            name='Weekly', 
                            line=dict(color='#f1c40f', width=2.5, dash='dash'),
                            marker=dict(size=6)
                        ))
                    
                    # Monthly line (white, dotted)
                    if 'Monthly' in chart_data.columns and not chart_data['Monthly'].isna().all():
                        monthly_plot = chart_data[chart_data['Monthly'].notna()]
                        fig.add_trace(go.Scatter(
                            x=monthly_plot['Date'], 
                            y=monthly_plot['Monthly'], 
                            mode='lines+markers',
                            name='Monthly', 
                            line=dict(color='white', width=2.5, dash='dot'),
                            marker=dict(size=6)
                        ))
                    
                    # Update layout
                    fig.update_layout(
                        title=dict(
                            text=f"<b>{currency_full}</b> - Strength Evolution", 
                            font=dict(size=14, color='#f1c40f'), 
                            x=0.5
                        ),
                        xaxis=dict(
                            title=dict(text="<b>Date</b>", font=dict(size=10, color='#e2e8f0')), 
                            tickangle=45,
                            tickfont=dict(size=10)
                        ),
                        yaxis=dict(
                            title=dict(text="<b>Currency Strength</b>", font=dict(size=10, color='#e2e8f0')),
                            zeroline=True, 
                            zerolinecolor='#f1c40f',
                            zerolinewidth=1.5
                        ),
                        height=400, 
                        template="plotly_dark", 
                        hovermode='x unified',
                        legend=dict(
                            orientation="h", 
                            yanchor="bottom", 
                            y=1.02, 
                            xanchor="center", 
                            x=0.5,
                            font=dict(size=10)
                        ),
                        plot_bgcolor='rgba(15, 23, 42, 0.8)', 
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Add zero line
                    fig.add_hline(y=0, line_dash="solid", line_color="#e74c3c", line_width=1.5, opacity=0.7)
                    
                    st.plotly_chart(fig, use_container_width=True, key=f"htf_chart_{currency}")
                else:
                    st.info(f"📊 No data available for {currency_full}")
            
            if i + 1 < len(currencies_list):
                with col2:
                    currency = currencies_list[i + 1]
                    currency_full = currency_full_names.get(currency, currency)
                    st.markdown(f"### 💱 {currency_full} ({currency})")
                    
                    # Prepare chart data from all three timeframes
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
                        
                        # Daily line (blue)
                        if 'Daily' in chart_data.columns and not chart_data['Daily'].isna().all():
                            daily_plot = chart_data[chart_data['Daily'].notna()]
                            fig.add_trace(go.Scatter(
                                x=daily_plot['Date'], 
                                y=daily_plot['Daily'], 
                                mode='lines+markers',
                                name='Daily', 
                                line=dict(color='#3498db', width=2.5),
                                marker=dict(size=6)
                            ))
                        
                        # Weekly line (yellow, dashed)
                        if 'Weekly' in chart_data.columns and not chart_data['Weekly'].isna().all():
                            weekly_plot = chart_data[chart_data['Weekly'].notna()]
                            fig.add_trace(go.Scatter(
                                x=weekly_plot['Date'], 
                                y=weekly_plot['Weekly'], 
                                mode='lines+markers',
                                name='Weekly', 
                                line=dict(color='#f1c40f', width=2.5, dash='dash'),
                                marker=dict(size=6)
                            ))
                        
                        # Monthly line (white, dotted)
                        if 'Monthly' in chart_data.columns and not chart_data['Monthly'].isna().all():
                            monthly_plot = chart_data[chart_data['Monthly'].notna()]
                            fig.add_trace(go.Scatter(
                                x=monthly_plot['Date'], 
                                y=monthly_plot['Monthly'], 
                                mode='lines+markers',
                                name='Monthly', 
                                line=dict(color='white', width=2.5, dash='dot'),
                                marker=dict(size=6)
                            ))
                        
                        # Update layout
                        fig.update_layout(
                            title=dict(
                                text=f"<b>{currency_full}</b> - Strength Evolution", 
                                font=dict(size=14, color='#f1c40f'), 
                                x=0.5
                            ),
                            xaxis=dict(
                                title=dict(text="<b>Date</b>", font=dict(size=10, color='#e2e8f0')), 
                                tickangle=45,
                                tickfont=dict(size=10)
                            ),
                            yaxis=dict(
                                title=dict(text="<b>Currency Strength</b>", font=dict(size=10, color='#e2e8f0')),
                                zeroline=True, 
                                zerolinecolor='#f1c40f',
                                zerolinewidth=1.5
                            ),
                            height=400, 
                            template="plotly_dark", 
                            hovermode='x unified',
                            legend=dict(
                                orientation="h", 
                                yanchor="bottom", 
                                y=1.02, 
                                xanchor="center", 
                                x=0.5,
                                font=dict(size=10)
                            ),
                            plot_bgcolor='rgba(15, 23, 42, 0.8)', 
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        
                        # Add zero line
                        fig.add_hline(y=0, line_dash="solid", line_color="#e74c3c", line_width=1.5, opacity=0.7)
                        
                        st.plotly_chart(fig, use_container_width=True, key=f"htf_chart_{currency}")
                    else:
                        st.info(f"📊 No data available for {currency_full}")
            
            st.markdown("---")
# ──── Pair Matrix Tab ─────────────────────
with tab_results:
    if db_daily.empty or len(db_daily) < 2:
        st.info("📊 Please enter at least two days of data to view results")
    else:
        st.header("🎯 28 Pairs Matrix")
        
        # ================== Session State Init ==================
        if 'selected_date' not in st.session_state:
            st.session_state.selected_date = None
        
        # ================== Date List Creation ==================
        all_dates = db_daily['Date'].sort_values(ascending=False).tolist()
        
        date_options = []
        date_map = {}
        
        for date in all_dates:
            date_str = date.strftime("%Y-%m-%d")
            if date == all_dates[0]:
                date_str = f"📅 {date_str} (Latest)"
            date_options.append(date_str)
            date_map[date_str] = date
        
        # ================== Date Selector ==================
        col_date1, col_date2, col_date3 = st.columns([1, 2, 1])
        with col_date2:
            selected_date_str = st.selectbox(
                "📆 Select Date to View Analysis:",
                options=date_options,
                index=0,
                key="date_selector"
            )
            
            st.session_state.selected_date = date_map[selected_date_str]
            
            st.markdown(f"""
            <div style="text-align: center; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                        border-radius: 10px; padding: 8px; margin: 10px 0; border: 1px solid #f1c40f;">
                <span style="color: #f1c40f; font-weight: bold;">📅 Selected Date: {selected_date_str}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ================== Calculate Data for Selected Date ==================
        selected_date = st.session_state.selected_date
        selected_row = db_daily[db_daily['Date'] == selected_date]
        
        if selected_row.empty:
            st.error(f"❌ No data found for {selected_date_str}")
        else:
            latest = selected_row.iloc[0]
            
            # Get previous daily data
            date_index = db_daily[db_daily['Date'] == selected_date].index[0]
            if date_index > 0:
                prev_row = db_daily.iloc[date_index - 1]
                prev = prev_row
            else:
                prev = None
                st.warning("⚠️ This is the first day in data, no previous data for delta calculations")
            
            # Get Economy data for selected date and previous
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
            
            # Get Yield data for selected date and previous
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
            
            # ================== Get Weekly Current & Previous ==================
            selected_date_obj = pd.to_datetime(selected_date)
            
            # Weekly data preparation
            week_start = (selected_date_obj - pd.Timedelta(days=selected_date_obj.weekday())).date()
            weekly_current = {}
            weekly_delta = {}
            
            if not db_weekly.empty:
                db_weekly['Week_Start'] = pd.to_datetime(db_weekly['Week_Start']).dt.date
                weekly_current_row = db_weekly[db_weekly['Week_Start'] == week_start]
                weekly_sorted = db_weekly.sort_values('Week_Start')
                
                if not weekly_current_row.empty:
                    weekly_idx = db_weekly[db_weekly['Week_Start'] == week_start].index[0]
                    for curr in currencies:
                        if curr in weekly_current_row.columns and pd.notna(weekly_current_row.iloc[0][curr]):
                            weekly_current[curr] = weekly_current_row.iloc[0][curr]
                            if weekly_idx > 0:
                                prev_weekly_val = db_weekly.iloc[weekly_idx - 1][curr]
                                if pd.notna(prev_weekly_val):
                                    weekly_delta[curr] = weekly_current[curr] - prev_weekly_val
                                else:
                                    weekly_delta[curr] = 0
                            else:
                                weekly_delta[curr] = 0
                        else:
                            weekly_current[curr] = latest[curr] if curr in latest.index else 0
                            weekly_delta[curr] = 0
                else:
                    for curr in currencies:
                        weekly_current[curr] = latest[curr] if curr in latest.index else 0
                        weekly_delta[curr] = 0
            else:
                for curr in currencies:
                    weekly_current[curr] = latest[curr] if curr in latest.index else 0
                    weekly_delta[curr] = 0
            
            # Monthly data preparation
            month_start = selected_date_obj.replace(day=1).date()
            monthly_current = {}
            monthly_delta = {}
            
            if not db_monthly.empty:
                db_monthly['Month_Start'] = pd.to_datetime(db_monthly['Month_Start']).dt.date
                monthly_current_row = db_monthly[db_monthly['Month_Start'] == month_start]
                monthly_sorted = db_monthly.sort_values('Month_Start')
                
                if not monthly_current_row.empty:
                    monthly_idx = db_monthly[db_monthly['Month_Start'] == month_start].index[0]
                    for curr in currencies:
                        if curr in monthly_current_row.columns and pd.notna(monthly_current_row.iloc[0][curr]):
                            monthly_current[curr] = monthly_current_row.iloc[0][curr]
                            if monthly_idx > 0:
                                prev_monthly_val = db_monthly.iloc[monthly_idx - 1][curr]
                                if pd.notna(prev_monthly_val):
                                    monthly_delta[curr] = monthly_current[curr] - prev_monthly_val
                                else:
                                    monthly_delta[curr] = 0
                            else:
                                monthly_delta[curr] = 0
                        else:
                            monthly_current[curr] = latest[curr] if curr in latest.index else 0
                            monthly_delta[curr] = 0
                else:
                    for curr in currencies:
                        monthly_current[curr] = latest[curr] if curr in latest.index else 0
                        monthly_delta[curr] = 0
            else:
                for curr in currencies:
                    monthly_current[curr] = latest[curr] if curr in latest.index else 0
                    monthly_delta[curr] = 0
            
            # Delta calculations for daily
            delta = {}
            if prev is not None:
                delta = {c: latest[c] - prev[c] for c in currencies}
            
            # Helper function for color based on change (new version for delta)
            def get_delta_color(delta_val):
                if delta_val > 0:
                    return "#10b981"
                elif delta_val < 0:
                    return "#ef4444"
                else:
                    return "#f1c40f"
            
            def get_delta_arrow(delta_val):
                if delta_val > 0:
                    return "▲"
                elif delta_val < 0:
                    return "▼"
                else:
                    return "●"
            
            # Helper function for comparing two values
            def get_change_color(new_val, old_val):
                if old_val is None or pd.isna(old_val) or new_val is None or pd.isna(new_val):
                    return "#6b7280"
                if new_val > old_val:
                    return "#10b981"
                elif new_val < old_val:
                    return "#ef4444"
                else:
                    return "#f1c40f"
            
            def get_change_arrow(new_val, old_val):
                if old_val is None or pd.isna(old_val) or new_val is None or pd.isna(new_val):
                    return ""
                if new_val > old_val:
                    return "▲"
                elif new_val < old_val:
                    return "▼"
                else:
                    return "●"
            
            # Currency full names and flags
            currency_full_names = {
                "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound",
                "JPY": "Japanese Yen", "CHF": "Swiss Franc", "CAD": "Canadian Dollar",
                "AUD": "Australian Dollar", "NZD": "New Zealand Dollar"
            }
            
            currency_flags = {
                "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
                "CHF": "🇨🇭", "CAD": "🇨🇦", "AUD": "🇦🇺", "NZD": "🇳🇿"
            }
            
            # ================== Build Results ==================
            results = []
            
            for pair in pairs:
                base, quote = pair[:3], pair[3:]
                
                # === Strength Calculations ===
                strength_today = latest[base] - latest[quote]
                
                if prev is not None:
                    health_delta = strength_today - (prev[base] - prev[quote])
                    base_delta = delta.get(base, 0)
                    quote_delta = delta.get(quote, 0)
                    volatility = abs(base_delta - quote_delta)
                    
                    # Confirmation logic
                    if base_delta > health_delta and quote_delta > health_delta:
                        confirmation = "UP TREND"
                        conf_color = "#10b981"
                    elif base_delta < health_delta and quote_delta < health_delta:
                        confirmation = "DOWN TREND"
                        conf_color = "#ef4444"
                    else:
                        confirmation = "RANGE"
                        conf_color = "#f59e0b"
                else:
                    health_delta = 0
                    base_delta = 0
                    quote_delta = 0
                    volatility = 0
                    confirmation = "NO DATA"
                    conf_color = "#6b7280"
                
                # === Economic Power of Pair ===
                eco_pair = None
                if economy_today is not None:
                    if base in economy_today.index and quote in economy_today.index:
                        if pd.notna(economy_today[base]) and pd.notna(economy_today[quote]):
                            eco_pair = economy_today[base] - economy_today[quote]
                
                # === Yield Power of Pair ===
                yield_pair = None
                if yield_today is not None:
                    if base in yield_today.index and quote in yield_today.index:
                        if pd.notna(yield_today[base]) and pd.notna(yield_today[quote]):
                            yield_pair = yield_today[base] - yield_today[quote]
                
                # === Individual Currency Changes ===
                # Economic change for Base
                base_eco_val = economy_today[base] if economy_today is not None and base in economy_today.index and pd.notna(economy_today[base]) else None
                base_eco_prev = economy_prev[base] if economy_prev is not None and base in economy_prev.index and pd.notna(economy_prev[base]) else None
                base_eco_color = get_change_color(base_eco_val, base_eco_prev)
                base_eco_arrow = get_change_arrow(base_eco_val, base_eco_prev)
                
                # Economic change for Quote
                quote_eco_val = economy_today[quote] if economy_today is not None and quote in economy_today.index and pd.notna(economy_today[quote]) else None
                quote_eco_prev = economy_prev[quote] if economy_prev is not None and quote in economy_prev.index and pd.notna(economy_prev[quote]) else None
                quote_eco_color = get_change_color(quote_eco_val, quote_eco_prev)
                quote_eco_arrow = get_change_arrow(quote_eco_val, quote_eco_prev)
                
                # Yield change for Base
                base_yield_val = yield_today[base] if yield_today is not None and base in yield_today.index and pd.notna(yield_today[base]) else None
                base_yield_prev = yield_prev[base] if yield_prev is not None and base in yield_prev.index and pd.notna(yield_prev[base]) else None
                base_yield_color = get_change_color(base_yield_val, base_yield_prev)
                base_yield_arrow = get_change_arrow(base_yield_val, base_yield_prev)
                
                # Yield change for Quote
                quote_yield_val = yield_today[quote] if yield_today is not None and quote in yield_today.index and pd.notna(yield_today[quote]) else None
                quote_yield_prev = yield_prev[quote] if yield_prev is not None and quote in yield_prev.index and pd.notna(yield_prev[quote]) else None
                quote_yield_color = get_change_color(quote_yield_val, quote_yield_prev)
                quote_yield_arrow = get_change_arrow(quote_yield_val, quote_yield_prev)
                
                # Daily delta for Base
                base_daily_delta = latest[base] - prev[base] if prev is not None else 0
                base_daily_color = get_delta_color(base_daily_delta)
                base_daily_arrow = get_delta_arrow(base_daily_delta)
                
                # Daily delta for Quote
                quote_daily_delta = latest[quote] - prev[quote] if prev is not None else 0
                quote_daily_color = get_delta_color(quote_daily_delta)
                quote_daily_arrow = get_delta_arrow(quote_daily_delta)
                
                # Weekly delta for Base
                base_weekly_delta = weekly_delta.get(base, 0)
                base_weekly_color = get_delta_color(base_weekly_delta)
                base_weekly_arrow = get_delta_arrow(base_weekly_delta)
                
                # Weekly delta for Quote
                quote_weekly_delta = weekly_delta.get(quote, 0)
                quote_weekly_color = get_delta_color(quote_weekly_delta)
                quote_weekly_arrow = get_delta_arrow(quote_weekly_delta)
                
                # Monthly delta for Base
                base_monthly_delta = monthly_delta.get(base, 0)
                base_monthly_color = get_delta_color(base_monthly_delta)
                base_monthly_arrow = get_delta_arrow(base_monthly_delta)
                
                # Monthly delta for Quote
                quote_monthly_delta = monthly_delta.get(quote, 0)
                quote_monthly_color = get_delta_color(quote_monthly_delta)
                quote_monthly_arrow = get_delta_arrow(quote_monthly_delta)
                
                results.append({
                    "pair": pair,
                    "base": base,
                    "quote": quote,
                    "strength": strength_today,
                    "health_delta": health_delta,
                    "volatility": volatility,
                    "eco_pair": eco_pair,
                    "yield_pair": yield_pair,
                    "confirmation": confirmation,
                    "conf_color": conf_color,
                    # Base data
                    "base_flag": currency_flags.get(base, "💰"),
                    "base_name": currency_full_names.get(base, base),
                    "base_eco_val": base_eco_val,
                    "base_eco_color": base_eco_color,
                    "base_eco_arrow": base_eco_arrow,
                    "base_yield_val": base_yield_val,
                    "base_yield_color": base_yield_color,
                    "base_yield_arrow": base_yield_arrow,
                    "base_daily_delta": base_daily_delta,
                    "base_daily_color": base_daily_color,
                    "base_daily_arrow": base_daily_arrow,
                    "base_weekly_delta": base_weekly_delta,
                    "base_weekly_color": base_weekly_color,
                    "base_weekly_arrow": base_weekly_arrow,
                    "base_monthly_delta": base_monthly_delta,
                    "base_monthly_color": base_monthly_color,
                    "base_monthly_arrow": base_monthly_arrow,
                    # Quote data
                    "quote_flag": currency_flags.get(quote, "💰"),
                    "quote_name": currency_full_names.get(quote, quote),
                    "quote_eco_val": quote_eco_val,
                    "quote_eco_color": quote_eco_color,
                    "quote_eco_arrow": quote_eco_arrow,
                    "quote_yield_val": quote_yield_val,
                    "quote_yield_color": quote_yield_color,
                    "quote_yield_arrow": quote_yield_arrow,
                    "quote_daily_delta": quote_daily_delta,
                    "quote_daily_color": quote_daily_color,
                    "quote_daily_arrow": quote_daily_arrow,
                    "quote_weekly_delta": quote_weekly_delta,
                    "quote_weekly_color": quote_weekly_color,
                    "quote_weekly_arrow": quote_weekly_arrow,
                    "quote_monthly_delta": quote_monthly_delta,
                    "quote_monthly_color": quote_monthly_color,
                    "quote_monthly_arrow": quote_monthly_arrow,
                })
            
            # Sort by absolute strength
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values("strength", key=abs, ascending=False).reset_index(drop=True)
            
            # ================== Display 28 Cards ==================
            for i in range(0, len(df_results), 1):
                row = df_results.iloc[i]
                
                # Card border color based on strength
                if row['strength'] > 0:
                    border_color = "#10b981"
                    bg_gradient = "linear-gradient(135deg, #0a2f1f 0%, #0a1a2f 100%)"
                elif row['strength'] < 0:
                    border_color = "#ef4444"
                    bg_gradient = "linear-gradient(135deg, #2f1a1a 0%, #0a1a2f 100%)"
                else:
                    border_color = "#f59e0b"
                    bg_gradient = "linear-gradient(135deg, #2d2a1a 0%, #0a1a2f 100%)"
                
                # Format values
                eco_pair_str = f"{row['eco_pair']:+.2f}" if row['eco_pair'] is not None else "N/A"
                yield_pair_str = f"{row['yield_pair']:+.2f}" if row['yield_pair'] is not None else "N/A"
                
                base_eco_str = f"{row['base_eco_val']:.2f}" if row['base_eco_val'] is not None else "N/A"
                quote_eco_str = f"{row['quote_eco_val']:.2f}" if row['quote_eco_val'] is not None else "N/A"
                
                base_yield_str = f"{row['base_yield_val']:.2f}%" if row['base_yield_val'] is not None else "N/A"
                quote_yield_str = f"{row['quote_yield_val']:.2f}%" if row['quote_yield_val'] is not None else "N/A"
                
                card_html = f'''
                <div style="background: {bg_gradient}; padding: 20px; border-radius: 16px; margin: 15px 0; 
                            border: 2px solid {border_color}; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
                    
                    <!-- Header: Pair Name -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2 style="margin:0; color: {border_color}; font-size: 32px; font-weight: 700;">{row['pair']}</h2>
                        <div style="background: {border_color}20; padding: 6px 16px; border-radius: 20px; border: 1px solid {border_color};">
                            <span style="color: {border_color}; font-size: 14px; font-weight: bold;">PAIR STRENGTH</span>
                        </div>
                    </div>
                    
                    <!-- Row 1: Three Power Boxes -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                        <!-- Economic Power -->
                        <div style="background: rgba(0,0,0,0.4); border-radius: 12px; padding: 14px 8px; text-align: center; border: 1px solid #334155;">
                            <div style="font-size: 12px; color: #94a3b8; margin-bottom: 6px;">🏭 ECONOMIC POWER</div>
                            <div style="font-size: 26px; font-weight: bold; color: #f1c40f;">{eco_pair_str}</div>
                            <div style="font-size: 10px; color: #64748b; margin-top: 4px;">Base - Quote</div>
                        </div>
                        <!-- Financial Power (Yield) -->
                        <div style="background: rgba(0,0,0,0.4); border-radius: 12px; padding: 14px 8px; text-align: center; border: 1px solid #334155;">
                            <div style="font-size: 12px; color: #94a3b8; margin-bottom: 6px;">📈 FINANCIAL POWER</div>
                            <div style="font-size: 26px; font-weight: bold; color: #f1c40f;">{yield_pair_str}</div>
                            <div style="font-size: 10px; color: #64748b; margin-top: 4px;">Yield Base - Quote</div>
                        </div>
                        <!-- Price Power (Strength Metrics) -->
                        <div style="background: rgba(0,0,0,0.4); border-radius: 12px; padding: 14px 8px; text-align: center; border: 1px solid #334155;">
                            <div style="font-size: 12px; color: #94a3b8; margin-bottom: 6px;">💪 PRICE POWER</div>
                            <div style="display: flex; justify-content: center; gap: 16px;">
                                <div>
                                    <div style="font-size: 10px; color: #64748b;">Strength</div>
                                    <div style="font-size: 18px; font-weight: bold; color: {border_color};">{row['strength']:+.2f}</div>
                                </div>
                                <div>
                                    <div style="font-size: 10px; color: #64748b;">Health Δ</div>
                                    <div style="font-size: 18px; font-weight: bold; color: {'#10b981' if row['health_delta'] >= 0 else '#ef4444'};">{row['health_delta']:+.2f}</div>
                                </div>
                                <div>
                                    <div style="font-size: 10px; color: #64748b;">Volatility</div>
                                    <div style="font-size: 18px; font-weight: bold; color: #f59e0b;">{row['volatility']:.2f}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Row 2: Three Columns for Base vs Quote -->
                    <div style="display: grid; grid-template-columns: 1fr 0.15fr 1fr; gap: 8px; margin-bottom: 16px;">
                        <!-- Base Column -->
                        <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 14px 10px;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                                <span style="font-size: 28px;">{row['base_flag']}</span>
                                <div>
                                    <div style="font-weight: bold; color: #f1c40f; font-size: 16px;">{row['base']}</div>
                                    <div style="font-size: 10px; color: #64748b;">{row['base_name']}</div>
                                </div>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 8px;">
                                <!-- Economic Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">🏭 Economic:</span>
                                    <span style="font-weight: bold; color: {row['base_eco_color']};">{row['base_eco_arrow']} {base_eco_str}</span>
                                </div>
                                <!-- Yield Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">📈 Yield:</span>
                                    <span style="font-weight: bold; color: {row['base_yield_color']};">{row['base_yield_arrow']} {base_yield_str}</span>
                                </div>
                                <!-- Daily Score Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">📅 Daily Δ:</span>
                                    <span style="font-weight: bold; color: {row['base_daily_color']};">{row['base_daily_arrow']} {row['base_daily_delta']:+.2f}</span>
                                </div>
                                <!-- Weekly Score Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">📆 Weekly Δ:</span>
                                    <span style="font-weight: bold; color: {row['base_weekly_color']};">{row['base_weekly_arrow']} {row['base_weekly_delta']:+.2f}</span>
                                </div>
                                <!-- Monthly Score Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">🗓️ Monthly Δ:</span>
                                    <span style="font-weight: bold; color: {row['base_monthly_color']};">{row['base_monthly_arrow']} {row['base_monthly_delta']:+.2f}</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- VS Separator -->
                        <div style="display: flex; align-items: center; justify-content: center; position: relative;">
                            <div style="background: #334155; width: 2px; height: 80%;"></div>
                            <div style="position: absolute; background: #1e293b; padding: 8px 4px; border-radius: 20px; border: 1px solid #475569;">
                                <span style="color: #f1c40f; font-weight: bold; font-size: 14px;">VS</span>
                            </div>
                        </div>
                        
                        <!-- Quote Column -->
                        <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 14px 10px;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                                <span style="font-size: 28px;">{row['quote_flag']}</span>
                                <div>
                                    <div style="font-weight: bold; color: #f1c40f; font-size: 16px;">{row['quote']}</div>
                                    <div style="font-size: 10px; color: #64748b;">{row['quote_name']}</div>
                                </div>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 8px;">
                                <!-- Economic Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">🏭 Economic:</span>
                                    <span style="font-weight: bold; color: {row['quote_eco_color']};">{row['quote_eco_arrow']} {quote_eco_str}</span>
                                </div>
                                <!-- Yield Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">📈 Yield:</span>
                                    <span style="font-weight: bold; color: {row['quote_yield_color']};">{row['quote_yield_arrow']} {quote_yield_str}</span>
                                </div>
                                <!-- Daily Score Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">📅 Daily Δ:</span>
                                    <span style="font-weight: bold; color: {row['quote_daily_color']};">{row['quote_daily_arrow']} {row['quote_daily_delta']:+.2f}</span>
                                </div>
                                <!-- Weekly Score Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">📆 Weekly Δ:</span>
                                    <span style="font-weight: bold; color: {row['quote_weekly_color']};">{row['quote_weekly_arrow']} {row['quote_weekly_delta']:+.2f}</span>
                                </div>
                                <!-- Monthly Score Change -->
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #94a3b8;">🗓️ Monthly Δ:</span>
                                    <span style="font-weight: bold; color: {row['quote_monthly_color']};">{row['quote_monthly_arrow']} {row['quote_monthly_delta']:+.2f}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Row 3: Confirmation Box -->
                    <div style="background: {row['conf_color']}15; border-radius: 12px; padding: 12px; 
                                text-align: center; border: 1.5px solid {row['conf_color']}; margin-top: 8px;">
                        <span style="font-size: 20px; font-weight: bold; color: {row['conf_color']};">
                            {row['confirmation']}
                        </span>
                    </div>
                </div>
                '''
                st.components.v1.html(card_html, height=580, scrolling=False)

# ──── Signal Matrix Tab ─────────────────────
with tab_signal:
    st.header("📊 Signal Matrix - Multi-Timeframe Currency Strength")
    st.caption("Economic • Yield • Monthly • Weekly • Daily — Color = Current Value, Arrow = Change vs Previous")
    
    if db_daily.empty:
        st.info("📊 Please enter daily data first")
    else:
        # ================== Session State Init ==================
        if 'signal_selected_date' not in st.session_state:
            st.session_state.signal_selected_date = None
        
        # ================== Date List Creation ==================
        all_dates = db_daily['Date'].sort_values(ascending=False).tolist()
        
        date_options = []
        date_map = {}
        
        for date in all_dates:
            date_str = date.strftime("%Y-%m-%d")
            if date == all_dates[0]:
                date_str = f"📅 {date_str} (Latest)"
            date_options.append(date_str)
            date_map[date_str] = date
        
        # ================== Date Selector ==================
        col_date1, col_date2, col_date3 = st.columns([1, 2, 1])
        with col_date2:
            selected_date_str = st.selectbox(
                "📆 Select Date to View Analysis:",
                options=date_options,
                index=0,
                key="signal_date_selector"
            )
            
            st.session_state.signal_selected_date = date_map[selected_date_str]
            
            st.markdown(f"""
            <div style="text-align: center; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                        border-radius: 10px; padding: 8px; margin: 10px 0; border: 1px solid #f1c40f;">
                <span style="color: #f1c40f; font-weight: bold;">📅 Selected Date: {selected_date_str}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ================== Calculate Data for Selected Date ==================
        selected_date = st.session_state.signal_selected_date
        selected_row = db_daily[db_daily['Date'] == selected_date]
        
        if selected_row.empty:
            st.error(f"❌ No data found for {selected_date_str}")
        else:
            latest = selected_row.iloc[0]
            
            # Get previous daily data
            date_index = db_daily[db_daily['Date'] == selected_date].index[0]
            if date_index > 0:
                prev_row = db_daily.iloc[date_index - 1]
                prev = prev_row
            else:
                prev = None
            
            # Get Economy data
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
            
            # Get Yield data
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
            def get_cell_color(value, threshold, is_positive_green=True):
                if value is None or pd.isna(value):
                    return "#6b7280"
                if abs(value) <= threshold:
                    return "#f1c40f"
                if is_positive_green:
                    return "#10b981" if value > 0 else "#ef4444"
                else:
                    return "#ef4444" if value > 0 else "#10b981"
            
            def get_arrow(current_val, prev_val):
                if current_val is None or prev_val is None or pd.isna(current_val) or pd.isna(prev_val):
                    return "●"
                if current_val > prev_val:
                    return "▲"
                elif current_val < prev_val:
                    return "▼"
                else:
                    return "●"
            
            def get_delta_color_and_arrow(current_val, prev_val):
                if current_val is None or prev_val is None or pd.isna(current_val) or pd.isna(prev_val):
                    return "#6b7280", "●"
                delta = current_val - prev_val
                if delta > 0:
                    return "#10b981", "▲"
                elif delta < 0:
                    return "#ef4444", "▼"
                else:
                    return "#f1c40f", "●"
            
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
            
            # ================== 1. Currency Snapshot Cards (4x2) ==================
            st.subheader("💱 Currency Snapshot")
            
            # Row 1 (4 currencies)
            cols_row1 = st.columns(4)
            for idx, curr in enumerate(currencies_list[:4]):
                with cols_row1[idx]:
                    curr_val = latest[curr] if curr in latest.index else 0
                    curr_prev = prev[curr] if prev is not None and curr in prev.index else curr_val
                    
                    eco_val = economy_today[curr] if economy_today is not None and curr in economy_today.index and pd.notna(economy_today[curr]) else None
                    eco_prev = economy_prev[curr] if economy_prev is not None and curr in economy_prev.index and pd.notna(economy_prev[curr]) else eco_val
                    
                    yld_val = yield_today[curr] if yield_today is not None and curr in yield_today.index and pd.notna(yield_today[curr]) else None
                    yld_prev = yield_prev[curr] if yield_prev is not None and curr in yield_prev.index and pd.notna(yield_prev[curr]) else yld_val
                    
                    daily_delta = curr_val - curr_prev if prev is not None else 0
                    daily_color, daily_arrow = get_delta_color_and_arrow(curr_val, curr_prev)
                    
                    weekly_curr = weekly_current.get(curr, curr_val)
                    weekly_prev_v = weekly_prev_val.get(curr, weekly_curr)
                    weekly_delta = weekly_curr - weekly_prev_v
                    weekly_color, weekly_arrow = get_delta_color_and_arrow(weekly_curr, weekly_prev_v)
                    
                    monthly_curr = monthly_current.get(curr, curr_val)
                    monthly_prev_v = monthly_prev_val.get(curr, monthly_curr)
                    monthly_delta = monthly_curr - monthly_prev_v
                    monthly_color, monthly_arrow = get_delta_color_and_arrow(monthly_curr, monthly_prev_v)
                    
                    eco_str = f"{eco_val:.2f}" if eco_val is not None else "N/A"
                    eco_arrow = get_arrow(eco_val, eco_prev)
                    eco_color, _ = get_delta_color_and_arrow(eco_val, eco_prev)
                    
                    yld_str = f"{yld_val:.2f}%" if yld_val is not None else "N/A"
                    yld_arrow = get_arrow(yld_val, yld_prev)
                    yld_color, _ = get_delta_color_and_arrow(yld_val, yld_prev)
                    
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
                                <span style="font-size: 11px; color: #94a3b8;">🏭 Economic:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {eco_color};">{eco_arrow} {eco_str}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📈 Yield:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {yld_color};">{yld_arrow} {yld_str}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📅 Daily Δ:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {daily_color};">{daily_arrow} {daily_delta:+.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📆 Weekly Δ:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {weekly_color};">{weekly_arrow} {weekly_delta:+.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">🗓️ Monthly Δ:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {monthly_color};">{monthly_arrow} {monthly_delta:+.2f}</span>
                            </div>
                        </div>
                    </div>
                    '''
                    st.markdown(card_html, unsafe_allow_html=True)
            
            # Row 2 (4 currencies)
            cols_row2 = st.columns(4)
            for idx, curr in enumerate(currencies_list[4:]):
                with cols_row2[idx]:
                    curr_val = latest[curr] if curr in latest.index else 0
                    curr_prev = prev[curr] if prev is not None and curr in prev.index else curr_val
                    
                    eco_val = economy_today[curr] if economy_today is not None and curr in economy_today.index and pd.notna(economy_today[curr]) else None
                    eco_prev = economy_prev[curr] if economy_prev is not None and curr in economy_prev.index and pd.notna(economy_prev[curr]) else eco_val
                    
                    yld_val = yield_today[curr] if yield_today is not None and curr in yield_today.index and pd.notna(yield_today[curr]) else None
                    yld_prev = yield_prev[curr] if yield_prev is not None and curr in yield_prev.index and pd.notna(yield_prev[curr]) else yld_val
                    
                    daily_delta = curr_val - curr_prev if prev is not None else 0
                    daily_color, daily_arrow = get_delta_color_and_arrow(curr_val, curr_prev)
                    
                    weekly_curr = weekly_current.get(curr, curr_val)
                    weekly_prev_v = weekly_prev_val.get(curr, weekly_curr)
                    weekly_delta = weekly_curr - weekly_prev_v
                    weekly_color, weekly_arrow = get_delta_color_and_arrow(weekly_curr, weekly_prev_v)
                    
                    monthly_curr = monthly_current.get(curr, curr_val)
                    monthly_prev_v = monthly_prev_val.get(curr, monthly_curr)
                    monthly_delta = monthly_curr - monthly_prev_v
                    monthly_color, monthly_arrow = get_delta_color_and_arrow(monthly_curr, monthly_prev_v)
                    
                    eco_str = f"{eco_val:.2f}" if eco_val is not None else "N/A"
                    eco_arrow = get_arrow(eco_val, eco_prev)
                    eco_color, _ = get_delta_color_and_arrow(eco_val, eco_prev)
                    
                    yld_str = f"{yld_val:.2f}%" if yld_val is not None else "N/A"
                    yld_arrow = get_arrow(yld_val, yld_prev)
                    yld_color, _ = get_delta_color_and_arrow(yld_val, yld_prev)
                    
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
                                <span style="font-size: 11px; color: #94a3b8;">🏭 Economic:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {eco_color};">{eco_arrow} {eco_str}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📈 Yield:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {yld_color};">{yld_arrow} {yld_str}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📅 Daily Δ:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {daily_color};">{daily_arrow} {daily_delta:+.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">📆 Weekly Δ:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {weekly_color};">{weekly_arrow} {weekly_delta:+.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; color: #94a3b8;">🗓️ Monthly Δ:</span>
                                <span style="font-weight: bold; font-size: 12px; color: {monthly_color};">{monthly_arrow} {monthly_delta:+.2f}</span>
                            </div>
                        </div>
                    </div>
                    '''
                    st.markdown(card_html, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ================== 2. Pairs Signal Matrix Table ==================
            st.subheader("📈 Pairs Signal Matrix")
            st.caption("Color = Current Value | Arrow = Change vs Previous")
            
            # Thresholds
            ECO_THRESHOLD = 2.0
            YIELD_THRESHOLD = 0.2
            PRICE_THRESHOLD = 0.3
            
            # Pairs order
            pairs_ordered = [
                "EURUSD", "EURGBP", "EURAUD", "EURNZD", "EURCAD", "EURCHF", "EURJPY",
                "GBPUSD", "GBPAUD", "GBPNZD", "GBPCAD", "GBPCHF", "GBPJPY",
                "AUDUSD", "AUDNZD", "AUDCAD", "AUDCHF", "AUDJPY",
                "NZDUSD", "NZDCAD", "NZDCHF", "NZDJPY",
                "USDCAD", "USDCHF", "USDJPY",
                "CADCHF", "CADJPY",
                "CHFJPY"
            ]
            
            # Build table data
            table_data = []
            
            for pair in pairs_ordered:
                base, quote = pair[:3], pair[3:]
                
                # === Economic ===
                eco_current = None
                eco_prev = None
                if economy_today is not None and economy_prev is not None:
                    if base in economy_today.index and quote in economy_today.index:
                        if pd.notna(economy_today[base]) and pd.notna(economy_today[quote]):
                            eco_current = economy_today[base] - economy_today[quote]
                    if base in economy_prev.index and quote in economy_prev.index:
                        if pd.notna(economy_prev[base]) and pd.notna(economy_prev[quote]):
                            eco_prev = economy_prev[base] - economy_prev[quote]
                
                eco_color = get_cell_color(eco_current, ECO_THRESHOLD, True)
                eco_arrow = get_arrow(eco_current, eco_prev)
                eco_display = f"{eco_current:+.2f}" if eco_current is not None else "N/A"
                
                # === Yield ===
                yield_current = None
                yield_prev = None
                if yield_today is not None and yield_prev is not None:
                    if base in yield_today.index and quote in yield_today.index:
                        if pd.notna(yield_today[base]) and pd.notna(yield_today[quote]):
                            yield_current = yield_today[base] - yield_today[quote]
                    if base in yield_prev.index and quote in yield_prev.index:
                        if pd.notna(yield_prev[base]) and pd.notna(yield_prev[quote]):
                            yield_prev = yield_prev[base] - yield_prev[quote]
                
                yield_color = get_cell_color(yield_current, YIELD_THRESHOLD, True)
                yield_arrow = get_arrow(yield_current, yield_prev)
                yield_display = f"{yield_current:+.2f}" if yield_current is not None else "N/A"
                
                # === Monthly ===
                monthly_base_curr = monthly_current.get(base, 0)
                monthly_quote_curr = monthly_current.get(quote, 0)
                monthly_pair_current = monthly_base_curr - monthly_quote_curr
                
                monthly_base_prev = monthly_prev_val.get(base, monthly_base_curr)
                monthly_quote_prev = monthly_prev_val.get(quote, monthly_quote_curr)
                monthly_pair_prev = monthly_base_prev - monthly_quote_prev
                
                monthly_color = get_cell_color(monthly_pair_current, PRICE_THRESHOLD, True)
                monthly_arrow = get_arrow(monthly_pair_current, monthly_pair_prev)
                monthly_display = f"{monthly_pair_current:+.2f}"
                
                # === Weekly ===
                weekly_base_curr = weekly_current.get(base, 0)
                weekly_quote_curr = weekly_current.get(quote, 0)
                weekly_pair_current = weekly_base_curr - weekly_quote_curr
                
                weekly_base_prev = weekly_prev_val.get(base, weekly_base_curr)
                weekly_quote_prev = weekly_prev_val.get(quote, weekly_quote_curr)
                weekly_pair_prev = weekly_base_prev - weekly_quote_prev
                
                weekly_color = get_cell_color(weekly_pair_current, PRICE_THRESHOLD, True)
                weekly_arrow = get_arrow(weekly_pair_current, weekly_pair_prev)
                weekly_display = f"{weekly_pair_current:+.2f}"
                
                # === Daily ===
                daily_current = latest[base] - latest[quote]
                daily_prev = prev[base] - prev[quote] if prev is not None else daily_current
                
                daily_color = get_cell_color(daily_current, PRICE_THRESHOLD, True)
                daily_arrow = get_arrow(daily_current, daily_prev)
                daily_display = f"{daily_current:+.2f}"
                
                table_data.append({
                    "Pair": pair,
                    "Economic": eco_display,
                    "Economic_Color": eco_color,
                    "Economic_Arrow": eco_arrow,
                    "Yield": yield_display,
                    "Yield_Color": yield_color,
                    "Yield_Arrow": yield_arrow,
                    "Monthly": monthly_display,
                    "Monthly_Color": monthly_color,
                    "Monthly_Arrow": monthly_arrow,
                    "Weekly": weekly_display,
                    "Weekly_Color": weekly_color,
                    "Weekly_Arrow": weekly_arrow,
                    "Daily": daily_display,
                    "Daily_Color": daily_color,
                    "Daily_Arrow": daily_arrow,
                })
            
            # Display table
            st.markdown("""
            <style>
                .signal-table {
                    width: 100%;
                    border-collapse: collapse;
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    border-radius: 12px;
                    overflow: hidden;
                    font-family: 'Inter', sans-serif;
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
                    padding: 10px 8px;
                    text-align: center;
                    border-bottom: 1px solid #334155;
                    font-size: 13px;
                    font-weight: 500;
                }
                .signal-table tr:hover {
                    background: rgba(241, 196, 15, 0.05);
                }
                .pair-cell {
                    font-weight: 700;
                    color: #e2e8f0;
                }
            </style>
            """, unsafe_allow_html=True)
            
                       # Display table using st.components.v1.html for proper rendering
            table_html = """
            <!DOCTYPE html>
            <html>
            <head>
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
                    padding: 10px 8px;
                    text-align: center;
                    border-bottom: 1px solid #334155;
                    font-size: 13px;
                    font-weight: 500;
                }
                .signal-table tr:hover {
                    background: rgba(241, 196, 15, 0.05);
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
                        <td style="color: {row['Economic_Color']};">{row['Economic_Arrow']} {row['Economic']}</td>
                        <td style="color: {row['Yield_Color']};">{row['Yield_Arrow']} {row['Yield']}</td>
                        <td style="color: {row['Monthly_Color']};">{row['Monthly_Arrow']} {row['Monthly']}</td>
                        <td style="color: {row['Weekly_Color']};">{row['Weekly_Arrow']} {row['Weekly']}</td>
                        <td style="color: {row['Daily_Color']};">{row['Daily_Arrow']} {row['Daily']}</td>
                    </tr>
                """
            
            table_html += """
                </tbody>
            </table>
            </body>
            </html>
            """
            
            st.components.v1.html(table_html, height=650, scrolling=True)
            
            # Legend
            st.markdown("---")
            st.markdown("""
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; padding: 10px;">
                <div style="display: flex; align-items: center; gap: 8px;"><span style="color: #10b981; font-size: 20px;">▲</span> <span style="color: #94a3b8;">Increasing</span></div>
                <div style="display: flex; align-items: center; gap: 8px;"><span style="color: #ef4444; font-size: 20px;">▼</span> <span style="color: #94a3b8;">Decreasing</span></div>
                <div style="display: flex; align-items: center; gap: 8px;"><span style="color: #f1c40f; font-size: 20px;">●</span> <span style="color: #94a3b8;">Unchanged / Neutral</span></div>
                <div style="display: flex; align-items: center; gap: 8px;"><span style="background: #10b981; width: 16px; height: 16px; border-radius: 4px;"></span> <span style="color: #94a3b8;">Positive</span></div>
                <div style="display: flex; align-items: center; gap: 8px;"><span style="background: #ef4444; width: 16px; height: 16px; border-radius: 4px;"></span> <span style="color: #94a3b8;">Negative</span></div>
                <div style="display: flex; align-items: center; gap: 8px;"><span style="background: #f1c40f; width: 16px; height: 16px; border-radius: 4px;"></span> <span style="color: #94a3b8;">Neutral (± threshold)</span></div>
            </div>
            """, unsafe_allow_html=True)
