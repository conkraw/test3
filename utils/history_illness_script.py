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

def load_historical_features_from_firebase(db, document_id):
    """Load historical features from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    if user_data.exists:
        hx_data = user_data.to_dict().get('hxfeatures', {})
        for diagnosis, features in hx_data.items():
            if diagnosis in st.session_state.diagnoses:
                idx = st.session_state.diagnoses.index(diagnosis)
                # Ensure historical features list is initialized
                while len(st.session_state.historical_features) <= idx:
                    st.session_state.historical_features.append([])
                # Populate the historical features for the diagnosis
                st.session_state.historical_features[idx] = [feature['historical_feature'] for feature in features]

def main(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "historical_features"  # Start on historical features page
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'diagnoses_s2' not in st.session_state:  # Initialize diagnoses_s2
        st.session_state.diagnoses_s2 = [""] * 5  
    if 'historical_features' not in st.session_state:
        st.session_state.historical_features = [[] for _ in range(5)]  # Initialize as lists for each diagnosis
    if 'selected_buttons' not in st.session_state:
        st.session_state.selected_buttons = [False] * 5  
    if 'selected_moving_diagnosis' not in st.session_state:
        st.session_state.selected_moving_diagnosis = ""  
    
    # Load diagnoses from file
    dx_options = read_diagnoses_from_file()
    dx_options.insert(0, "")  

    # Load historical features from Firebase
    load_historical_features_from_firebase(db, document_id)

    # Title of the app
    st.title("Historical Features App")

    # Historical Features Page
    if st.session_state.current_page == "historical_features":
        st.markdown("""
            ### HISTORICAL FEATURES
            Please provide up to 5 historical features that influence the differential diagnosis.
        """)

        # Display historical features
        cols = st.columns(len(st.session_state.diagnoses) + 1)
        with cols[0]:
            st.markdown("Historical Features")

        for i in range(5):
            cols = st.columns(len(st.session_state.diagnoses) + 1)
            with cols[0]:
                historical_feature_value = (
                    st.session_state.historical_features[i][0] 
                    if i < len(st.session_state.historical_features) and st.session_state.historical_features[i] 
                    else ""
                )
                st.session_state.historical_features[i] = st.text_input(
                    f"Historical Feature {i + 1}", 
                    value=historical_feature_value,
                    key=f"hist_row_{i}", 
                    label_visibility="collapsed"
                )

            for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
                with col:
                    st.selectbox(
                        "hxfeatures for " + diagnosis,
                        options=["", "Supports", "Does not support"],
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
                hxfeatures = {}  # Changed from assessments
                for i in range(5):
                    for diagnosis in st.session_state.diagnoses:
                        hxfeature = st.session_state[f"select_{i}_{diagnosis}_hist"]  # Changed from assessment
                        if diagnosis not in entry['hxfeatures']:  # Changed from assessments
                            entry['hxfeatures'][diagnosis] = []  # Changed from assessments
                        # Create a structured entry with historical feature and its hxfeature
                        entry['hxfeatures'][diagnosis].append({  # Changed from assessments
                            'historical_feature': st.session_state.historical_features[i],
                            'hxfeature': hxfeature  # Changed from assessment
                        })
                
                session_data = collect_session_data()  # Collect session data

                # Upload to Firebase using the current diagnosis order
                upload_message = upload_to_firebase(db, document_id, entry)
                
                st.session_state.page = "Physical Examination Features"  # Change to the next page
                st.success("Historical features submitted successfully.")
                st.rerun()  # Rerun to update the app

