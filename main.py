import sqlite3
import os
import operator
from typing import Annotated, TypedDict, List

# --- Imports for LangChain ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage

# --- Imports for LangGraph ---
# Note: We are NOT importing ToolNode anymore to avoid your error
from langgraph.graph import StateGraph, END, START

# --- 1. Environment & Database Setup ---
# os.environ["GOOGLE_API_KEY"] = "Your-Key-Here" 

DB_FILE = "sakila.db"
if not os.path.exists(DB_FILE):
    print(f"Error: Database file '{DB_FILE}' not found. Run create_db.py first.")
    exit()

db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")

# --- 2. Define the Tools & LLM ---

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

# Create a dictionary for easy tool lookup (needed for our manual node)
tools_by_name = {tool.name: tool for tool in tools}

llm_with_tools = llm.bind_tools(tools)

# --- 3. Define the Graph State ---

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# --- 4. Define the Nodes (Manually) ---

def call_model(state: AgentState):
    """The 'Brain' node: sends history to Gemini and gets a response."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    """
    The Manual 'Tool' node.
    This replaces 'from langgraph.prebuilt import ToolNode'
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    results = []
    
    # Iterate over all tool calls requested by the LLM
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        print(f"   🛠️  Agent is calling tool: {tool_name}...")
        
        # 1. Find the tool
        if tool_name not in tools_by_name:
            result = f"Error: Tool '{tool_name}' not found."
        else:
            # 2. Run the tool
            try:
                tool_instance = tools_by_name[tool_name]
                result = tool_instance.invoke(tool_args)
            except Exception as e:
                result = f"Error executing tool: {e}"
        
        # 3. Create a message acting as the tool's output
        results.append(ToolMessage(
            tool_call_id=tool_call["id"],
            name=tool_name,
            content=str(result)
        ))
        
    return {"messages": results}

def should_continue(state: AgentState):
    """The 'Decision' logic."""
    last_message = state["messages"][-1]
    
    # If the LLM returned a tool call, go to our manual 'tool_node'
    if last_message.tool_calls:
        return "tools"
    # Otherwise, stop
    return END

# --- 5. Build the Graph ---

workflow = StateGraph(AgentState)

# Add the two nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node) # We use our manual function here

# Define the edges
workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

app = workflow.compile()

# --- 6. Run the Chatbot ---
print("--- 🚀 AEGIS Agent (Manual Node) is Ready ---")
print("Ask questions about 'sakila.db'. Type 'exit' to quit.")

sys_msg = SystemMessage(content="You are a helpful SQL assistant. You have access to a database. Use the tools to answer user questions.")

while True:
    user_input = input("\n👤 User: ")
    if user_input.lower() == 'exit':
        break
        
    initial_state = {"messages": [sys_msg, HumanMessage(content=user_input)]}
    
    try:
        # We use stream to see the steps, but we just print the final answer at the end
        final_response = None
        
        for event in app.stream(initial_state):
            # Capture the latest message from the agent node
            if "agent" in event:
                final_response = event["agent"]["messages"][0].content
        
        print(f"\n🤖 AEGIS: {final_response}")
        
    except Exception as e:
        print(f"Error: {e}")