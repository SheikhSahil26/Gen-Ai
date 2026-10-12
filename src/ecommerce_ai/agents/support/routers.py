def route_after_retrieval(state) -> str:

    if state.get("requires_escalation"):
        return "escalate"

    if state.get("can_resolve"):
        return "generate_answer"

    return "escalate"


def route_after_answer_validation(state) -> str:

    if state.get("requires_escalation"):
        return "escalate"

    if state.get("can_resolve"):
        return "end"

    return "escalate"