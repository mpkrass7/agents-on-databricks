# %%
import os
import time

import streamlit as st
from agents import function_tool, set_tracing_disabled
from databricks.sdk import WorkspaceClient
from openai import AsyncOpenAI
from rich import print
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
from databricks.sdk.core import Config
from databricks.vector_search.client import VectorSearchClient


# Initialize environment variables
set_tracing_disabled(True)

# Initialize clients
w = WorkspaceClient()
v_client = VectorSearchClient()
CONFIG = Config()
sync_client = w.serving_endpoints.get_open_ai_client()
client = AsyncOpenAI(base_url=sync_client.base_url, api_key=CONFIG.token)


@function_tool
def get_store_performance_info(user_query: str):
    """
    Provide information about the store location, store performance, returns, BOPIS(buy online pick up in store) etc.
    """
    st.write(
        f"<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='{CONFIG.host}/genie/rooms/{st.session_state.GENIE_SPACE_STORE_PERFORMANCE_ID}/monitoring' target='_blank'>get_store_performance_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    space_id = os.getenv("GENIE_SPACE_STORE_PERFORMANCE_ID")
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
        f"<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='{CONFIG.host}/genie/rooms/{st.session_state.GENIE_SPACE_STORE_PERFORMANCE_ID}/monitoring' target='_blank'>get_product_inventory_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    space_id = os.getenv("GENIE_SPACE_PRODUCT_INV_ID")
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
        f"<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='{CONFIG.host}/explore/data/models/mk_fiddles/genie_multi_agent/retail_code_of_conduct_bot?o=1720970340056130' target='_blank'>get_business_conduct_policy_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    print("INFO: `get_business_conduct_policy_info` tool called")


    vector_search_endpoint_name = "vector-search-multi-agent-genie"
    index_name = f"{'mk_fiddles'}.{'genie_multi_agent'}.retail_code_of_conduct_index"

    index = v_client.get_index(vector_search_endpoint_name, index_name)

    return index.similarity_search(
        query_text=search_query, 
        columns=["sec_id", "text_chunks"],
        num_results=2
        )
