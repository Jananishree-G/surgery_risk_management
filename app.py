import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(page_title="Surgery Risk Management System", page_icon="🏥", layout="wide")

# Initialize session state
if 'patients' not in st.session_state:
    st.session_state.patients = []

class SurgeryRiskCalculator:
    @staticmethod
    def calculate_risk_score(age, bmi, comorbidities, surgery_type, asa_class):
        """Calculate surgery risk score based on multiple factors"""
        score = 0
        
        # Age factor
        if age < 18: score += 1
        elif age < 40: score += 2
        elif age < 65: score += 4
        else: score += 7
        
        # BMI factor
        if bmi < 18.5: score += 3
        elif bmi > 30: score += 4
        elif bmi > 35: score += 6
        
        # Comorbidities
        score += len(comorbidities) * 2
        
        # Surgery type
        surgery_scores = {
            "Minor": 1, "Moderate": 3, "Major": 6, "Complex": 9
        }
        score += surgery_scores.get(surgery_type, 3)
        
        # ASA class
        score += asa_class * 2
        
        return min(score, 30)  # Cap at 30
    
    @staticmethod
    def get_risk_category(score):
        if score <= 8: return "Low", "🟢"
        elif score <= 15: return "Moderate", "🟡"
        elif score <= 22: return "High", "🟠"
        else: return "Critical", "🔴"

def main():
    st.title("🏥 Surgery Risk Management System")
    st.markdown("### Comprehensive Patient Risk Assessment & Management")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", 
                               ["Patient Registration", "Risk Assessment", "Dashboard", "Patient Records"])
    
    if page == "Patient Registration":
        patient_registration()
    elif page == "Risk Assessment":
        risk_assessment()
    elif page == "Dashboard":
        dashboard()
    elif page == "Patient Records":
        patient_records()

def patient_registration():
    st.header("👤 Patient Registration")
    
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*")
            age = st.number_input("Age*", min_value=1, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
            weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70)
        
        with col2:
            surgery_date = st.date_input("Surgery Date", min_value=date.today())
            surgery_type = st.selectbox("Surgery Type", 
                                      ["Minor", "Moderate", "Major", "Complex"])
            surgeon = st.text_input("Surgeon Name")
            asa_class = st.selectbox("ASA Physical Status", [1, 2, 3, 4, 5])
            emergency = st.checkbox("Emergency Surgery")
        
        # Medical History
        st.subheader("Medical History")
        comorbidities = st.multiselect("Comorbidities", 
                                     ["Diabetes", "Hypertension", "Heart Disease", 
                                      "Kidney Disease", "Lung Disease", "Cancer", 
                                      "Blood Disorders", "Liver Disease"])
        
        allergies = st.text_area("Allergies")
        medications = st.text_area("Current Medications")
        notes = st.text_area("Additional Notes")
        
        submitted = st.form_submit_button("Register Patient")
        
        if submitted and name:
            bmi = weight / ((height/100) ** 2)
            patient_id = len(st.session_state.patients) + 1
            
            patient = {
                'id': patient_id,
                'name': name,
                'age': age,
                'gender': gender,
                'height': height,
                'weight': weight,
                'bmi': round(bmi, 2),
                'surgery_date': surgery_date,
                'surgery_type': surgery_type,
                'surgeon': surgeon,
                'asa_class': asa_class,
                'emergency': emergency,
                'comorbidities': comorbidities,
                'allergies': allergies,
                'medications': medications,
                'notes': notes,
                'registration_date': datetime.now()
            }
            
            st.session_state.patients.append(patient)
            st.success(f"✅ Patient {name} registered successfully! (ID: {patient_id})")

def risk_assessment():
    st.header("⚕️ Surgery Risk Assessment")
    
    if not st.session_state.patients:
        st.warning("No patients registered. Please register a patient first.")
        return
    
    # Select patient
    patient_names = [f"{p['name']} (ID: {p['id']})" for p in st.session_state.patients]
    selected = st.selectbox("Select Patient", patient_names)
    
    if selected:
        patient_id = int(selected.split("ID: ")[1].split(")")[0])
        patient = next(p for p in st.session_state.patients if p['id'] == patient_id)
        
        st.subheader(f"Risk Assessment for {patient['name']}")
        
        # Calculate risk score
        risk_score = SurgeryRiskCalculator.calculate_risk_score(
            patient['age'], patient['bmi'], patient['comorbidities'],
            patient['surgery_type'], patient['asa_class']
        )
        
        risk_category, risk_emoji = SurgeryRiskCalculator.get_risk_category(risk_score)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Risk Score", f"{risk_score}/30")
        with col2:
            st.metric("Risk Category", f"{risk_emoji} {risk_category}")
        with col3:
            mortality_risk = min(risk_score * 0.5, 15)
            st.metric("Estimated Mortality Risk", f"{mortality_risk:.1f}%")
        
        # Risk breakdown
        st.subheader("Risk Factor Analysis")
        
        factors = {
            'Age Factor': min(patient['age'] // 10, 7),
            'BMI Factor': 4 if patient['bmi'] > 30 else (3 if patient['bmi'] < 18.5 else 1),
            'Comorbidities': len(patient['comorbidities']) * 2,
            'Surgery Complexity': {'Minor': 1, 'Moderate': 3, 'Major': 6, 'Complex': 9}[patient['surgery_type']],
            'ASA Class': patient['asa_class'] * 2
        }
        
        fig = px.bar(x=list(factors.keys()), y=list(factors.values()),
                     title="Risk Score Breakdown", color=list(factors.values()),
                     color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("Recommendations")
        recommendations = []
        
        if risk_category == "Critical":
            recommendations.extend([
                "🚨 Consider postponing non-emergency surgery",
                "🏥 ICU bed should be reserved post-operatively",
                "👨‍⚕️ Senior surgeon consultation required"
            ])
        elif risk_category == "High":
            recommendations.extend([
                "⚠️ Enhanced monitoring required",
                "🩺 Pre-operative optimization needed",
                "🏥 Post-op HDU/ICU monitoring considered"
            ])
        elif risk_category == "Moderate":
            recommendations.extend([
                "📋 Standard pre-operative assessment",
                "👀 Regular post-operative monitoring",
                "💊 Optimize medications pre-operatively"
            ])
        else:
            recommendations.append("✅ Standard care protocol applicable")
        
        for rec in recommendations:
            st.write(rec)

def dashboard():
    st.header("📊 Surgery Risk Dashboard")
    
    if not st.session_state.patients:
        st.warning("No patient data available.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.patients)
    
    # Calculate risk scores for all patients
    df['risk_score'] = df.apply(lambda row: SurgeryRiskCalculator.calculate_risk_score(
        row['age'], row['bmi'], row['comorbidities'], 
        row['surgery_type'], row['asa_class']), axis=1)
    
    df['risk_category'] = df['risk_score'].apply(
        lambda x: SurgeryRiskCalculator.get_risk_category(x)[0])
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", len(df))
    with col2:
        high_risk = len(df[df['risk_category'].isin(['High', 'Critical'])])
        st.metric("High Risk Patients", high_risk)
    with col3:
        avg_age = df['age'].mean()
        st.metric("Average Age", f"{avg_age:.1f}")
    with col4:
        emergency_count = df['emergency'].sum()
        st.metric("Emergency Cases", emergency_count)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk distribution
        risk_counts = df['risk_category'].value_counts()
        fig1 = px.pie(values=risk_counts.values, names=risk_counts.index,
                      title="Risk Category Distribution")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Surgery type vs risk
        fig2 = px.box(df, x='surgery_type', y='risk_score',
                      title="Risk Score by Surgery Type")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Age vs Risk scatter
    fig3 = px.scatter(df, x='age', y='risk_score', color='risk_category',
                      size='bmi', hover_data=['name', 'surgery_type'],
                      title="Age vs Risk Score")
    st.plotly_chart(fig3, use_container_width=True)

def patient_records():
    st.header("📋 Patient Records")
    
    if not st.session_state.patients:
        st.warning("No patient records available.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(st.session_state.patients)
    
    # Add risk scores
    df['risk_score'] = df.apply(lambda row: SurgeryRiskCalculator.calculate_risk_score(
        row['age'], row['bmi'], row['comorbidities'], 
        row['surgery_type'], row['asa_class']), axis=1)
    
    df['risk_category'] = df['risk_score'].apply(
        lambda x: SurgeryRiskCalculator.get_risk_category(x)[0])
    
    # Display options
    st.subheader("Filter Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_filter = st.multiselect("Filter by Risk", 
                                   df['risk_category'].unique(),
                                   default=df['risk_category'].unique())
    with col2:
        surgery_filter = st.multiselect("Filter by Surgery Type",
                                      df['surgery_type'].unique(),
                                      default=df['surgery_type'].unique())
    with col3:
        sort_by = st.selectbox("Sort by", ['name', 'age', 'risk_score', 'surgery_date'])
    
    # Filter data
    filtered_df = df[
        (df['risk_category'].isin(risk_filter)) &
        (df['surgery_type'].isin(surgery_filter))
    ].sort_values(sort_by)
    
    # Display table
    display_columns = ['id', 'name', 'age', 'gender', 'surgery_type', 'surgery_date', 
                      'asa_class', 'risk_score', 'risk_category']
    
    st.dataframe(filtered_df[display_columns], use_container_width=True)
    
    # Patient details
    if st.checkbox("Show Detailed View"):
        selected_id = st.selectbox("Select Patient for Details", 
                                 filtered_df['id'].tolist())
        
        if selected_id:
            patient = filtered_df[filtered_df['id'] == selected_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Basic Information")
                st.write(f"**Name:** {patient['name']}")
                st.write(f"**Age:** {patient['age']}")
                st.write(f"**Gender:** {patient['gender']}")
                st.write(f"**BMI:** {patient['bmi']}")
                st.write(f"**Surgery Date:** {patient['surgery_date']}")
                st.write(f"**Surgeon:** {patient['surgeon']}")
            
            with col2:
                st.subheader("Risk Assessment")
                st.write(f"**Risk Score:** {patient['risk_score']}/30")
                st.write(f"**Risk Category:** {patient['risk_category']}")
                st.write(f"**ASA Class:** {patient['asa_class']}")
                st.write(f"**Comorbidities:** {', '.join(patient['comorbidities']) if patient['comorbidities'] else 'None'}")
                
            if patient['notes']:
                st.subheader("Additional Notes")
                st.write(patient['notes'])

if __name__ == "__main__":
    main()