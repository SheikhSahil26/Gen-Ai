from ecommerce_ai.graph.graph import app_graph


def test_product_request():
    result = app_graph.invoke(
        {
            "user_input": "Show me a laptop",
            "intent": "unknown",
            "response": "",
        }
    )

    assert result["intent"] == "product"
    assert result["response"] == "Product workflow selected."


def test_shopping_request():
    result = app_graph.invoke(
        {
            "user_input": "Add this to my cart",
            "intent": "unknown",
            "response": "",
        }
    )

    assert result["intent"] == "shopping"


def test_order_request():
    result = app_graph.invoke(
        {
            "user_input": "Where is my order?",
            "intent": "unknown",
            "response": "",
        }
    )

    assert result["intent"] == "order"


def test_support_request():
    result = app_graph.invoke(
        {
            "user_input": "My product arrived damaged",
            "intent": "unknown",
            "response": "",
        }
    )

    assert result["intent"] == "support"