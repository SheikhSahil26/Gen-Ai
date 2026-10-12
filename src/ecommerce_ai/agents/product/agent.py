from langchain_ollama import ChatOllama

from ecommerce_ai.repositories.product_repository import (
    ProductRepository,
)
from ecommerce_ai.tools.product_tools import (
    create_product_tools,
)


def create_product_agent(
    repository: ProductRepository,
):

    tools = create_product_tools(
        repository
    )

    model = ChatOllama(
        model="gpt-oss:120b-cloud",
        temperature=0,
    )

    model_with_tools = model.bind_tools(
        tools
    )

    return model_with_tools, tools