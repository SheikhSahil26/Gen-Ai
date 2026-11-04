from ecommerce_ai.llm import create_chat_model
from ecommerce_ai.repositories.order_repository import OrderRepository
from ecommerce_ai.repositories.shopping_repository import ShoppingRepository
from ecommerce_ai.tools.order_tools import create_order_tools


def create_order_agent(
    repository: OrderRepository,
    shopping_repository: ShoppingRepository | None = None,
):
    tools = create_order_tools(repository, shopping_repository)
    model = create_chat_model(temperature=0)
    return model.bind_tools(tools), tools
