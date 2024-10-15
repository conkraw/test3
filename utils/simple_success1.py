import streamlit as st

def display_simple_success1():
    st.title("Thank You for Your Participation!")
    st.markdown("""
    Your assessment is complete. We appreciate the time and effort you've taken to provide your responses. 

    Thank you once again for your contribution!
    """)

# Call the function where appropriate in your app
if st.button("Submit"):

    st.success("Your submission was successful!")
    st.markdown("You can now close this window or navigate away. Thank you!")


if __name__ == '__main__':
    main()

