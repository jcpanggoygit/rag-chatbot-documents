import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("🧠 Document QA Chatbot")

# Upload document
st.header("📄 Upload PDF Document")
uploaded_file = st.file_uploader("Select a PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("Uploading and processing document..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{API_URL}/upload/", files=files)
        if response.status_code == 200:
            st.success("Document successfully processed")
        else:
            st.error("Error processing the document")

# Ask a question
st.header("❓ Ask a Question")

question = st.text_input("Type your question here:")
if st.button("Ask"):
    if not question.strip():
        st.warning("Please type a question first.")
    else:
        with st.spinner("Thinking..."):
            data = {"question": question}
            response = requests.post(f"{API_URL}/ask/", data=data)
            if response.status_code == 200:
                answer_data = response.json().get("answer", "")
                if isinstance(answer_data, dict):
                    answer_text = answer_data.get("result", str(answer_data))
                else:
                    answer_text = str(answer_data)

                st.markdown("**Answer:** " + answer_text)
            else:
                st.error("Could not retrieve an answer.")