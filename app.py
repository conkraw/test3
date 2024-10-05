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
import uuid  # To generate unique document IDs

def save_user_state(db):
    if st.session_state.user_code:
        entry = {
            "last_page": st.session_state.page,
            # Add other session data if needed
        }
        upload_to_firebase(db, st.session_state.user_code, entry)

def load_last_page(db):
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]  # Get collection name from secrets
    if st.session_state.user_code:
        user_data = db.collection(collection_name).document(st.session_state.user_code).get()
        if user_data.exists:
            return user_data.to_dict().get("last_page")
    return "welcome"

        
def main():
    # Initialize Firebase
    db = initialize_firebase()
    
    # Initialize session state
    if "user_code" not in st.session_state: ###
        st.session_state.user_code = None ###
        
    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    
    # Generate a unique document ID at the start of the session
    if "document_id" not in st.session_state:
        st.session_state.document_id = None    

    if st.session_state.user_code:
        last_page = load_last_page(db)
        if last_page:
            st.session_state.page = last_page

    # Page routing
    if st.session_state.page == "welcome":
        welcome_page()
    elif st.session_state.page == "login":
        users = load_users()
        #login_page(users)  # Pass document ID
        st.session_state.document_id = login_page(users, db) 
    elif st.session_state.page == "intake_form":
        display_intake_form(db, st.session_state.document_id)
    elif st.session_state.page == "diagnoses":
        display_diagnoses(db,st.session_state.document_id)
    elif st.session_state.page == "Intervention Entry":
        intervention_entry_main(db,st.session_state.document_id)
    elif st.session_state.page == "History with AI":
        run_virtual_patient(db,st.session_state.document_id)
    elif st.session_state.page == "Focused Physical Examination":
        display_focused_physical_examination(db, st.session_state.document_id)  # Pass document ID
    elif st.session_state.page == "Physical Examination Components":
        display_physical_examination()
    elif st.session_state.page == "History Illness Script":
        history_illness_script(db,st.session_state.document_id)
    elif st.session_state.page == "Physical Examination Features":
        display_physical_examination_features(db,st.session_state.document_id)
    elif st.session_state.page == "Laboratory Tests":
        display_laboratory_tests(db,st.session_state.document_id)
    elif st.session_state.page == "Radiology Tests":
        display_radiological_tests(db,st.session_state.document_id)
    elif st.session_state.page == "Other Tests":
        display_other_tests(db,st.session_state.document_id)
    elif st.session_state.page == "Results":
        display_results_image()
    elif st.session_state.page == "Laboratory Features":
        display_laboratory_features(db,st.session_state.document_id)
    elif st.session_state.page == "Treatments":
        display_treatments(db,st.session_state.document_id)
    elif st.session_state.page == "Simple Success":
        display_simple_success1()

if __name__ == "__main__":
    main()

