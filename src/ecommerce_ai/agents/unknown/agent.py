from langchain_ollama import ChatOllama
from ecommerce_ai.agents.unknown.graph import create_unknown_graph

def create_unknown_agent():
    model = ChatOllama(model="gpt-oss:120b-cloud", temperature=0.3)
    return create_unknown_graph(model)
