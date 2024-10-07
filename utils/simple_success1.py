import streamlit as st

def display_simple_success1():
    st.title("User Results Summary")

    # Input for unique code
    unique_code = st.text_input("Enter User Unique Code:")
    
    if st.button("Fetch Results"):
        if unique_code:
            user_data = fetch_user_data(unique_code)
            if user_data:
                st.subheader("User Information")
                st.write(f"**User Name:** {user_data['user_name']}")
                st.write(f"**Unique Code:** {user_data['unique_code']}")
                st.write(f"**Last Page Visited:** {user_data['last_page']}")

                st.subheader("Diagnoses")
                st.write("### Diagnoses S1")
                for diagnosis in user_data["diagnoses_s1"]:
                    st.write(f"- {diagnosis}")

                st.write("### Diagnoses S2")
                for diagnosis in user_data["diagnoses_s2"]:
                    st.write(f"- {diagnosis}")

                st.write("### Diagnoses S3")
                for diagnosis in user_data["diagnoses_s3"]:
                    st.write(f"- {diagnosis}")

                st.write("### Diagnoses S4")
                for diagnosis in user_data["diagnoses_s4"]:
                    st.write(f"- {diagnosis}")

                st.write("### Diagnoses S5")
                for diagnosis in user_data["diagnoses_s5"]:
                    st.write(f"- {diagnosis}")

                st.write("### Diagnoses S6")
                for diagnosis in user_data["diagnoses_s6"]:
                    st.write(f"- {diagnosis}")

                st.write("### Diagnoses S7")
                for diagnosis in user_data["diagnoses_s7"]:
                    st.write(f"- {diagnosis}")

                st.subheader("Interventions")
                for intervention in user_data["interventions"]:
                    st.write(f"- {intervention}")

                st.subheader("Confirmed Exams")
                st.write(", ".join(user_data["confirmed_exams"]) if user_data["confirmed_exams"] else "None provided")

                st.subheader("Vital Signs Data")
                for key, value in user_data["vs_data"].items():
                    st.write(f"- **{key.capitalize()}:** {value}")

                st.subheader("Excluded Exams")
                st.write(", ".join(user_data["excluded_exams"]) if user_data["excluded_exams"] else "None provided")

                st.subheader("Responses")
                st.write(", ".join(user_data["responses"]) if user_data["responses"] else "None provided")

                st.subheader("Historical Features")
                st.write(", ".join(user_data["hxfeatures"]) if user_data["hxfeatures"] else "None provided")

                st.subheader("Questions Asked")
                st.write(", ".join(user_data["questions_asked"]) if user_data["questions_asked"] else "None provided")

                st.subheader("Physical Examination Features")
                st.write(", ".join(user_data["pefeatures"]) if user_data["pefeatures"] else "None provided")

                st.subheader("Radiological Tests")
                st.write(", ".join(user_data["radiological_tests"]) if user_data["radiological_tests"] else "None provided")

                st.subheader("Other Tests")
                st.write(", ".join(user_data["other_tests"]) if user_data["other_tests"] else "None provided")
            else:
                st.error("No data found for the provided unique code.")
        else:
            st.error("Please enter a unique code.")

if __name__ == '__main__':
    main()


