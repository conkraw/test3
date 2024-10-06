import streamlit as st
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase

def load_existing_examination(db, document_id):
    """Load existing questions and responses from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    
    if user_data.exists:
        return user_data.to_dict().get("excluded_exams", []), user_data.to_dict().get("confirmed_exams", [])
    return [], []


def display_focused_physical_examination(db, document_id):
    st.title("Focused Physical Examination Selection")

    # Load existing examination selections into session state if not already present
    if 'excluded_exams' not in st.session_state or 'confirmed_exams' not in st.session_state:
        existing_examinations = load_existing_examination(db, document_id)
        st.session_state.excluded_exams = existing_examinations.get("excluded_exams", [])
        st.session_state.confirmed_exams = existing_examinations.get("confirmed_exams", [])

    # Define options for examination
    options1 = [
        "General Appearance", "Eyes", "Ears, Neck, Throat",
        "Lymph Nodes", "Cardiovascular", "Lungs",
        "Skin", "Abdomen", "Extremities",
        "Musculoskeletal", "Neurological", "Psychiatry", "Genitourinary"
    ]

    # Multiselect for excluding hypotheses
    st.markdown("<h5>Please select the parts of physical examination required, in order to exclude some unlikely, but important hypotheses:</h5>", unsafe_allow_html=True)
    selected_exams1 = st.multiselect("Select options:", options1, default=st.session_state.excluded_exams, key="exclude_exams")
    st.session_state.excluded_exams = selected_exams1  # Store back into session state

    # Multiselect for confirming hypotheses
    st.markdown("<h5>Please select examinations necessary to confirm the most likely hypothesis and to discriminate between others:</h5>", unsafe_allow_html=True)
    selected_exams2 = st.multiselect("Select options:", options1, default=st.session_state.confirmed_exams, key="confirm_exams")
    st.session_state.confirmed_exams = selected_exams2  # Store back into session state
    
    if st.button("Submit", key="focused_pe_submit_button"):
        # Ensure both selections have been made
        if not st.session_state.excluded_exams:
            st.error("Please select at least one examination that will allow you to exclude some unlikely, but important hypotheses.")
        elif not st.session_state.confirmed_exams:
            st.error("Please select at least one examination to confirm the most likely hypothesis and to discriminate between others.")
        else:
            entry = {
                'excluded_exams': st.session_state.excluded_exams,
                'confirmed_exams': st.session_state.confirmed_exams,
            }

            # Collect session data
            session_data = collect_session_data()  # Collect session data

            # Upload the session data to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.success("Your selections have been saved successfully.")
            
            # Change the session state to navigate to the next page
            st.session_state.page = "Physical Examination Components"
            st.rerun()  # Rerun to navigate to the next page


