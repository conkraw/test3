import streamlit as st
from utils.file_operations import read_text_file, load_vital_signs
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase, initialize_firebase

def load_user_data(db):
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    if st.session_state.user_code:
        user_data = db.collection(collection_name).document(st.session_state.user_code).get()
        if user_data.exists:
            return user_data.to_dict()
    return {}

def display_intake_form(db, document_id):
    st.markdown(f"<h3 style='font-family: \"DejaVu Sans\";'>Welcome {st.session_state.user_name}! Here is the intake form.</h3>", unsafe_allow_html=True)

    # Read and display the text from ptinfo.txt
    txt_file_path = "ptinfo.txt"
    document_text = read_text_file(txt_file_path)

    if document_text:
        st.markdown(f"<h2>Patient Information:</h2>{document_text}", unsafe_allow_html=True)
    else:
        st.write("No text found in the document.")

    # Load vital signs
    vital_signs_file = "vital_signs.txt"
    vital_signs = load_vital_signs(vital_signs_file)

    # Load user data
    user_data = load_user_data(db)
    vs_data = user_data.get('vs_data', {}) if user_data else {}

    # Check if vital_signs is not empty before creating checkboxes
    if vital_signs:
        st.markdown("<h2>Vital Signs:</h2>", unsafe_allow_html=True)

        # Checkboxes for vital signs
        heart_rate_checkbox = st.checkbox(f"HEART RATE: {vital_signs.get('heart_rate', 'N/A')}", key='heart_rate_checkbox', value=vs_data.get('heart_rate', False))
        respiratory_rate_checkbox = st.checkbox(f"RESPIRATORY RATE: {vital_signs.get('respiratory_rate', 'N/A')}", key='respiratory_rate_checkbox', value=vs_data.get('respiratory_rate', False))
        blood_pressure_checkbox = st.checkbox(f"BLOOD PRESSURE: {vital_signs.get('blood_pressure', 'N/A')}", key='blood_pressure_checkbox', value=vs_data.get('blood_pressure', False))
        pulseox_checkbox = st.checkbox(f"PULSE OXIMETRY: {vital_signs.get('pulseox', 'N/A')}", key='pulseox_checkbox', value=vs_data.get('pulseox', False))
        temperature_checkbox = st.checkbox(f"TEMPERATURE: {vital_signs.get('temperature', 'N/A')}", key='temperature_checkbox', value=vs_data.get('temperature', False))
        weight_checkbox = st.checkbox(f"WEIGHT: {vital_signs.get('weight', 'N/A')}", key='weight_checkbox', value=vs_data.get('weight', False))

        # Button to proceed to the diagnoses page
        if st.button("Next", key="intake_next_button"):
            st.session_state.vs_data = { 
                'unique_code': st.session_state.unique_code,
                'heart_rate': heart_rate_checkbox,
                'respiratory_rate': respiratory_rate_checkbox,
                'blood_pressure': blood_pressure_checkbox,
                'pulseox': pulseox_checkbox,
                'temperature': temperature_checkbox,
                'weight': weight_checkbox,
            }

            entry = {'vs_data': st.session_state.vs_data}

            # Upload to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.session_state.intake_submitted = True
            st.session_state.page = "diagnoses"  # Move to Diagnoses page
            
            st.rerun()  # Rerun the app to refresh the page
    else:
        st.error("No vital signs data available.")

def main():
    # Initialize Firebase
    db = initialize_firebase()

    # Session state initialization
    if "user_code" not in st.session_state:
        st.session_state.user_code = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Guest"
    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    # Load last page or proceed
    if st.session_state.user_code:
        user_data = load_user_data(db)
        if user_data:
            st.session_state.user_name = user_data.get("user_name", "Guest")
            st.session_state.vs_data = user_data.get("vs_data", {})

    # Page routing based on session state
    if st.session_state.page == "intake_form":
        display_intake_form(db, st.session_state.document_id)

if __name__ == "__main__":
    main()

