# Store Intelligence Assistant

An interactive Streamlit app for exploring store performance, inventory, and business policies, powered by Databricks and OpenAI agents SDK.

## What is this app?

This app is a conversational assistant that helps users query and analyze:
- 📊 Store performance metrics
- 🔄 Return and business conduct policies
- 🛍️ BOPIS (Buy Online, Pick Up In Store) information
- 📦 Product inventory across stores
- 📈 Monthly Sales Forecasts for stores

It leverages Databricks-hosted resources, Databricks Genie rooms, and a large language model (LLM) to provide on-demand, context-aware answers.
The repo also shows how to deploy this app to Databricks Apps.

---

## Quick Demo

The following is a quick demo of the working application:

![Demo of the Store Intelligence Analyst](Demo-Agent-Polling-Genie-Rooms-VectorIndexes.gif)


## Key Databricks Resources

### 1. **Databricks Genie Rooms**
The app uses Genie rooms to power its data tools. These Genie rooms are used by the app's tools to fetch live data and answer user questions.
- **Store Performance Genie Room:**
For revenue, BOPIS, forecasts, store performance metrics
 
- **Product Inventory Genie Room:**
For inventory snapshots, product details etc.

### 2. **Databricks Vector Search**  
- **Business Conduct Policy Table:**
For querying and finding out specific information about vendor conduct policy using a vector index

### 3. **LLM (Large Language Model)**
- The app uses a Databricks-hosted LLM, specified by the `DATABRICKS_MODEL` variable in app_config.yaml.
- The LLM is accessed via the OpenAI-compatible API endpoint provided by Databricks Mosaic AI Gateway.
- All chat and tool responses are generated or orchestrated by this model.

---

## How does it work?

- The app is built with [Streamlit](https://streamlit.io/) for a modern, interactive UI.
- User questions are routed to an agent, which can:
  - Answer directly using the LLM
  - Call specialized tools that query Genie rooms or Databricks tables for live data
- All Databricks credentials and resource IDs are managed via environment variables (see `.env` setup).

---

## Tools & Data Flows

- **get_store_performance_info:**
  - Queries the Store Performance Genie room for sales, location, and forecast data.
- **get_product_inventory_info:**
  - Queries the Product Inventory Genie room for inventory snapshots and product data.
- **get_business_conduct_policy_info:**
  - Queries a Databricks Vector Search Index for business conduct and return policies.

---

## Vector Search Index

The vector search index was hydrated using the process highlighted in the [vector_search_setup.png](./vectorsearch-tooluse.png) file in this repository.

---

## Customization
- The UI and agent instructions can be customized in `streamlit_multi_genie_tools.py`.
- The tool call behavior can be modified in `toolkit.py`

---

## Requirements
- Python 3.12
- Access to a Databricks workspace with Genie enabled
- A Databricks-hosted LLM (or compatible OpenAI endpoint)


## Building and Deploying your Application
1. Make sure you have the databricks cli installed. See the [docs](https://docs.databricks.com/aws/en/dev-tools/cli/install) for more information.
2. Clone the repository
3. Install the requirements using `pip install -r requirements.txt` (note that this app requires Python 3.12 and a virtual environment is recommended)
4. Create a `.env` file in the root directory with your app workspace path, app name and secret scope name. **Don't forget to set the environment variables by running `source ./.env` in your terminal.**
   Example `.env` file:
    ```
    APP_WORKSPACE_PATH="/Workspace/Users/marshall.krassenstein@databricks.com/store-agent-with-tools"
    APP_NAME="store-intel-agent-with-tools" # Replace with your app name
    SCOPE_NAME="store-intel-agent-with-tools-scope" # Replace with your scope name
    DATABRICKS_CONFIG_PROFILE="PROFILE_FOR_WORKSPACE_HERE" # Replace with your databricks config profile found in ~/.databrickscfg
    ```

5. Make sure you're signed into the databricks workspace you want. A common way to sign into a workspace for the cli is to use `databricks auth login -p PROFILE_FOR_WORKSPACE_HERE`. Note that the profile is found in your `~/.databrickscfg` file and you can add as many profiles as you want. 
    Example Config:
    ```
    [PROFILE_FOR_YOUR_WORKSPACE_HERE]
    host      = https://workspace_name.databricks.net/
    auth_type = databricks-cli
    ```

6. Run `python scripts/app_setup.py` to set up the app in your Databricks workspace. This will:
   - Create the app in your workspace
   - Create a secret scope for your PAT and attach it to the app
7. From your project directory, run:
    ```bash
    databricks sync --watch . $APP_WORKSPACE_PATH
    ```
    - This will upload your code and watch for changes.
    - Exclude files/folders using `.gitignore` if needed.
8. On your workspace, fill out the top cell of variable names and run the Agent Multi Tool Setup notebook. **The cluster must not be running on serverless**. Running this notebook will create the Genie rooms, vector search index, and other resources needed for the app and write it to a file `app_config.yaml`
9. Deploy the app:
    ```bash
    databricks apps deploy $APP_NAME --source-code-path $APP_WORKSPACE_PATH
    ```
10. After deploying, you can view and use the app by going to your Databricks workspace, clicking on **Compute > Apps** tab, and finding your app. Click the app name to view deployment status and launch the Streamlit UI.
    
## How to Run the App Locally
If you want to test your app locally, follow the first 8 steps download the `app_config.yaml` file generated by the Agent Multi Tool Setup notebook. Place it in the root directory of your app. This file contains the configuration for the application, including Genie room IDs, vector search index names, and other necessary variables. 

Once downloaded, you can run the app locally with `streamlit run streamlit_multi_genie_tools.py`.

Note that you can also supply your `app_config.yaml` file so long as you have the required variables set up in it.
Example config file:
```yaml
  CATALOG: ""
  SCHEMA: ""
  DATABRICKS_MODEL: "databricks-claude-3-7-sonnet"
  GENIE_SPACE_STORE_PERFORMANCE_ID: ""
  GENIE_SPACE_PRODUCT_INV_ID: ""
  MLFLOW_EXPERIMENT_ID: ""
  VECTOR_SEARCH_INDEX_NAME: "your_catalog.your_schema.your_vector_search_index_name"
```

> ⚠️ **Warning:** The Genie spaces in this app are created using a non-public API and the routes can change at any time. If running the Agent Multi Tool Setup notebook fails at the genie creation stage, you will need to comment out the code, manually create each of your genie spaces, and save the IDs to their corresponding variables.


---

**References:**
- [Databricks Apps: Get Started](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/get-started)
- [Databricks Apps: App Development & Secrets](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development)
- [Databricks Apps: Configuration](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/configuration)


