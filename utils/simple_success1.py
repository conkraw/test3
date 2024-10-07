import streamlit as st
from firebase_admin import firestore

# Initialize Firestore (make sure to initialize Firebase app before this)
db = firestore.client()

def fetch_user_data(unique_code):
    """Fetch user data from Firestore based on unique code."""
    collection_name = st.secrets["FIREBASE_COLLECTION_NAME"]
    user_data_ref = db.collection(collection_name).document(unique_code)
    user_data = user_data_ref.get()
    
    if user_data.exists:
        return user_data.to_dict()
    return None

def display_simple_success1():
    st.title("User Results Summary")

    # Use the unique code from session state
    if 'unique_code' not in st.session_state:
        st.error("No unique code found in session state.")
        return

    unique_code = st.session_state.unique_code
    st.write(f"Fetching results for Unique Code: **{unique_code}**")

    user_data = fetch_user_data(unique_code)
    if user_data:
        st.subheader("User Information")
        st.write(f"**User Name:** {user_data.get('user_name', 'N/A')}")
        st.write(f"**Unique Code:** {user_data['unique_code']}")
        st.write(f"**Last Page Visited:** {user_data.get('last_page', 'N/A')}")

        st.subheader("Diagnoses")
        for key in ['diagnoses_s1', 'diagnoses_s2', 'diagnoses_s3', 'diagnoses_s4', 'diagnoses_s5', 'diagnoses_s6', 'diagnoses_s7']:
            st.write(f"### {key.replace('_', ' ').capitalize()}")
            diagnoses = user_data.get(key, [])
            for diagnosis in diagnoses:
                st.write(f"- {diagnosis}")

        st.subheader("Interventions")
        interventions = user_data.get("interventions", [])
        for intervention in interventions:
            st.write(f"- {intervention}")

        st.subheader("Confirmed Exams")
        st.write(", ".join(user_data.get("confirmed_exams", [])) or "None provided")

        st.subheader("Vital Signs Data")
        vs_data = user_data.get("vs_data", {})
        for key, value in vs_data.items():
            st.write(f"- **{key.capitalize()}:** {value}")

        st.subheader("Excluded Exams")
        st.write(", ".join(user_data.get("excluded_exams", [])) or "None provided")

        st.subheader("Responses")
        st.write(", ".join(user_data.get("responses", [])) or "None provided")

        st.subheader("Historical Features")
        st.write(", ".join(user_data.get("hxfeatures", [])) or "None provided")

        st.subheader("Questions Asked")
        st.write(", ".join(user_data.get("questions_asked", [])) or "None provided")

        st.subheader("Physical Examination Features")
        st.write(", ".join(user_data.get("pefeatures", [])) or "None provided")

        st.subheader("Radiological Tests")
        st.write(", ".join(user_data.get("radiological_tests", [])) or "None provided")

        st.subheader("Other Tests")
        st.write(", ".join(user_data.get("other_tests", [])) or "None provided")
    else:
        st.error("No data found for the unique code.")

if __name__ == '__main__':
    main()

