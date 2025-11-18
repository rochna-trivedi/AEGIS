import sqlite3
import os
from typing import TypedDict, List
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.agents import create_sql_agent, AgentExecutor
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI

# --- Environment Setup (IMPORTANT) ---
# Make sure to set your OpenAI API key in your environment variables
# os.environ["OPENAI_API_KEY"] = "your_api_key_here"

# --- 1. Connect to your Sakila Database ---
DB_FILE = "sakila.db"
if not os.path.exists(DB_FILE):
    print(f"Error: Database file '{DB_FILE}' not found.")
    print("Please run the 'create_db.py' script first.")
    exit()
    
# Initialize the LangChain SQLDatabase connector
# This doesn't load the whole DB, just connects to it
db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")

# --- 2. Create the Interaction Agent ---

# Define the LLM we'll use. 
# gpt-4-turbo is excellent for SQL generation
# 2. LLM Setup
api_version = "2024-02-01"
model_name = "gpt-4"
llm = AzureChatOpenAI(model=model_name, azure_deployment=model_name, api_version=api_version, max_tokens=2000, temperature=0.0)

# Create the pre-built LangChain SQL Agent
# This agent already knows how to use tools to:
# 1. See the database schema
# 2. Write a SQL query
# 3. Execute the query
# 4. Get the answer and respond
sql_agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",
    verbose=True, # Set to True to see the agent's thoughts
    handle_parsing_errors=True # Robustness for SQL syntax errors
)

# --- 3. Define the LangGraph State ---

# This is the "memory" of our graph.
# It will pass the user's question to the agent.
class AgentState(TypedDict):
    question: str
    answer: str

# --- 4. Define the Graph Nodes ---

# We only have one node: the interaction agent
def run_interaction_agent(state: AgentState):
    """Runs the SQL agent to answer the user's question."""
    print("--- 🤖 INTERACTION AGENT ---")
    question = state["question"]
    
    # Invoke the agent executor
    # The agent will think, run SQL, and get the result
    result = sql_agent_executor.invoke({"input": question})
    
    return {"answer": result["output"]}

# --- 5. Build the Graph ---

# This is the simplest possible graph: START -> agent -> END
workflow = StateGraph(AgentState)

# Add our single node
workflow.add_node("interaction_agent", run_interaction_agent)

# Set the entry point
workflow.set_entry_point("interaction_agent")

# Add the exit point
workflow.add_edge("interaction_agent", END)

# Compile the graph into a runnable app
app = workflow.compile()

# --- 6. Test the Agent ---
print("--- 🚀 AEGIS Agent is Ready (Read-Only) ---")
print("Ask me questions about the Sakila database. Type 'exit' to quit.")

while True:
    user_input = input("\n👤 User: ")
    if user_input.lower() == 'exit':
        break
        
    try:
        # Run the graph
        full_state = app.invoke({"question": user_input})
        
        # Print the final answer
        print(f"\n🤖 AEGIS: {full_state['answer']}")
        
    except Exception as e:
        print(f"\n💥 Error: {e}")