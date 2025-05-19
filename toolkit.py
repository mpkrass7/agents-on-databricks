# %%
from agents import function_tool
import os
import requests
import time
from unitycatalog.ai.core.databricks import (
    DatabricksFunctionClient,
    FunctionExecutionResult,
)
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai import OpenAI
from rich import print
import streamlit as st
# %%
# Load environment variables
load_dotenv("/Users/sathish.gangichetty/Documents/openai-agents/apps/.env-local")

# Initialize environment variables
BASE_URL = os.getenv("DATABRICKS_BASE_URL") or ""
API_KEY = os.getenv("DATABRICKS_TOKEN") or ""
MODEL_NAME = os.getenv("DATABRICKS_MODEL") or ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""

# Initialize clients
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
w = WorkspaceClient(
    host=os.getenv("DATABRICKS_HOST"), token=os.getenv("DATABRICKS_TOKEN")
)
dbclient = DatabricksFunctionClient(client=w)


@function_tool
def get_store_performance_info(user_query: str):
    """
    For us, we use this to get information about the store location, store performance, returns, BOPIS(buy online pick up in store) etc.
    """
    st.write(
        "<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='https://adb-984752964297111.11.azuredatabricks.net/genie/rooms/01f023ae84651418a1203b194dff21a9?o=984752964297111' target='_blank'>get_store_performance_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    print("INFO: `get_store_performance_info` tool called")
    databricks_instance = os.getenv("DATABRICKS_HOST")
    space_id = os.getenv("GENIE_SPACE_ID")
    access_token = os.getenv("DATABRICKS_TOKEN")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    poll_interval = 2.0
    timeout = 60.0

    # Step 1: Start a new conversation
    start_url = (
        f"{databricks_instance}/api/2.0/genie/spaces/{space_id}/start-conversation"
    )
    payload = {"content": user_query}
    resp = requests.post(start_url, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()
    print(data)
    conversation_id = data["conversation_id"]
    message_id = data["message_id"]

    # Step 2: Poll for completion
    poll_url = f"{databricks_instance}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
    start_time = time.time()
    while True:
        poll_resp = requests.get(poll_url, headers=headers)
        poll_resp.raise_for_status()
        poll_data = poll_resp.json()
        status = poll_data.get("status")
        if status == "COMPLETED":
            attachment_id = poll_data["attachments"][0]["attachment_id"]
            url = f"{databricks_instance}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/query-result"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["statement_response"]
        if time.time() - start_time > timeout:
            raise TimeoutError("Genie API query timed out.")
        time.sleep(poll_interval)


@function_tool
def get_product_inventory_info(user_query: str):
    """
    For us, we use this to get information about products and the current inventory snapshot across stores
    """
    st.write(
        "<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='https://adb-984752964297111.11.azuredatabricks.net/genie/rooms/01f02c2c29211c388b9b5b9b6f5a80c9?o=984752964297111' target='_blank'>get_product_inventory_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    print("INFO: `get_product_inventory_info` tool called")
    databricks_instance = os.getenv("DATABRICKS_HOST")
    space_id = os.getenv("GENIE_SPACE_PRODUCT_INV_ID")
    access_token = os.getenv("DATABRICKS_TOKEN")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    poll_interval = 2.0
    timeout = 60.0

    # Step 1: Start a new conversation
    start_url = (
        f"{databricks_instance}/api/2.0/genie/spaces/{space_id}/start-conversation"
    )
    payload = {"content": user_query}
    resp = requests.post(start_url, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()
    print(data)
    conversation_id = data["conversation_id"]
    message_id = data["message_id"]

    # Step 2: Poll for completion
    poll_url = f"{databricks_instance}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
    start_time = time.time()
    while True:
        poll_resp = requests.get(poll_url, headers=headers)
        poll_resp.raise_for_status()
        poll_data = poll_resp.json()
        status = poll_data.get("status")
        if status == "COMPLETED":
            attachment_id = poll_data["attachments"][0]["attachment_id"]
            url = f"{databricks_instance}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/query-result"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["statement_response"]
        if time.time() - start_time > timeout:
            raise TimeoutError("Genie API query timed out.")
        time.sleep(poll_interval)


@function_tool
def get_business_conduct_policy_info(search_query: str) -> FunctionExecutionResult:
    st.write(
        "<span style='color:green;'>[🛠️TOOL-CALL]: the <a href='https://adb-984752964297111.11.azuredatabricks.net/explore/data/main/sgfs/retail_conduct_policy?o=984752964297111&activeTab=overview' target='_blank'>get_business_conduct_policy_info</a> tool was called</span>",
        unsafe_allow_html=True,
    )
    print("INFO: `get_business_conduct_policy_info` tool called")
    return dbclient.execute_function(
        function_name="main.sgfs.retail_club_conduct",
        parameters={"search_query": search_query},
    )
