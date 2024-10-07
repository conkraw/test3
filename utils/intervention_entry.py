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

def read_intervention_options():
    """Read intervention options from int.txt."""
    try:
        with open('int.txt', 'r') as file:
            interventions = [line.strip() for line in file.readlines() if line.strip()]
        return interventions
    except Exception as e:
        st.error(f"Error reading int.txt: {e}")
        return []

def main(db, document_id):
    st.title("Intervention Description Entry")

    # Load existing intervention description
    existing_intervention = load_existing_intervention(db, document_id)

    # Load intervention options from file
    intervention_options = read_intervention_options()
    intervention_options.insert(0, "")  # Add a blank option for no selection

    # Prompt for user input
    st.header("Select an intervention that you would currently perform.")
    selected_intervention = st.selectbox("Interventions", options=intervention_options, index=intervention_options.index(existing_intervention) if existing_intervention in intervention_options else 0)

    # Button to save to Firebase
    if st.button("Save Intervention", key="interventions_submit_button"):
        if selected_intervention:
            # Collect session data
            session_data = collect_session_data()  # Collect session data
            
            # Create entry with the selected intervention data
            entry = {
                "interventions": selected_intervention
            }
            
            # Upload the session data to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.success("Your intervention has been saved successfully.")
            
            st.session_state.page = "History with AI"  # Change to the next page
            st.session_state.document_id = document_id 
            st.rerun()  # Rerun to navigate to the next page
        else:
            st.error("Please select an intervention.")

if __name__ == '__main__':
    main(db, document_id)
