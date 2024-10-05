import streamlit as st

def login_page(users, db):
    st.markdown("<p style='font-family: \"DejaVu Sans\";'>Please enter your unique code to access the assessment.</p>", unsafe_allow_html=True)
    
    unique_code_input = st.text_input("Unique Code:")
    
    if st.button("Submit"):
        if unique_code_input:
            unique_code = unique_code_input.strip()  # Keep it as a string
            
            # Check if the unique_code exists in the 'code' column of the users dataframe
            if unique_code in users['code'].values:
                # Store the unique code and user name in session state
                st.session_state.user_name = users.loc[users['code'] == unique_code, 'name'].values[0]
                st.session_state.user_code = unique_code

                # Navigate to the intake form page
                st.session_state.page = "intake_form"  # Change to assessment page
                st.session_state.document_id = unique_code
                st.rerun()  # Rerun to refresh the view
            else:
                st.error("Invalid code. Please try again.")
        else:
            st.error("Please enter a code.")

