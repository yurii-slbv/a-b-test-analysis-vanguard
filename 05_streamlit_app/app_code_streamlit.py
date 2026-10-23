import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & LIGHT MODE STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vanguard A/B Test Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for executive metric cards (st.metric)
st.markdown("""
    <style>
    /* Metric Cards Styling with uniform height */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.04);
        min-height: 140px; /* Forza la stessa altezza per tutti e tre i riquadri */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    div[data-testid="stMetric"] label, 
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
    }

    /* Key Findings Box Styling */
.key-finding-box {
    background-color: #f1f5f9;
    border-left: 5px solid #00d26a;
    padding: 18px 22px;
    border-radius: 8px;
    margin-bottom: 20px;
    color: #0f172a !important;
}
.key-finding-box h4 {
    color: #0f172a !important;
    margin-top: 0;
}
.key-finding-box li {
    color: #334155 !important;
    margin-bottom: 6px;
}
.key-finding-box b {
    color: #0f172a !important;
}
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. DATA LOADING & CACHING
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("vanguard_tableau_final.csv")
    df['date_time'] = pd.to_datetime(df['date_time'])
    return df

df = load_data()


# ---------------------------------------------------------
# 3. SIDEBAR FILTERS (ALL STRINGS IN ENGLISH)
# ---------------------------------------------------------
st.sidebar.header("🔍 Analysis Filters")

# Filter: Experimental Group using Checkboxes
st.sidebar.subheader("Experimental Group:")
show_control = st.sidebar.checkbox("Control", value=True)
show_test = st.sidebar.checkbox("Test", value=True)

# Build list of active variations
selected_variations = []
if show_control:
    selected_variations.append("Control")
if show_test:
    selected_variations.append("Test")

# Filter: Age Group
age_options = ["All"] + sorted([str(x) for x in df['age_group'].dropna().unique()])
selected_age = st.sidebar.selectbox("Age Group:", age_options)

# Filter: Gender
gender_options = ["All"] + list(df['gendr'].dropna().unique())
selected_gender = st.sidebar.selectbox("Gender:", gender_options)

# Apply filters dynamically to dataset
df_filtered = df.copy()

# Filter dataset by selected variation checkboxes
df_filtered = df_filtered[df_filtered['Variation'].isin(selected_variations)]

if selected_age != "All":
    df_filtered = df_filtered[df_filtered['age_group'] == selected_age]

if selected_gender != "All":
    df_filtered = df_filtered[df_filtered['gendr'] == selected_gender]

# ---------------------------------------------------------
# 4. HEADER & TOP-LEVEL KPI CARDS
# ---------------------------------------------------------
st.title("📊 Vanguard A/B Test Results Dashboard")
st.markdown(
    "An interactive executive overview analyzing **User Experience**, **Funnel Conversion Rates**, "
    "and **Error Rates** between the **Control** and **Test** groups."
)

st.divider()

# Compute dynamic KPI values based on total unique clients in each group (confirm / total_clients)
total_clients = df_filtered['client_id'].nunique()
clients_confirm = df_filtered[df_filtered['process_step'] == 'confirm']['client_id'].nunique()

# Definition: confirmed clients / total unique clients
completion_rate = (clients_confirm / total_clients * 100) if total_clients > 0 else 0.0

total_events = df_filtered['visit_id'].count()
total_errors = df_filtered['is_error'].sum()
overall_error_rate = (total_errors / total_events * 100) if total_events > 0 else 0.0

# Render top metric banner
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    st.metric(label="Total Unique Clients", value=f"{total_clients:,}")

with kpi_col2:
    st.metric(
        label="Overall Completion Rate",
        value=f"{completion_rate:.2f}%",
        delta=f"Confirmed: {clients_confirm:,} / {total_clients:,}"
    )

with kpi_col3:
    st.metric(
        label="Overall Error Rate",
        value=f"{overall_error_rate:.2f}%",
        delta=f"Total Errors: {total_errors:,}",
        delta_color="inverse"
    )


# ---------------------------------------------------------
# 5. KEY FINDINGS BOX (EXECUTIVE TAKEAWAYS)
# ---------------------------------------------------------
st.subheader("📌 Key Executive Findings")

if set(selected_variations) == {"Control", "Test"}:
    ctrl_total = df_filtered[df_filtered['Variation'] == 'Control']['client_id'].nunique()
    ctrl_confirm = df_filtered[(df_filtered['Variation'] == 'Control') & (df_filtered['process_step'] == 'confirm')]['client_id'].nunique()
    test_total = df_filtered[df_filtered['Variation'] == 'Test']['client_id'].nunique()
    test_confirm = df_filtered[(df_filtered['Variation'] == 'Test') & (df_filtered['process_step'] == 'confirm')]['client_id'].nunique()
    
    rate_ctrl = (ctrl_confirm / ctrl_total * 100) if ctrl_total > 0 else 0.0
    rate_test = (test_confirm / test_total * 100) if test_total > 0 else 0.0
    uplift = rate_test - rate_ctrl
    target_gap = 5.0 - uplift

    st.markdown(f"""
    <div class="key-finding-box">
        <h4>Executive Summary Highlights</h4>
        <ul>
            <li><b>Statistically Significant Uplift:</b> The Test UI improved completion rate from <b>{rate_ctrl:.2f}%</b> to <b>{rate_test:.2f}%</b> (+<b>{uplift:.2f}%</b> uplift).</li>
            <li><b>Below Target Threshold:</b> The +{uplift:.2f}% lift is statistically significant but falls short of Vanguard's <b>5.0 percentage point</b> target by <b>{target_gap:.2f}%</b>.</li>
            <li><b>Friction at Onboarding:</b> Step 1 is 23% slower in the Test group and users navigate back to Start twice as often (19% vs 11%).</li>
            <li><b>Recommendation:</b> Do not roll out the current version yet. Refine Step 1 usability and re-test.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
elif len(selected_variations) == 1:
    st.info(f"Currently displaying metrics exclusively for the **{selected_variations[0]}** group.")
else:
    st.warning("⚠️ Please select at least one Experimental Group checkbox in the sidebar.")

st.divider()
# ---------------------------------------------------------
# 6. TABBED VISUALIZATIONS & DEEP DIVE ANALYTICS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏆 Completion Rate (Main KPI)",
    "📉 Funnel Analysis", 
    "🔀 Sankey Navigation Flow",
    "⏱️ Time-on-Step Analysis",
    "⚠️ Error Rate Analysis", 
    "🔥 Demographics & Drop-off Heatmap",
    "👥 Demographics & Hypothesis Testing"
])

step_label_map = {'start': 'Start', 'step_1': 'Step 1', 'step_2': 'Step 2', 'step_3': 'Step 3', 'confirm': 'Confirm'}
step_order = ['Start', 'Step 1', 'Step 2', 'Step 3', 'Confirm']


# =========================================================
# --- TAB 1: MAIN KPI - COMPLETION RATE VS 5PP TARGET ---
# =========================================================
with tab1:
    st.subheader("🏆 Main KPI: Completion Rate vs. 5 pp Target")
    
    comp_df = df_filtered.groupby('Variation').agg(
        total_clients=('client_id', 'nunique'),
        confirmed_clients=('client_id', lambda x: x[df_filtered.loc[x.index, 'process_step'] == 'confirm'].nunique())
    ).reset_index()
    
    comp_df['completion_rate'] = (comp_df['confirmed_clients'] / comp_df['total_clients']) * 100
    
    ctrl_row = comp_df[comp_df['Variation'] == 'Control']
    ctrl_rate = ctrl_row['completion_rate'].values[0] if not ctrl_row.empty else 0.0
    target_threshold = ctrl_rate + 5.0
    
    fig_kpi = px.bar(
        comp_df,
        x='Variation',
        y='completion_rate',
        text=comp_df['completion_rate'].apply(lambda x: f"{x:.2f}%"),
        labels={'Variation': 'Experimental Group', 'completion_rate': 'Completion Rate (%)'},
        title="Completion Rate Comparison with Vanguard's 5 pp Target Line",
        color='Variation',
        color_discrete_map={'Control': '#1f77b4', 'Test': '#ff7f0e'}
    )
    
    if ctrl_rate > 0:
        fig_kpi.add_hline(
            y=target_threshold,
            line_dash="dash",
            line_color="#ff4b4b",
            line_width=2,
            annotation_text=f"5 pp Target Threshold ({target_threshold:.2f}%)",
            annotation_position="top right"
        )
    
    fig_kpi.update_layout(yaxis_range=[0, 85])
    st.plotly_chart(fig_kpi, use_container_width=True)
    
    # 1-sentence chart takeaway
    st.caption("💡 **Takeaway:** The Test UI improves completion to 69.29% (+3.71%), but remains below Vanguard's required 5.0 percentage point target threshold (70.58%).")


# --- TAB 2: FUNNEL ANALYSIS ---
with tab2:
    st.subheader("📉Funnel Conversion Rate by Step")
    
    funnel_df = df_filtered.groupby(['process_step', 'Variation'])['client_id'].nunique().reset_index()
    
    group_totals = df_filtered.groupby('Variation')['client_id'].nunique().to_dict()
    funnel_df['group_total_clients'] = funnel_df['Variation'].map(group_totals)
    funnel_df['retention_percentage'] = (funnel_df['client_id'] / funnel_df['group_total_clients']) * 100
    
    funnel_df['process_step'] = funnel_df['process_step'].map(step_label_map)
    funnel_df = funnel_df[funnel_df['process_step'].isin(step_order)]
    funnel_df['process_step'] = pd.Categorical(funnel_df['process_step'], categories=step_order, ordered=True)
    funnel_df = funnel_df.sort_values('process_step')
    
    fig_funnel = px.bar(
        funnel_df, x='process_step', y='retention_percentage', color='Variation', barmode='group',
        text=funnel_df['retention_percentage'].apply(lambda x: f"{x:.1f}%"),
        labels={'process_step': 'Process Step', 'retention_percentage': 'Retention Rate (% of All Clients)'},
        title="Client Retention Rate Across Process Steps (Share of Total Group Sample)",
        color_discrete_map={'Control': '#1f77b4', 'Test': '#ff7f0e'}
    )
    fig_funnel.update_layout(yaxis_range=[0, 110], hovermode="x unified")
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # 1-sentence chart takeaway
    st.caption("💡 **Takeaway:** The Test UI maintains higher retention across every step, leading to higher final confirmation.")


# --- TAB 3: SANKEY NAVIGATION FLOW ---
with tab3:
    st.subheader("🔀 User Navigation Flow (Sankey Diagram)")
    st.markdown("Visualize real user transitions between process steps, highlighting forward progress and backward loops.")
    
    sankey_group = st.radio("Select Experimental Group for Sankey Flow:", ["Test", "Control"], horizontal=True)
    
    df_sankey = df_filtered[df_filtered['Variation'] == sankey_group].sort_values(['visit_id', 'date_time'])
    df_sankey['next_step'] = df_sankey.groupby('visit_id')['process_step'].shift(-1)
    
    trans_counts = df_sankey.dropna(subset=['next_step']).groupby(['process_step', 'next_step']).size().reset_index(name='value')
    
    all_raw_steps = ['start', 'step_1', 'step_2', 'step_3', 'confirm']
    raw_step_map = {step: i for i, step in enumerate(all_raw_steps)}
    
    trans_counts['source'] = trans_counts['process_step'].map(raw_step_map)
    trans_counts['target'] = trans_counts['next_step'].map(raw_step_map)
    
    trans_counts_clean = trans_counts[trans_counts['source'] != trans_counts['target']]
    
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15, thickness=20, line=dict(color="black", width=0.5),
            label=['Start', 'Step 1', 'Step 2', 'Step 3', 'Confirm'],
            color=['#1f77b4', '#386cb0', '#7fc97f', '#beaed4', '#fdc086']
        ),
        link=dict(
            source=trans_counts_clean['source'].tolist(),
            target=trans_counts_clean['target'].tolist(),
            value=trans_counts_clean['value'].tolist()
        )
    )])
    fig_sankey.update_layout(title_text=f"Navigation Flow Transitions - {sankey_group} Group", font_size=12)
    st.plotly_chart(fig_sankey, use_container_width=True)
    
    # 1-sentence chart takeaway
    st.caption(f"💡 **Takeaway:** The Sankey diagram reveals significant backward loops from Step 1 back to Start in the {sankey_group} group.")


# --- TAB 4: TIME-ON-STEP ANALYSIS ---
with tab4:
    st.subheader("⏱️ Time-on-Step Duration Analysis")
    st.markdown("Analyze median seconds spent by users on each step before transitioning to the next screen.")
    
    df_time = df_filtered.sort_values(['visit_id', 'date_time'])
    df_time['next_date_time'] = df_time.groupby('visit_id')['date_time'].shift(-1)
    df_time['duration_sec'] = (df_time['next_date_time'] - df_time['date_time']).dt.total_seconds()
    
    valid_time_df = df_time[(df_time['duration_sec'] > 0) & (df_time['duration_sec'] <= 1800)].copy()
    valid_time_df['process_step_clean'] = valid_time_df['process_step'].map(step_label_map)
    
    duration_summary = valid_time_df.groupby(['process_step_clean', 'Variation'])['duration_sec'].median().reset_index()
    duration_summary['process_step_clean'] = pd.Categorical(duration_summary['process_step_clean'], categories=step_order, ordered=True)
    duration_summary = duration_summary.sort_values('process_step_clean')
    
    fig_time = px.bar(
        duration_summary, x='process_step_clean', y='duration_sec', color='Variation', barmode='group',
        text=duration_summary['duration_sec'].apply(lambda x: f"{x:.0f}s"),
        labels={'process_step_clean': 'Process Step', 'duration_sec': 'Median Duration (Seconds)'},
        title="Median Time Spent Per Step (Control vs Test)",
        color_discrete_map={'Control': '#1f77b4', 'Test': '#ff7f0e'}
    )
    st.plotly_chart(fig_time, use_container_width=True)
    
    # 1-sentence chart takeaway
    st.caption("💡 **Takeaway:** Users in the Test group spend 23% longer on Step 1 (27s vs 20s), signaling higher initial cognitive friction.")


# --- TAB 5: ERROR RATE ANALYSIS ---
with tab5:
    st.subheader("⚠️Error Rate Analysis (Backward Navigation)")
    
    error_df = df_filtered.groupby(['process_step', 'Variation']).agg(
        total_errors=('is_error', 'sum'), total_visits=('visit_id', 'count')
    ).reset_index()
    error_df['error_rate'] = (error_df['total_errors'] / error_df['total_visits']) * 100
    error_df['process_step'] = error_df['process_step'].map(step_label_map)
    error_df['process_step'] = pd.Categorical(error_df['process_step'], categories=step_order, ordered=True)
    error_df = error_df.sort_values('process_step')
    
    fig_error = px.bar(
        error_df, x='process_step', y='error_rate', color='Variation', barmode='group',
        text=error_df['error_rate'].apply(lambda x: f"{x:.2f}%"),
        labels={'process_step': 'Process Step', 'error_rate': 'Error Rate (%)'},
        title="Error Rate by Process Step",
        color_discrete_map={'Control': '#1f77b4', 'Test': '#ff7f0e'}
    )
    fig_error.update_layout(yaxis_range=[0, max(error_df['error_rate'].max() * 1.2, 10) if not error_df.empty else 10])
    st.plotly_chart(fig_error, use_container_width=True)
    
    # 1-sentence chart takeaway
    st.caption("💡 **Takeaway:** The error rate at the Start step is significantly higher in the Test group (19.05% vs 10.86%), showing frequent backward navigation.")


# --- TAB 6: DEMOGRAPHICS & HYPOTHESIS TESTING ---
with tab6:
    col_demo, col_stat = st.columns([3, 2])
    
    with col_demo:
        st.subheader("🔥 Step-by-Step Drop-Off Rate Heatmap")
        st.markdown("Percentage of users dropping off between consecutive steps across age groups.")
        
        pivot_clients = df_filtered.groupby(['age_group', 'process_step'])['client_id'].nunique().unstack(fill_value=0)
        raw_steps = ['start', 'step_1', 'step_2', 'step_3', 'confirm']
        existing_steps = [s for s in raw_steps if s in pivot_clients.columns]
        
        if len(existing_steps) > 1:
            pivot_clients = pivot_clients[existing_steps]
            dropoff_data = pd.DataFrame(index=pivot_clients.index)
            step_names = ['Start', 'Step 1', 'Step 2', 'Step 3', 'Confirm']
            
            for i in range(len(existing_steps) - 1):
                col_curr = existing_steps[i]
                col_next = existing_steps[i + 1]
                label_curr = step_names[i]
                label_next = step_names[i + 1]
                
                dropoff_data[f"{label_curr} ➔ {label_next}"] = (
                    (pivot_clients[col_curr] - pivot_clients[col_next]) / pivot_clients[col_curr] * 100
                ).clip(lower=0)
            
            fig_heatmap = px.imshow(
                dropoff_data,
                text_auto=".1f",
                color_continuous_scale="Reds",
                labels=dict(x="Step Transition", y="Age Group", color="Drop-off Rate (%)"),
                title="Drop-off Rate (%) Heatmap by Age Group"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            st.caption("💡 **Takeaway:** Senior clients (65+) experience the highest drop-off rate between Step 3 and Confirmation (17.2%).")
            
    with col_stat:
        st.subheader("🧪 Statistical Significance Test")
        st.write("Two-sample Z-Test for Completion Rate proportions:")
        
        ctrl_total = df_filtered[df_filtered['Variation'] == 'Control']['client_id'].nunique()
        ctrl_confirm = df_filtered[(df_filtered['Variation'] == 'Control') & (df_filtered['process_step'] == 'confirm')]['client_id'].nunique()
        test_total = df_filtered[df_filtered['Variation'] == 'Test']['client_id'].nunique()
        test_confirm = df_filtered[(df_filtered['Variation'] == 'Test') & (df_filtered['process_step'] == 'confirm')]['client_id'].nunique()
        
        if ctrl_total > 0 and test_total > 0:
            p1 = test_confirm / test_total
            p2 = ctrl_confirm / ctrl_total
            p_pooled = (test_confirm + ctrl_confirm) / (test_total + ctrl_total)
            
            se = np.sqrt(p_pooled * (1 - p_pooled) * (1/test_total + 1/ctrl_total))
            z_stat = (p1 - p2) / se
            p_value = norm.sf(abs(z_stat)) * 2
            
            st.metric(label="Z-Statistic", value=f"{z_stat:.4f}")
            st.metric(label="P-Value", value=f"{p_value:.5e}")
            
            is_significant = p_value < 0.05
            if is_significant:
                st.success("✅ **Statistically Significant** (p < 0.05). The conversion uplift is real and not due to random noise.")
            else:
                st.warning("⚠️ **Not Statistically Significant** (p >= 0.05). No statistical difference detected.")
        else:
            st.info("Select 'All' in experimental group filter to compare Control and Test statistically.")

# --- ADDITION 7: Demographics, Heatmaps & Hypothesis Testing (Z-Test) ---
with tab7:
    col_demo, col_stat = st.columns([3, 2])
    
    with col_demo:
        st.subheader("👥Conversion Rate by Age Group")
        age_df = df_filtered.groupby(['age_group', 'Variation', 'process_step'])['client_id'].nunique().unstack(fill_value=0).reset_index()
        
        if 'start' in age_df.columns and 'confirm' in age_df.columns:
            age_df['conversion_rate'] = (age_df['confirm'] / age_df['start']) * 100
            fig_age = px.bar(
                age_df, x='age_group', y='conversion_rate', color='Variation', barmode='group',
                text=age_df['conversion_rate'].apply(lambda x: f"{x:.1f}%"),
                labels={'age_group': 'Age Group', 'conversion_rate': 'Conversion Rate (%)'},
                title="Conversion Rate Comparison Across Age Groups",
                color_discrete_map={'Control': '#1f77b4', 'Test': '#ff7f0e'}
            )
            fig_age.update_layout(yaxis_range=[0, 110])
            st.plotly_chart(fig_age, use_container_width=True)
            st.caption("💡 **Takeaway:** The Test UI improves conversion across all age groups, with the strongest gains seen in Under 35 (+5.1 pp) and 65+ (+6.7 pp) clients, backed by absolute statistical significance (p < 0.001).")
    with col_stat:
        st.subheader("🧪 Statistical Significance Test")
        st.write("Two-sample Z-Test for Completion Rate proportions:")
        
        ctrl_start = df_filtered[(df_filtered['Variation'] == 'Control') & (df_filtered['process_step'] == 'start')]['client_id'].nunique()
        ctrl_confirm = df_filtered[(df_filtered['Variation'] == 'Control') & (df_filtered['process_step'] == 'confirm')]['client_id'].nunique()
        test_start = df_filtered[(df_filtered['Variation'] == 'Test') & (df_filtered['process_step'] == 'start')]['client_id'].nunique()
        test_confirm = df_filtered[(df_filtered['Variation'] == 'Test') & (df_filtered['process_step'] == 'confirm')]['client_id'].nunique()
        
        if ctrl_start > 0 and test_start > 0:
            p1 = test_confirm / test_start
            p2 = ctrl_confirm / ctrl_start
            p_pooled = (test_confirm + ctrl_confirm) / (test_start + ctrl_start)
            
            se = np.sqrt(p_pooled * (1 - p_pooled) * (1/test_start + 1/ctrl_start))
            z_stat = (p1 - p2) / se
            p_value = norm.sf(abs(z_stat)) * 2
            
            st.metric(label="Z-Statistic", value=f"{z_stat:.4f}")
            st.metric(label="P-Value", value=f"{p_value:.5e}")
            
            is_significant = p_value < 0.05
            if is_significant:
                st.success("✅ **Statistically Significant** (p < 0.05). The Test UI significantly increases conversion.")
            else:
                st.warning("⚠️ **Not Statistically Significant** (p >= 0.05). No statistical difference detected.")
        else:
            st.info("Select 'All' in experimental group filter to compare Control and Test statistically.")



# ---------------------------------------------------------
# 7. EXPORT FILTERED DATASET
# ---------------------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("📥 Export Data")
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Download Filtered CSV",
    data=csv_data,
    file_name="vanguard_filtered_data.csv",
    mime="text/csv"
)
