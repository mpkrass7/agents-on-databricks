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
- The app uses a Databricks-hosted LLM, specified by the `DATABRICKS_MODEL` environment variable.
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

## Quickstart

1. Clone this repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file with Databricks credentials and model info.
3. Run the app:
   ```bash
   streamlit run streamlit_multi_genie_tools.py
   ```

---

## Customization
- Update the Genie room IDs or Databricks model in your `.env` file to point to your own resources.
- The UI and agent instructions can be customized in `streamlit_multi_genie_tools.py`.

---

## Requirements
- Python 3.12
- Access to a Databricks workspace with Genie enabled
- A Databricks-hosted LLM (or compatible OpenAI endpoint)


## To Run the App Locally
1. Create a virtual env locally using uv `uv venv --python 3.12`
2. Then, install the requirements using `uv pip install -r requirements.txt`
3. Make sure your app_config.yaml file is set up with the required variables. You can fill these in yourself or create them by running `scripts/build_dependencies.py`. 
note: you only need the `MLFLOW_EXPERIMENT_ID` if you want to enable montioring or write to an existing external monitor
```
DATABRICKS_MODEL: "databricks-claude-3-7-sonnet"
GENIE_SPACE_STORE_PERFORMANCE_ID: ""
GENIE_SPACE_PRODUCT_INV_ID: ""
MLFLOW_EXPERIMENT_ID: ""
DATABRICKS_SERVING_ENDPOINT_NAME: ""
```
4. Run the app `streamlit run streamlit_multi_genie_tools.py` (you might have to create a .streamlit folder on the root of the project to control the theme as you might see fit using a `config.toml file`)
5. You might have to create a .streamlit folder on the root of the project to control the theme as you might see fit using a `config.toml file`

Example `config.toml` file
```
[theme]
base="light"
primaryColor="#FF4B4B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#31333F"
font="sans serif"
```

---

## Deploying to Databricks Apps

You can deploy this Streamlit app to your Databricks workspace as a Databricks App for secure, scalable access. Here's how:

### 1. Create the App in Your Workspace

In your terminal, run:
```bash
databricks apps create <app-name>
```
Replace `<app-name>` with your desired app name (e.g., `store-intel-assistant`).

### 2. Sync Your Local App to Databricks Workspace

From your project directory, run:
```bash
databricks sync --watch . $APP_WORKSPACE_PATH
```
- This will upload your code and watch for changes.
- Exclude files/folders using `.gitignore` if needed.

### 3. Deploy the App

After syncing, deploy the app with:
```bash
databricks apps deploy <app-name> --source-code-path $APP_WORKSPACE_PATH
```
- Replace `<app-name>` and the workspace path as appropriate.

### 4. View and Use the App
- Go to your Databricks workspace, click **Compute > Apps** tab, and find your app.
- Click the app name to view deployment status and launch the Streamlit UI.

---

**References:**
- [Databricks Apps: Get Started](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/get-started)
- [Databricks Apps: App Development & Secrets](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development)
- [Databricks Apps: Configuration](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/configuration)


