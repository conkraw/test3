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

def load_historical_features(db, document_id):
    """Load existing historical features from Firebase."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data = db.collection(collection_name).document(document_id).get()
    if user_data.exists:
        hxfeatures = user_data.to_dict().get('hxfeatures', {})
        # Initialize historical_features with empty strings if not found
        historical_features = [""] * 5
        for diagnosis in hxfeatures:
            for feature in hxfeatures[diagnosis]:
                index = hxfeatures[diagnosis].index(feature)
                if index < len(historical_features):
                    historical_features[index] = feature['historical_feature']
        return historical_features
    else:
        return [""] * 5  # Default to empty if no data

def main(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "historical_features"
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'diagnoses_s2' not in st.session_state:  
        st.session_state.diagnoses_s2 = [""] * 5  
    if 'historical_features' not in st.session_state:
        st.session_state.historical_features = load_historical_features(db, document_id)  # Load from Firebase
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
                # Populate text input with existing value from session state
                st.session_state.historical_features[i] = st.text_input(
                    f"",
                    value=st.session_state.historical_features[i],  # Load existing value
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
            if not any(st.session_state.historical_features):
                st.error("Please enter at least one historical feature.")
            else:
                entry = {
                    'hxfeatures': {},
                    'diagnoses_s2': st.session_state.diagnoses_s2
                }

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

                # Upload to Firebase
                upload_message = upload_to_firebase(db, document_id, entry)
                
                st.session_state.page = "Physical Examination Features"
                st.success("Historical features submitted successfully.")
                st.rerun()


