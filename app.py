import streamlit as st
from transformers import pipeline
import pytesseract 
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Initialize summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Set up Tesseract OCR path (update if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# App title
st.set_page_config(page_title="Smart Notes", layout="centered")
st.title("🧠 SMART NOTES")
st.write("Summarize text, YouTube videos, or extract notes from images.")

# Input options
option = st.radio("Select Input Type:", ["Text", "YouTube Link", "Image"])

# Summarize text
def summarize_text(text):
    if len(text.split()) < 30:
        st.warning("Please enter at least 30 words for better summarization.")
        return None
    return summarizer(text, max_length=150, min_length=40, do_sample=False)[0]['summary_text']

# Extract text from image
def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file)
    return pytesseract.image_to_string(image)

# Extract video ID
def extract_video_id(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['youtu.be']:
            return parsed_url.path[1:]
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            if parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            if parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
        return None
    except Exception:
        return None

# Summarize YouTube video
def summarize_youtube_link(url):
    video_id = extract_video_id(url)
    if not video_id:
        st.error("Invalid YouTube link.")
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([t['text'] for t in transcript])
        return summarizer(full_text, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

# Main logic
summary = None
if option == "Text":
    text_input = st.text_area("Enter the text to summarize:")
    if st.button("Summarize Text"):
        with st.spinner("Summarizing..."):
            summary = summarize_text(text_input)

elif option == "YouTube Link":
    link = st.text_input("Enter YouTube video link:")
    if st.button("Summarize Video"):
        with st.spinner("Fetching and summarizing transcript..."):
            summary = summarize_youtube_link(link)

elif option == "Image":
    uploaded_file = st.file_uploader("Upload an image with text", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        with st.spinner("Extracting text from image..."):
            extracted_text = extract_text_from_image(uploaded_file)
            st.subheader("Extracted Text:")
            st.write(extracted_text)
            summary = summarize_text(extracted_text)

# Display summary
if summary:
    st.subheader("📝 Summary:")
    st.write(summary)