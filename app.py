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
    "📊 Daily Dashboord",
    "🔍 Pair Matrix ",
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
                    <div style='font-size: 20px; font-weight: bold; margin-bottom: 10px;'>Americas</div>
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
                    <div style='font-size: 40px; margin-bottom: 10px;'>AS</div>
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
            
            # ========== Currency Cards ==========
            st.subheader("💱 Currency Cards")
            
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
            
            # Additional currency data
            currency_extra_data = {
                "USD": {
                    "yield": "5.25%",
                    "prev_meeting": "2024-01-31",
                    "next_meeting": "2024-03-20",
                    "central_bank": "Federal Reserve",
                    "flag": "🇺🇸"
                },
                "EUR": {
                    "yield": "4.50%",
                    "prev_meeting": "2024-01-25",
                    "next_meeting": "2024-03-07",
                    "central_bank": "European Central Bank",
                    "flag": "🇪🇺"
                },
                "GBP": {
                    "yield": "5.25%",
                    "prev_meeting": "2024-02-01",
                    "next_meeting": "2024-03-21",
                    "central_bank": "Bank of England",
                    "flag": "🇬🇧"
                },
                "JPY": {
                    "yield": "-0.10%",
                    "prev_meeting": "2024-01-23",
                    "next_meeting": "2024-03-19",
                    "central_bank": "Bank of Japan",
                    "flag": "🇯🇵"
                },
                "CHF": {
                    "yield": "1.75%",
                    "prev_meeting": "2024-01-15",
                    "next_meeting": "2024-03-21",
                    "central_bank": "Swiss National Bank",
                    "flag": "🇨🇭"
                },
                "CAD": {
                    "yield": "5.00%",
                    "prev_meeting": "2024-01-24",
                    "next_meeting": "2024-03-06",
                    "central_bank": "Bank of Canada",
                    "flag": "🇨🇦"
                },
                "AUD": {
                    "yield": "4.35%",
                    "prev_meeting": "2024-02-06",
                    "next_meeting": "2024-03-19",
                    "central_bank": "Reserve Bank of Australia",
                    "flag": "🇦🇺"
                },
                "NZD": {
                    "yield": "5.50%",
                    "prev_meeting": "2024-02-07",
                    "next_meeting": "2024-03-13",
                    "central_bank": "Reserve Bank of New Zealand",
                    "flag": "🇳🇿"
                }
            }
            
            # Function to display currency pairs as a table
            def show_currency_pairs_table(currency_code, current_data, prev_data, pairs):
                """Display table for pairs related to a specific currency"""
                # Filter pairs containing the currency
                related_pairs = [pair for pair in pairs if currency_code in pair]
                
                currency_full = currency_full_names.get(currency_code, currency_code)
                st.subheader(f"🔍 {currency_full} Pairs")
                
                # Calculate data for each pair
                table_data = []
                for pair in related_pairs:
                    base, quote = pair[:3], pair[3:]
                    
                    # Pair Strength
                    strength_today = current_data[base] - current_data[quote]
                    
                    # Signal based on pair strength
                    if strength_today > 0:
                        signal = "BUY"
                        signal_display = "🟢 BUY"
                    elif strength_today < 0:
                        signal = "SELL"
                        signal_display = "🔴 SELL"
                    else:
                        signal = "WAIT"
                        signal_display = "🟡 WAIT"
                    
                    # Calculate deltas if previous data available
                    if prev_data is not None:
                        delta = {c: current_data[c] - prev_data[c] for c in currencies}
                        base_delta = delta[base]
                        quote_delta = delta[quote]
                        health_delta = (current_data[base] - current_data[quote]) - (prev_data[base] - prev_data[quote])
                        volatility = abs(base_delta - quote_delta)
                        
                        # Delta Power (Change in pair strength)
                        delta_power = strength_today - (prev_data[base] - prev_data[quote])
                        
                        # Base vs Quote comparison
                        if current_data[base] > current_data[quote]:
                            base_vs_quote = f"{base} > {quote}"
                        elif current_data[base] < current_data[quote]:
                            base_vs_quote = f"{base} < {quote}"
                        else:
                            base_vs_quote = f"{base} = {quote}"
                        
                        # Economy (Confirmation - Up Trend / Down Trend / Range)
                        if base_delta > health_delta and quote_delta > health_delta:
                            economy = "📈 Up Trend"
                        elif base_delta < health_delta and quote_delta < health_delta:
                            economy = "📉 Down Trend"
                        else:
                            economy = "🔄 Range"
                    else:
                        base_delta = 0
                        quote_delta = 0
                        delta_power = 0
                        volatility = 0
                        base_vs_quote = "N/A"
                        economy = "❓ No Data"
                    
                    table_data.append({
                        "Pair": pair,
                        "Signal": signal_display,
                        "Power": f"{strength_today:+.0f}",
                        "Δ Power": f"{delta_power:+.0f}",
                        "Base vs Quote": base_vs_quote,
                        "Volatility": f"{volatility:.0f}",
                        "Economy": economy
                    })
                
                # Create DataFrame
                df_table = pd.DataFrame(table_data)
                
                # Sort by Power (highest first)
                df_table['Power_Num'] = df_table['Power'].str.replace('+', '').astype(float)
                df_table = df_table.sort_values('Power_Num', ascending=False).drop('Power_Num', axis=1)
                
                # Display table with custom styling
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
                        "Volatility": st.column_config.TextColumn("Volatility", width="small"),
                        "Economy": st.column_config.TextColumn("Economy", width="medium")
                    }
                )
                
                # Add color coding explanation
                st.caption("📌 **Note:** 🟢 BUY = Positive Power | 🔴 SELL = Negative Power | 🟡 WAIT = Zero Power")
            
            # Display currency cards in grid (2x4)
            for i in range(0, len(currencies), 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    currency_code = currencies[i]
                    strength = current_data[currency_code]
                    strength_color = "#10b981" if strength >= 0 else "#ef4444"
                    extra = currency_extra_data.get(currency_code, {})
                    full_name = currency_full_names.get(currency_code, currency_code)
                    
                    # Session state key for showing pairs table
                    if f"show_pairs_{currency_code}" not in st.session_state:
                        st.session_state[f"show_pairs_{currency_code}"] = False
                    
                    card_html = f'''
                    <div style="background: linear-gradient(135deg, #1e2a3a 0%, #0f172a 100%); 
                                border-radius: 15px; padding: 20px; margin: 10px 0;
                                border: 1px solid #334155;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <div style="font-size: 48px;">{extra.get('flag', '💰')}</div>
                            <div>
                                <h2 style="margin:0; color: #f1c40f;">{full_name}</h2>
                                <div style="font-size: 12px; color: #94a3b8;">{extra.get('central_bank', '')}</div>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                            <span>💪 Economic Strength:</span>
                            <span style="font-weight: bold; color: {strength_color};">{strength:+.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                            <span>📈 Yield:</span>
                            <span style="font-weight: bold; color: #f1c40f;">{extra.get('yield', 'N/A')}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;">
                            <span>📅 Previous Meeting:</span>
                            <span>{extra.get('prev_meeting', 'N/A')}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 13px;">
                            <span>📅 Next Meeting:</span>
                            <span style="color: #f1c40f;">{extra.get('next_meeting', 'N/A')}</span>
                        </div>
                    </div>
                    '''
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Single button to show pairs table
                    if st.button(f"📊 {full_name} Pairs", key=f"btn_{currency_code}"):
                        st.session_state[f"show_pairs_{currency_code}"] = not st.session_state[f"show_pairs_{currency_code}"]
                        st.rerun()
                    
                    # Show pairs table if button is active
                    if st.session_state[f"show_pairs_{currency_code}"]:
                        show_currency_pairs_table(currency_code, current_data, prev_data, pairs)
                
                if i + 1 < len(currencies):
                    with col2:
                        currency_code = currencies[i + 1]
                        strength = current_data[currency_code]
                        strength_color = "#10b981" if strength >= 0 else "#ef4444"
                        extra = currency_extra_data.get(currency_code, {})
                        full_name = currency_full_names.get(currency_code, currency_code)
                        
                        if f"show_pairs_{currency_code}" not in st.session_state:
                            st.session_state[f"show_pairs_{currency_code}"] = False
                        
                        card_html = f'''
                        <div style="background: linear-gradient(135deg, #1e2a3a 0%, #0f172a 100%); 
                                    border-radius: 15px; padding: 20px; margin: 10px 0;
                                    border: 1px solid #334155;">
                            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                                <div style="font-size: 48px;">{extra.get('flag', '💰')}</div>
                                <div>
                                    <h2 style="margin:0; color: #f1c40f;">{full_name}</h2>
                                    <div style="font-size: 12px; color: #94a3b8;">{extra.get('central_bank', '')}</div>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                                <span>💪 Economic Strength:</span>
                                <span style="font-weight: bold; color: {strength_color};">{strength:+.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                                <span>📈 Yield:</span>
                                <span style="font-weight: bold; color: #f1c40f;">{extra.get('yield', 'N/A')}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;">
                                <span>📅 Previous Meeting:</span>
                                <span>{extra.get('prev_meeting', 'N/A')}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 13px;">
                                <span>📅 Next Meeting:</span>
                                <span style="color: #f1c40f;">{extra.get('next_meeting', 'N/A')}</span>
                            </div>
                        </div>
                        '''
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Single button to show pairs table
                        if st.button(f"📊 {full_name} Pairs", key=f"btn_{currency_code}"):
                            st.session_state[f"show_pairs_{currency_code}"] = not st.session_state[f"show_pairs_{currency_code}"]
                            st.rerun()
                        
                        # Show pairs table if button is active
                        if st.session_state[f"show_pairs_{currency_code}"]:
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
        for i in range(0, len(currencies), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                currency = currencies[i]
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
            
            if i + 1 < len(currencies):
                with col2:
                    currency = currencies[i + 1]
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
        # الحصول على جميع التواريخ المتاحة من البيانات اليومية
        all_dates = db_daily['Date'].sort_values(ascending=False).tolist()  # ترتيب تنازلي (الأحدث أولاً)
        
        # تنسيق التواريخ للعرض
        date_options = []
        date_map = {}  # لتخزين العلاقة بين النص المعروض والقيمة الفعلية
        
        for date in all_dates:
            # تنسيق التاريخ بشكل مقروء (مثال: 2024-01-15)
            date_str = date.strftime("%Y-%m-%d")
            # تحديد ما إذا كان هذا هو اليوم الأحدث
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
                index=0,  # تحديد الأحدث كافتراضي
                key="date_selector"
            )
            
            # تحديث session state بالتاريخ المختار
            st.session_state.selected_date = date_map[selected_date_str]
            
            # عرض التاريخ المختار بشكل بارز
            st.markdown(f"""
            <div style="text-align: center; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                        border-radius: 10px; padding: 8px; margin: 10px 0; border: 1px solid #f1c40f;">
                <span style="color: #f1c40f; font-weight: bold;">📅 التاريخ المختار: {selected_date_str}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ================== حساب البيانات للتاريخ المختار ==================
        # الحصول على بيانات اليوم المختار
        selected_date = st.session_state.selected_date
        selected_row = db_daily[db_daily['Date'] == selected_date]
        
        if selected_row.empty:
            st.error(f"❌ لا توجد بيانات للتاريخ {selected_date_str}")
        else:
            latest = selected_row.iloc[0]
            
            # الحصول على البيانات السابقة (اليوم الذي يسبق التاريخ المختار)
            date_index = db_daily[db_daily['Date'] == selected_date].index[0]
            if date_index > 0:
                prev_row = db_daily.iloc[date_index - 1]
                prev = prev_row
            else:
                # إذا كان التاريخ المختار هو أول يوم، لا يوجد بيانات سابقة
                prev = None
                st.warning("⚠️ هذا هو أول يوم في البيانات، لا توجد بيانات سابقة لحساب التغيرات")
            
            # حساب الدلتا (التغيرات) إذا توجد بيانات سابقة
            delta = {}
            if prev is not None:
                delta = {c: latest[c] - prev[c] for c in currencies}
            
            results = []
            
            for pair in pairs:
                base, quote = pair[:3], pair[3:]
                
                # الإشارة الأساسية = قوة الزوج (Base - Quote)
                strength_today = latest[base] - latest[quote]
                
                # تحديد الإشارة بناءً على القوة
                if strength_today > 0:
                    signal = "BUY"
                    signal_color = "🟢"
                elif strength_today < 0:
                    signal = "SELL"
                    signal_color = "🔴"
                else:
                    signal = "WAIT"
                    signal_color = "🟡"
                
                # حساب قوة الإشارة (نسبة مئوية)
                max_strength = 5.0
                strength_percent = min(abs(strength_today) / max_strength * 100, 100)
                
                # حساب الدلتا (إذا توفرت بيانات سابقة)
                if prev is not None:
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
                else:
                    # إذا لم توجد بيانات سابقة، اعرض قيم صفرية
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
                    if "BUY" in row["الإشارة"]:
                        bg_gradient = "linear-gradient(135deg, #0a2f1f, #051a0f)"
                        border_color = "#10b981"
                    elif "SELL" in row["الإشارة"]:
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
                
                # ================== الكرت الثاني ==================
                with col2:
                    if i + 1 < len(df_results):
                        row = df_results.iloc[i + 1]
                        pair = row["الزوج"]
                        
                        # تحديد الألوان حسب الإشارة
                        if "BUY" in row["الإشارة"]:
                            bg_gradient = "linear-gradient(135deg, #0a2f1f, #051a0f)"
                            border_color = "#10b981"
                        elif "SELL" in row["الإشارة"]:
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
