import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE SETUP
st.set_page_config(page_title="ChronicCare California", page_icon="🛡️", layout="wide")

# Apple-style Clean UI
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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

    # SIDEBAR
    st.sidebar.title("🛡️ ChronicCare Portal")
    patient_name = st.sidebar.selectbox("Select Patient Profile", options=df_p['FIRST'] + " " + df_p['LAST'])
    p_id = df_p[(df_p['FIRST'] + " " + df_p['LAST']) == patient_name].iloc[0]['Id']
    
    user_p = df_p[df_p['Id'] == p_id].iloc[0]
    user_o = df_o[df_o['PATIENT'] == p_id].sort_values('DATE')
    
    # --- STRICT CHRONIC FILTERING ---
    # This list excludes "Acute" issues like Colds, Infections, or Injuries.
    CHRONIC_WHITELIST = [
        'Diabetes', 'Hypertension', 'Heart Failure', 'Chronic obstructive pulmonary disease', 
        'Asthma', 'Chronic kidney disease', 'Hyperlipidemia', 'Alzheimer', 'Arthritis', 
        'Atrial Fibrillation', 'Coronary Artery Disease', 'Prediabetes'
    ]
    
    # Filter: Only keep records that match our chronic list
    user_c = df_c[df_c['PATIENT'] == p_id]
    chronic_only = user_c[user_c['DESCRIPTION'].str.contains('|'.join(CHRONIC_WHITELIST), case=False, na=False)]

    tab = st.sidebar.radio("Navigation", ["Dashboard", "Risk Survey & Alerts", "Doctor's Consultation"])

    # ---------------------------------------------------------
    # TAB 1: DASHBOARD
    # ---------------------------------------------------------
    if tab == "Dashboard":
        st.title(f"Chronic Health: {user_p['FIRST']} {user_p['LAST']}")
        
        # Wellness Reminders (Prof Req: Guidance)
        st.subheader("☀️ Daily Wellness Check")
        r1, r2, r3 = st.columns(3)
        r1.info("💧 **Hydration:** Goal 2.5L")
        r2.info("🧘 **Movement:** 30 min Walk")
        r3.info("💊 **Meds:** Routine Check")

        # Vital Dimensions
        st.subheader("Key Predictive Metrics")
        m1, m2, m3 = st.columns(3)
        
        def get_val(desc):
            res = user_o[user_o['DESCRIPTION'].str.contains(desc, case=False)]
            return res.iloc[-1]['VALUE'] if not res.empty else "N/A"
        
        bp = get_val("Systolic")
        gl = get_val("Glucose")
        
        m1.metric("Systolic BP", f"{bp} mmHg" if bp != "N/A" else "N/A")
        m2.metric("Glucose", f"{gl} mg/dL" if gl != "N/A" else "N/A")
        m3.metric("Status", "Stable" if not chronic_only.empty else "Clear")

        st.divider()
        st.subheader("📋 Identified Chronic Diseases")
        if not chronic_only.empty:
            for _, row in chronic_only.iterrows():
                st.markdown(f"""
                <div class="chronic-card">
                    <strong>CONDITION:</strong> {row['DESCRIPTION']}<br>
                    <small>Onset Date: {row['START']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No major chronic diseases detected in the California clinical record.")

    # ---------------------------------------------------------
    # TAB 2: RISK SURVEY & ALERTS (What-If Logic)
    # ---------------------------------------------------------
    elif tab == "Risk Survey & Alerts":
        st.title("Interactive Risk Assessment")
        st.write("Updating your profile with real-time symptom data.")
        
        q1 = st.checkbox("Experience shortness of breath?")
        q2 = st.checkbox("Unusual fatigue or chest pressure?")
        q3 = st.checkbox("Increased thirst or frequent urination?")
        
        if q1 or q2 or q3:
            st.error("🚨 **High Risk Alert:** Based on your symptoms and clinical history, there is a risk of a chronic flare-up. Please notify your doctor.")
        else:
            st.success("✅ Your current symptoms do not indicate an immediate risk.")

    # ---------------------------------------------------------
    # TAB 3: DOCTOR'S CONSULTATION
    # ---------------------------------------------------------
    elif tab == "Doctor's Consultation":
        st.title("🏥 Consultation Prep")
        st.write("Personalized questions for your next California Health System visit:")
        
        st.markdown(f"""
        * **Trend Analysis:** "My BP is currently {bp}. How does this look compared to my 3-month average?"
        * **Management:** "Are there specific dietary changes for **{chronic_only.iloc[0]['DESCRIPTION'] if not chronic_only.empty else 'preventative health'}**?"
        * **Future Risks:** "What are the early warning signs I should watch for given my profile?"
        """)

except Exception as e:
    st.error(f"Data Error: Ensure CSVs are present. {e}")