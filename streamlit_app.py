import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(page_title="Tenkai", page_icon="📈", layout="centered")

st.title("Tenkai")

with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload a financial PDF", type=["pdf"])
    if uploaded_file and uploaded_file.name not in st.session_state.get("ingested_files", []):
        with st.spinner("Ingesting document..."):
            response = requests.post(
                f"{API_URL}/ingest",
                files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            )
            if response.status_code == 200:
                data = response.json()
                if "ingested_files" not in st.session_state:
                    st.session_state.ingested_files = []
                st.session_state.ingested_files.append(uploaded_file.name)
                st.success(f"Ingested {data['chunks']} chunks from {data['ingested']}")
            else:
                st.error("Failed to ingest document")
    elif uploaded_file:
        st.info(f"{uploaded_file.name} already ingested")

st.header("Ask a question")

if "message" not in st.session_state:
    st.session_state.message = []

for message in st.session_state.message:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("e.g. What was Apple's total revenue in 2024?"):
    st.session_state.message.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            response = requests.get(f"{API_URL}/query", params={"q": prompt})
            if response.status_code == 200:
                data = response.json()
                answer = data["answer"]
                sources = list(set(data["sources"]))
                full_response = f"{answer}\n\n**Sources:** {', '.join(sources)}"
                st.markdown(full_response.replace("$", "\\$"))
                st.session_state.message.append({"role": "assistant", "content": full_response})

            else:
                st.error("Failed to get response")







