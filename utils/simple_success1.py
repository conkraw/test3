import streamlit as st

def display_simple_success1():
    st.title("Thank You for Your Participation!")
    st.markdown("""
    Your assessment is complete. We appreciate the time and effort you've taken to provide your responses. 

    Thank you once again for your contribution!
    """)

def main():
    display_simple_success1()  # Display the main message

    # Place the Submit button at the bottom
    if st.button("Submit"):
        st.success("Your submission was successful!")
        st.markdown("You can now close this window or navigate away. Thank you!")

if __name__ == '__main__':
    main()

