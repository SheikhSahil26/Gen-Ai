from langchain_ollama import ChatOllama

from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.repositories.shopping_repository import ShoppingRepository
from ecommerce_ai.tools.shopping_tools import create_shopping_tools


def create_shopping_agent(repository: ShoppingRepository, product_repository: ProductRepository):
    tools = create_shopping_tools(repository, product_repository)
    model = ChatOllama(model="gpt-oss:120b-cloud", temperature=0)
    return model.bind_tools(tools), tools
