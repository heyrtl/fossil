# FOSSIL + CrewAI

CrewAI is a multi-agent framework focused on role-based agent collaboration. FOSSIL integrates via the Python SDK as a tool or as a pre/post-task hook.

---

## Install

```bash
pip install openfossil[local] crewai
```

---

## As a CrewAI tool

Wrap FOSSIL search as a tool so any agent in your crew can call it:

```python
from crewai.tools import BaseTool
from fossil import Fossil, format_for_injection
from pydantic import BaseModel, Field

fossil = Fossil()

class FossilSearchInput(BaseModel):
    situation: str = Field(description="What is the agent about to attempt?")

class FossilSearchTool(BaseTool):
    name: str = "fossil_search"
    description: str = (
        "Search FOSSIL for similar past agent failures before attempting a task. "
        "Returns past failures and their resolutions as context."
    )
    args_schema: type[BaseModel] = FossilSearchInput

    def _run(self, situation: str) -> str:
        results = fossil.search(situation, top_k=3, min_score=0.5)
        if not results:
            return "No similar past failures found."
        return format_for_injection(results)
```

Add the tool to any agent:

```python
from crewai import Agent

researcher = Agent(
    role="Research Agent",
    goal="Extract structured data from documents",
    backstory="You are an expert at parsing and extracting information.",
    tools=[FossilSearchTool()],
    verbose=True,
)
```

---

## As a task callback

Record failures automatically using CrewAI task callbacks:

```python
from crewai import Task
from fossil import Fossil, FailureType, ResolutionType, Severity, TaskDomain

fossil = Fossil()

def on_task_failure(task_output):
    fossil.record(
        situation=task.description[:300],
        failure_type=FailureType.MISINTERPRETATION,
        failure=str(task_output)[:300],
        severity=Severity.MAJOR,
        resolution_type=ResolutionType.PROMPT_CHANGE,
        resolution="under investigation",
        framework="crewai",
        model="llama-3.3-70b-versatile",
        domain=TaskDomain.RESEARCH,
        verified=False,
    )

task = Task(
    description="Extract vendor, amount, and due date from the invoice.",
    expected_output="A JSON object with vendor, amount, due_date fields.",
    agent=researcher,
    callback=on_task_failure,
)
```

---

## Full crew example

```python
from crewai import Agent, Task, Crew, Process
from fossil import Fossil, format_for_injection

fossil = Fossil()

# inject fossil context into agent backstory
situation = "extracting structured fields from unstructured invoice text"
results = fossil.search(situation, top_k=2, min_score=0.5)
fossil_context = format_for_injection(results)

extractor = Agent(
    role="Data Extractor",
    goal="Extract structured data accurately from documents",
    backstory=f"You are a precise data extraction specialist.\n\n{fossil_context}",
    verbose=True,
)

task = Task(
    description="Extract vendor, amount, currency, due_date from this invoice: ...",
    expected_output="Valid JSON with all four fields",
    agent=extractor,
)

crew = Crew(
    agents=[extractor],
    tasks=[task],
    process=Process.sequential,
)

result = crew.kickoff()
```

---

## Using the remote API

```python
fossil = Fossil(api_url="https://fossil-api.hello-76a.workers.dev")
```

---

## Common CrewAI failure patterns

| Situation | Failure type |
|---|---|
| Agent completed only part of a multi-step task | `premature_termination` |
| Wrong agent picked up the task | `misinterpretation` |
| Agent exceeded its role and modified things it shouldn't | `scope_creep` |
| Two agents produced contradictory outputs | `compounding_error` |
| Agent couldn't proceed due to ambiguous task spec | `ambiguity_paralysis` |