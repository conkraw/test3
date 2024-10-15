import streamlit as st
from utils.session_management import collect_session_data
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

# Function to read laboratory tests from a file
def read_lab_tests_from_file():
    try:
        with open('labtests.txt', 'r') as file:
            lab_tests = [line.strip() for line in file.readlines() if line.strip()]
        return lab_tests
    except Exception as e:
        st.error(f"Error reading labtests.txt: {e}")
        return []

def load_laboratory_tests(db, document_id):
    """Load existing laboratory tests from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    
    lab_rows = [""] * 5  # Default to empty for 5 tests
    dropdown_defaults = {dx: [""] * 5 for dx in st.session_state.diagnoses}  # Prepare default dropdowns

    if user_data.exists:
        lab_tests = user_data.to_dict().get('laboratory_tests', {})

        # Iterate through each diagnosis and populate the lab_rows and dropdown defaults
        for diagnosis, tests in lab_tests.items():
            for i, test in enumerate(tests):
                if i < 5:  # Ensure we stay within bounds
                    if test['laboratory_test']:
                        lab_rows[i] = test['laboratory_test']  # Populate lab rows directly
                    dropdown_defaults[diagnosis][i] = test['assessment']  # Set dropdown default values

    return lab_rows, dropdown_defaults

def display_laboratory_tests(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "laboratory_tests"
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'selected_moving_diagnosis' not in st.session_state:
        st.session_state.selected_moving_diagnosis = st.session_state.diagnoses[0] if st.session_state.diagnoses else ""

    # Load diagnoses and laboratory tests from files
    dx_options = read_diagnoses_from_file()
    lab_tests = read_lab_tests_from_file()
    dx_options.insert(0, "")

    # Load existing laboratory tests from Firebase
    st.session_state.lab_rows, st.session_state.dropdown_defaults = load_laboratory_tests(db, document_id)

    st.title("Laboratory Tests")
    st.markdown("Of the following, please select up to 5 laboratory tests that you would order and describe how they influence the differential diagnosis.")

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

    # Display laboratory tests
    cols = st.columns(len(st.session_state.diagnoses) + 1)
    with cols[0]:
        st.markdown("Laboratory Tests")

    for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
        with col:
            st.markdown(diagnosis)

    for i in range(5):
        cols = st.columns(len(st.session_state.diagnoses) + 1)
        with cols[0]:
            lab_test_options = read_lab_tests_from_file()
            # Add the blank option at the end
            lab_test_options.append("")  # Add blank option at the end
            selected_lab_test = st.selectbox(
                f"Test for row {i + 1}",
                options=lab_test_options,
                index=(lab_test_options.index(st.session_state.lab_rows[i]) if st.session_state.lab_rows[i] in lab_test_options else 0),
                key=f"lab_row_{i}",
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
                    key=f"select_{i}_{diagnosis}_lab",
                    label_visibility="collapsed"
                )

        # Submit button for laboratory tests
    
    if st.button("Submit", key="labtests_submit_button"):
        lab_tests_data = {}  # Store lab tests and assessments
        selected_lab_tests = []  # Track selected lab tests for uniqueness check
    
        # Check if at least one laboratory test is selected
        if not any(st.session_state[f"lab_row_{i}"] for i in range(5)):
            st.error("Please select at least one laboratory test.")
        else:
            duplicate_found = False  # Flag to track duplicates
    
            for i in range(5):
                lab_test = st.session_state[f"lab_row_{i}"]
                if lab_test:  # Only check if a test is selected
                    if lab_test in selected_lab_tests:
                        duplicate_found = True  # Duplicate detected
                        break
                    selected_lab_tests.append(lab_test)  # Add to selected tests
    
                for diagnosis in st.session_state.diagnoses:
                    assessment = st.session_state[f"select_{i}_{diagnosis}_lab"]
                    if diagnosis not in lab_tests_data:
                        lab_tests_data[diagnosis] = []
                    lab_tests_data[diagnosis].append({
                        'laboratory_test': lab_test,
                        'assessment': assessment
                    })
    
            if duplicate_found:
                st.error("Please select unique laboratory tests. Duplicate selections are not allowed.")
            else:
                # Set diagnoses_s4 to the current state of diagnoses
                st.session_state.diagnoses_s4 = [dx for dx in st.session_state.diagnoses if dx]  # Update with current order
    
                entry = {
                    'laboratory_tests': lab_tests_data,  # Include laboratory tests data
                    'diagnoses_s4': st.session_state.diagnoses_s4  # Include diagnoses_s4 in the entry
                }
    
                # Upload to Firebase using the current diagnosis order
                upload_message = upload_to_firebase(db, document_id, entry)
                
                st.session_state.page = "Radiology Tests"  # Change to the Simple Success page
                st.success("Laboratory tests submitted successfully.")
                st.rerun()  # Rerun to update the app
    

