import streamlit as st
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="ChronicCare California", page_icon="🛡️", layout="wide")

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
    e = pd.read_csv('encounters.csv') # Loading Encounters
    return p, o, c, e

try:
    df_p, df_o, df_c, df_e = load_data()

    # --- SIDEBAR & PATIENT SELECTION ---
    st.sidebar.title("🛡️ ChronicCare Portal")
    patient_name = st.sidebar.selectbox("Select Patient Profile", options=df_p['FIRST'] + " " + df_p['LAST'])
    p_id = df_p[(df_p['FIRST'] + " " + df_p['LAST']) == patient_name].iloc[0]['Id']
    
    user_p = df_p[df_p['Id'] == p_id].iloc[0]
    user_o = df_o[df_o['PATIENT'] == p_id].sort_values('DATE')
    user_e = df_e[df_e['PATIENT'] == p_id].sort_values('START')

    # --- VITALS LOGIC ---
    def get_latest_vital(desc):
        res = user_o[user_o['DESCRIPTION'].str.contains(desc, case=False, na=False)]
        return res.iloc[-1]['VALUE'] if not res.empty else "N/A"

    current_bp = get_latest_vital("Systolic")
    current_gl = get_latest_vital("Glucose")

    # --- STRICT CHRONIC FILTER ---
    CHRONIC_LIST = ['Diabetes', 'Hypertension', 'Heart Failure', 'COPD', 'Asthma', 'Kidney Disease', 'Hyperlipidemia', 'Alzheimer', 'Arthritis']
    user_c = df_c[df_c['PATIENT'] == p_id]
    chronic_only = user_c[user_c['DESCRIPTION'].str.contains('|'.join(CHRONIC_LIST), case=False, na=False)]

    tab = st.sidebar.radio("Navigation", ["Dashboard", "Encounter History", "Risk Survey", "Consultation Prep"])

    # ---------------------------------------------------------
    # TAB 1: DASHBOARD
    # ---------------------------------------------------------
    if tab == "Dashboard":
        st.title(f"Chronic Health Summary: {user_p['FIRST']} {user_p['LAST']}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Latest Systolic BP", f"{current_bp} mmHg")
        m2.metric("Latest Glucose", f"{current_gl} mg/dL")
        m3.metric("Chronic Conditions", len(chronic_only))

        st.divider()
        st.subheader("📋 Active Chronic Diagnoses")
        if not chronic_only.empty:
            for _, row in chronic_only.iterrows():
                st.success(f"**{row['DESCRIPTION']}** (Started: {row['START']})")
        else:
            st.info("No chronic conditions detected.")

    # ---------------------------------------------------------
    # TAB 2: ENCOUNTER HISTORY (Using encounters.csv)
    # ---------------------------------------------------------
    elif tab == "Encounter History":
        st.title("🏥 Clinical Encounters & Costs")
        st.write("Reviewing visits across California healthcare facilities.")
        
        if not user_e.empty:
            # Dimensions: Provider/Facility, Cost, and Reason
            total_cost = user_e['TOTAL_CLAIM_COST'].sum()
            st.metric("Total Healthcare Expenditure", f"${total_cost:,.2f}")
            
            # Simplified Table for User
            display_e = user_e[['START', 'ENCOUNTERCLASS', 'DESCRIPTION', 'TOTAL_CLAIM_COST']].copy()
            display_e.columns = ['Date', 'Type', 'Reason for Visit', 'Cost ($)']
            st.table(display_e.tail(10)) # Show last 10 visits
        else:
            st.warning("No encounter history found for this patient.")

    # ---------------------------------------------------------
    # TAB 3: RISK SURVEY
    # ---------------------------------------------------------
    elif tab == "Risk Survey":
        st.title("Interactive Risk Assessment")
        q1 = st.checkbox("Any chest pain or difficulty breathing?")
        q2 = st.checkbox("Sudden changes in vision or extreme thirst?")
        
        if q1 or q2:
            st.error("🚨 **High Risk Alert:** Based on your chronic profile, these symptoms require immediate clinical attention.")
        else:
            st.success("✅ No immediate symptomatic risks detected.")

    # ---------------------------------------------------------
    # TAB 4: CONSULTATION PREP
    # ---------------------------------------------------------
    elif tab == "Consultation Prep":
        st.title("🏥 Preparation for Doctor")
        st.markdown(f"""
        **Based on your history in {user_p['CITY']}:**
        1. "I have had {len(user_e)} clinical encounters. Are my chronic conditions stabilizing?"
        2. "My latest BP is {current_bp}. Should we adjust my management plan?"
        3. "Which specific triggers in my local area should I avoid for my respiratory health?"
        """)

except Exception as e:
    st.error(f"Error loading healthcare dimensions: {e}")