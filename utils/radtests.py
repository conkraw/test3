import streamlit as st
from utils.session_management import collect_session_data  # NEED THIS
from utils.firebase_operations import upload_to_firebase  

# Function to read diagnoses from a file
def read_diagnoses_from_file():
    try:
        with open('dx_list.txt', 'r') as file:
            diagnoses = [line.strip() for line in file.readlines() if line.strip()]
        return diagnoses
    except Exception as e:
        st.error(f"Error reading dx_list.txt: {e}")
        return []

# Function to read radiological tests from a file
def read_rad_tests_from_file():
    try:
        with open('radtests.txt', 'r') as file:
            rad_tests = [line.strip() for line in file.readlines() if line.strip()]
        return rad_tests
    except Exception as e:
        st.error(f"Error reading radtests.txt: {e}")
        return []

def display_radiological_tests(db, document_id):  # Updated to include db and document_id
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "radiological_tests"
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'selected_moving_diagnosis' not in st.session_state:
        st.session_state.selected_moving_diagnosis = ""  

    # Load diagnoses and radiological tests from files
    dx_options = read_diagnoses_from_file()
    rad_tests = read_rad_tests_from_file()
    dx_options.insert(0, "")  

    # Retain previous diagnoses if available
    if 'diagnoses_s5' in st.session_state:
        st.session_state.diagnoses = st.session_state.diagnoses_s5

    st.title("Radiological Tests App")

    st.markdown("""Of the following, please select up to 5 radiological tests that you would order and describe how they influence the differential diagnosis.""")

    # Reorder section in the sidebar
    with st.sidebar:
        st.subheader("Reorder Diagnoses")

        selected_diagnosis = st.selectbox(
            "Select a diagnosis to move",
            options=st.session_state.diagnoses,
            index=st.session_state.diagnoses.index(st.session_state.selected_moving_diagnosis) if st.session_state.selected_moving_diagnosis in st.session_state.diagnoses else 0,
            key="move_diagnosis"
        )

        move_direction = st.radio("Adjust Priority:", options=["Higher Priority", "Lower Priority"], key="move_direction")

        if st.button("Adjust Priority"):
            idx = st.session_state.diagnoses.index(selected_diagnosis)
            if move_direction == "Higher Priority" and idx > 0:
                st.session_state.diagnoses[idx], st.session_state.diagnoses[idx - 1] = (
                    st.session_state.diagnoses[idx - 1], st.session_state.diagnoses[idx]
                )
                st.session_state.selected_moving_diagnosis = st.session_state.diagnoses[idx - 1]  
            elif move_direction == "Lower Priority" and idx < len(st.session_state.diagnoses) - 1:
                st.session_state.diagnoses[idx], st.session_state.diagnoses[idx + 1] = (
                    st.session_state.diagnoses[idx + 1], st.session_state.diagnoses[idx]
                )
                st.session_state.selected_moving_diagnosis = st.session_state.diagnoses[idx + 1]  

        # Change a diagnosis section
        st.subheader("Change a Diagnosis")
        change_diagnosis = st.selectbox(
            "Select a diagnosis to change",
            options=st.session_state.diagnoses,
            key="change_diagnosis"
        )

        new_diagnosis_search = st.text_input("Search for a new diagnosis", "")
        if new_diagnosis_search:
            new_filtered_options = [dx for dx in dx_options if new_diagnosis_search.lower() in dx.lower() and dx not in st.session_state.diagnoses]
            if new_filtered_options:
                st.write("**Available Options:**")
                for option in new_filtered_options:
                    if st.button(f"{option}", key=f"select_new_{option}"):
                        index_to_change = st.session_state.diagnoses.index(change_diagnosis)
                        st.session_state.diagnoses[index_to_change] = option
                        st.rerun()  

    # Display radiological tests
    cols = st.columns(len(st.session_state.diagnoses) + 1)
    with cols[0]:
        st.markdown("Radiological Tests")

    for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
        with col:
            st.markdown(diagnosis)

    for i in range(5):
        cols = st.columns(len(st.session_state.diagnoses) + 1)
        with cols[0]:
            selected_rad_test = st.selectbox(
                f"",
                options=[""] + rad_tests,
                key=f"rad_row_{i}",
                label_visibility="collapsed",
            )

        for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
            with col:
                st.selectbox(
                    "Assessment for " + diagnosis,
                    options=["", "Necessary", "Neither More Nor Less Useful", "Unnecessary"],
                    key=f"select_{i}_{diagnosis}_rad",
                    label_visibility="collapsed"
                )

    # Submit button for radiological tests
    if st.button("Submit", key="radtests_submit_button"):
        assessments = {}
        at_least_one_selected = False

        for i in range(5):
            selected_rad_test = st.session_state[f"rad_row_{i}"]
            for diagnosis in st.session_state.diagnoses:
                assessment = st.session_state[f"select_{i}_{diagnosis}_rad"]
                if selected_rad_test:  # Check if a radiological test is selected
                    at_least_one_selected = True
                if diagnosis not in assessments:
                    assessments[diagnosis] = []
                assessments[diagnosis].append({
                    'radiological_test': selected_rad_test,
                    'assessment': assessment
                })

        # Check if at least one radiological test is selected
        if not at_least_one_selected:
            st.error("Please select at least one radiological test.")
        else:
            # Save diagnoses to Firebase
            st.session_state.diagnoses_s5 = [dx for dx in st.session_state.diagnoses if dx]  # Update with current order

            entry = {
                'radiological_tests': assessments,  # Include radiological tests data
                'diagnoses_s5': st.session_state.diagnoses_s5  # Include diagnoses_s5 in the entry
            }

            # Upload to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.session_state.page = "Other Tests"  # Change to the Simple Success page
            st.success("Radiological tests submitted successfully.")
            st.rerun()  # Rerun to update the app

