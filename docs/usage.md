# Setup & Usage

## Prerequisites

1.  **Python 3.10+**
2.  **API Key:** A **Google Gemini API Key** is required for the models used in the primary `main.py` script. Free tiers are available at Google AI Studio.
3.  **Virtual Environment:** Highly recommended to prevent dependency conflicts.

---

## 1. Installation

It is recommended to set up and activate a virtual environment (`venv`) in your project's root folder before installing dependencies.

    # 1. Activate your environment (Mac/Linux example)
    source venv/bin/activate

    # 2. Install core dependencies
    # This includes LangChain, LangGraph, Google GenAI, and Community tools.
    pip install langchain langchain-community langchain-google-genai langgraph

---

## 2. Environment Setup

The application uses the `GOOGLE_API_KEY` environment variable to authenticate with the Gemini API. Set this key in your terminal session before running the script.

    export GOOGLE_API_KEY="AIzaSy...your_secret_key"

---

## 3. Database Setup (Sakila Testbed)

The AEGIS agents operate on the **Sakila sample database** for realistic testing scenarios. You must run the utility script (`python3 utility/create_db.py`) to download the schema and populate the `data/sakila.db` file before starting the agent. 

[Image of Sakila database schema diagram]


    # Run this script from the root AEGIS directory
    python3 utility/create_db.py

---

## 4. Running AEGIS

The current implementation focuses on the **Interaction Agent**.

### Start the Agent

Run the primary application script:

    python3 src/main.py

### Example Interaction

You can now interact with your **Interaction Agent** using natural language:

| Query | Expected Action |
| :--- | :--- |
| `How many actors have the first name 'JOE'?` | Agent calls the `sql_db_query` tool to run a SQL query. |
| `What is the longest film in the database?` | Agent calls the `sql_db_query` tool. |
| `Tell me a joke.` | Agent responds directly using the LLM without calling a tool. |