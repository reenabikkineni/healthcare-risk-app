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
    e = pd.read_csv('encounters.csv')
    return p, o, c, e

try:
    df_p, df_o, df_c, df_e = load_data()

    # --- THE HARD CHRONIC FILTER ---
    # We only care about these specific chronic conditions
    CHRONIC_LIST = [
        'Diabetes', 'Hypertension', 'Heart Failure', 'COPD', 'Asthma', 
        'Kidney Disease', 'Hyperlipidemia', 'Alzheimer', 'Arthritis', 'Prediabetes'
    ]
    
    # 1. Find the IDs of patients who have at least one of these diseases
    has_chronic = df_c['DESCRIPTION'].str.contains('|'.join(CHRONIC_LIST), case=False, na=False)
    chronic_patient_ids = df_c[has_chronic]['PATIENT'].unique()
    
    # 2. Filter the patient list to ONLY include those people
    # This removes all "healthy" or "acute-only" patients from the app entirely
    df_p_chronic = df_p[df_p['Id'].isin(chronic_patient_ids)].copy()
    df_p_chronic['FULL_NAME'] = df_p_chronic['FIRST'] + " " + df_p_chronic['LAST']

    # --- SIDEBAR ---
    st.sidebar.title("🛡️ ChronicCare Portal")
    
    # The dropdown will now ONLY show the chronic patients
    patient_name = st.sidebar.selectbox(
        f"Select Patient ({len(df_p_chronic)} Chronic Profiles Found)", 
        options=df_p_chronic['FULL_NAME'].sort_values()
    )
    
    # Get Data for the selected person
    selected_row = df_p_chronic[df_p_chronic['FULL_NAME'] == patient_name].iloc[0]
    p_id = selected_row['Id']
    
    user_o = df_o[df_o['PATIENT'] == p_id].sort_values('DATE')
    user_e = df_e[df_e['PATIENT'] == p_id].sort_values('START')
    user_c = df_c[df_c['PATIENT'] == p_id]
    
    # Filter the specific chronic records for display
    chronic_display = user_c[user_c['DESCRIPTION'].str.contains('|'.join(CHRONIC_LIST), case=False, na=False)]

    # --- VITALS ---
    def get_latest_vital(desc):
        res = user_o[user_o['DESCRIPTION'].str.contains(desc, case=False, na=False)]
        return res.iloc[-1]['VALUE'] if not res.empty else "N/A"

    current_bp = get_latest_vital("Systolic")
    current_gl = get_latest_vital("Glucose")

    tab = st.sidebar.radio("Navigation", ["Dashboard", "Encounter History", "Risk Survey", "Consultation Prep"])

    # ---------------------------------------------------------
    # TAB 1: DASHBOARD
    # ---------------------------------------------------------
    if tab == "Dashboard":
        st.title(f"Chronic Health Summary: {patient_name}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Latest Systolic BP", f"{current_bp} mmHg")
        m2.metric("Latest Glucose", f"{current_gl} mg/dL")
        m3.metric("Chronic Diagnoses", len(chronic_display))

        st.divider()
        st.subheader("📋 Active Chronic Conditions")
        for _, row in chronic_display.iterrows():
            st.success(f"**{row['DESCRIPTION']}** (Onset: {row['START']})")

    # ---------------------------------------------------------
    # TAB 2: ENCOUNTER HISTORY
    # ---------------------------------------------------------
    elif tab == "Encounter History":
        st.title("🏥 Clinical Visits & Claims")
        if not user_e.empty:
            total_cost = user_e['TOTAL_CLAIM_COST'].sum()
            st.metric("Total Medical Spend", f"${total_cost:,.2f}")
            st.table(user_e[['START', 'DESCRIPTION', 'TOTAL_CLAIM_COST']].tail(10))
        else:
            st.write("No encounter history available.")

    # ---------------------------------------------------------
    # TAB 3: RISK SURVEY (What-if logic)
    # ---------------------------------------------------------
    elif tab == "Risk Survey":
        st.title("Symptom-Based Risk Alert")
        q1 = st.checkbox("Shortness of breath or persistent cough?")
        q2 = st.checkbox("Severe thirst or frequent urination?")
        
        if q1 or q2:
            st.error("🚨 **Alert:** Symptom profile indicates potential chronic flare-up.")
        else:
            st.success("✅ Symptoms appear stable for current chronic profile.")

    # ---------------------------------------------------------
    # TAB 4: CONSULTATION PREP
    # ---------------------------------------------------------
    elif tab == "Consultation Prep":
        st.title("🏥 Doctor's Visit Prep")
        st.write("Suggested questions for your healthcare provider:")
        st.info(f"1. How does my {current_bp} BP affect my {chronic_display.iloc[0]['DESCRIPTION'] if not chronic_display.empty else 'health'}?")
        st.info("2. Are there any local environmental factors in California I should avoid?")
        st.info("3. Is my medication dosage still appropriate for these glucose levels?")

except Exception as e:
    st.error(f"Filter Error: {e}")