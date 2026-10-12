from ecommerce_ai.graph.state import EcommerceState

VALID_TASKS = {
    "product",
    "shopping",
    "order",
    "support",
    "unknown",
    "end",
}


def route_next_task(state: EcommerceState) -> str:

    next_task = state.get(
        "next_worker",
        "end",
    )

    if next_task not in VALID_TASKS:
        raise ValueError(
            f"Invalid next worker: {next_task}"
        )

    return next_task