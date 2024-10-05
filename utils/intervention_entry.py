import streamlit as st
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase

def load_existing_intervention(db, document_id):
    """Load existing intervention description from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    
    if user_data.exists:
        return user_data.to_dict().get("interventions", "")
    return ""

def main(db, document_id):
    st.title("Intervention Description Entry")

    # Load existing intervention description
    existing_intervention = load_existing_intervention(db, document_id)

    # Prompt for user input
    st.header("Describe any interventions that you would currently perform.")
    interventions = st.text_area("Interventions Description", height=200, value=existing_intervention)

    # Button to save to Firebase
    if st.button("Save Intervention", key="interventions_submit_button"):
        if interventions:
            # Collect session data
            session_data = collect_session_data()  # Collect session data
            
            # Create entry with the interventions data
            entry = {
                "interventions": interventions
            }
            
            # Upload the session data to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.success("Your interventions have been saved successfully.")
            
            st.session_state.page = "History with AI"  # Change to the next page
            st.session_state.document_id = document_id 
            st.rerun()  # Rerun to navigate to the next page
        else:
            st.error("Please enter a description of the interventions.")

if __name__ == '__main__':
    main()
