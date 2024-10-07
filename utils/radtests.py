import streamlit as st
from utils.session_management import collect_session_data  # Ensure this is included
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

def load_radiological_tests(db, document_id):
    """Load existing radiological tests from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    
    rad_rows = [""] * 5  # Default to empty for 5 tests
    dropdown_defaults = {dx: [""] * 5 for dx in st.session_state.diagnoses}  # Prepare default dropdowns

    if user_data.exists:
        rad_tests = user_data.to_dict().get('radiological_tests', {})

        # Iterate through each diagnosis and populate the rad_rows and dropdown defaults
        for diagnosis, tests in rad_tests.items():
            for i, test in enumerate(tests):
                if i < 5:  # Ensure we stay within bounds
                    if test['radiological_test']:
                        rad_rows[i] = test['radiological_test']  # Populate rad rows directly
                    dropdown_defaults[diagnosis][i] = test['assessment']  # Set dropdown default values

    return rad_rows, dropdown_defaults

def display_radiological_tests(db, document_id):
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

    # Load existing radiological tests from Firebase
    st.session_state.rad_rows, st.session_state.dropdown_defaults = load_radiological_tests(db, document_id)

    st.title("Radiological Tests App")
    st.markdown("Of the following, please select up to 5 radiological tests that you would order and describe how they influence the differential diagnosis.")

    # Reorder section in the sidebar
    with st.sidebar:
        st.subheader("Reorder Diagnoses")

        selected_diagnosis = st.selectbox(
            "Select a diagnosis to move",
            options=st.session_state.diagnoses,
            index=(st.session_state.diagnoses.index(st.session_state.selected_moving_diagnosis) if st.session_state.selected_moving_diagnosis in st.session_state.diagnoses else 0),
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
                f"Test for row {i + 1}",
                options=[""] + read_rad_tests_from_file(),
                index=(read_rad_tests_from_file().index(st.session_state.rad_rows[i]) if st.session_state.rad_rows[i] in read_rad_tests_from_file() else 0),
                key=f"rad_row_{i}",
                label_visibility="collapsed",
            )

        for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
            with col:
                assessment_options = ["", "Necessary", "Neither More Nor Less Useful", "Unnecessary"]
                dropdown_value = st.session_state.dropdown_defaults.get(diagnosis, [""] * 5)[i]
                index = assessment_options.index(dropdown_value) if dropdown_value in assessment_options else 0

                st.selectbox(
                    "Assessment for " + diagnosis,
                    options=assessment_options,
                    index=index,
                    key=f"select_{i}_{diagnosis}_rad",
                    label_visibility="collapsed"
                )

    # Submit button for radiological tests
    if st.button("Submit", key="radtests_submit_button"):
        rad_tests_data = {}  # Store rad tests and assessments
        # Check if at least one radiological test is selected
        if not any(st.session_state[f"rad_row_{i}"] for i in range(5)):
            st.error("Please select at least one radiological test.")
        else:
            for i in range(5):
                for diagnosis in st.session_state.diagnoses:
                    assessment = st.session_state[f"select_{i}_{diagnosis}_rad"]
                    if diagnosis not in rad_tests_data:
                        rad_tests_data[diagnosis] = []
                    rad_tests_data[diagnosis].append({
                        'radiological_test': st.session_state[f"rad_row_{i}"],
                        'assessment': assessment
                    })

            # Set diagnoses_s5 to the current state of diagnoses
            st.session_state.diagnoses_s5 = [dx for dx in st.session_state.diagnoses if dx]  # Update with current order

            entry = {
                'radiological_tests': rad_tests_data,  # Include radiological tests data
                'diagnoses_s5': st.session_state.diagnoses_s5  # Include diagnoses_s5 in the entry
            }

            # Upload to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.session_state.page = "Other Tests"  # Change to the Simple Success page
            st.success("Radiological tests submitted successfully.")
            st.rerun()  # Rerun to update the app



