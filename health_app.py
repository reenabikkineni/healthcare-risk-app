import streamlit as st
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="MyHealth Personal Dashboard", page_icon="👤", layout="wide")

# UI Styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #007AFF !important; font-weight: 700; }
    .stMetric { background-color: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(128, 128, 128, 0.2); }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    p = pd.read_csv('patients.csv')
    o = pd.read_csv('observations.csv')
    c = pd.read_csv('conditions.csv')
    e = pd.read_csv('encounters.csv')
    return p, o, c, e

try:
    df_p, df_o, df_c, df_e = load_data()

    # --- THE HARD CHRONIC FILTER (KEPT SAME) ---
    CHRONIC_LIST = ['Diabetes', 'Hypertension', 'Heart Failure', 'COPD', 'Asthma', 'Kidney Disease', 'Hyperlipidemia', 'Alzheimer', 'Arthritis', 'Prediabetes']
    has_chronic = df_c['DESCRIPTION'].str.contains('|'.join(CHRONIC_LIST), case=False, na=False)
    chronic_patient_ids = df_c[has_chronic]['PATIENT'].unique()
    df_p_chronic = df_p[df_p['Id'].isin(chronic_patient_ids)].copy()
    df_p_chronic['FULL_NAME'] = df_p_chronic['FIRST'] + " " + df_p_chronic['LAST']

    # --- SIDEBAR (Updated to "MyHealth") ---
    st.sidebar.title("👤 MyHealth Dashboard")
    patient_name = st.sidebar.selectbox("Welcome Back! Select Your Profile", options=df_p_chronic['FULL_NAME'].sort_values())
    
    # FILE UPLOAD SECTION (KEPT SAME)
    st.sidebar.divider()
    st.sidebar.subheader("📤 My Medical Records")
    uploaded_file = st.sidebar.file_uploader("Add Hospital Visit Summary", type=['pdf', 'png', 'jpg', 'jpeg'])
    
    doc_risk_alert = False
    if uploaded_file is not None:
        st.sidebar.success("Document added to your history!")
        doc_risk_alert = True 

    selected_row = df_p_chronic[df_p_chronic['FULL_NAME'] == patient_name].iloc[0]
    p_id = selected_row['Id']
    first_name = selected_row['FIRST']
    
    user_o = df_o[df_o['PATIENT'] == p_id].sort_values('DATE')
    user_e = df_e[df_e['PATIENT'] == p_id].sort_values('START')
    user_c = df_c[df_c['PATIENT'] == p_id]
    chronic_display = user_c[user_c['DESCRIPTION'].str.contains('|'.join(CHRONIC_LIST), case=False, na=False)]

    def get_latest_vital(desc):
        res = user_o[user_o['DESCRIPTION'].str.contains(desc, case=False, na=False)]
        return res.iloc[-1]['VALUE'] if not res.empty else "N/A"

    current_bp = get_latest_vital("Systolic")
    current_gl = get_latest_vital("Glucose")

    tab = st.sidebar.radio("My Navigation", ["Home", "My History", "Health Check", "Doctor Prep"])

    # ---------------------------------------------------------
    # TAB 1: HOME (PERSONALIZED)
    # ---------------------------------------------------------
    if tab == "Home":
        st.title(f"👋 Hello, {first_name}!")
        st.write("Here is your personal health overview for today.")
        
        if doc_risk_alert:
            st.warning(f"🔔 **Personal Update:** We noticed new information in your uploaded file: '{uploaded_file.name}'.")

        m1, m2, m3 = st.columns(3)
        m1.metric("Current Blood Pressure", f"{current_bp} mmHg")
        m2.metric("Latest Glucose Level", f"{current_gl} mg/dL")
        m3.metric("Conditions Tracked", len(chronic_display))

        st.divider()
        st.subheader("📋 My Tracked Conditions")
        for _, row in chronic_display.iterrows():
            st.success(f"**{row['DESCRIPTION']}**")

    # ---------------------------------------------------------
    # TAB 2: MY HISTORY
    # ---------------------------------------------------------
    elif tab == "My History":
        st.title("🏥 My Medical Visits")
        if not user_e.empty:
            total_cost = user_e['TOTAL_CLAIM_COST'].sum()
            st.metric("Total Healthcare Value received", f"${total_cost:,.2f}")
            st.table(user_e[['START', 'DESCRIPTION', 'TOTAL_CLAIM_COST']].tail(10))

    # ---------------------------------------------------------
    # TAB 3: HEALTH CHECK
    # ---------------------------------------------------------
    elif tab == "Health Check":
        st.title("🧘 How are you feeling today?")
        q1 = st.checkbox("Are you having any trouble breathing?")
        q2 = st.checkbox("Are you feeling more thirsty than usual?")
        if q1 or q2:
            st.error("🚨 **Alert:** Please contact your care team. These symptoms may need attention.")
        else:
            st.success("✅ Everything looks stable based on your symptoms.")

    # ---------------------------------------------------------
    # TAB 4: DOCTOR PREP
    # ---------------------------------------------------------
    elif tab == "Doctor Prep":
        st.title("🏥 My Visit Planner")
        st.write("Take these questions to your next appointment:")
        st.info(f"1. Based on my latest Blood Pressure ({current_bp}), should we change anything?")
        st.info(f"2. My glucose is {current_gl}. Is this a healthy trend for my profile?")
        if doc_risk_alert:
            st.info(f"3. Let's discuss the findings in my recent report: {uploaded_file.name}")

except Exception as e:
    st.error(f"Dashboard Error: {e}")