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

def load_laboratory_features(db, document_id):
    """Load existing laboratory features and diagnoses from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    
    if user_data.exists:
        assessments = user_data.to_dict().get('assessments', {})
        diagnoses_s7 = user_data.to_dict().get('diagnoses_s7', [])
        laboratory_features = [""] * 5  # Default to empty for 5 features
        dropdown_defaults = {diagnosis: [""] * 5 for diagnosis in assessments}  # Prepare default dropdowns
        
        # Populate laboratory features and dropdowns based on Firebase data
        for diagnosis, features in assessments.items():
            for i, feature in enumerate(features):
                if i < len(laboratory_features):  # Ensure we stay within bounds
                    laboratory_features[i] = feature['laboratory_feature']
                    dropdown_defaults[diagnosis][i] = feature['assessment']  # Set dropdown default values
        
        return laboratory_features, dropdown_defaults, diagnoses_s7
    else:
        return [""] * 5, {}, []  # Default to empty if no data

def display_laboratory_features(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "laboratory_features"
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'laboratory_features' not in st.session_state:
        st.session_state.laboratory_features, st.session_state.dropdown_defaults, st.session_state.diagnoses_s7 = load_laboratory_features(db, document_id)
    if 'selected_moving_diagnosis' not in st.session_state:
        st.session_state.selected_moving_diagnosis = ""  

    # Load diagnoses from file
    dx_options = read_diagnoses_from_file()
    dx_options.insert(0, "")  

    st.title("Laboratory Features Illness Script")
    st.markdown("""
            ### Laboratory Features
            Please provide up to 5 historical features that influence the differential diagnosis.
        """)

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

    # Display laboratory features
    cols = st.columns(len(st.session_state.diagnoses) + 1)
    with cols[0]:
        st.markdown("Laboratory Features")

    for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
        with col:
            st.markdown(diagnosis)

    for i in range(5):
        cols = st.columns(len(st.session_state.diagnoses) + 1)
        with cols[0]:
            # Prefill with existing values from session state
            st.session_state.laboratory_features[i] = st.text_input(
                f"Feature {i + 1}",
                value=st.session_state.laboratory_features[i],  # Prefill with existing value
                key=f"lab_row_{i}",
                label_visibility="collapsed"
            )

        for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
            with col:
                # Safely get dropdown default value
                dropdown_value = st.session_state.dropdown_defaults.get(diagnosis, [""] * 5)[i]
                index = ["", "Supports", "Does not support"].index(dropdown_value) if dropdown_value in ["", "Supports", "Does not support"] else 0

                st.selectbox(
                    "Assessment for " + diagnosis,
                    options=["", "Supports", "Does not support"],
                    index=index,
                    key=f"select_{i}_{diagnosis}_lab",
                    label_visibility="collapsed"
                )

    # Submit button for laboratory features
    if st.button("Submit", key="lab_features_submit_button"):
        # Ensure at least one laboratory feature is provided
        if not any(st.session_state.laboratory_features):
            st.error("Please enter at least one laboratory feature.")
        else:
            assessments = {}
            for i in range(5):
                for diagnosis in st.session_state.diagnoses:
                    assessment = st.session_state[f"select_{i}_{diagnosis}_lab"]
                    if diagnosis not in assessments:
                        assessments[diagnosis] = []
                    assessments[diagnosis].append({
                        'laboratory_feature': st.session_state.laboratory_features[i],
                        'assessment': assessment
                    })
            
            # Update diagnoses_s7 to the current state of diagnoses
            st.session_state.diagnoses_s7 = [dx for dx in st.session_state.diagnoses if dx]

            entry = {
                'assessments': assessments,
                'diagnoses_s7': st.session_state.diagnoses_s7
            }

            # Upload to Firebase using the current diagnosis order
            upload_message = upload_to_firebase(db, document_id, entry)
            
            st.session_state.page = "Simple Success"  # Change to the next page
            st.success("Laboratory features submitted successfully.")
            st.rerun()  # Rerun to update the app

# Call the function to run the app
# This would normally be placed in your main entry point
# display_laboratory_features(db, document_id)
