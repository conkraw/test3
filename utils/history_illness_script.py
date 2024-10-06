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
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]  # Get collection name from secrets
    user_data = db.collection(collection_name).document(document_id).get()
    
    if user_data.exists:
        data = user_data.to_dict()
        diagnoses = []
        historical_features = {}

        if "hxfeatures" in data:
            hxfeatures = data["hxfeatures"]
            for diagnosis, features in hxfeatures.items():
                diagnoses.append(diagnosis)
                historical_features[diagnosis] = features  # Assuming features is a dict with historical_feature and hxfeature

        return diagnoses, historical_features
    return [], {}

def main(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "historical_features"  # Start on historical features page
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'historical_features' not in st.session_state:
        st.session_state.historical_features = {}  # Initialize as a dictionary

    # Load diagnoses from file
    dx_options = read_diagnoses_from_file()
    dx_options.insert(0, "")  

    # Load existing data from Firebase
    if not st.session_state.diagnoses or not st.session_state.historical_features:
        st.session_state.diagnoses, loaded_historical_features = load_existing_data(db, document_id)
        st.session_state.historical_features.update(loaded_historical_features)

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

                # Text input for historical feature
                historical_feature = st.text_input(
                    f"Historical feature for {diagnosis}",
                    value=st.session_state.historical_features.get(diagnosis, {}).get("historical_feature", ""),
                    key=f"hist_row_{diagnosis}"
                )

                # Dropdown for hxfeature
                hxfeature_options = ["", "Supports", "Does not support"]
                hxfeature = st.selectbox(
                    f"Hxfeature for {diagnosis}",
                    options=hxfeature_options,
                    index=hxfeature_options.index(st.session_state.historical_features.get(diagnosis, {}).get("hxfeature", "")) if diagnosis in st.session_state.historical_features else 0,
                    key=f"select_{diagnosis}_hxfeature"
                )

                # Store in session state
                st.session_state.historical_features[diagnosis] = {
                    "historical_feature": historical_feature,
                    "hxfeature": hxfeature
                }

        # Submit button for historical features
        if st.button("Submit", key="hx_features_submit_button"):
            entry = {
                'hxfeatures': st.session_state.historical_features,
                'diagnoses_s2': st.session_state.diagnoses
            }

            # Upload to Firebase
            upload_message = upload_to_firebase(db, document_id, entry)
            st.success("Historical features submitted successfully.")
            st.session_state.current_page = "Next Page"  # Adjust as needed
            st.rerun()  # Rerun to update the app




