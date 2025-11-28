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

DB_FILE = "data/sakila.db"
if not os.path.exists(DB_FILE):
    print(f"Error: Database file '{DB_FILE}' not found. Run create_db.py first.")
    exit()

db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")

# --- 2. Initialize LLM and Tools (Lazy Loading) ---
# These will be initialized only when the FastAPI app starts
llm = None
toolkit = None
tools = None
tools_by_name = None
llm_with_tools = None

def initialize_llm():
    """Initialize LLM and tools. Called at FastAPI startup."""
    global llm, toolkit, tools, tools_by_name, llm_with_tools
    
    if llm is not None:
        return  # Already initialized
    
    print("🚀 Initializing LLM and tools...")
    
    # Check if API key is set
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError(
            "GOOGLE_API_KEY environment variable not set. "
            "Please set it before starting the server: export GOOGLE_API_KEY=your_key"
        )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
    )
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    
    # Create a dictionary for easy tool lookup (needed for our manual node)
    tools_by_name = {tool.name: tool for tool in tools}
    
    llm_with_tools = llm.bind_tools(tools)
    
    print(f"✅ LLM initialized with {len(tools)} tools")

# --- 3. Define the Graph State ---

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# --- 4. Define the Nodes (Manually) ---

def call_model(state: AgentState):
    """The 'Brain' node: sends history to Gemini and gets a response."""
    if llm_with_tools is None:
        raise RuntimeError("LLM not initialized. Make sure GOOGLE_API_KEY is set.")
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    """
    The Manual 'Tool' node.
    This replaces 'from langgraph.prebuilt import ToolNode'
    """
    if tools_by_name is None:
        raise RuntimeError("Tools not initialized. Make sure GOOGLE_API_KEY is set.")
    
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

# --- 5. Build the Graph (will be initialized at startup) ---

def build_graph():
    """Build the LangGraph workflow. Called after LLM is initialized."""
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
    
    return workflow.compile()

app = None  # Will be initialized at startup

app = None  # Will be initialized at startup

# --- Replace the old console loop with FastAPI setup ---

from fastapi import FastAPI
from contextlib import asynccontextmanager

# Define a simple Pydantic model for the request (optional but recommended)
# from pydantic import BaseModel
# class ChatRequest(BaseModel):
#     question: str

@asynccontextmanager
async def lifespan(app_service: FastAPI):
    """Lifespan context for FastAPI startup and shutdown."""
    # Startup: Initialize LLM and build graph
    global app
    initialize_llm()
    app = build_graph()
    print("✅ FastAPI app ready!")
    yield
    # Shutdown logic here if needed
    print("🛑 FastAPI app shutting down...")

# Initialize FastAPI application with lifespan
app_service = FastAPI(
    title="AEGIS Interaction Agent API",
    description="Exposes the LangGraph AEGIS Interaction Agent as a service.",
    lifespan=lifespan,
)

@app_service.post("/chat")
async def chat_endpoint(question: str):
    """Chat endpoint that uses the LangGraph agent to answer questions."""
    if app is None:
        return {"response": "Error: Agent not initialized. Check server logs."}
    
    # Use the same system instruction as before
    sys_msg = SystemMessage(content="You are a helpful SQL assistant. You have access to a database. Use the tools to answer user questions.")
    
    # Run the graph with the new user input
    initial_state = {"messages": [sys_msg, HumanMessage(content=question)]}
    
    final_response = "Error: Could not process request."
    
    # Run the stream to execute the graph
    try:
        # NOTE: Using a simple invoke() might be easier than stream() for a basic API endpoint
        final_state = app.invoke(initial_state)
        
        # Get the content of the last message (which is the final answer)
        final_response = final_state["messages"][-1].content
        
        return {"response": final_response}

    except Exception as e:
        print(f"Error executing graph: {e}")
        return {"response": f"An error occurred: {str(e)}"}

@app_service.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "AEGIS Agent API is running"}

if __name__ == "__main__":
    # Remove the old console loop and replace with uvicorn start command
    # You will run this from your terminal later: uvicorn src.main:app_service --reload
    print("Agent initialized. Run 'uvicorn src.main:app_service --reload' to start the server.")