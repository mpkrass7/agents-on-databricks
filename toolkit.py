# %%
import time

import streamlit as st
from agents import function_tool, set_tracing_disabled
from databricks.sdk import WorkspaceClient
from openai import AsyncOpenAI
from rich import print

# Initialize environment variables
set_tracing_disabled(True)

# Initialize clients
w = WorkspaceClient(host=st.session_state.host, token=st.session_state.token)

sync_client = w.serving_endpoints.get_open_ai_client()
client = AsyncOpenAI(base_url=sync_client.base_url, api_key=st.session_state.token)


@function_tool
def get_store_performance_info(user_query: str):
    """
    Provide information about the store location, store performance, returns, BOPIS(buy online pick up in store) etc.
    """
    st.write(
        f"<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='https://{st.session_state.host}/genie/rooms/{st.session_state.GENIE_SPACE_STORE_PERFORMANCE_ID}/monitoring' target='_blank'>get_store_performance_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    space_id = st.session_state.GENIE_SPACE_STORE_PERFORMANCE_ID
    print(f"INFO: `get_store_performance_info` tool called with space_id: {space_id}")
    timeout = 60.0
    poll_interval = 2.0
    # Step 1: Start a new conversation using the SDK
    message = w.genie.start_conversation_and_wait(space_id, user_query)
    conversation_id = message.conversation_id
    message_id = message.id
    # Step 2: Poll for completion using the SDK
    start_time = time.time()
    while True:
        msg = w.genie.get_message(space_id, conversation_id, message_id)
        status = msg.status.value if msg.status else None
        if status == "COMPLETED":
            if msg.attachments and len(msg.attachments) > 0:
                attachment_id = msg.attachments[0].attachment_id
                result = w.genie.get_message_attachment_query_result(
                    space_id, conversation_id, message_id, attachment_id
                )
                return result.statement_response.as_dict()
            else:
                return {"error": "No attachments found in message."}
        if time.time() - start_time > timeout:
            raise TimeoutError("Genie API query timed out.")
        time.sleep(poll_interval)


@function_tool
def get_product_inventory_info(user_query: str):
    """
    Provide information about products and the current inventory snapshot across stores.
    """
    st.write(
        f"<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='https://{st.session_state.host}/genie/rooms/{st.session_state.GENIE_SPACE_STORE_PERFORMANCE_ID}/monitoring' target='_blank'>get_product_inventory_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    space_id = space_id = st.session_state.GENIE_SPACE_PRODUCT_INV_ID
    print(f"INFO: `get_product_inventory_info` tool called with space_id: {space_id}")
    timeout = 60.0
    poll_interval = 2.0
    # Step 1: Start a new conversation using the SDK
    message = w.genie.start_conversation_and_wait(space_id, user_query)
    conversation_id = message.conversation_id
    message_id = message.id
    # Step 2: Poll for completion using the SDK
    start_time = time.time()
    while True:
        msg = w.genie.get_message(space_id, conversation_id, message_id)
        status = msg.status.value if msg.status else None
        if status == "COMPLETED":
            if msg.attachments and len(msg.attachments) > 0:
                attachment_id = msg.attachments[0].attachment_id
                result = w.genie.get_message_attachment_query_result(
                    space_id, conversation_id, message_id, attachment_id
                )
                return result.statement_response.as_dict()
            else:
                return {"error": "No attachments found in message."}
        if time.time() - start_time > timeout:
            raise TimeoutError("Genie API query timed out.")
        time.sleep(poll_interval)


@function_tool
def get_business_conduct_policy_info(search_query: str) -> str:
    st.write(
        f'<span style="color:green;">[🛠️TOOL-CALL]: the <a href="https://{st.session_state.host}/explore/data/{st.session_state.CATALOG}/{st.session_state.SCHEMA}/retail_code_of_conduct_index" target="_blank">get_business_conduct_policy_info</a> tool was called</span>',
        unsafe_allow_html=True,
    )
    print("INFO: `get_business_conduct_policy_info` tool called")
    
    index_name = f"{st.session_state.CATALOG}.{st.session_state.SCHEMA}.retail_code_of_conduct_index"
    
    return w.vector_search_indexes.query_index(
        index_name=index_name,
        query_text=search_query,
        columns=["sec_id", "text_chunks"],
        num_results=2,
    )
