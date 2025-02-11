import streamlit as st
from openai import OpenAI


def retrieve_assistant():
    """
    Retrieves the OpenAI assistant.

    Returns:
        Assistant: The OpenAI assistant.
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    assistant = client.beta.assistants.retrieve(assistant_id=st.secrets["ASSISTANT_ID"])
    return assistant


st.title("Model Inventory Chatbot")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    thread = client.beta.threads.create(messages=[{"role": "user", "content": prompt}])
    assistant = retrieve_assistant()

    run = client.beta.threads.runs.create_and_poll(
        assistant_id=assistant.id,
        thread_id=thread.id,
        model=st.session_state["openai_model"],
    )
    run_steps = client.beta.threads.runs.steps.list(thread_id=thread.id, run_id=run.id)
    run_steps = list(run_steps)

    message_id = run_steps[0].step_details.message_creation.message_id
    message = client.beta.threads.messages.retrieve(
        message_id=message_id, thread_id=thread.id
    )

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write(message.content[0].text.value)
    st.session_state.messages.append({"role": "assistant", "content": response})
