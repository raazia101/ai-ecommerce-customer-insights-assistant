"""
Week 10 Streamlit chat application.

Frontend for the E-commerce Customer Insights Assistant.
The UI communicates with the Week 10 FastAPI backend.
"""

from __future__ import annotations

import uuid

import requests
import streamlit as st


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="E-commerce Customer Insights Assistant",
    page_icon="ðŸ¤–",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("E-commerce Customer Insights Assistant")

st.caption(
    "Ask about customers, orders, KPIs, and documentation."
)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Conversation")

    st.write(
        f"**Session:** `{st.session_state.session_id}`"
    )

    if st.button("Clear chat", use_container_width=True):
        try:
            requests.delete(
                f"{API_URL}/chat/{st.session_state.session_id}",
                timeout=10,
            )
        except requests.RequestException:
            pass

        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("Supported questions")

    st.markdown(
        """
        - Customer lookups
        - Order status
        - KPI questions
        - Documentation questions
        """
    )



# ---------------------------------------------------------------------------
# Display conversation history
# ---------------------------------------------------------------------------

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    source_name = source.get(
                        "source",
                        "Unknown source",
                    )

                    relevance = source.get("relevance")

                    if relevance is not None:
                        st.write(
                            f"- {source_name} "
                            f"(relevance: {relevance:.3f})"
                        )
                    else:
                        st.write(f"- {source_name}")

        # Show feedback controls only for assistant messages.
        if message["role"] == "assistant":
            feedback_col1, feedback_col2, _ = st.columns(
                [1, 1, 8]
            )

            with feedback_col1:
                if st.button(
                    "ðŸ‘",
                    key=f"positive_{i}",
                ):
                    st.toast("Thanks for the feedback!")

            with feedback_col2:
                if st.button(
                    "ðŸ‘Ž",
                    key=f"negative_{i}",
                ):
                    st.toast("Thanks for the feedback!")

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

user_message = st.chat_input(
    "Ask a question..."
)

if user_message:
    # Display the user's message immediately.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    # Send the request to FastAPI.
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "session_id": st.session_state.session_id,
                        "message": user_message,
                    },
                    timeout=60,
                )

                response.raise_for_status()
                data = response.json()

                assistant_message = data.get(
                    "response",
                    "I couldn't produce a response.",
                )

                status = data.get("status", "success")
                sources = data.get("sources", [])

                st.markdown(assistant_message)

                if status != "success":
                    st.caption(f"Status: `{status}`")

                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            source_name = source.get(
                                "source",
                                "Unknown source",
                            )

                            relevance = source.get("relevance")

                            if relevance is not None:
                                st.write(
                                    f"- {source_name} "
                                    f"(relevance: {relevance:.3f})"
                                )
                            else:
                                st.write(
                                    f"- {source_name}"
                                )

                # Save assistant response.
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message,
                        "sources": sources,
                        "status": status,
                        "tool_used": data.get("tool_used"),
                    }
                )

                # -------------------------------------------------------
                # Feedback
                # -------------------------------------------------------

                feedback_col1, feedback_col2, _ = st.columns(
                    [1, 1, 8]
                )

                with feedback_col1:
                    if st.button(
                        "ðŸ‘",
                        key=f"positive_{len(st.session_state.messages)}",
                    ):
                        st.toast("Thanks for the feedback!")

                with feedback_col2:
                    if st.button(
                        "ðŸ‘Ž",
                        key=f"negative_{len(st.session_state.messages)}",
                    ):
                        st.toast("Thanks for the feedback!")

            except requests.RequestException as exc:
                error_message = (
                    "I couldn't connect to the assistant service. "
                    "Please make sure the FastAPI server is running."
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

                st.caption(f"Connection error: {exc}")

            except ValueError:
                error_message = (
                    "The assistant returned an invalid response."
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
