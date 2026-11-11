"""Standalone Streamlit sandbox for the experimental Vocogni AI core.

Run with: streamlit run ai_lab_app.py
This entrypoint is deliberately not wired into the production app.py navigation.
"""
from __future__ import annotations

import streamlit as st

from ai_prototype.engine import answer, analyze_learning_patterns

st.set_page_config(page_title="Vocogni AI Lab", page_icon="🧪", layout="centered")
st.title("Vocogni AI Lab")
st.caption("Experimental language model + explainable learning-pattern prototype")
st.warning("Sandbox only. Do not enter personal, confidential, or sensitive learner data. Model requests may be sent to the configured provider.")

with st.expander("Configure the model", expanded=False):
    st.write("Set these environment variables before launching the app:")
    st.code("VOCogni_LLM_BASE_URL=https://your-provider.example/v1\nVOCogni_LLM_MODEL=your-model-name\nVOCogni_LLM_API_KEY=your-api-key")
    st.caption("Use a provider endpoint compatible with the OpenAI chat-completions format. Never commit API keys.")

if "ai_lab_messages" not in st.session_state:
    st.session_state.ai_lab_messages = []
if "ai_lab_attempts" not in st.session_state:
    st.session_state.ai_lab_attempts = []

st.subheader("1. Natural-language learning assistant")
for message in st.session_state.ai_lab_messages[-10:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("mode"):
            st.caption(f"Response mode: {message['mode']}")
query = st.chat_input("Ask a question or request an explanation…")
if query:
    st.session_state.ai_lab_messages.append({"role": "user", "content": query})
    result = answer(query, st.session_state.ai_lab_messages[:-1], st.session_state.ai_lab_attempts)
    st.session_state.ai_lab_messages.append({"role": "assistant", "content": result["text"], "mode": result["mode"]})
    st.rerun()

st.divider()
st.subheader("2. Learning-pattern recognition")
st.write("Paste anonymized incorrect attempts. The prototype looks for explicit textual signals such as sign handling, inverse operations, equality balance, fractions, distribution, and keyword-based reasoning.")
with st.form("pattern_form"):
    attempt_text = st.text_area("Incorrect attempts (one per line)", height=140, placeholder="I changed -5 to +5 when moving it…\nI added the denominators…")
    submitted = st.form_submit_button("Analyze patterns", type="primary")
if submitted:
    st.session_state.ai_lab_attempts = [
        {"correct": False, "response": line.strip()} for line in attempt_text.splitlines() if line.strip()
    ]
    report = analyze_learning_patterns(st.session_state.ai_lab_attempts)
    st.session_state.ai_lab_report = report
if "ai_lab_report" in st.session_state:
    report = st.session_state.ai_lab_report
    st.metric("Incorrect attempts inspected", report["incorrect_attempts_inspected"])
    if report["patterns"]:
        for item in report["patterns"]:
            with st.container(border=True):
                st.markdown(f"**{item['label']}** · {item['signal']}")
                st.write(item["description"])
                st.write(f"Evidence count: {item['evidence_count']}")
                st.write(f"Review: {item['review']}")
    else:
        st.info("No supported pattern was detected in the supplied wording. That does not mean there is no learning difficulty.")
    st.caption(report["interpretation"])
