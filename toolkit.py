# %%
import os
import time

import streamlit as st
from agents import function_tool, set_tracing_disabled
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
from openai import AsyncOpenAI
from rich import print
from unitycatalog.ai.core.databricks import (DatabricksFunctionClient,
                                             FunctionExecutionResult)

# %%
# Load environment variables
load_dotenv(".env")

# Initialize environment variables
BASE_URL = os.getenv("DATABRICKS_BASE_URL") or ""
API_KEY = os.getenv("DATABRICKS_TOKEN") or ""
MODEL_NAME = os.getenv("DATABRICKS_MODEL") or ""
set_tracing_disabled(True)


# Initialize clients
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
w = WorkspaceClient(
    host=os.getenv("DATABRICKS_HOST"),
    token=os.getenv("DATABRICKS_TOKEN"),
    auth_type="pat",
)
dbclient = DatabricksFunctionClient(client=w)


@function_tool
def get_store_performance_info(user_query: str):
    """
    Provide information about the store location, store performance, returns, BOPIS(buy online pick up in store) etc.
    """
    st.write(
        f"<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='{os.getenv('DATABRICKS_HOST')}/genie/rooms/{os.getenv('GENIE_SPACE_STORE_PERFORMANCE_ID')}/monitoring' target='_blank'>get_store_performance_info</a> tool was called</span>",
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
        f"<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='{os.getenv('DATABRICKS_HOST')}/genie/rooms/{os.getenv('GENIE_SPACE_PRODUCT_INV_ID')}/monitoring' target='_blank'>get_product_inventory_info</a> tool was called</span>",
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
def get_business_conduct_policy_info(search_query: str) -> FunctionExecutionResult:
    st.write(
        "<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='<REPLACE_ME_WITH_WORKSPACE_URL_TO_BUSINESS_CONDUCT_POLICY_UC_TOOL>' target='_blank'>get_business_conduct_policy_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    print("INFO: `get_business_conduct_policy_info` tool called")
    return dbclient.execute_function(
        function_name="<REPLACE_ME_WITH_3_LEVEL_NAMESPACE_FOR_BUSINESS_CONDUCT_POLICY_UC_TOOL, e.g. catalog.schema.function>",
        parameters={"search_query": search_query},
    )
