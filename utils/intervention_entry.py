import streamlit as st
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase

def load_existing_interventions(db, document_id):
    """Load existing intervention descriptions from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    
    if user_data.exists:
        return user_data.to_dict().get("interventions", [])
    return []

def read_intervention_options():
    """Load intervention options from int.txt."""
    try:
        with open('int.txt', 'r') as file:
            interventions = [line.strip() for line in file.readlines() if line.strip()]
        return interventions
    except Exception as e:
        st.error(f"Error reading int.txt: {e}")
        return []

def main(db, document_id):
    st.title("Intervention Description Entry")

    # Load existing interventions
    existing_interventions = load_existing_interventions(db, document_id)

    # Load intervention options from file
    intervention_options = read_intervention_options()

    # Prompt for user input
    st.header("Select any interventions that you would currently perform.")
    selected_interventions = st.multiselect("Interventions", options=intervention_options, default=existing_interventions)

    # Define the acute intervention option
    no_acute_intervention = "No Acute Interventions Are Currently Required"

    # Button to save to Firebase
    if st.button("Save Intervention", key="interventions_submit_button"):
        # Check for the specific condition
        if no_acute_intervention in selected_interventions and len(selected_interventions) > 1:
            st.error(f"You cannot select '{no_acute_intervention}' with other interventions. Please select only one or none.")
        elif selected_interventions:
            # Create entry with the interventions data
            entry = {
                "interventions": selected_interventions
            }
            
            # Upload the session data to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.success("Your interventions have been saved successfully.")
            st.session_state.page = "History with AI"  # Change to the next page
            st.session_state.document_id = document_id 
            st.rerun()  # Rerun to navigate to the next page
        else:
            st.error("Please select at least one intervention.")

if __name__ == '__main__':
    main(db, document_id)
