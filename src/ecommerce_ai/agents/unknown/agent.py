from ecommerce_ai.llm import create_chat_model
from ecommerce_ai.agents.unknown.graph import create_unknown_graph

def create_unknown_agent():
    model = create_chat_model(temperature=0.3)
    return create_unknown_graph(model)
