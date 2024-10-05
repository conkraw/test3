import streamlit as st
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase

def login_page(users, db):
    st.markdown("<p style='font-family: \"DejaVu Sans\";'>Please enter your unique code to access the assessment.</p>", unsafe_allow_html=True)
    
    unique_code_input = st.text_input("Unique Code:")
    
    if st.button("Submit"):
        if unique_code_input:
            unique_code = unique_code_input.strip()  # Keep it as a string
            
            # Check if the unique_code exists in the 'code' column of the users dataframe
            if unique_code in users['code'].values:
                # Store the unique code in session state
                st.session_state.unique_code = unique_code

                # Define the entry data to be uploaded to Firebase (optional)
                entry = {
                    "unique_code": unique_code,
                    # Add any other session data as needed
                }

                # Upload the session data to Firebase (if necessary)
                # upload_message = upload_to_firebase(db, st.session_state.document_id, entry)

                # Navigate to the intake form page
                st.session_state.page = "intake_form"  # Change to assessment page
                st.session_state.document_id = unique_code  # Set document ID for future uploads
                st.rerun()  # Rerun to refresh the view
            else:
                st.error("Invalid code. Please try again.")
        else:
            st.error("Please enter a code.")


