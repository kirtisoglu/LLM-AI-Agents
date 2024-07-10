

import os


# Access environment variables
langchain_tracing = os.getenv('LANGCHAIN_TRACING_V2')
langchain_api_key = os.getenv('LANGCHAIN_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')



from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from IPython.display import Image, display


class State(TypedDict):
    
    """
    Class of StateGraph. A StateGraph object defines the structure of our chatbot as a state machine.
    We add nodes to represent the llm and functions our chatbot can call and edges to specify how 
    the bot should transition between these functions.
    
    :param TypedDict: State
    :type TypedDict: Dict
    """
    
    # Messages have the type "list". The `add_messages` function in the annotation defines how this state key 
    # should be updated (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# Choose a chatbot (LLM) and add it to the graph as node
llm = ChatAnthropic(model="claude-3-haiku-20240307")


def chatbot(state: State):
    "Chatbot node function that takes the current State as input and returns an updated messages list"
    # The first argument is the unique node name. The second argument is the function or 
    # object that will be called whenever the node is used.
    return {"messages": [llm.invoke(state["messages"])]}

# add an entry point. This tells our graph where to start its work each time we run it.
graph_builder.add_node("chatbot", chatbot)

# Set a finish point. This instructs the graph "any time this node is run, you can exit.
graph_builder.add_edge("chatbot", END)

#This creates a CompiledGraph we can use invoke on our state.
graph = graph_builder.compile()


# visualize the graph using the get_graph method and one of the "draw" methods, like draw_ascii or draw_png.
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass


# Run the chatbot. You can exit chat loop at any time by typing "quit", "exit", or "q".
while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            
        
            
# 2. Enhancing the Chatbot with Tools
import getpass

from langchain_community.tools.tavily_search import TavilySearchResults

os.environ["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"] = getpass.getpass()


tool = TavilySearchResults(max_results=2)
tools = [tool]
#tool.invoke("What's a 'node' in LangGraph?")


 # Adding Memory to the Chatbot