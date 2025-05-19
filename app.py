import streamlit as st
import httpx
import pyttsx3
from io import BytesIO
from PyPDF2 import PdfReader

DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

st.set_page_config(page_title="🤖 DeepSeek Chatbot", page_icon="💬")
st.title("🤖 DeepSeek AI Chatbot + File Upload + Suara")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ Opsi")
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

# Upload file
file_text = ""
uploaded_file = st.file_uploader("📎 Upload file (txt/pdf)", type=["txt", "pdf"])
if uploaded_file:
    if uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        file_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    st.success("✅ File berhasil dibaca!")

# Tampilkan chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input chat
if prompt := st.chat_input("Ketik sesuatu..."):

    if file_text:
        prompt = f"Berdasarkan file berikut:\n{file_text[:3000]}\n\nPertanyaan: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 DeepSeek sedang merespons..."):

            # Panggil DeepSeek API
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }

            body = {
                "model": "deepseek-chat",  # Atau deepseek-coder / deepseek-v2
                "messages": [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                "temperature": 0.7
            }

            try:
                response = httpx.post(DEEPSEEK_API_URL, headers=headers, json=body)
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # TTS (optional)
            tts_engine = pyttsx3.init()
            tts_engine.save_to_file(reply, "bot_audio.mp3")
            tts_engine.runAndWait()
            with open("bot_audio.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")
