
import streamlit as st
import requests

st.set_page_config(
    page_title="Cricket RAG Assistant",
    page_icon="🏏",
    layout="centered",
)

API_URL = "http://127.0.0.1:8000/ask"

st.title("🏏 Cricket RAG Assistant")
st.write("Ask questions about your cricket match documents.")

st.divider()

question = st.text_input(
    "Your cricket question",
    placeholder="Which teams played in this match?",
)

match_id = st.text_input(
    "Match ID (optional)",
    placeholder="Leave blank to search all matches",
)

if st.button("Ask Question"):
    if not question.strip():
        st.error("Please enter a question.")
    else:
        payload = {
            "question": question.strip(),
            "match_id": match_id.strip() or None,
        }

        with st.spinner("Finding your cricket answer..."):
            try:
                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=120,
                )

                if response.ok:
                    result = response.json()
                    st.subheader("Answer")
                    st.write(
                        result.get("answer", result)
                    )
                else:
                    st.error(
                        f"API error ({response.status_code})"
                    )
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to FastAPI. "
                    "Make sure the backend is running on port 8000."
                )
            except requests.exceptions.Timeout:
                st.error(
                    "The request took too long. Try again."
                )
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

st.divider()
st.caption("Cricket RAG Assistant | FastAPI + Streamlit")
