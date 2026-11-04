from ecommerce_ai.llm import create_chat_model

from ecommerce_ai.agents.support.graph import (
    create_support_graph,
)


def create_support_agent():

    model = create_chat_model(temperature=0)

    return create_support_graph(
        model=model,
    )
