from langgraph.graph import END, START, StateGraph

from ecommerce_ai.agents.support.nodes import (
    create_escalation_node,
    create_generate_answer_node,
    create_retrieve_knowledge_node,
    create_understand_support_query_node,
    create_validate_answer_node,
    create_validate_retrieval_node,
)
from ecommerce_ai.agents.support.routers import (
    route_after_answer_validation,
    route_after_retrieval,
)
from ecommerce_ai.agents.support.state import SupportAgentState
from ecommerce_ai.rag.retriever import get_support_retriever


def create_support_graph(model):

    retriever = get_support_retriever()

    graph = StateGraph(
        SupportAgentState
    )

    graph.add_node(
        "understand_support_query",
        create_understand_support_query_node(model),
    )

    graph.add_node(
        "retrieve_knowledge",
        create_retrieve_knowledge_node(retriever),
    )

    graph.add_node(
        "validate_retrieval",
        create_validate_retrieval_node(model),
    )

    graph.add_node(
        "generate_answer",
        create_generate_answer_node(model),
    )

    graph.add_node(
        "validate_answer",
        create_validate_answer_node(model),
    )

    graph.add_node(
        "escalate",
        create_escalation_node(),
    )

    graph.add_edge(
        START,
        "understand_support_query",
    )

    graph.add_edge(
        "understand_support_query",
        "retrieve_knowledge",
    )

    graph.add_edge(
        "retrieve_knowledge",
        "validate_retrieval",
    )

    graph.add_conditional_edges(
        "validate_retrieval",
        route_after_retrieval,
        {
            "generate_answer": "generate_answer",
            "escalate": "escalate",
        },
    )

    graph.add_edge(
        "generate_answer",
        "validate_answer",
    )

    graph.add_conditional_edges(
        "validate_answer",
        route_after_answer_validation,
        {
            "end": END,
            "escalate": "escalate",
        },
    )

    graph.add_edge(
        "escalate",
        END,
    )

    return graph.compile()