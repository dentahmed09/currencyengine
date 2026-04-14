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

tab_dashboard, tab_results, tab_signal, tab_signal_engine = st.tabs([
    "📊 Daily Dashboard",
    "🔍 Pair Matrix", 
    "📊 Signal Matrix",
    "📡 Signal Engine"
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

# ──── تبويب Pair Matrix ─────────────────────
with tab_results:
    if db_daily.empty or len(db_daily) < 2:
        st.info("📊 أدخل بيانات يومين على الأقل لعرض النتائج")
    else:
        st.header("🎯 28 Pairs Results")
        
        # ================== تهيئة Session State ==================
        if 'selected_date' not in st.session_state:
            st.session_state.selected_date = None
        
        # ================== إنشاء قائمة التواريخ ==================
        all_dates = db_daily['Date'].sort_values(ascending=False).tolist()
        
        date_options = []
        date_map = {}
        
        for date in all_dates:
            date_str = date.strftime("%Y-%m-%d")
            if date == all_dates[0]:
                date_str = f"📅 {date_str} (الأحدث)"
            date_options.append(date_str)
            date_map[date_str] = date
        
        # ================== عرض القائمة المنسدلة ==================
        col_date1, col_date2, col_date3 = st.columns([1, 2, 1])
        with col_date2:
            selected_date_str = st.selectbox(
                "📆 اختر التاريخ لعرض النتائج:",
                options=date_options,
                index=0,
                key="date_selector"
            )
            
            st.session_state.selected_date = date_map[selected_date_str]
            
            st.markdown(f"""
            <div style="text-align: center; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                        border-radius: 10px; padding: 8px; margin: 10px 0; border: 1px solid #f1c40f;">
                <span style="color: #f1c40f; font-weight: bold;">📅 التاريخ المختار: {selected_date_str}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ================== حساب البيانات للتاريخ المختار ==================
        selected_date = st.session_state.selected_date
        selected_row = db_daily[db_daily['Date'] == selected_date]
        
        if selected_row.empty:
            st.error(f"❌ لا توجد بيانات للتاريخ {selected_date_str}")
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

# ──── Signal Matrix Tab ─────────────────────
with tab_signal:
    st.header("📊 Signal Matrix - Multi-Timeframe Currency Strength")
    st.caption("Economic • Yield • Monthly • Weekly • Daily — White = Current Value, Arrow = Change vs Previous")
    
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
        
        if isinstance(selected_date, pd.Timestamp):
            selected_date = selected_date.date()
        
        selected_row = db_daily[db_daily['Date'] == selected_date]
        
        if selected_row.empty:
            st.error(f"❌ No data found for {selected_date_str}")
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
                """Return color for arrow based on direction of change"""
                if current_val is None or prev_val is None or pd.isna(current_val) or pd.isna(prev_val):
                    return "#f1c40f"  # Yellow for no data
                if current_val > prev_val:
                    return "#10b981"  # Green for up
                elif current_val < prev_val:
                    return "#ef4444"  # Red for down
                else:
                    return "#f1c40f"  # Yellow for unchanged
            
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
                    
                    # === تعديل الاقتصاد والعوائد لعرض التغير فقط ===
                    eco_val = economy_today[curr] if economy_today is not None and curr in economy_today.index and pd.notna(economy_today[curr]) else None
                    eco_prev = economy_prev[curr] if economy_prev is not None and curr in economy_prev.index and pd.notna(economy_prev[curr]) else eco_val
                    
                    yld_val = yield_today[curr] if yield_today is not None and curr in yield_today.index and pd.notna(yield_today[curr]) else None
                    yld_prev = yield_prev[curr] if yield_prev is not None and curr in yield_prev.index and pd.notna(yield_prev[curr]) else yld_val
                    
                    # ===== تعديل النص ليكون التغير =====
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
                    # =================================
                    
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
                    
                    # === تعديل الاقتصاد والعوائد لعرض التغير فقط ===
                    eco_val = economy_today[curr] if economy_today is not None and curr in economy_today.index and pd.notna(economy_today[curr]) else None
                    eco_prev = economy_prev[curr] if economy_prev is not None and curr in economy_prev.index and pd.notna(economy_prev[curr]) else eco_val
                    
                    yld_val = yield_today[curr] if yield_today is not None and curr in yield_today.index and pd.notna(yield_today[curr]) else None
                    yld_prev = yield_prev[curr] if yield_prev is not None and curr in yield_prev.index and pd.notna(yield_prev[curr]) else yld_val
                    
                    # ===== تعديل النص ليكون التغير =====
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
                    # =================================
                    
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
            
            ECO_THRESHOLD = 2.0
            YIELD_THRESHOLD = 0.2
            PRICE_THRESHOLD = 0.3
            
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

# ──── Signal Engine Tab ─────────────────────
# أضف "📡 Signal Engine" لقائمة التبويبات الموجودة:
# tab_dashboard, tab_results, tab_signal, tab_signal_engine = st.tabs([...])

with tab_signal_engine:
    st.header("📡 Signal Engine")
    st.caption("نظام الإشارات المبني على الأولوية: Economic → Yield → Daily")

    if db_daily.empty or db_economy.empty:
        st.info("📊 يرجى إدخال بيانات Daily و ECONOMY أولاً")
    else:
        # ══════════════════════════════════════════
        # 1. اختيار التاريخ
        # ══════════════════════════════════════════
        all_dates_se = db_daily['Date'].sort_values(ascending=False).tolist()
        date_opts_se = []
        date_map_se  = {}
        for d in all_dates_se:
            ds = d.strftime("%Y-%m-%d")
            label = f"📅 {ds} (Latest)" if d == all_dates_se[0] else ds
            date_opts_se.append(label)
            date_map_se[label] = d

        col_se1, col_se2, col_se3 = st.columns([1, 2, 1])
        with col_se2:
            sel_str_se = st.selectbox(
                "📆 اختر التاريخ:",
                options=date_opts_se,
                index=0,
                key="se_date_selector"
            )
        sel_date_se = date_map_se[sel_str_se]

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
            """
            يرجع: 'up' / 'down' / 'flat' / None
            بناءً على مقارنة القيمة الحالية بالسابقة
            """
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

        def direction_symbol(d):
            if d == 'up':   return '▲', '#10b981'
            if d == 'down': return '▼', '#ef4444'
            if d == 'flat': return '●', '#f1c40f'
            return '—', '#64748b'

        # ══════════════════════════════════════════
        # 4. منطق الإشارة لكل زوج
        # ══════════════════════════════════════════
        def get_pair_signal(base, quote):
            """
            Priority Waterfall:
            1. Economic base UP  + Economic quote DOWN  → STRONG BUY  (77%)
            2. Economic base DOWN + Economic quote UP   → STRONG SELL (77%)
            3. Economic base UP/DOWN (بدون تعاكس)       → BUY/SELL    (70%)
            4. Economic flat → شوف Yield               → BUY/SELL    (61%)
            5. كل حاجة flat → Daily فقط               → ENTRY ONLY
            """
            eco_base  = get_direction(eco_curr,   eco_prev,   base)
            eco_quote = get_direction(eco_curr,   eco_prev,   quote)
            yld_base  = get_direction(yield_curr, yield_prev, base)  if yield_curr is not None else None
            yld_quote = get_direction(yield_curr, yield_prev, quote) if yield_curr is not None else None
            daily_val = None
            if daily_curr is not None:
                b = daily_curr.get(base,  0)
                q = daily_curr.get(quote, 0)
                if pd.notna(b) and pd.notna(q):
                    diff = b - q
                    daily_val = 'up' if diff > 0 else 'down' if diff < 0 else 'flat'

            signal    = None
            source    = None
            strength  = None
            confidence = None

            # ── Case 1 & 2: Economic تعاكس واضح ──
            if eco_base == 'up' and eco_quote == 'down':
                signal     = 'BUY'
                source     = 'Economic ↑↓'
                strength   = 'STRONG'
                confidence = 77

            elif eco_base == 'down' and eco_quote == 'up':
                signal     = 'SELL'
                source     = 'Economic ↓↑'
                strength   = 'STRONG'
                confidence = 77

            # ── Case 3: Economic اتجاه بدون تعاكس ──
            elif eco_base == 'up' and eco_quote != 'down':
                signal     = 'BUY'
                source     = 'Economic ↑'
                strength   = 'MODERATE'
                confidence = 70

            elif eco_base == 'down' and eco_quote != 'up':
                signal     = 'SELL'
                source     = 'Economic ↓'
                strength   = 'MODERATE'
                confidence = 70

            elif eco_quote == 'down' and eco_base != 'up':
                signal     = 'BUY'
                source     = 'Economic (Q↓)'
                strength   = 'MODERATE'
                confidence = 70

            elif eco_quote == 'up' and eco_base != 'down':
                signal     = 'SELL'
                source     = 'Economic (Q↑)'
                strength   = 'MODERATE'
                confidence = 70

            # ── Case 4: Economic ثبات → Yield ──
            elif eco_base == 'flat' or eco_quote == 'flat' or eco_base is None:
                if yld_base is not None and yld_quote is not None:
                    if yld_base == 'up' and yld_quote != 'up':
                        signal     = 'BUY'
                        source     = 'Yield ↑'
                        strength   = 'WEAK'
                        confidence = 61
                    elif yld_base == 'down' and yld_quote != 'down':
                        signal     = 'SELL'
                        source     = 'Yield ↓'
                        strength   = 'WEAK'
                        confidence = 61
                    elif yld_quote == 'down' and yld_base != 'down':
                        signal     = 'BUY'
                        source     = 'Yield (Q↓)'
                        strength   = 'WEAK'
                        confidence = 61
                    elif yld_quote == 'up' and yld_base != 'up':
                        signal     = 'SELL'
                        source     = 'Yield (Q↑)'
                        strength   = 'WEAK'
                        confidence = 61

            # ── Case 5: Daily فقط للدخول ──
            if signal is None:
                if daily_val == 'up':
                    signal     = 'BUY'
                    source     = 'Daily Entry'
                    strength   = 'ENTRY'
                    confidence = 83  # هدف فقط، مش إغلاق
                elif daily_val == 'down':
                    signal     = 'SELL'
                    source     = 'Daily Entry'
                    strength   = 'ENTRY'
                    confidence = 83
                else:
                    signal     = 'WAIT'
                    source     = '—'
                    strength   = 'NONE'
                    confidence = 0

            # ── Daily Entry Alignment ──
            daily_aligned = None
            if daily_val is not None and daily_val != 'flat' and signal in ['BUY','SELL']:
                if (signal == 'BUY'  and daily_val == 'up') or \
                   (signal == 'SELL' and daily_val == 'down'):
                    daily_aligned = True
                else:
                    daily_aligned = False

            return {
                'signal':        signal,
                'source':        source,
                'strength':      strength,
                'confidence':    confidence,
                'eco_base':      eco_base,
                'eco_quote':     eco_quote,
                'daily_aligned': daily_aligned,
                'daily_dir':     daily_val,
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
        # 6. ملخص الإشارات (metric cards)
        # ══════════════════════════════════════════
        strong_buy  = len(df_se[(df_se['signal']=='BUY')  & (df_se['strength']=='STRONG')])
        strong_sell = len(df_se[(df_se['signal']=='SELL') & (df_se['strength']=='STRONG')])
        mod_buy     = len(df_se[(df_se['signal']=='BUY')  & (df_se['strength']=='MODERATE')])
        mod_sell    = len(df_se[(df_se['signal']=='SELL') & (df_se['strength']=='MODERATE')])
        weak        = len(df_se[df_se['strength']=='WEAK'])
        entry_only  = len(df_se[df_se['strength']=='ENTRY'])
        wait        = len(df_se[df_se['signal']=='WAIT'])
        aligned     = len(df_se[df_se['daily_aligned']==True])

        st.markdown("---")
        st.subheader("📊 ملخص اليوم")

        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div style='background:rgba(16,185,129,0.1); border:1px solid #10b981;
                        border-radius:12px; padding:14px; text-align:center;'>
                <div style='font-size:11px;color:#94a3b8;'>STRONG BUY / SELL</div>
                <div style='font-size:28px;font-weight:bold;color:#10b981;'>{strong_buy}</div>
                <div style='font-size:11px;color:#ef4444;font-weight:bold;'>{strong_sell} SELL</div>
                <div style='font-size:10px;color:#f1c40f;'>77% confidence</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style='background:rgba(241,196,15,0.1); border:1px solid #f1c40f;
                        border-radius:12px; padding:14px; text-align:center;'>
                <div style='font-size:11px;color:#94a3b8;'>MODERATE BUY / SELL</div>
                <div style='font-size:28px;font-weight:bold;color:#f1c40f;'>{mod_buy}</div>
                <div style='font-size:11px;color:#f1c40f;font-weight:bold;'>{mod_sell} SELL</div>
                <div style='font-size:10px;color:#f1c40f;'>70% confidence</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div style='background:rgba(99,102,241,0.1); border:1px solid #818cf8;
                        border-radius:12px; padding:14px; text-align:center;'>
                <div style='font-size:11px;color:#94a3b8;'>YIELD / ENTRY</div>
                <div style='font-size:28px;font-weight:bold;color:#818cf8;'>{weak + entry_only}</div>
                <div style='font-size:11px;color:#94a3b8;'>{weak} Yield • {entry_only} Entry</div>
                <div style='font-size:10px;color:#f1c40f;'>61% / 83% target</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div style='background:rgba(148,163,184,0.1); border:1px solid #475569;
                        border-radius:12px; padding:14px; text-align:center;'>
                <div style='font-size:11px;color:#94a3b8;'>Daily Aligned</div>
                <div style='font-size:28px;font-weight:bold;color:#e2e8f0;'>{aligned}</div>
                <div style='font-size:11px;color:#94a3b8;'>{wait} WAIT</div>
                <div style='font-size:10px;color:#94a3b8;'>إشارة + دخول متوافقين</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ══════════════════════════════════════════
        # 7. فلتر
        # ══════════════════════════════════════════
        col_f1, col_f2 = st.columns([2,1])
        with col_f1:
            filter_opt = st.radio(
                "فلتر:",
                ["الكل", "STRONG فقط (77%)", "BUY فقط", "SELL فقط", "Daily Aligned"],
                horizontal=True,
                key="se_filter"
            )
        with col_f2:
            show_wait = st.checkbox("إظهار WAIT", value=False, key="se_show_wait")

        df_filtered = df_se.copy()
        if filter_opt == "STRONG فقط (77%)":
            df_filtered = df_filtered[df_filtered['strength'] == 'STRONG']
        elif filter_opt == "BUY فقط":
            df_filtered = df_filtered[df_filtered['signal'] == 'BUY']
        elif filter_opt == "SELL فقط":
            df_filtered = df_filtered[df_filtered['signal'] == 'SELL']
        elif filter_opt == "Daily Aligned":
            df_filtered = df_filtered[df_filtered['daily_aligned'] == True]

        if not show_wait:
            df_filtered = df_filtered[df_filtered['signal'] != 'WAIT']

        # ══════════════════════════════════════════
        # 8. الجدول الرئيسي
        # ══════════════════════════════════════════
        strength_order = {'STRONG': 0, 'MODERATE': 1, 'WEAK': 2, 'ENTRY': 3, 'NONE': 4}
        df_filtered['_order'] = df_filtered['strength'].map(strength_order)
        df_filtered = df_filtered.sort_values(['_order', 'confidence'], ascending=[True, False])

        def build_signal_table(df):
            rows_html = ""
            for _, row in df.iterrows():
                pair      = row['pair']
                signal    = row['signal']
                source    = row['source']
                strength  = row['strength']
                conf      = row['confidence']
                eco_b     = row['eco_base']
                eco_q     = row['eco_quote']
                daily_dir = row['daily_dir']
                aligned   = row['daily_aligned']

                # ألوان الإشارة
                if signal == 'BUY':
                    sig_color = '#10b981'
                    sig_bg    = 'rgba(16,185,129,0.15)'
                    border_c  = '#10b981'
                elif signal == 'SELL':
                    sig_color = '#ef4444'
                    sig_bg    = 'rgba(239,68,68,0.15)'
                    border_c  = '#ef4444'
                else:
                    sig_color = '#f1c40f'
                    sig_bg    = 'rgba(241,196,15,0.1)'
                    border_c  = '#f1c40f'

                # قوة الإشارة
                if strength == 'STRONG':
                    str_color = '#10b981'
                    str_label = '⚡ STRONG'
                elif strength == 'MODERATE':
                    str_color = '#f1c40f'
                    str_label = '◆ MODERATE'
                elif strength == 'WEAK':
                    str_color = '#818cf8'
                    str_label = '◇ WEAK'
                elif strength == 'ENTRY':
                    str_color = '#94a3b8'
                    str_label = 'SCALP'
                else:
                    str_color = '#475569'
                    str_label = '— NONE'

                # اتجاه Economic
                eb_sym, eb_col = direction_symbol(eco_b)
                eq_sym, eq_col = direction_symbol(eco_q)

                # Daily alignment
                if aligned is True:
                    align_html = '<span style="color:#10b981;font-size:11px;">✓ Yes</span>'
                elif aligned is False:
                    align_html = '<span style="color:#ef4444;font-size:11px;">✗ NO</span>'
                else:
                    align_html = '<span style="color:#64748b;font-size:11px;">—</span>'

                # Daily direction
                dd_sym, dd_col = direction_symbol(daily_dir)

                # Confidence bar
                bar_color = '#10b981' if conf >= 75 else '#f1c40f' if conf >= 60 else '#94a3b8'

                rows_html += f"""
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:10px 8px;font-weight:700;color:#e2e8f0;font-size:13px;">{pair}</td>
                    <td style="padding:10px 8px;">
                        <span style="background:{sig_bg};color:{sig_color};border:1px solid {border_c};
                                     padding:3px 10px;border-radius:20px;font-weight:700;font-size:12px;">
                            {signal}
                        </span>
                    </td>
                    <td style="padding:10px 8px;font-size:11px;color:{str_color};font-weight:600;">{str_label}</td>
                    <td style="padding:10px 8px;text-align:center;">
                        <span style="color:{eb_col};font-weight:bold;">{eb_sym}</span>
                        <span style="color:#64748b;font-size:10px;"> vs </span>
                        <span style="color:{eq_col};font-weight:bold;">{eq_sym}</span>
                    </td>
                    <td style="padding:10px 8px;font-size:11px;color:#94a3b8;">{source}</td>
                    <td style="padding:10px 8px;">
                        <div style="display:flex;align-items:center;gap:6px;">
                            <div style="background:#1e293b;border-radius:4px;height:6px;width:60px;overflow:hidden;">
                                <div style="background:{bar_color};height:100%;width:{conf}%;border-radius:4px;"></div>
                            </div>
                            <span style="font-size:11px;color:{bar_color};font-weight:600;">{conf}%</span>
                        </div>
                    </td>
                    <td style="padding:10px 8px;text-align:center;">
                        <span style="color:{dd_col};font-weight:bold;">{dd_sym}</span>
                    </td>
                    <td style="padding:10px 8px;text-align:center;">{align_html}</td>
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
            th {{ background:#1e293b; color:#f1c40f; padding:10px 8px;
                 text-align:left; font-size:11px; font-weight:600;
                 border-bottom:2px solid #f1c40f; white-space:nowrap; }}
            tr:hover {{ background:rgba(241,196,15,0.04); }}
        </style></head><body>
        <table>
            <thead><tr>
                <th>Pair</th>
                <th>Signal</th>
                <th>Strength</th>
                <th>Eco B vs Q</th>
                <th>Source</th>
                <th>Confidence</th>
                <th>Daily</th>
                <th>Aligned</th>
            </tr></thead>
            <tbody>{build_signal_table(df_filtered)}</tbody>
        </table></body></html>"""

        row_count   = len(df_filtered)
        table_height = max(200, row_count * 44 + 60)
        st.components.v1.html(table_html, height=table_height, scrolling=True)

        # ══════════════════════════════════════════
        # 9. Legend
        # ══════════════════════════════════════════
        st.markdown("---")
        st.markdown("""
        <div style="display:flex;flex-wrap:wrap;gap:20px;padding:10px;font-size:12px;">
            <span style="color:#10b981;">⚡ STRONG = اقتصادين متعاكسين (77%)</span>
            <span style="color:#f1c40f;">◆ MODERATE = اقتصاد واتجاه واحد (70%)</span>
            <span style="color:#818cf8;">◇ WEAK = Yield فقط (61%)</span>
            <span style="color:#94a3b8;">↗ ENTRY = Daily فقط — هدف 83% مش إغلاق</span>
            <span style="color:#10b981;">✓ Aligned = إشارة ودخول في نفس الاتجاه</span>
        </div>
        """, unsafe_allow_html=True)
