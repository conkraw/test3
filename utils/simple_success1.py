import streamlit as st

def display_simple_success1():
    # Check if the required session state variables exist
    if 'diagnoses' in st.session_state and 'treatments' in st.session_state:
        diagnoses = st.session_state.diagnoses
        treatments = st.session_state.treatments
        assessments = {diagnosis: [] for diagnosis in diagnoses}

        # Retrieve assessments from session state if they exist
        if 'assessments' in st.session_state:
            assessments = st.session_state.assessments

        st.title("Summary of Results")

        st.markdown("""
            ### Summary of Diagnoses and Treatments
            Below are the diagnoses along with the treatments and their assessments.
        """)

        for diagnosis in diagnoses:
            if diagnosis:
                st.subheader(diagnosis)
                if diagnosis in assessments:
                    for treatment_info in assessments[diagnosis]:
                        st.write(f"**Treatment:** {treatment_info['treatment']}")
                        st.write(f"**Assessment:** {treatment_info['assessment']}")
                else:
                    st.write("No treatments recorded for this diagnosis.")

        st.markdown("")
        if st.button("End Session"):
            # Clear session state
            st.session_state.clear()
            st.success("Session ended successfully. Please close this window or tab.")

    else:
        st.error("No results available. Please complete the previous steps first.")

# To use the display_summary function, just call it in the main app logic
if __name__ == "__main__":
    display_simple_success1()

