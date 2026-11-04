from ecommerce_ai.llm import create_chat_model
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

    model = create_chat_model(temperature=0)

    model_with_tools = model.bind_tools(
        tools
    )

    return model_with_tools, tools
