import streamlit as st
from utils.file_operations import read_text_file, load_vital_signs
from utils.firebase_operations import upload_to_firebase

def display_intake_form(db, document_id):
    st.markdown(f"<h3 style='font-family: \"DejaVu Sans\";'>Welcome {st.session_state.user_name}! Here is the intake form.</h3>", unsafe_allow_html=True)

    # Read and display the text from ptinfo.txt
    txt_file_path = "ptinfo.txt"
    document_text = read_text_file(txt_file_path)

    if document_text:
        st.markdown("<h2 style='font-family: \"DejaVu Sans\"; font-size: 24px; color: #2c3e50;'>Patient Information:</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-family: \"DejaVu Sans\"; font-size: 18px; color: #34495e;'>{document_text.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
    else:
        st.write("No text found in the document.")

    # Load vital signs from Firebase
    #if "vs_data" not in st.session_state:
    #    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    #    user_data = db.collection(collection_name).document(document_id).get()
    #    if user_data.exists:
    #        st.session_state.vs_data = user_data.to_dict().get('vs_data', {
    #            'heart_rate': False,
    #            'respiratory_rate': False,
    #            'blood_pressure': False,
    #            'pulseox': False,
    #            'temperature': False,
    #            'weight': False,
    #        })
    #    else:
    #        st.session_state.vs_data = {
    #            'heart_rate': False,
    #            'respiratory_rate': False,
    #            'blood_pressure': False,
    #            'pulseox': False,
    #            'temperature': False,
    #            'weight': False,
    #        }

    # Load original vital signs values for display
    vital_signs = load_vital_signs("vital_signs.txt")

    if st.session_state.vs_data:
        st.markdown("<h2 style='font-family: \"DejaVu Sans\"; font-size: 24px; color: #2c3e50;'>Vital Signs:</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-family: \"DejaVu Sans\"; font-size: 18px;'>Check the vital signs that are abnormal:</h4>", unsafe_allow_html=True)

        # Display vital signs checkboxes
        col1, col2 = st.columns([1, 2])

        with col2:
            heart_rate_checkbox = st.checkbox(f"HEART RATE: {vital_signs.get('heart_rate', 'N/A')}", value=st.session_state.vs_data['heart_rate'], key='heart_rate_checkbox')
            respiratory_rate_checkbox = st.checkbox(f"RESPIRATORY RATE: {vital_signs.get('respiratory_rate', 'N/A')}", value=st.session_state.vs_data['respiratory_rate'], key='respiratory_rate_checkbox')
            blood_pressure_checkbox = st.checkbox(f"BLOOD PRESSURE: {vital_signs.get('blood_pressure', 'N/A')}", value=st.session_state.vs_data['blood_pressure'], key='blood_pressure_checkbox')
            pulseox_checkbox = st.checkbox(f"PULSE OXIMETRY: {vital_signs.get('pulseox', 'N/A')}", value=st.session_state.vs_data['pulseox'], key='pulseox_checkbox')
            temperature_checkbox = st.checkbox(f"TEMPERATURE: {vital_signs.get('temperature', 'N/A')}", value=st.session_state.vs_data['temperature'], key='temperature_checkbox')
            weight_checkbox = st.checkbox(f"WEIGHT: {vital_signs.get('weight', 'N/A')}", value=st.session_state.vs_data['weight'], key='weight_checkbox')

        # Button to proceed to the diagnoses page
        if st.button("Next", key="intake_next_button"):
            entry = {
                'vs_data': {
                    'heart_rate': heart_rate_checkbox,
                    'respiratory_rate': respiratory_rate_checkbox,
                    'blood_pressure': blood_pressure_checkbox,
                    'pulseox': pulseox_checkbox,
                    'temperature': temperature_checkbox,
                    'weight': weight_checkbox,
                },
                'last_page': 'intake_form'
            }
            
            # Print session state before upload for debugging
            st.write("Session state before upload:", st.session_state)

            # Attempt to upload data to Firebase
            try:
                upload_to_firebase(db, document_id, entry)
                st.success("Data uploaded successfully!")
            except Exception as e:
                st.error(f"Error uploading data: {e}")

            # Set the session state for the next page
            st.session_state.page = "diagnoses"
            st.write(f"Current page set to: {st.session_state.page}")
            #st.rerun()  # Ensure the app refreshes to show the new page
    else:
        st.error("No vital signs data available.")
