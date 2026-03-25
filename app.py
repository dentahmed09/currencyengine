import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Currency Strength Engine v2", layout="wide")

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

# ==================== غيّر الأسماء دي حسب Google Sheet بتاعك ====================
SHEET_NAME = "Currency Daily Data"   # اسم الـ Google Sheet بالظبط
DAILY_WS   = "daily"                 # اسم تبويب اليومي
WEEKLY_WS  = "weekly"                # اسم تبويب الأسبوعي
MONTHLY_WS = "monthly"               # اسم تبويب الشهري

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
    sheet = client.open(SHEET_NAME)
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
    sheet = client.open(SHEET_NAME)
    ws = sheet.worksheet(worksheet_name)
    ws.clear()
    ws.update([df.columns.tolist()] + df.values.tolist())

# ====================== تحميل البيانات ======================
db_daily   = load_data(DAILY_WS, "Date")
db_weekly  = load_data(WEEKLY_WS, "Week_Start")
db_monthly = load_data(MONTHLY_WS, "Month_Start")

st.title("Currency Strength Engine v2")

tab_input, tab_dashboard, tab_results = st.tabs([
    "📥 إدخال البيانات",
    "📊 داش بورد يومي",
    "🔍 نتائج الأزواج",
])

# ──── تبويب الإدخال ────────────────────────────────────────────────────
with tab_input:
    st.header("إدخال البيانات")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("يومي")
        with st.form("daily_form", clear_on_submit=True):
            d_date = st.date_input("التاريخ", datetime.now().date(), key="d_date")
            d_scores = {c: st.number_input(f"{c}", -100., 100., 0., 0.1, format="%.2f", key=f"d_{c}") for c in currencies}
            
            if st.form_submit_button("حفظ يومي"):
                curr = load_data(DAILY_WS, "Date")
                new = pd.DataFrame([{"Date": d_date, **d_scores}])
                new['Date'] = pd.to_datetime(new['Date']).dt.date
                
                if not curr.empty:
                    curr = curr[curr['Date'] != d_date]
                
                final = pd.concat([curr, new]).sort_values('Date')
                save_data(final, DAILY_WS)
                st.success("✅ تم حفظ البيانات اليومية")
                st.rerun()

    with col2:
        st.subheader("أسبوعي")
        with st.form("weekly_form", clear_on_submit=True):
            w_date = st.date_input("بداية الأسبوع", datetime.now().date(), key="w_date")
            w_scores = {c: st.number_input(f"{c}", -100., 100., 0., 0.1, format="%.2f", key=f"w_{c}") for c in currencies}
            
            if st.form_submit_button("حفظ أسبوعي"):
                curr = load_data(WEEKLY_WS, "Week_Start")
                new = pd.DataFrame([{"Week_Start": w_date, **w_scores}])
                new['Week_Start'] = pd.to_datetime(new['Week_Start']).dt.date
                
                if not curr.empty:
                    curr = curr[curr['Week_Start'] != w_date]
                
                final = pd.concat([curr, new]).sort_values('Week_Start')
                save_data(final, WEEKLY_WS)
                st.success("✅ تم حفظ البيانات الأسبوعية")
                st.rerun()

    with col3:
        st.subheader("شهري")
        with st.form("monthly_form", clear_on_submit=True):
            m_date = st.date_input("بداية الشهر", datetime.now().date(), key="m_date")
            m_scores = {c: st.number_input(f"{c}", -100., 100., 0., 0.1, format="%.2f", key=f"m_{c}") for c in currencies}
            
            if st.form_submit_button("حفظ شهري"):
                curr = load_data(MONTHLY_WS, "Month_Start")
                new = pd.DataFrame([{"Month_Start": m_date, **m_scores}])
                new['Month_Start'] = pd.to_datetime(new['Month_Start']).dt.date
                
                if not curr.empty:
                    curr = curr[curr['Month_Start'] != m_date]
                
                final = pd.concat([curr, new]).sort_values('Month_Start')
                save_data(final, MONTHLY_WS)
                st.success("✅ تم حفظ البيانات الشهرية")
                st.rerun()

# ──── تبويب داش بورد يومي ─────────────────────────────────
with tab_dashboard:
    if db_daily.empty:
        st.info("أدخل بيانات يومية أولاً")
    else:
        st.header("🌙 داش بورد يومي – آخر تحديث")
        
        latest = db_daily.iloc[-1]
        prev = db_daily.iloc[-2] if len(db_daily) >= 2 else None
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥧 ترتيب العملات حسب القوة")
            strength_df = latest[currencies].to_frame('القوة').sort_values('القوة', ascending=False).reset_index(names='العملة')
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=strength_df['العملة'],
                values=strength_df['القوة'].abs(),
                textinfo='label+percent',
                hole=0.35,
                marker=dict(colors=['#f39c12', '#e67e22', '#e74c3c', '#3498db', '#2ecc71', '#1abc9c', '#9b59b6', '#34495e']),
            )])
            fig_pie.update_layout(title="توزيع قوة العملات", height=500, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
            
            with st.expander("عرض الترتيب التفصيلي"):
                st.dataframe(strength_df.style.format({'القوة': '{:.2f}'}), hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 التغيرات اليومية")
            if prev is not None:
                deltas = {c: latest[c] - prev[c] for c in currencies}
                sorted_currencies = sorted(currencies, key=lambda x: deltas[x])
                sorted_deltas = [deltas[c] for c in sorted_currencies]
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=sorted_currencies,
                    y=sorted_deltas,
                    marker_color=['#ef4444' if x < 0 else '#10b981' if x > 0 else '#6b7280' for x in sorted_deltas],
                    text=[f"{x:+.2f}" for x in sorted_deltas],
                    textposition='outside'
                ))
                fig_bar.update_layout(title="التغيرات اليومية", height=500, template="plotly_dark")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("لا يوجد يوم سابق لحساب التغيرات")

        # باقي الشارتات (الـ 8 عملات) - محتفظين بالكود الأصلي
        st.markdown("---")
        st.subheader("📈 تطور قوة العملات (يومي - أسبوعي - شهري)")
        
        for i in range(0, len(currencies), 2):
            for j in range(2):
                if i + j >= len(currencies):
                    break
                currency = currencies[i + j]
                st.markdown(f"### 💱 {currency}")
                
                chart_data = pd.DataFrame()
                
                if not db_daily.empty:
                    daily = db_daily[['Date', currency]].copy().rename(columns={currency: 'يومي'})
                    chart_data = daily
                if not db_weekly.empty:
                    weekly = db_weekly[['Week_Start', currency]].copy().rename(columns={'Week_Start': 'Date', currency: 'أسبوعي'})
                    chart_data = chart_data.merge(weekly, on='Date', how='outer') if not chart_data.empty else weekly
                if not db_monthly.empty:
                    monthly = db_monthly[['Month_Start', currency]].copy().rename(columns={'Month_Start': 'Date', currency: 'شهري'})
                    chart_data = chart_data.merge(monthly, on='Date', how='outer') if not chart_data.empty else monthly
                
                if not chart_data.empty:
                    chart_data = chart_data.sort_values('Date').reset_index(drop=True)
                    fig = go.Figure()
                    
                    if 'يومي' in chart_data.columns:
                        fig.add_trace(go.Scatter(x=chart_data['Date'], y=chart_data['يومي'], name='يومي', line=dict(color='#3498db', width=2.5)))
                    if 'أسبوعي' in chart_data.columns:
                        fig.add_trace(go.Scatter(x=chart_data['Date'], y=chart_data['أسبوعي'], name='أسبوعي', line=dict(color='#f1c40f', width=2.5, dash='dash')))
                    if 'شهري' in chart_data.columns:
                        fig.add_trace(go.Scatter(x=chart_data['Date'], y=chart_data['شهري'], name='شهري', line=dict(color='white', width=2.5, dash='dot')))
                    
                    fig.update_layout(
                        title=f"{currency} - تطور القوة",
                        xaxis_title="التاريخ",
                        yaxis_title="قوة العملة",
                        height=400,
                        template="plotly_dark",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"لا توجد بيانات لـ {currency}")

# ──── تبويب نتائج الأزواج ─────────────────────────────────
with tab_results:
    if db_daily.empty or len(db_daily) < 2:
        st.info("أدخل بيانات يومين على الأقل لعرض النتائج")
    else:
        st.header("نتائج الأزواج – تحليل 5 نقاط")
        
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
                signal = "شراء"
                color = "🟢"
                strength = min(total_score * 20, 100)
            elif total_score < 0:
                signal = "بيع"
                color = "🔴"
                strength = min(abs(total_score) * 20, 100)
            else:
                signal = "ثبات"
                color = "🟡"
                strength = 0
            
            results.append({
                "الزوج": pair, "H": health_delta, "B": base_delta, "Q": quote_delta,
                "Comp": score_comp, "Diff": score_diff, "Total": total_score,
                "الإشارة": f"{color} {signal}", "القوة %": strength,
                "score_h": score_h, "score_b": score_b, "score_q": score_q,
                "score_comp": score_comp, "score_diff": score_diff
            })
        
        df_results = pd.DataFrame(results).sort_values("Total", ascending=False).reset_index(drop=True)
        
        for idx, row in df_results.iterrows():
            pair = row["الزوج"]
            total = row["Total"]
            signal = row["الإشارة"]
            strength = row["القوة %"]
            
            categories = ['H (Health Δ)', 'B (Base Δ)', 'Q (Quote Δ)', 'Comp', 'Diff']
            values = [row["score_h"], row["score_b"], row["score_q"], row["score_comp"], row["score_diff"]]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=values, y=categories, orientation='h',
                                 marker_color=['gold' if v > 0 else 'red' if v < 0 else 'gray' for v in values],
                                 text=values, textposition='auto'))
            fig.update_layout(
                title=f"{pair} → {signal} | Total Score: {total} | قوة الإشارة: {strength:.0f}%",
                xaxis=dict(range=[-1.2, 1.2]),
                height=280,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Health Delta", f"{row['H']:+.2f}")
            col2.metric("Base Delta", f"{row['B']:+.2f}")
            col3.metric("Quote Delta", f"{row['Q']:+.2f}")
            col4.metric("Total Score", f"{total} / 5")
            
            st.markdown("---")
        
        st.subheader("ملخص الإشارات")
        summary_df = df_results[["الزوج", "Total", "الإشارة", "القوة %"]].copy()
        st.dataframe(summary_df.style.format({"Total": "{:+d}", "القوة %": "{:.0f}%"}), 
                     hide_index=True, use_container_width=True, height=600)

# ──── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**التخزين**")
    st.caption(f"Google Sheet: **{SHEET_NAME}**")
    st.caption(f"يومي: {DAILY_WS} | أسبوعي: {WEEKLY_WS} | شهري: {MONTHLY_WS}")
    
    if st.button("🗑️ مسح كل البيانات"):
        if st.checkbox("متأكد؟ سيتم حذف كل البيانات من Google Sheets"):
            empty_df = pd.DataFrame(columns=["Date"] + currencies)
            save_data(empty_df, DAILY_WS)
            save_data(pd.DataFrame(columns=["Week_Start"] + currencies), WEEKLY_WS)
            save_data(pd.DataFrame(columns=["Month_Start"] + currencies), MONTHLY_WS)
            st.success("تم مسح كل البيانات")
            st.rerun()
