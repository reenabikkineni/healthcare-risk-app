import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE SETUP
st.set_page_config(page_title="ChronicCare California", page_icon="🛡️", layout="wide")

# Apple-style UI Styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #007AFF !important; font-weight: 700; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #efeff4; }
    .chronic-card { 
        background-color: #f8f9fa; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 8px solid #007AFF; 
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    p = pd.read_csv('patients.csv')
    o = pd.read_csv('observations.csv')
    c = pd.read_csv('conditions.csv')
    return p, o, c

try:
    df_p, df_o, df_c = load_data()

    # --- SIDEBAR & PATIENT SELECTION ---
    st.sidebar.title("🛡️ ChronicCare Portal")
    patient_name = st.sidebar.selectbox("Select Patient Profile", options=df_p['FIRST'] + " " + df_p['LAST'])
    p_id = df_p[(df_p['FIRST'] + " " + df_p['LAST']) == patient_name].iloc[0]['Id']
    
    user_p = df_p[df_p['Id'] == p_id].iloc[0]
    user_o = df_o[df_o['PATIENT'] == p_id].sort_values('DATE')

    # --- DEFINE GLOBAL VITALS (Fixed the 'bp' error) ---
    def get_latest_vital(desc):
        res = user_o[user_o['DESCRIPTION'].str.contains(desc, case=False, na=False)]
        return res.iloc[-1]['VALUE'] if not res.empty else "N/A"

    current_bp = get_latest_vital("Systolic")
    current_gl = get_latest_vital("Glucose")

    # --- STRICT CHRONIC FILTER ---
    CHRONIC_LIST = ['Diabetes', 'Hypertension', 'Heart Failure', 'COPD', 'Asthma', 'Kidney Disease', 'Hyperlipidemia', 'Alzheimer', 'Arthritis']
    user_c = df_c[df_c['PATIENT'] == p_id]
    chronic_only = user_c[user_c['DESCRIPTION'].str.contains('|'.join(CHRONIC_LIST), case=False, na=False)]

    tab = st.sidebar.radio("Navigation", ["Dashboard", "Risk Survey & Alerts", "Doctor's Consultation"])

    # ---------------------------------------------------------
    # TAB 1: DASHBOARD
    # ---------------------------------------------------------
    if tab == "Dashboard":
        st.title(f"Chronic Health: {user_p['FIRST']} {user_p['LAST']}")
        
        st.subheader("☀️ Daily Wellness Check")
        r1, r2, r3 = st.columns(3)
        r1.info("💧 **Hydration:** Goal 2.5L")
        r2.info("🧘 **Movement:** 30 min Walk")
        r3.info("💊 **Meds:** Routine Check")

        st.subheader("Key Predictive Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Systolic BP", f"{current_bp} mmHg")
        m2.metric("Glucose", f"{current_gl} mg/dL")
        m3.metric("Status", "Stable" if not chronic_only.empty else "No Chronic Issues")

        st.divider()
        st.subheader("📋 Identified Chronic Diseases")
        if not chronic_only.empty:
            for _, row in chronic_only.iterrows():
                st.markdown(f'<div class="chronic-card"><b>{row["DESCRIPTION"]}</b><br><small>Onset: {row["START"]}</small></div>', unsafe_allow_html=True)
        else:
            st.info("No chronic conditions found for this patient.")

    # ---------------------------------------------------------
    # TAB 2: RISK SURVEY (What-If)
    # ---------------------------------------------------------
    elif tab == "Risk Survey & Alerts":
        st.title("Interactive Risk Assessment")
        q1 = st.checkbox("Experience shortness of breath?")
        q2 = st.checkbox("Increased thirst or frequent urination?")
        
        if q1 or q2:
            st.error("🚨 **High Risk Alert:** Symptoms suggest potential chronic flare-up.")
        else:
            st.success("✅ No immediate symptomatic risks.")

    # ---------------------------------------------------------
    # TAB 3: DOCTOR'S CONSULTATION (No longer has the error!)
    # ---------------------------------------------------------
    elif tab == "Doctor's Consultation":
        st.title("🏥 Consultation Prep")
        st.write(f"Personalized questions based on your latest vitals ({current_bp} BP / {current_gl} Glucose):")
        
        st.markdown(f"""
        1. **Vitals:** "My Systolic BP is currently **{current_bp}**. Is this within the safe range for my age group?"
        2. **Condition Management:** "What lifestyle changes can I make to prevent complications from **{chronic_only.iloc[0]['DESCRIPTION'] if not chronic_only.empty else 'future chronic risks'}**?"
        3. **Medication:** "Are these readings consistent with the medications I am currently prescribed?"
        """)

except Exception as e:
    st.error(f"App Error: {e}")