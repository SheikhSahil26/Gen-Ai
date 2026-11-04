"""Check Ollama Cloud chat and tool-call compatibility before deployment."""

import asyncio
import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from ecommerce_ai.classifiers.intent_classifier import (
    INTENT_CLASSIFICATION_PROMPT,
    IntentClassification,
    IntentClassifier,
)
from ecommerce_ai.config.settings import settings
from ecommerce_ai.llm import create_chat_model


@tool
def deployment_connection_check() -> str:
    """Return a fixed status string to verify model tool calling."""
    return "connection check passed"


async def main() -> None:
    if not settings.ollama_api_key:
        raise SystemExit(
            "OLLAMA_API_KEY is missing. Add your Ollama Cloud API key to .env, then retry."
        )

    classifier = IntentClassifier()
    classifier_response = await classifier.model.ainvoke(
        [
            SystemMessage(content=INTENT_CLASSIFICATION_PROMPT),
            HumanMessage(content="Show me a laptop under 70000"),
        ]
    )
    try:
        IntentClassification.model_validate_json(classifier_response.content)
    except (ValueError, TypeError) as error:
        raise RuntimeError("Classifier response was not valid intent JSON.") from error
    print("Classifier request succeeded and returned valid intent JSON.")

    tool_model = create_chat_model().bind_tools(
        [deployment_connection_check],
        tool_choice="required",
    )
    tool_response = await tool_model.ainvoke(
        "Call deployment_connection_check now. Do not answer without calling it."
    )
    if not any(
        call.get("name") == "deployment_connection_check"
        for call in tool_response.tool_calls
    ):
        raise RuntimeError("The model did not return the requested tool call.")
    print("Tool-call request succeeded.")


if __name__ == "__main__":
    asyncio.run(main())
