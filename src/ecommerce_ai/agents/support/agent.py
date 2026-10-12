from langchain_ollama import ChatOllama

from ecommerce_ai.agents.support.graph import (
    create_support_graph,
)


def create_support_agent():

    model = ChatOllama(
        model="gpt-oss:120b-cloud",
        temperature=0,
    )

    return create_support_graph(
        model=model,
    )