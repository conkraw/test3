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

def load_data_from_firebase(db, document_id):
    if 'diagnoses_s2' not in st.session_state:
        collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
        user_data = db.collection(collection_name).document(document_id).get()
        
        if user_data.exists:
            data = user_data.to_dict()
            st.session_state.diagnoses_s2 = data.get('diagnoses_s2', [""] * 5)
            hxfeatures = data.get('hxfeatures', {})

            # Initialize historical features correctly
            st.session_state.historical_features = []
            for diagnosis in st.session_state.diagnoses_s2:
                historical_info = hxfeatures.get(diagnosis, {})
                st.session_state.historical_features.append({
                    'historical_feature': historical_info.get('historical_feature', ""),
                    'hxfeature': historical_info.get('hxfeature', "")
                })
        else:
            st.session_state.diagnoses_s2 = [""] * 5
            st.session_state.historical_features = [{"historical_feature": "", "hxfeature": ""} for _ in range(5)]

def main(db, document_id):
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "historical_features"
    if 'diagnoses' not in st.session_state:
        st.session_state.diagnoses = [""] * 5
    if 'historical_features' not in st.session_state:
        st.session_state.historical_features = [{"historical_feature": "", "hxfeature": ""} for _ in range(5)]

    # Load diagnoses from file
    dx_options = read_diagnoses_from_file()
    dx_options.insert(0, "")

    # Load data from Firebase
    load_data_from_firebase(db, document_id)

    # Debugging: Print the current state of historical_features
    st.write("Current historical features:", st.session_state.historical_features)

    # Title of the app
    st.title("Historical Features App")

    # Historical Features Page
    if st.session_state.current_page == "historical_features":
        st.markdown("### HISTORICAL FEATURES\nPlease provide up to 5 historical features that influence the differential diagnosis.")

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
                    value=st.session_state.historical_features[i]['historical_feature'], 
                    key=f"hist_row_{i}", 
                    label_visibility="collapsed"
                )
                st.session_state.historical_features[i]['historical_feature'] = historical_feature_value

            for diagnosis, col in zip(st.session_state.diagnoses, cols[1:]):
                with col:
                    hxfeature_index = ["", "Supports", "Does not support"].index(
                        st.session_state.historical_features[i]['hxfeature']
                    )
                    hxfeature = st.selectbox(
                        "hxfeatures for " + diagnosis,
                        options=["", "Supports", "Does not support"],
                        index=hxfeature_index,
                        key=f"select_{i}_{diagnosis}_hist",
                        label_visibility="collapsed"
                    )
                    st.session_state.historical_features[i]['hxfeature'] = hxfeature

        # Submit button for historical features
        if st.button("Submit", key="hx_features_submit_button"):
            if not any(feature['historical_feature'] for feature in st.session_state.historical_features):
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
                            entry['hxfeatures'][diagnosis] = {}
                        entry['hxfeatures'][diagnosis] = {
                            'historical_feature': st.session_state.historical_features[i]['historical_feature'],
                            'hxfeature': hxfeature
                        }

                # Upload to Firebase
                upload_message = upload_to_firebase(db, document_id, entry)
                st.success("Historical features submitted successfully.")
                st.session_state.page = "Physical Examination Features"
                st.rerun()

# Uncomment and replace with actual Firebase initialization
# db = initialize_firebase()
# document_id = "your_document_id"
# main(db, document_id)
