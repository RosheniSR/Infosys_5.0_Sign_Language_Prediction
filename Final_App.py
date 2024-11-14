import streamlit as st
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import tempfile
import os
from googletrans import Translator

# Dictionary mapping class indices to words
CLASS_LABELS = {
    0: "a", 1: "a lot", 2: "abdomen", 3: "able", 4: "about", 5: "above", 6: "accent", 7: "accept", 8: "accident",
    9: "accomplish", 10: "accountant", 11: "across", 12: "act", 13: "action", 14: "active", 15: "activity", 
    16: "actor", 17: "adapt", 18: "add", 19: "address", 20: "adjective", 21: "adjust", 22: "admire", 23: "admit",
    24: "adopt", 25: "adult", 26: "advanced", 27: "advantage", 28: "adverb", 29: "affect", 30: "afraid", 
    31: "africa", 32: "after", 33: "afternoon", 34: "again", 35: "against", 36: "age", 37: "agenda", 38: "ago",
    39: "agree", 40: "agreement", 41: "ahead", 42: "aid", 43: "aim", 44: "airplane", 45: "alarm", 46: "alcohol",
    47: "algebra", 48: "all", 49: "all day", 50: "allergy"
}

# Dictionary of supported languages
LANGUAGES = {
    'English': 'en',
    'Hindi': 'hi',
    'Bengali': 'bn',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Chinese (Simplified)': 'zh-cn',
    'Russian': 'ru',
    'Arabic': 'ar'
}

def set_background_image(image_url, text_color="#FFFFFF", font_size="18px"):
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-image: url("{image_url}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: {text_color};
                font-family: 'Arial', sans-serif;
                font-size: {font_size};
            }}
            h1, h2, h3 {{
                color: {text_color};
            }}
            .button {{
                background-color: #007BFF;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                cursor: pointer;
                transition: background-color 0.3s;
            }}
            .button:hover {{
                background-color: #0056b3;
            }}
            .file-upload {{
                border: 2px dashed #007BFF;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .translation-box {{
                background-color: rgba(255, 255, 255, 0.9);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border: 2px solid #007BFF;
            }}
        </style>
        """, unsafe_allow_html=True)

@st.cache_resource
def load_sign_language_model():
    model_path = r"C:\Users\roshe\Documents\PROJECTS\Sign Language\model_metrics\sign_language_cnn_model_50_classes.h5"
    model = load_model(model_path)
    return model

def translate_text(text, target_lang):
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_lang)
        return translation.text
    except Exception as e:
        return f"Translation error: {str(e)}"

def predict_sign_language(video_path, model):
    cap = cv2.VideoCapture(video_path)
    predictions = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % 10 == 0:
            frame = cv2.resize(frame, (255, 255))
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = gray_frame.reshape(1, 255, 255, 1)
            gray_frame = gray_frame / 255.0

            prediction = model.predict(gray_frame)
            predicted_class = np.argmax(prediction, axis=1)[0]
            predictions.append(predicted_class)
        frame_count += 1

    cap.release()
    
    final_prediction = max(set(predictions), key=predictions.count)
    return CLASS_LABELS.get(final_prediction, "Unknown")

def login():
    set_background_image("https://marketplace.canva.com/EAFCO6pfthY/1/0/1600w/canva-blue-green-watercolor-linktree-background-F2CyNS5sQdM.jpg", text_color="#2B63A9")
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "Rose" and password == "rose":
            st.success("Logged in successfully!", icon="✅")
            return True
        else:
            st.error("Incorrect username or password. Please try again.")
            return False

def sidebar_navigation():
    st.sidebar.title("Navigation")
    return st.sidebar.radio("Go to:", ["Welcome", "Sign Language Recognition", "About Us"])

def sign_language_recognition_page():
    set_background_image("https://marketplace.canva.com/EAFCO6pfthY/1/0/1600w/canva-blue-green-watercolor-linktree-background-F2CyNS5sQdM.jpg", text_color="#2B63A9", font_size="18px")
    st.title("Sign Language Recognition")
    st.write("Upload a video of sign language to get the recognized text and its translation.")
    
    st.subheader("Instructions:")
    st.write("""
        1. Ensure the video file is clear and only contains the signing gesture.
        2. Upload the video in MP4, AVI, or MOV format.
        3. Click the **Predict** button to get the recognition result.
        4. Select a language and click **Translate** to see the translation.
    """)
    
    uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "avi", "mov"])
    
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name

        st.video(video_path)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Predict"):
                model = load_sign_language_model()
                prediction = predict_sign_language(video_path, model)
                st.session_state.prediction = prediction  # Store prediction in session state
                st.markdown('<div class="translation-box">', unsafe_allow_html=True)
                st.write("Recognized Word:")
                st.subheader(prediction)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            selected_language = st.selectbox("Select Language for Translation", list(LANGUAGES.keys()))
            
            if st.button("Translate") and hasattr(st.session_state, 'prediction'):
                translated_text = translate_text(st.session_state.prediction, LANGUAGES[selected_language])
                st.markdown('<div class="translation-box">', unsafe_allow_html=True)
                st.write(f"Translation ({selected_language}):")
                st.subheader(translated_text)
                st.markdown('</div>', unsafe_allow_html=True)

        os.remove(video_path)

    st.markdown('<div class="footer">Developed by Rosheni</div>', unsafe_allow_html=True)

def welcome_page():
    set_background_image("https://marketplace.canva.com/EAFCO6pfthY/1/0/1600w/canva-blue-green-watercolor-linktree-background-F2CyNS5sQdM.jpg", text_color="#2B63A9", font_size="20px")
    st.title("Welcome to the Sign Language Recognition App")
    st.write("""
        This Sign Language Recognition App is dedicated to breaking communication barriers for individuals with hearing and speech impairments.
        Through this innovative application, users can upload videos of sign language, and our advanced machine learning algorithms 
        translate these signs into comprehensible text. We believe in creating a more accessible and inclusive society for everyone, 
        where communication is not hindered by physical limitations.

        The app is designed with user-friendly features and state-of-the-art technology to recognize gestures accurately. Our mission 
        is to provide a seamless, empowering experience, enabling people to express themselves and connect with others effortlessly.
        
        Whether you're a family member, a friend, or an educator, this app can help bridge the gap and foster deeper understanding and 
        stronger relationships.
    """)
    st.markdown('<div class="footer">Developed by Rosheni</div>', unsafe_allow_html=True)

def about_us_page():
    set_background_image("https://marketplace.canva.com/EAFCO6pfthY/1/0/1600w/canva-blue-green-watercolor-linktree-background-F2CyNS5sQdM.jpg", text_color="#2B63A9", font_size="20px")
    st.title("About Us")
    st.write("""
        This Sign Language Recognition App is a groundbreaking tool aimed at promoting inclusivity and accessibility in communication.
        People with hearing or speech impairments face significant communication challenges, especially with those who are unfamiliar 
        with sign language. Our app bridges this communication gap by using cutting-edge technology to interpret sign language gestures 
        and convert them into readable text.

        **Our Vision:**  
        We envision a world where everyone, regardless of physical ability, can communicate freely and effectively. We are committed 
        to fostering an inclusive society by empowering individuals and making essential communication tools available to all.

        **Our Mission:**  
        To develop intuitive, high-quality solutions that make everyday interactions easier for individuals with communication challenges. 
        By harnessing the power of machine learning, our app recognizes the nuances of sign language and delivers accurate text interpretations.

        **Conclusion:**  
        The Sign Language Recognition App is designed to empower people with hearing or speech impairments, enabling seamless communication 
        with those unfamiliar with sign language. This app represents a step towards a more inclusive society, where everyone has a voice, 
        irrespective of any physical limitations.
    """)
    st.markdown('<div class="footer">Developed by Rosheni</div>', unsafe_allow_html=True)

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.session_state.logged_in = login()
    else:
        selected_page = sidebar_navigation()
        if selected_page == "Welcome":
            welcome_page()
        elif selected_page == "Sign Language Recognition":
            sign_language_recognition_page()
        elif selected_page == "About Us":
            about_us_page()

if __name__ == "__main__":
    main()