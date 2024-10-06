import streamlit as st
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase  

def read_diagnoses_from_file():
    try:
        with open('dx_list.txt', 'r') as file:
            diagnoses = [line.strip() for line in file.readlines() if line.strip()]
        return diagnoses
    except Exception as e:
        st.error(f"Error reading dx_list.txt: {e}")
        return []

def read_lab_tests_from_file():
    try:
        with open('labtests.txt', 'r') as file:
            lab_tests = [line.strip() for line in file.readlines() if line.strip()]
        return lab_tests
    except Exception as e:
        st.error(f"Error reading labtests.txt: {e}")
        return []

def fetch_laboratory_tests_from_firebase(user_data):
    """Extract laboratory tests from the fetched user data."""
    lab_rows = [""] * 5  # Default to empty for 5 tests
    dropdown_defaults = {dx: [""] * 5 for dx in st.session_state.diagnoses}  # Prepare default dropdowns

    if user_data.exists:
        lab_tests = user_data.to_dict().get('laboratory_tests', {})
        for diagnosis, tests in lab_tests.items():
            for i, test in enumerate(tests):
                if i < 5:  # Ensure we stay within bounds
                    if test['laboratory_test']:
                        lab_rows[i] = test['laboratory_test']  # Populate lab rows directly
                    dropdown_defaults[diagnosis][i] = test['assessment']  # Set dropdown default values

    return lab_rows, dropdown_defaults

def load_laboratory_tests(db, document_id):
    """Load existing laboratory tests from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()

    return fetch_laboratory_tests_from_firebase(user_data)

def display_laboratory_tests(db, document_id):
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "laboratory_tests"
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = read_diagnoses_from_file()  # Load diagnoses initially
    if 'selected_moving_diagnosis' not in st.session_state:
        st.session_state.selected_moving_diagnosis = ""
    
    st.session_state.lab_rows, st.session_state.dropdown_defaults = load_laboratory_tests(db, document_id)

    st.title("Laboratory Tests")
    st.markdown("Select up to 5 laboratory tests and describe how they influence the differential diagnosis.")

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
            selected_lab_test = st.selectbox(
                f"Test {i + 1}",
                options=[""] + read_lab_tests_from_file(),
                index=read_lab_tests_from_file().index(st.session_state.lab_rows[i]) if st.session_state.lab_rows[i] in read_lab_tests_from_file() else 0,
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
        lab_tests_data = {}
        if not any(st.session_state[f"lab_row_{i}"] for i in range(5)):
            st.error("Please select at least one laboratory test.")
        else:
            for i in range(5):
                for diagnosis in st.session_state.diagnoses:
                    assessment = st.session_state[f"select_{i}_{diagnosis}_lab"]
                    if diagnosis not in lab_tests_data:
                        lab_tests_data[diagnosis] = []
                    lab_tests_data[diagnosis].append({
                        'laboratory_test': st.session_state[f"lab_row_{i}"],
                        'assessment': assessment
                    })

            entry = {
                'laboratory_tests': lab_tests_data,
                'diagnoses_s4': st.session_state.diagnoses
            }

            upload_message = upload_to_firebase(db, document_id, entry)
            st.success("Laboratory tests submitted successfully.")
            st.rerun()  # Rerun to update the app


