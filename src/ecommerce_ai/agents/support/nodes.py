from langchain_core.messages import HumanMessage

from ecommerce_ai.agents.support.prompts import (
    ANSWER_VALIDATION_PROMPT,
    RETRIEVAL_VALIDATION_PROMPT,
    SUPPORT_ANSWER_PROMPT,
    SUPPORT_QUERY_ANALYSIS_PROMPT,
)
from ecommerce_ai.schemas.support import (
    RetrievalValidation,
    SupportAnswerValidation,
    SupportQueryAnalysis,
)


def _parse_structured_output(text: str, schema):
    text = text.strip()
    try:
        return schema.model_validate_json(text)
    except Exception:
        pass
    if "```" in text:
        for block in text.split("```"):
            block = block.strip()
            if block.startswith("json"):
                block = block[4:].strip()
            try:
                return schema.model_validate_json(block)
            except Exception:
                pass
    data = {}
    alias_map = {
        "relevant and sufficient": "relevant",
        "is_relevant": "relevant",
        "is_grounded": "grounded",
        "grounded in knowledge": "grounded",
    }
    for line in text.splitlines():
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip().strip("-* ").lower()
            k = alias_map.get(k, k)
            v = v.strip().strip("\"'")
            if v.lower() == "true":
                v = True
            elif v.lower() == "false":
                v = False
            elif v.replace(".", "", 1).isdigit():
                try:
                    v = float(v)
                except Exception:
                    pass
            data[k] = v
    return schema.model_validate(data)


def create_understand_support_query_node(model):

    async def understand_support_query(state):

        query = state["messages"][-1].content

        prompt = (
            SUPPORT_QUERY_ANALYSIS_PROMPT
            + "\n\nUSER QUERY:\n"
            + query
            + "\n\nReturn ONLY a JSON object with fields: support_intent, search_query, requires_order_context, requires_product_context."
        )

        response = await model.ainvoke(
            [HumanMessage(content=prompt)]
        )

        result = _parse_structured_output(
            response.content, SupportQueryAnalysis
        )

        return {
            "original_query": query,
            "current_query": query,
            "support_intent": result.support_intent,
            "search_query": result.search_query,
            "requires_order_context": result.requires_order_context,
            "requires_product_context": result.requires_product_context,
        }

    return understand_support_query


def create_retrieve_knowledge_node(retriever):

    async def retrieve_knowledge(state):

        search_query = state["search_query"]

        documents = await retriever.ainvoke(
            search_query
        )

        retrieved_documents = []

        for document in documents:
            retrieved_documents.append(
                {
                    "content": document.page_content,
                    "metadata": document.metadata,
                }
            )

        return {
            "retrieved_documents": retrieved_documents,
        }

    return retrieve_knowledge


def create_validate_retrieval_node(model):

    async def validate_retrieval(state):

        query = state["current_query"]

        documents = state.get(
            "retrieved_documents",
            [],
        )

        if not documents:
            return {
                "relevant_documents": [],
                "retrieval_confidence": 0.0,
                "can_resolve": False,
                "requires_escalation": True,
                "escalation_reason": (
                    "No relevant support knowledge was found."
                ),
            }

        knowledge = "\n\n".join(
            document["content"]
            for document in documents
        )

        prompt = (
            RETRIEVAL_VALIDATION_PROMPT.format(
                query=query,
                knowledge=knowledge,
            )
            + "\n\nReturn ONLY a JSON object with fields: relevant (boolean), confidence (float between 0 and 1), reason (string)."
        )

        response = await model.ainvoke(
            [HumanMessage(content=prompt)]
        )

        result = _parse_structured_output(
            response.content, RetrievalValidation
        )

        if not result.relevant:
            return {
                "relevant_documents": [],
                "retrieval_confidence": result.confidence,
                "can_resolve": False,
                "requires_escalation": True,
                "escalation_reason": result.reason,
            }

        return {
            "relevant_documents": documents,
            "retrieval_confidence": result.confidence,
            "can_resolve": True,
            "requires_escalation": False,
        }

    return validate_retrieval


def create_generate_answer_node(model):

    async def generate_answer(state):

        query = state["current_query"]

        documents = state.get(
            "relevant_documents",
            [],
        )

        knowledge = "\n\n".join(
            document["content"]
            for document in documents
        )

        product_context = state.get(
            "active_product_context"
        )

        order_context = state.get(
            "active_order_context"
        )

        prompt = SUPPORT_ANSWER_PROMPT.format(
            query=query,
            knowledge=knowledge,
            product_context=product_context,
            order_context=order_context,
        )

        response = await model.ainvoke(
            [HumanMessage(content=prompt)]
        )

        citations = [
            document["metadata"]
            for document in documents
        ]

        return {
            "grounded_answer": response.content,
            "citations": citations,
        }

    return generate_answer


def create_validate_answer_node(model):

    async def validate_answer(state):

        answer = state.get(
            "grounded_answer",
            "",
        )

        documents = state.get(
            "relevant_documents",
            [],
        )

        knowledge = "\n\n".join(
            document["content"]
            for document in documents
        )

        product_context = state.get(
            "active_product_context"
        )

        order_context = state.get(
            "active_order_context"
        )

        prompt = (
            ANSWER_VALIDATION_PROMPT.format(
                query=state["current_query"],
                knowledge=knowledge,
                product_context=product_context,
                order_context=order_context,
                answer=answer,
            )
            + "\n\nReturn ONLY a JSON object with fields: grounded (boolean), confidence (float between 0 and 1), requires_escalation (boolean), reason (string)."
        )

        response = await model.ainvoke(
            [HumanMessage(content=prompt)]
        )

        result = _parse_structured_output(
            response.content, SupportAnswerValidation
        )

        if not result.grounded:
            return {
                "can_resolve": False,
                "requires_escalation": True,
                "escalation_reason": result.reason,
            }

        if result.requires_escalation:
            return {
                "can_resolve": False,
                "requires_escalation": True,
                "escalation_reason": result.reason,
            }

        return {
            "can_resolve": True,
            "requires_escalation": False,
        }

    return validate_answer


def create_escalation_node():

    async def escalation(state):

        reason = state.get(
            "escalation_reason"
        )

        answer = (
            "I don't have enough verified information "
            "to resolve this issue automatically."
        )

        if reason:
            answer += (
                f" The issue requires further support "
                f"because: {reason}"
            )

        return {
            "grounded_answer": answer,
            "requires_escalation": True,
            "can_resolve": False,
        }

    return escalation
