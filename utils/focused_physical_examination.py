import streamlit as st
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase

def load_existing_examination(db, document_id):
    """Load existing physical examination selections from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()

    if user_data.exists:
        return user_data.to_dict().get("examinations", {})
    return {"excluded_exams": [], "confirmed_exams": []}

def display_focused_physical_examination(db, document_id):
    st.title("Focused Physical Examination Selection")

    # Load existing examination selections
    existing_examinations = load_existing_examination(db, document_id)
    selected_exams1 = existing_examinations.get("excluded_exams", [])
    selected_exams2 = existing_examinations.get("confirmed_exams", [])

    # Prompt for excluding hypotheses
    st.markdown("<h5>Please select the parts of physical examination required, in order to exclude some unlikely, but important hypotheses:</h5>", unsafe_allow_html=True)
    options1 = [
        "General Appearance", "Eyes", "Ears, Neck, Throat",
        "Lymph Nodes", "Cardiovascular", "Lungs",
        "Skin", "Abdomen", "Extremities",
        "Musculoskeletal", "Neurological", "Psychiatry", "Genitourinary"
    ]
    selected_exams1 = st.multiselect("Select options:", options1, default=selected_exams1, key="exclude_exams")

    # Prompt for confirming hypotheses
    st.markdown("<h5>Please select examinations necessary to confirm the most likely hypothesis and to discriminate between others:</h5>", unsafe_allow_html=True)
    selected_exams2 = st.multiselect("Select options:", options1, default=selected_exams2, key="confirm_exams")
    
    if st.button("Submit", key="focused_pe_submit_button"):
        # Ensure both selections have been made
        if not selected_exams1:
            st.error("Please select at least one examination that will allow you to exclude some unlikely, but important hypotheses.")
        elif not selected_exams2:
            st.error("Please select at least one examination to confirm the most likely hypothesis and to discriminate between others.")
        else:
            entry = {
                'excluded_exams': selected_exams1,
                'confirmed_exams': selected_exams2,
            }

            # Collect session data
            session_data = collect_session_data()  # Collect session data

            # Upload the session data to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.success("Your selections have been saved successfully.")
            
            # Change the session state to navigate to the next page
            st.session_state.page = "Physical Examination Components"
            st.rerun()  # Rerun to navigate to the next page

if __name__ == '__main__':
    # Assuming you have a function to initialize your Firebase `db` connection and get `document_id`
    # main(db, document_id) would be called here
    #pass
