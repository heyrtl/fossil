# FOSSIL + LangChain

LangChain is the most widely used Python agent framework. FOSSIL integrates directly via the Python SDK — no MCP required.

---

## Install

```bash
pip install openfossil[local] langchain
```

---

## Basic integration

```python
from fossil import Fossil, FailureType, ResolutionType, Severity, TaskDomain, format_for_injection
from langchain.chat_models import init_chat_model
from langchain.schema import SystemMessage, HumanMessage

fossil = Fossil()

def run_with_fossil(task: str, base_system: str) -> str:
    # search before acting
    results = fossil.search(task, top_k=3, min_score=0.5)
    fossil_context = format_for_injection(results)

    system = base_system + "\n\n" + fossil_context if fossil_context else base_system

    llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")
    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=task),
    ])
    return response.content
```

---

## With error handling and auto-recording

```python
import re
import json
from fossil import Fossil, FailureType, ResolutionType, Severity, TaskDomain, format_for_injection

fossil = Fossil()

def extract_json(task: str, llm) -> dict:
    situation = f"extracting structured JSON from LLM response: {task[:100]}"

    # search FOSSIL first
    results = fossil.search(situation, top_k=2, min_score=0.5)
    context = format_for_injection(results)

    system = (
        "Extract the requested fields as a JSON object. "
        "Do not wrap output in markdown fences.\n\n" + context
    )

    response = llm.invoke(system + "\n\n" + task)
    raw = response.content

    # sanitize and parse
    cleaned = re.sub(r"^```[a-z]*\n?|```$", "", raw.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # record the failure
        fossil.record(
            situation=situation,
            failure_type=FailureType.FORMAT_FAILURE,
            failure=f"JSONDecodeError on output: {raw[:200]}",
            severity=Severity.MAJOR,
            resolution_type=ResolutionType.INPUT_SANITIZATION,
            resolution="strip markdown fences before parsing",
            framework="langchain",
            model="llama-3.3-70b-versatile",
            domain=TaskDomain.DATA_ANALYSIS,
        )
        raise
```

---

## With LangGraph

```python
from langgraph.graph import StateGraph
from fossil import Fossil, format_for_injection
from typing import TypedDict

fossil = Fossil()

class AgentState(TypedDict):
    task: str
    fossil_context: str
    result: str

def fossil_search_node(state: AgentState) -> AgentState:
    results = fossil.search(state["task"], top_k=3, min_score=0.5)
    state["fossil_context"] = format_for_injection(results)
    return state

def agent_node(state: AgentState) -> AgentState:
    system = "You are a helpful agent.\n\n" + state["fossil_context"]
    # ... run LLM with system prompt
    state["result"] = "..."
    return state

graph = StateGraph(AgentState)
graph.add_node("fossil_search", fossil_search_node)
graph.add_node("agent", agent_node)
graph.add_edge("fossil_search", "agent")
graph.set_entry_point("fossil_search")

app = graph.compile()
app.invoke({"task": "extract fields from this invoice", "fossil_context": "", "result": ""})
```

---

## Using the remote API (no local model)

```python
fossil = Fossil(api_url="https://fossil-api.hello-76a.workers.dev")
```

Drop-in replacement. No `sentence-transformers` or `torch` needed.

---

## Common LangChain failure patterns

| Situation | Failure type |
|---|---|
| Chain output doesn't match Pydantic model | `format_failure` |
| Agent called wrong tool from tool list | `hallucinated_tool` |
| Memory not passed correctly between chain steps | `context_loss` |
| Agent loops on the same tool call | `infinite_loop` |
| Output parser raises on valid but unexpected format | `format_failure` |