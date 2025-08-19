def run(state):
    # MVP: pretend we ran policies; enforce simple rule in code
    violations = []
    if state.get("plan", {}).get("public"):
        violations.append("Service must not be public in MVP")
    state["reports"]["policy"] = {"violations": violations}
    return state