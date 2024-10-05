import streamlit as st
from utils.file_operations import read_text_file, load_vital_signs
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase

def display_intake_form(db, document_id):
    st.markdown(f"<h3 style='font-family: \"DejaVu Sans\";'>Welcome {st.session_state.user_name}! Here is the intake form.</h3>", unsafe_allow_html=True)

    # Read and display the text from ptinfo.txt
    txt_file_path = "ptinfo.txt"
    document_text = read_text_file(txt_file_path)

    if document_text:
        title_html = """
        <h2 style="font-family: 'DejaVu Sans'; font-size: 24px; margin-bottom: 10px; color: #2c3e50;">
            Patient Information:
        </h2>
        """
        st.markdown(title_html, unsafe_allow_html=True)

        custom_html = f"""
        <div style="font-family: 'DejaVu Sans'; font-size: 18px; line-height: 1.5; color: #34495e; background-color: #ecf0f1; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            {document_text.replace('\n', '<br>')}
        </div>
        """
        st.markdown(custom_html, unsafe_allow_html=True)
    else:
        st.write("No text found in the document.")

    # Load vital signs from Firebase
    if "vs_data" not in st.session_state:
        collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
        user_data = db.collection(collection_name).document(document_id).get()
        if user_data.exists:
            st.session_state.vs_data = user_data.to_dict().get('vs_data', {
                'heart_rate': False,
                'respiratory_rate': False,
                'blood_pressure': False,
                'pulseox': False,
                'temperature': False,
                'weight': False,
            })
        else:
            st.session_state.vs_data = {
                'heart_rate': False,
                'respiratory_rate': False,
                'blood_pressure': False,
                'pulseox': False,
                'temperature': False,
                'weight': False,
            }

    # Load original vital signs values for display
    vital_signs = load_vital_signs("vital_signs.txt")

    # Display the vital signs checkboxes
    if st.session_state.vs_data:
        title_html = """
        <h2 style="font-family: 'DejaVu Sans'; font-size: 24px; margin-bottom: 0; color: #2c3e50;">
            Vital Signs:</h2>
        """
        st.markdown(title_html, unsafe_allow_html=True)

        st.markdown("<h4 style='font-family: \"DejaVu Sans\"; font-size: 18px; margin: -20px 0 0 0;'>&nbsp;Of the following vital signs within the intake form, check the vital signs that are abnormal.</h4>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])  # Define two columns

        with col2:
            st.markdown("<div style='margin-left: 20px;'>", unsafe_allow_html=True)

            # Checkboxes for vital signs with values from session state
            heart_rate = vital_signs.get("heart_rate", "N/A")  # Get original value from vital_signs
            heart_rate_checkbox = st.checkbox(f"HEART RATE: {heart_rate}", value=st.session_state.vs_data['heart_rate'], key='heart_rate_checkbox')

            respiratory_rate = vital_signs.get("respiratory_rate", "N/A")
            respiratory_rate_checkbox = st.checkbox(f"RESPIRATORY RATE: {respiratory_rate}", value=st.session_state.vs_data['respiratory_rate'], key='respiratory_rate_checkbox')

            blood_pressure = vital_signs.get("blood_pressure", "N/A")
            blood_pressure_checkbox = st.checkbox(f"BLOOD PRESSURE: {blood_pressure}", value=st.session_state.vs_data['blood_pressure'], key='blood_pressure_checkbox')

            pulseox = vital_signs.get("pulseox", "N/A")
            pulseox_checkbox = st.checkbox(f"PULSE OXIMETRY: {pulseox}", value=st.session_state.vs_data['pulseox'], key='pulseox_checkbox')

            temperature = vital_signs.get("temperature", "N/A")
            temperature_checkbox = st.checkbox(f"TEMPERATURE: {temperature}", value=st.session_state.vs_data['temperature'], key='temperature_checkbox')

            weight = vital_signs.get("weight", "N/A")
            weight_checkbox = st.checkbox(f"WEIGHT: {weight}", value=st.session_state.vs_data['weight'], key='weight_checkbox')

            st.markdown("</div>", unsafe_allow_html=True)

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
                'last_page': 'intake_form'  # This assumes you want to upload vs_data
            }
        
            try:
                upload_message = upload_to_firebase(db, document_id, entry)
                st.success("Data uploaded successfully!")  # Success message
            except Exception as e:
                st.error(f"Error uploading data: {e}")  # Error message
        
            st.session_state.intake_submitted = True
            st.session_state.page = "diagnoses"  # Move to Diagnoses page
            st.write(f"Current page set to: {st.session_state.page}") 
            st.write(f"Session state after update: {st.session_state}") 
            #st.rerun()  # Rerun the app to refresh the page
    else:
        st.error("No vital signs data available.")
