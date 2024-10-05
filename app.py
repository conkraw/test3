import streamlit as st

st.set_page_config(layout="wide")

from utils.file_operations import load_users
from utils.welcome import welcome_page
from utils.login import login_page
from utils.intake_form import display_intake_form
from utils.diagnoses import display_diagnoses
from utils.intervention_entry import main as intervention_entry_main
from utils.history_with_ai import run_virtual_patient
from utils.focused_physical_examination import display_focused_physical_examination
from utils.physical_examination import main as display_physical_examination
from utils.history_illness_script import main as history_illness_script
from utils.simple_success import display_simple_success
from utils.simple_success1 import display_simple_success1
from utils.physical_examination_features import display_physical_examination_features
from utils.lab_tests import display_laboratory_tests
from utils.radtests import display_radiological_tests
from utils.othertests import display_other_tests
from utils.results import display_results_image
from utils.laboratory_features import display_laboratory_features
from utils.treatments import display_treatments
from utils.firebase_operations import initialize_firebase, upload_to_firebase
from utils.session_management import collect_session_data

def load_user_data(db):
    """Load user data from Firebase and store it in session state."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    if st.session_state.user_code:
        user_data = db.collection(collection_name).document(st.session_state.user_code).get()
        if user_data.exists:
            user_data_dict = user_data.to_dict()
            # Store all user data in session state
            for key, value in user_data_dict.items():
                st.session_state[key] = value

            # Debug statement to check if unique_code is in session state
            if "unique_code" in st.session_state:
                st.write("Unique Code and associated data loaded into session state:")
                st.write(f"Unique Code: {st.session_state.unique_code}")
                for key, value in st.session_state.items():
                    if key.startswith("unique_code") or key in user_data_dict:
                        st.write(f"{key}: {value}")
            else:
                st.write("No unique_code found in session state.")

def main():
    # Initialize Firebase
    db = initialize_firebase()
    
    # Initialize session state
    if "user_code" not in st.session_state:
        st.session_state.user_code = None
        
    if "user_name" not in st.session_state:
        st.session_state.user_name = None  # Initialize user_name
        
    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    
    if "document_id" not in st.session_state:
        st.session_state.document_id = None    

    # Page routing
    if st.session_state.page == "welcome":
        welcome_page()
    elif st.session_state.page == "login":
        users = load_users()
        st.session_state.document_id = login_page(users, db) 
    elif st.session_state.page == "intake_form":
        display_intake_form(db, st.session_state.document_id)
    elif st.session_state.page == "diagnoses":
        display_diagnoses(db, st.session_state.document_id)
    elif st.session_state.page == "Intervention Entry":
        intervention_entry_main(db, st.session_state.document_id)
    elif st.session_state.page == "History with AI":
        run_virtual_patient(db, st.session_state.document_id)
    elif st.session_state.page == "Focused Physical Examination":
        display_focused_physical_examination(db, st.session_state.document_id)
    elif st.session_state.page == "Physical Examination Components":
        display_physical_examination()
    elif st.session_state.page == "History Illness Script":
        history_illness_script(db, st.session_state.document_id)
    elif st.session_state.page == "Physical Examination Features":
        display_physical_examination_features(db, st.session_state.document_id)
    elif st.session_state.page == "Laboratory Tests":
        display_laboratory_tests(db, st.session_state.document_id)
    elif st.session_state.page == "Radiology Tests":
        display_radiological_tests(db, st.session_state.document_id)
    elif st.session_state.page == "Other Tests":
        display_other_tests(db, st.session_state.document_id)
    elif st.session_state.page == "Results":
        display_results_image()
    elif st.session_state.page == "Laboratory Features":
        display_laboratory_features(db, st.session_state.document_id)
    elif st.session_state.page == "Treatments":
        display_treatments(db, st.session_state.document_id)
    elif st.session_state.page == "Simple Success":
        display_simple_success1()

if __name__ == "__main__":
    main()

