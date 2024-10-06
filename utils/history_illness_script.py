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

def load_existing_data(db, document_id):
    """Load existing diagnoses and historical features from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    
    if user_data.exists:
        data = user_data.to_dict()
        diagnoses_s2 = data.get("diagnoses_s2", [""] * 5)
        hxfeatures = data.get("hxfeatures", {})
        return diagnoses_s2, hxfeatures
    return [""] * 5, {}  # Default values if no data

def main(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "historical_features"
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'diagnoses_s2' not in st.session_state or 'hxfeatures' not in st.session_state:
        st.session_state.diagnoses_s2, st.session_state.historical_features = load_existing_data(db, document_id)  
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
        st.markdown("""### HISTORICAL FEATURES
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
                st.session_state.diagnoses_s2 = [dx for dx in st.session_state.diagnoses if dx]

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
                            st.session_state.diagnoses_s2 = [dx for dx in st.session_state.diagnoses if dx]
                            st.rerun()  

        # Ensure diagnoses_s2 is always updated to the current state of diagnoses
        st.session_state.diagnoses_s2 = [dx for dx in st.session_state.diagnoses if dx]  

        # Display historical features and dropdowns
        for i in range(5):
            cols = st.columns(len(st.session_state.diagnoses) + 1)
            with cols[0]:
                historical_feature_value = st.session_state.historical_features.get(st.session_state.diagnoses[i], [{}])[0].get('historical_feature', '')
                st.session_state.historical_features[i] = st.text_input(f"Feature {i + 1}:", key=f"hist_row_{i}", label_visibility="collapsed", value=historical_feature_value)

            for j, diagnosis in enumerate(st.session_state.diagnoses):
                if diagnosis:  # Only create dropdowns for non-empty diagnoses
                    hxfeature_key = f"select_{i}_{diagnosis}_hist"

                    # Ensure hxfeatures for this diagnosis exists
                    existing_hxfeatures = st.session_state.historical_features.get(diagnosis, [])
                    
                    hxfeature_options = ["", "Supports", "Does not support"]
                    selected_hxfeature = ""
                    for hx in existing_hxfeatures:
                        if hx.get('historical_feature', '') == historical_feature_value:
                            selected_hxfeature = hx.get('hxfeature', "")
                            break
                    
                    index = hxfeature_options.index(selected_hxfeature) if selected_hxfeature in hxfeature_options else 0

                    st.selectbox(
                        f"Hxfeatures for {diagnosis}",
                        options=hxfeature_options,
                        key=hxfeature_key,
                        label_visibility="collapsed",
                        index=index
                    )

        # Submit button for historical features
        if st.button("Submit", key="hx_features_submit_button"):
            if not any(st.session_state.historical_features):  
                st.error("Please enter at least one historical feature.")
            else:
                entry = {
                    'hxfeatures': {},
                    'diagnoses_s2': st.session_state.diagnoses_s2  
                }

                hxfeatures = {}
                for i in range(5):
                    for diagnosis in st.session_state.diagnoses:
                        hxfeature = st.session_state[f"select_{i}_{diagnosis}_hist"]
                        if diagnosis not in entry['hxfeatures']:
                            entry['hxfeatures'][diagnosis] = []  
                        entry['hxfeatures'][diagnosis].append({
                            'historical_feature': st.session_state.historical_features[i],
                            'hxfeature': hxfeature  
                        })
                
                session_data = collect_session_data()  

                # Upload to Firebase using the current diagnosis order
                upload_message = upload_to_firebase(db, document_id, entry)
                
                st.session_state.page = "Physical Examination Features"  
                st.success("Historical features submitted successfully.")
                st.rerun()  






