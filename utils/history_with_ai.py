import streamlit as st
import json
import openai
from docx import Document
import time
import random
from utils.session_management import collect_session_data
from utils.firebase_operations import upload_to_firebase  

def read_croup_doc():
    doc = Document("croup.docx")
    croup_info = {}
    for para in doc.paragraphs:
        if ':' in para.text:
            question, answer = para.text.split(':', 1)
            croup_info[question.strip().lower()] = answer.strip().lower()
    return croup_info

# Load the document content
croup_info = read_croup_doc()

def get_chatgpt_response(user_input):
    user_input_lower = user_input.lower()
    
    alternative_responses = [
        "I'm not sure about that.",
        "I don't have that information.",
        "That's a good question, but I don't know.",
        "I'm not certain.",
    ]

    if user_input_lower in croup_info:
        answer = croup_info[user_input_lower]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": f"The answer is: {answer}"}
            ]
        )
        return response['choices'][0]['message']['content']
    else:
        return random.choice(alternative_responses)

def run_virtual_patient(db,document_id):
    st.title("Virtual Patient")

    st.info(
        "You will have the opportunity to perform a history and ask for important physical examination details. "
        "You will be limited to 15 minutes. Alternatively, you may end the session and move to the next page."
    )

    if 'start_time' not in st.session_state or st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    if 'session_data' not in st.session_state:
        st.session_state.session_data = {
            'questions_asked': [],
            'responses': []
        }

    elapsed_time = (time.time() - st.session_state.start_time) / 60

    if elapsed_time < 15:
        with st.form("question_form"):
            user_input = st.text_input("Ask the virtual patient typical history questions you would want to know for this case:")
            submit_button = st.form_submit_button("Ask")

            if submit_button and user_input:
                st.session_state.session_data['questions_asked'].append(user_input)

                virtual_patient_response = get_chatgpt_response(user_input)
                st.session_state.session_data['responses'].append(virtual_patient_response)

                st.write(f"Virtual Patient: {virtual_patient_response}")

                with st.sidebar:
                    st.header("Questions and Responses")
                    for question, response in zip(st.session_state.session_data['questions_asked'], st.session_state.session_data['responses']):
                        st.write(f"**Q:** {question}")
                        st.write(f"**A:** {response}")

                # Collect session data and prepare for upload to Firebase
                entry = collect_session_data()  # Collect session data
                entry['questions_asked'] = st.session_state.session_data['questions_asked']
                entry['responses'] = st.session_state.session_data['responses']  # Include responses

                # Upload to Firebase
                try:
                    #upload_message = upload_to_firebase(db, 'your_collection_name', document_id, entry)  # Provide a document ID
                    upload_message = upload_to_firebase(db, document_id, entry)
                    st.success("Your questions have been saved successfully.")
                except Exception as e:
                    st.error(f"Error uploading data: {e}")

    else:
        st.warning("Session time is up. Please end the session.")

    if st.button("End History Taking Session",key="end_session_button"):
        entry = collect_session_data()  # Collect session data
        entry['questions_asked'] = st.session_state.session_data['questions_asked']
        entry['responses'] = st.session_state.session_data['responses']
        
        # Upload to Firebase
        try:
            #upload_message = upload_to_firebase(db, 'your_collection_name', document_id, entry)  # Provide a document ID
            upload_message = upload_to_firebase(db, document_id, entry)
            st.success("Your questions have been saved successfully.")
        except Exception as e:
            st.error(f"Error uploading data: {e}")

        st.session_state.start_time = None
        st.session_state.page = "Focused Physical Examination"
        st.write("Session ended. You can start a new session.")
        st.rerun()
