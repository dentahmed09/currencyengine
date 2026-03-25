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

# ==================== Sheet ID (من اللينك بتاعك) ====================
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
# ──── تبويب نتائج الأزواج (مع إضافة زر لعرض الشارت) ─────────────────────
with tab_results:
    if db_daily.empty or len(db_daily) < 2:
        st.info("أدخل بيانات يومين على الأقل لعرض النتائج")
    else:
        st.header("نتائج الأزواج – تحليل 5 نقاط")
        
        # تهيئة session state لتخزين حالة الشارتات
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
        
        st.subheader("تحليل الـ 5 نقاط لكل زوج")
        
        for idx, row in df_results.iterrows():
            pair = row["الزوج"]
            total = row["Total"]
            signal = row["الإشارة"]
            strength = row["القوة %"]
            
            categories = ['H (Health Δ)', 'B (Base Δ)', 'Q (Quote Δ)', 'Comp', 'Diff']
            values = [row["score_h"], row["score_b"], row["score_q"], row["score_comp"], row["score_diff"]]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=values, y=categories, orientation='h',
                marker_color=['gold' if v > 0 else 'red' if v < 0 else 'gray' for v in values],
                text=values, textposition='auto', width=0.6
            ))
            fig.update_layout(
                title=f"{pair}  →  {signal}   |   Total Score: {total}   |   قوة الإشارة: {strength:.0f}%",
                xaxis=dict(range=[-1.2, 1.2], dtick=1, zeroline=True, zerolinecolor='black', zerolinewidth=3),
                yaxis=dict(title=""), height=280, template="plotly_white", margin=dict(l=80, r=20, t=60, b=40)
            )
            st.plotly_chart(fig, use_container_width=True, key=f"results_chart_{pair}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Health Delta", f"{row['H']:+.2f}")
            col2.metric("Base Delta", f"{row['B']:+.2f}")
            col3.metric("Quote Delta", f"{row['Q']:+.2f}")
            col4.metric("Total Score", f"{total} / 5")
            
            # زر عرض الشارت للزوج
            if st.button(f"📈 عرض شارت {pair}", key=f"btn_chart_{pair}"):
                # تبديل حالة الشارت
                st.session_state.show_chart[pair] = not st.session_state.show_chart.get(pair, False)
            
            # عرض الشارت إذا كان الزر مفعلاً
            if st.session_state.show_chart.get(pair, False):
                st.markdown(f"#### 📊 شارت الزوج {pair}")
                
                base, quote = pair[:3], pair[3:]
                plot_df = db_daily.set_index('Date')
                
                if base not in plot_df.columns or quote not in plot_df.columns:
                    st.warning(f"⚠️ البيانات غير كاملة للزوج {pair}")
                else:
                    plot_df['Strength'] = plot_df[base] - plot_df[quote]
                    plot_df['Δ ' + base] = plot_df[base].diff()
                    plot_df['Δ ' + quote] = plot_df[quote].diff()
                    plot_df = plot_df.dropna(subset=['Δ ' + base, 'Δ ' + quote])
                    
                    if plot_df.empty:
                        st.warning("⚠️ بيانات غير كافية لرسم الشارت")
                    else:
                        fig_pair = go.Figure()
                        
                        fig_pair.add_trace(go.Scatter(
                            x=plot_df.index, y=plot_df['Strength'],
                            name=f"✨ قوة {pair}",
                            line=dict(color='#f1c40f', width=3.5),
                            mode='lines+markers',
                            fill='tozeroy',
                            fillcolor='rgba(241, 196, 15, 0.1)'
                        ))
                        
                        fig_pair.add_trace(go.Scatter(
                            x=plot_df.index, y=plot_df['Δ ' + base],
                            name=f"📈 تغير {base}",
                            line=dict(color='#10b981', width=2.5, dash='dash'),
                            yaxis='y2'
                        ))
                        
                        fig_pair.add_trace(go.Scatter(
                            x=plot_df.index, y=plot_df['Δ ' + quote],
                            name=f"📉 تغير {quote}",
                            line=dict(color='#ef4444', width=2.5, dash='dash'),
                            yaxis='y2'
                        ))
                        
                        fig_pair.add_hline(y=0, line_dash="solid", line_color="#6b7280", line_width=1.5)
                        
                        fig_pair.update_layout(
                            title=dict(text=f"<b>{pair}</b> – قوة الزوج والتغييرات اليومية",
                                      font=dict(size=18, color='#f1c40f'), x=0.5),
                            height=500,
                            yaxis=dict(title=dict(text=f"<b>قوة الزوج</b><br>({base} - {quote})", font=dict(size=12))),
                            yaxis2=dict(title=dict(text="<b>التغيير اليومي</b>", font=dict(size=12)),
                                       overlaying='y', side='right', showgrid=False),
                            template="plotly_dark",
                            hovermode="x unified",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                            plot_bgcolor='rgba(15, 23, 42, 0.8)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(t=80, b=50, l=60, r=80)
                        )
                        
                        st.plotly_chart(fig_pair, use_container_width=True)
                        
                        # عرض آخر القيم
                        last = plot_df.iloc[-1]
                        c1, c2, c3 = st.columns(3)
                        c1.metric("قوة الزوج", f"{last['Strength']:.2f}")
                        c2.metric(f"Δ {base}", f"{last['Δ ' + base]:+.2f}")
                        c3.metric(f"Δ {quote}", f"{last['Δ ' + quote]:+.2f}")
            
            st.markdown("---")
        
        st.subheader("ملخص الإشارات")
        summary_df = df_results[["الزوج", "Total", "الإشارة", "القوة %"]].copy()
        summary_df = summary_df.style.format({"Total": "{:+d}", "القوة %": "{:.0f}%"})
        st.dataframe(summary_df, hide_index=True, use_container_width=True, height=600)
