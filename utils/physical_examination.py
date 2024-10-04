import streamlit as st
import os

# Load physical examination text from a file
def load_phys_exam_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File not found: {file_path}. Please check the file path.")
        return ""

# Function to display selected examination component text
def display_selected_component(selected_component):
    if selected_component:
        text = load_phys_exam_data("phys_exam.txt")
        
        if text:
            component_texts = text.split('\n\n')  # Assuming sections are separated by double newlines
            for component_text in component_texts:
                if selected_component.lower() in component_text.lower():
                    # Extract text after the first colon
                    content = component_text.split(':', 1)[-1].strip()
                    st.markdown(content)  # Display only the content, not the title
                    break
        else:
            st.write("No text available for the selected component.")

# Function to check and display an image if present
def display_image(base_image_name):
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.PNG', '.JPG', '.JPEG', '.GIF', '.BMP', '.TIFF']
    image_found = False

    for ext in image_extensions:
        image_path = f"{base_image_name}{ext}"
        if os.path.isfile(image_path):
            st.image(image_path, caption="Image interpretation required.", use_column_width=True)
            image_found = True
            break  # Exit loop if an image is found

    if not image_found:
        st.write("No images are available.")

# Function to check and display audio if present
def display_audio(base_audio_name):
    audio_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.MP3', '.WAV', '.OGG', '.FLAC']
    audio_found = False

    for ext in audio_extensions:
        audio_path = f"{base_audio_name}{ext}"
        if os.path.isfile(audio_path):
            st.audio(audio_path)
            audio_found = True
            break  # Exit loop if an audio file is found

    if not audio_found:
        st.write("No audio is available.")

# Function to check and display video if present
def display_video(base_video_name):
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.MP4', '.MOV', '.AVI', '.MKV']
    video_found = False

    for ext in video_extensions:
        video_path = f"{base_video_name}{ext}"
        if os.path.isfile(video_path):
            st.video(video_path)
            video_found = True
            break  # Exit loop if a video file is found

    if not video_found:
        st.write("No video is available.")

# Main Streamlit app function
def main():
    st.title("Physical Examination Components")

    st.markdown("""
    Please select and review the physical examination components to help develop your differential diagnosis.
    Please note that any image provided requires interpretation.
    """)

    # List of examination components
    components = [
        "","General Appearance", "Eyes", "Ears, Neck, Nose, Throat", "Lymph Nodes",
        "Cardiovascular", "Lungs", "Abdomen", "Skin", "Extremities",
        "Musculoskeletal", "Neurological", "Psychiatry", "Genitourinary", "Image", "Audio", "Video"
    ]

    # User selection
    selected_component = st.selectbox("Select a physical examination component:", components)

    # Display selected component text
    display_selected_component(selected_component)

    # Check for media files based on selected component
    if selected_component == "Image":
        display_image("image_1")  # Check for various formats of image_1
    elif selected_component == "Audio":
        display_audio("audio_1")  # Check for various formats of audio_1
    elif selected_component == "Video":
        display_video("video_1")  # Check for various formats of video_1

    # Add a submit button to go to the next page
    if st.button("Next",key="pe_submit_button"):
        st.session_state.page = "History Illness Script"  # Change to your actual next page
        st.rerun()  # Rerun the app to reflect the changes

if __name__ == '__main__':
    main()

