# Store Intelligence Assistant

An interactive Streamlit app for exploring store performance, inventory, and business policies, powered by Databricks and OpenAI agents SDK.

## What is this app?

This app is a conversational assistant that helps users query and analyze:
- 📊 Store performance metrics
- 🔄 Return and business conduct policies
- 🛍️ BOPIS (Buy Online, Pick Up In Store) information
- 📦 Product inventory across stores

It leverages Databricks-hosted resources, Databricks Genie rooms, and a large language model (LLM) to provide on-demand, context-aware answers.

---

## Key Databricks Resources

### 1. **Databricks Genie Rooms**
The app uses Genie rooms to power its data tools:
- **Store Performance Genie Room:**
For revenue, BOPIS, forecasts, store performance metrics
 
- **Product Inventory Genie Room:**
For inventory snapshots, product details etc.
  
- **Business Conduct Policy Table:**
For querying and finding out specific information about vendor conduct policy

These Genie rooms are used by the app's tools to fetch live data and answer user questions.

### 2. **LLM (Large Language Model)**
- The app uses a Databricks-hosted LLM, specified by the `DATABRICKS_MODEL` environment variable.
- The LLM is accessed via the OpenAI-compatible API endpoint provided by Databricks.
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

