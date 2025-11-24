import gradio as gr
import requests
import json

# Define the endpoint of your running FastAPI service
FASTAPI_ENDPOINT = "http://127.0.0.1:8000/chat"

def query_agent(message, history):
    """
    Sends the user message to the running FastAPI service and returns the response.
    """
    # FastAPI only takes the current question, so we ignore history for this simple demo
    
    # Prepare the data payload
    try:
        response = requests.post(
            FASTAPI_ENDPOINT, 
            # The FastAPI endpoint expects the question as a query parameter in this simple setup
            params={"question": message}
        )
        
        # Check if the API call was successful
        if response.status_code == 200:
            # Parse the JSON response
            api_response = response.json()
            return api_response.get("response", "Error: Response field missing from API.")
        else:
            return f"Error: API returned status code {response.status_code}. Response: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the FastAPI backend. Is the server running (uvicorn)? "
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


# Define the Gradio Chat Interface
if __name__ == "__main__":
    gr.ChatInterface(
        query_agent,
        title="AEGIS: Autonomous Database Chatbot (Interaction Agent)",
        description="Ask questions about the Sakila database. The agent translates your text to SQL.",
    ).launch()