import streamlit as st
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase  # Assuming this function exists

# Function to read diagnoses from a file
def read_diagnoses_from_file():
    try:
        with open('dx_list.txt', 'r') as file:
            diagnoses = [line.strip() for line in file.readlines() if line.strip()]
        return diagnoses
    except Exception as e:
        st.error(f"Error reading dx_list.txt: {e}")
        return []

# Function to load data from Firebase
def load_data_from_firebase(db, document_id):
    # Initialize the diagnoses session state if not present
    if 'diagnoses_s2' not in st.session_state:
        # Load existing diagnoses and historical features from Firebase
        collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
        user_data = db.collection(collection_name).document(document_id).get()
        
        if user_data.exists:
            data = user_data.to_dict()
            st.session_state.diagnoses_s2 = data.get('diagnoses_s2', [""] * 5)
            hxfeatures = data.get('hxfeatures', {})  # Get the hxfeatures section
            
            # Initialize historical features based on fetched hxfeatures
            st.session_state.historical_features = []
            for diagnosis in st.session_state.diagnoses_s2:
                if diagnosis in hxfeatures:
                    historical_info = hxfeatures[diagnosis]
                    st.session_state.historical_features.append({
                        'historical_feature': historical_info.get('historical_feature', ""),
                        'hxfeature': historical_info.get('hxfeature', "")
                    })
                else:
                    st.session_state.historical_features.append({
                        'historical_feature': "",
                        'hxfeature': ""
                    })
        else:
            st.session_state.diagnoses_s2 = [""] * 5  # Default to empty if no data
            st.session_state.historical_features = [{"historical_feature": "", "hxfeature": ""} for _ in range(5)]

def main(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "historical_features"
        
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'historical_features' not in st.session_state:
        st.session_state.historical_features = [{"historical_feature": "", "hxfeature": ""} for _ in range(5)]
    if 'selected_buttons' not in st.session_state:
        st.session_state.selected_buttons = [False] * 5  
    if 'selected_moving_diagnosis' not in st.session_state:
        st.session_state.selected_moving_diagnosis = ""

    # Load diagnoses from file
    dx_options = read_diagnoses_from_file()
    dx_options.insert(0, "")

    # Load data from Firebase
    load_data_from_firebase(db, document_id)

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

        # Ensure diagnoses_s2 is always updated to the current state of diagnoses
        st.session_state.diagnoses_s2 = [dx for dx in st.session_state.diagnoses if dx]  # Update diagnoses_s2

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
                historical_feature_value = st.text_input(
                    f"", 
                    value=st.session_state.historical_features[i]['historical_feature'] if isinstance(st.session_state.historical_features[i], dict) else "", 
                    key=f"hist_row_{i}", 
                    label_visibility="collapsed"
                )
                # Update the historical feature in session state
                st.session_state.historical_features[i]['historical_feature'] = historical_feature_value

            for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
                with col:
                    hxfeature_index = ["", "Supports", "Does not support"].index(
                        st.session_state.historical_features[i]['hxfeature'] if isinstance(st.session_state.historical_features[i], dict) else ""
                    )
                    hxfeature = st.selectbox(
                        "hxfeatures for " + diagnosis,
                        options=["", "Supports", "Does not support"],
                        index=hxfeature_index,
                        key=f"select_{i}_{diagnosis}_hist",
                        label_visibility="collapsed"
                    )
                    # Update hxfeature in session state
                    st.session_state.historical_features[i]['hxfeature'] = hxfeature

        # Submit button for historical features
        if st.button("Submit", key="hx_features_submit_button"):
            if not any(feature['historical_feature'] for feature in st.session_state.historical_features):
                st.error("Please enter at least one historical feature.")
            else:
                entry = {
                    'hxfeatures': {},  # Updated key to match Firebase structure
                    'diagnoses_s2': st.session_state.diagnoses_s2  # Include the reordered diagnoses here
                }

                for i in range(5):
                    diagnosis = st.session_state.diagnoses[i]
                    if diagnosis:
                        hxfeature = st.session_state.historical_features[i]['hxfeature']
                        historical_feature = st.session_state.historical_features[i]['historical_feature']
                        entry['hxfeatures'][diagnosis] = {
                            'historical_feature': historical_feature,
                            'hxfeature': hxfeature
                        }
                
                session_data = collect_session_data()  # Collect session data

                # Upload to Firebase using the current diagnosis order
                upload_message = upload_to_firebase(db, document_id, entry)
                
                st.session_state.page = "Physical Examination Features"  # Change to the Simple Success page
                st.success("Historical features submitted successfully.")
                st.rerun()  # Rerun to update the app

# Run the app
if __name__ == "__main__":
    main(db, st.session_state.document_id)

