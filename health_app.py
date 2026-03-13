import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE SETUP
st.set_page_config(page_title="ChronicCare California", page_icon="🛡️", layout="wide")

# Styling for a clean, medical look
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #007AFF !important; font-weight: 700; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #efeff4; }
    .chronic-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #007AFF; }
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

    # SIDEBAR
    st.sidebar.title("🛡️ ChronicCare")
    patient_name = st.sidebar.selectbox("Patient Login", options=df_p['FIRST'] + " " + df_p['LAST'])
    p_id = df_p[(df_p['FIRST'] + " " + df_p['LAST']) == patient_name].iloc[0]['Id']
    
    user_p = df_p[df_p['Id'] == p_id].iloc[0]
    user_o = df_o[df_o['PATIENT'] == p_id].sort_values('DATE')
    
    # --- ONLY CHRONIC DISEASES FILTER ---
    # We filter out common things like 'Cold' or 'Checkup' to focus on Chronic conditions
    chronic_keywords = ['Diabetes', 'Hypertension', 'Asthma', 'Heart', 'Kidney', 'Arthritis', 'COPD', 'Hyperlipidemia']
    user_c = df_c[(df_c['PATIENT'] == p_id) & (df_c['DESCRIPTION'].str.contains('|'.join(chronic_keywords), case=False))]

    tab = st.sidebar.radio("Navigate", ["My Dashboard", "Risk Survey & Alerts", "Doctor's Visit Guide"])

    # ---------------------------------------------------------
    # TAB 1: DASHBOARD & REMINDERS
    # ---------------------------------------------------------
    if tab == "My Dashboard":
        st.title(f"Chronic Health Summary: {user_p['FIRST']}")
        
        # Daily Wellness Reminders
        st.subheader("☀️ Daily Wellness Reminders")
        r1, r2, r3 = st.columns(3)
        r1.info("💧 **Hydration:** Drink 2L of water today.")
        r2.info("🧘 **Activity:** 20 min light walking.")
        r3.info("💊 **Meds:** Check your morning dosage.")

        # Vitals
        st.subheader("Latest Clinical Vitals")
        m1, m2, m3 = st.columns(3)
        def get_val(d):
            res = user_o[user_o['DESCRIPTION'].str.contains(d, case=False)]
            return res.iloc[-1]['VALUE'] if not res.empty else None
        
        bp = get_val("Systolic")
        gl = get_val("Glucose")
        m1.metric("Blood Pressure", f"{int(float(bp))} mmHg" if bp else "N/A")
        m2.metric("Glucose", f"{int(float(gl))} mg/dL" if gl else "N/A")
        m3.metric("BMI", "24.5") # Example placeholder

        st.subheader("📋 Diagnosed Chronic Conditions")
        if not user_c.empty:
            for cond in user_c['DESCRIPTION'].unique():
                st.markdown(f"<div class='chronic-box'><b>Chronic:</b> {cond}</div><br>", unsafe_allow_html=True)
        else:
            st.write("No major chronic conditions on record.")

    # ---------------------------------------------------------
    # TAB 2: RISK SURVEY & ALERTS (Interactive Updates)
    # ---------------------------------------------------------
    elif tab == "Risk Survey & Alerts":
        st.title("Interactive Risk Assessment")
        st.write("Answer these questions to update your health profile.")
        
        q1 = st.radio("Are you experiencing any shortness of breath today?", ["No", "Yes"])
        q2 = st.radio("Have you noticed any unusual swelling in your feet?", ["No", "Yes"])
        
        if q1 == "Yes" or q2 == "Yes":
            st.error("🚨 **Immediate Alert:** Your symptoms suggest potential cardiovascular strain. Please contact your provider.")
        else:
            st.success("✅ No immediate symptomatic risks detected today.")

    # ---------------------------------------------------------
    # TAB 3: DOCTOR'S VISIT GUIDE
    # ---------------------------------------------------------
    elif tab == "Doctor's Visit Guide":
        st.title("🏥 Prepare for your Consultation")
        st.write("Based on your California health records, here is what you should ask your doctor:")
        
        st.markdown(f"""
        1. **Regarding Blood Pressure:** "My latest reading was {int(float(bp)) if bp else 'N/A'}. Is this on target for my age?"
        2. **Regarding Chronic Management:** "How can I adjust my lifestyle to better manage my diagnosed conditions?"
        3. **Medication Review:** "Are my current prescriptions still the most effective for my long-term heart health?"
        """)
        
        st.download_button("Download Report for Doctor", "Patient Health Summary: ...", file_name="Health_Summary.txt")

except Exception as e:
    st.error("Please ensure patients.csv, observations.csv, and conditions.csv are in your folder.")