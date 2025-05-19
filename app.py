import streamlit as st
import openai
import pyttsx3
import base64
from io import BytesIO

# Optional: Untuk PDF parsing
from PyPDF2 import PdfReader

# Load API Key dari Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Setup tampilan halaman
st.set_page_config(page_title="🤖 AI Chatbot", page_icon="💬")
st.title("🤖 Chatbot AI Cerdas dengan Upload File + Suara")

# Inisialisasi sesi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tombol Reset Chat
with st.sidebar:
    st.header("⚙️ Opsi")
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

# Upload File
file_text = ""
uploaded_file = st.file_uploader("📎 Upload file (txt/pdf)", type=["txt", "pdf"])
if uploaded_file:
    if uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        file_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    st.success("✅ File berhasil dibaca!")

# Tampilkan riwayat chat
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    with st.chat_message(msg["role"]):
        bubble_color = "#DCF8C6" if is_user else "#F1F0F0"
        align = "right" if is_user else "left"
        st.markdown(
            f"<div style='text-align: {align}; background-color: {bubble_color}; padding: 10px; border-radius: 10px; margin: 5px 0;'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# Input Pengguna
if prompt := st.chat_input("Ketik sesuatu..."):

    # Tambahkan konteks file jika ada
    if file_text:
        prompt = f"Berdasarkan file berikut:\n{file_text[:3000]}\n\nPertanyaan: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Tampilkan pesan user
    with st.chat_message("user"):
        st.markdown(
            f"<div style='text-align: right; background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px 0;'>{prompt}</div>",
            unsafe_allow_html=True
        )

    # Kirim ke OpenAI
    with st.chat_message("assistant"):
        with st.spinner("🤖 Bot sedang mengetik..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            reply = response.choices[0].message["content"]

            # Tampilkan balasan bot
            st.markdown(
                f"<div style='text-align: left; background-color: #F1F0F0; padding: 10px; border-radius: 10px; margin: 5px 0;'>{reply}</div>",
                unsafe_allow_html=True
            )

            # Simpan balasan ke sesi
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Text-to-Speech
            tts_engine = pyttsx3.init()
            mp3_fp = BytesIO()
            tts_engine.save_to_file(reply, "bot_audio.mp3")
            tts_engine.runAndWait()

            # Putar audio
            audio_file = open("bot_audio.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
