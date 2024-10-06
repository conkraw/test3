import streamlit as st
from utils.session_management import collect_session_data  # NEAT THIS
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

def load_existing_data(db, document_id):
    """Load existing diagnoses and historical features from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    
    if user_data.exists:
        data = user_data.to_dict()
        diagnoses_s2 = data.get("diagnoses_s2", [""] * 5)
        hxfeatures = data.get("hxfeatures", {})

        historical_features = [""] * 5
        for i, diagnosis in enumerate(diagnoses_s2):
            if diagnosis in hxfeatures:
                historical_features[i] = hxfeatures[diagnosis][0].get('historical_feature', "")
        
        return diagnoses_s2, historical_features
    
    return [""] * 5, [""] * 5  # Default values if no data

def main(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "historical_features"  # Start on historical features page
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'diagnoses_s2' not in st.session_state:
        st.session_state.diagnoses_s2, st.session_state.historical_features = load_existing_data(db, document_id)
    else:
        st.session_state.historical_features = st.session_state.historical_features or [""] * 5
    if 'selected_buttons' not in st.session_state:
        st.session_state.selected_buttons = [False] * 5  
    if 'selected_moving_diagnosis' not in st.session_state:
        st.session_state.selected_moving_diagnosis = ""  
    
    # Load diagnoses from file
    dx_options = read_diagnoses_from_file()
    dx_options.insert(0, "")  

    # Title of the app
    st.title("Historical Features App")

    # Historical Features Page
    if st.session_state.current_page == "historical_features":
        st.markdown("""
            ### HISTORICAL FEATURES
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

                # Update diagnoses_s2 after moving
                st.session_state.diagnoses_s2 = [dx for dx in st.session_state.diagnoses if dx]  # Update with current order

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
                            # Update diagnoses_s2 here as well
                            st.session_state.diagnoses_s2 = [dx for dx in st.session_state.diagnoses if dx]  # Update diagnoses_s2
                            st.rerun()  

        # Display historical features
        cols = st.columns(len(st.session_state.diagnoses) + 1)
        with cols[0]:
            st.markdown("Historical Features")

        for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
            with col:
                st.markdown(diagnosis)

        for i in range(5):
            cols = st.columns(len(st.session_state.diagnoses) + 1)
            with cols[0]:
                st.session_state.historical_features[i] = st.text_input(f"Feature {i + 1}:", value=st.session_state.historical_features[i], key=f"hist_row_{i}", label_visibility="collapsed")

            for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
                with col:
                    st.selectbox(
                        "hxfeatures for " + diagnosis,
                        options=["", "Supports", "Does not support"],
                        index=["", "Supports", "Does not support"].index(st.session_state.historical_features[i]),
                        key=f"select_{i}_{diagnosis}_hist",
                        label_visibility="collapsed"
                    )

        # Submit button for historical features
        if st.button("Submit", key="hx_features_submit_button"):
            if not any(st.session_state.historical_features):  # Check if at least one historical feature is entered
                st.error("Please enter at least one historical feature.")
            else:
                entry = {
                    'hxfeatures': {},  # Changed from 'assessments'
                    'diagnoses_s2': st.session_state.diagnoses_s2  # Include the reordered diagnoses here
                }

                # Make sure to capture hxfeatures in the current order of diagnoses
                for i in range(5):
                    for diagnosis in st.session_state.diagnoses:
                        hxfeature = st.session_state[f"select_{i}_{diagnosis}_hist"]
                        if diagnosis not in entry['hxfeatures']:  # Changed from assessments
                            entry['hxfeatures'][diagnosis] = []  # Changed from assessments
                        # Create a structured entry with historical feature and its hxfeature
                        entry['hxfeatures'][diagnosis].append({
                            'historical_feature': st.session_state.historical_features[i],
                            'hxfeature': hxfeature  # Changed from assessment
                        })
                
                session_data = collect_session_data()  # Collect session data

                # Upload to Firebase using the current diagnosis order
                upload_message = upload_to_firebase(db, document_id, entry)
                
                st.session_state.page = "Physical Examination Features"  # Change to the Simple Success page
                st.success("Historical features submitted successfully.")
                st.rerun()  # Rerun to update the app


