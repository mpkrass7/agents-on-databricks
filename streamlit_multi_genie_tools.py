import asyncio
import atexit
import logging
import os
import warnings

import dotenv
import mlflow
import streamlit as st
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from databricks.sdk import WorkspaceClient
from mlflow.tracing.destination import Databricks
from openai import AsyncOpenAI
import yaml


if "DATABRICKS_MODEL" not in st.session_state:
    # Remove default environment variables so they don't conflict with your own
    os.environ.pop("DATABRICKS_CLIENT_ID", None)
    os.environ.pop("DATABRICKS_CLIENT_SECRET", None)

    try:
        st.session_state.host = os.environ["DATABRICKS_HOST"].replace("https://", "")
        st.session_state.token = os.environ["DATABRICKS_TOKEN"]
        mlflow.set_tracking_uri("databricks")
    except KeyError:
        print("Error: DATABRICKS_HOST or DATABRICKS_TOKEN environment variable is not set.")
        print("Error: DATABRICKS_TOKEN environment variable is not set.")
        print("Attempting to load from workspace")
        dotenv.load_dotenv()
        st.session_state.host = WorkspaceClient().config.host.replace("https://", "")
        st.session_state.token = WorkspaceClient().tokens.create().token_value
        mlflow.set_tracking_uri(f"databricks://{os.getenv("DATABRICKS_CONFIG_PROFILE", "DEFAULT")}")

    assert st.session_state.token, "Failed to set DATABRICKS_TOKEN environment variable"

    with open("app_config.yaml") as f:
        conf = yaml.safe_load(f)
        st.session_state.CATALOG = conf["CATALOG"]
        st.session_state.SCHEMA = conf["SCHEMA"]
        st.session_state.DATABRICKS_MODEL = conf["DATABRICKS_MODEL"]
        st.session_state.GENIE_SPACE_STORE_PERFORMANCE_ID = conf[
            "GENIE_SPACE_STORE_PERFORMANCE_ID"
        ]
        st.session_state.GENIE_SPACE_PRODUCT_INV_ID = conf["GENIE_SPACE_PRODUCT_INV_ID"]
        st.session_state.MLFLOW_EXPERIMENT_ID = conf["MLFLOW_EXPERIMENT_ID"]


from toolkit import (
    get_business_conduct_policy_info,
    get_product_inventory_info,
    get_store_performance_info,
)

# Suppress the AsyncHttpxClientWrapper.__del__ warning
warnings.filterwarnings("ignore", message=".*AsyncHttpxClientWrapper.__del__.*")
# Also suppress any ResourceWarning which often occurs with async clients
warnings.filterwarnings("ignore", category=ResourceWarning)
# Suppress warnings that mention AttributeError in their message
warnings.filterwarnings("ignore", message=".*AttributeError.*")


set_tracing_disabled(True)

# Initialize MLflow logging if configured (make this optional)
try:
    if st.session_state.MLFLOW_EXPERIMENT_ID:
        
        mlflow.tracing.set_destination(
            Databricks(experiment_id=st.session_state.MLFLOW_EXPERIMENT_ID)
        )
        mlflow.openai.autolog()
        logging.info("MLflow logging enabled")
    else:
        logging.info("MLflow logging disabled - MLFLOW_EXPERIMENT_ID not set")
except Exception as e:
    logging.warning(f"Failed to initialize MLflow logging: {str(e)}")

# Initialize clients
w = WorkspaceClient(host=st.session_state.host, token=st.session_state.token)
sync_client = w.serving_endpoints.get_open_ai_client()
client = AsyncOpenAI(base_url=sync_client.base_url, api_key=st.session_state.token)


# Register a cleanup function to properly close the async client at exit
async def close_client():
    try:
        await client.close()
        logging.info("AsyncOpenAI client closed successfully")
    except Exception as e:
        logging.warning(f"Error closing AsyncOpenAI client: {str(e)}")


# Register the cleanup to run at exit
atexit.register(lambda: asyncio.run(close_client()))

# Set page configuration
st.set_page_config(
    page_title="Store Intelligence Assistant",
    layout="wide",
    page_icon="🛒",
)


# Hide hamburger menu and footer
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# Custom CSS for modern styling
st.markdown(
    """
    <style>
    :root {
        --st-bg: #fff;
        --st-fg: #222;
        --st-card-bg: #f8f9fa;
        --st-card-border: #e9ecef;
    }
    body, .main {
        background: var(--st-bg) !important;
        color: var(--st-fg) !important;
    }
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.07);
        background: var(--st-card-bg);
        color: var(--st-fg);
    }
    .stChatInput {
        border-radius: 12px;
        padding: 1rem;
        margin-top: 2rem;
        background: var(--st-card-bg);
        color: var(--st-fg);
    }
    .stAlert {
        border-radius: 12px;
        padding: 1.5rem;
        background: var(--st-card-bg);
        color: var(--st-fg);
    }
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid var(--st-card-border);
        color: var(--st-fg);
        background: var(--st-bg);
    }
    h1, h3 {
        color: var(--st-fg) !important;
    }
    .card {
        background: var(--st-card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.07);
        margin: 1rem 0;
        color: var(--st-fg);
        border: 1px solid var(--st-card-border);
    }
    ul, li, p {
        color: var(--st-fg);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize the agent
agent = Agent(
    name="Assistant",
    instructions="""You are a helpful assistant that can answer questions about the store performance, returns, BOPIS(buy online pick up in store) etc. 
    You can optionally choose to use the tools provided to you to answer the questions. 
    If the question is not related to store location, performance or policy, you can answer the question based on your knowledge or say that you don't know.
    Use the get_store_performance_info tool to get the store performance or location information. When forecasts are returned, present the table as is. 
    Additionally, add a small note to the table to say that this is an on-demand forecast for the give store and forecasting horizon.
    If any policy is asked, use the get_business_conduct_policy_info tool to get the policy information.
    Use the get_product_inventory_info tool to get the product inventory information.
    You have access to the full chat history, so you can reference previous messages and maintain context throughout the conversation.""",
    model=OpenAIChatCompletionsModel(
        model=st.session_state.DATABRICKS_MODEL, openai_client=client
    ),
    tools=[
        get_business_conduct_policy_info,
        get_store_performance_info,
        get_product_inventory_info,
    ],
)


@mlflow.trace(span_type="AGENT")
async def poll_runner(agent=agent, chat_history=None, prompt=None):
    print(f"Chat history:\n{chat_history}\n\nUser's latest question: {prompt}")
    return await Runner.run(
        agent,
        f"Chat history:\n{chat_history}\n\nUser's latest question: {prompt}",
    )


# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit UI
st.title("Store Intelligence Assistant 🤖")

# Create a modern info box with cards
with st.container():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
        <div class="card">
            <h3>Hi, I'm a Store Intelligence Assistant!</h3>
            <p>I can help you with:</p>
            <ul>
                <li>📊 Store performance metrics</li>
                <li>🔄 Return policies</li>
                <li>🛍️ BOPIS (Buy Online, Pick Up In Store) information</li>
                <li>📋 Business conduct policies</li>
                <li>📦 Product inventory information</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="card">
            <h3>Example Questions</h3>
            <ul>
                <li>What was the total sales for store 110 last year?</li>
                <li>Based on our current inventory snapshot, give me the store id that has the highest on order for baby products?</li>
                <li>What is the overtime policy for vendors?</li>
                <li>Generate a sales forecast for store 110 for the next 6 months</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

# Display chat history with improved styling
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input with improved styling
if prompt := st.chat_input(
    "Ask me anything about store performance, policies, or inventory..."
):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    try:
        with st.spinner("Thinking..."):
            # Run the agent asynchronously with chat history
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Include chat history in the context
            chat_history = "\n".join(
                [
                    f"{msg['role']}: {msg['content']}"
                    for msg in st.session_state.messages
                ]
            )
            result = loop.run_until_complete(
                poll_runner(agent=agent, chat_history=chat_history, prompt=prompt)
            )
            response = result.final_output
    except Exception as e:
        response = f"An error occurred: {str(e)}"

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Modern footer
st.markdown(
    """
<div class="footer">
    <p>Demo powered by <a href="https://databricks.com">Databricks 🚀</a></p>
    <p style="color: #666; font-size: 0.9rem;">© 2025 Store Intelligence Assistant</p>
</div>
""",
    unsafe_allow_html=True,
)
