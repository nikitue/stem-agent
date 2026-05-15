# STEM Agent: Autonomous Specialization in SRE Incident Response

## Setup & Execution Instructions

### Prerequisites
To run this simulation locally, you need Python 3.9+ and [Ollama](https://ollama.com/) installed on your machine to serve the local LLM.

1. **Install Ollama:** Download and install from ollama.com.
2. **Pull the Model:** The agent is tuned for the 8-billion parameter Llama 3.1 model. Pull it via your terminal:
   ```bash
   ollama pull llama3.1
   ```
3. **Install dependencies:** Ensure you are in the project directory and install the required Python packages (just the ollama package) using the provided requirements.txt file:
   ```pip install -r requirements.txt```
4. **Run the program** execute ```python main.py``` to start the program

The output is text in the console displaying the agent working on 10 runs (episodes) of tackling technical issues. The format is `THOUGHT` of the model, followed by the `ACTION` it takes, and then how the `SYSTEM` responds to it.

## Domain and Approach

The prompt challenged us to build an agent that becomes specific through its own process. I chose the DevOps/Site Reliability Engineering (SRE) incident triage domain. This domain mirrors how human engineers learn: we start by reading generic Runbooks (slow, exploratory), and eventually memorize the patterns to automate the fixes (fast, specialized).

#### What is it?
The environment is a deterministic mock of a microservices topology (`Frontend -> API Gateway -> Checkout -> Payment-DB & Redis-Cache`). It acts as the "world" for our agent, exposing external tools for **Observability** (e.g., `query_metrics`, `trace_dependencies`, reading runbooks) and **Actuation** (e.g., `rollback_deployment`, `scale_up_cache`).

#### How does it work?
When an episode starts, the environment generates a surface-level alert (e.g., *"USER REPORT: Users cannot complete checkout."*). However, beneath the surface, the environment randomizes the **hidden root cause** (either a Database lock or a Cache Out-of-Memory error). The agent cannot see the root cause; it must use its tools to diagnose the system state before acting.

### The Role of the Simulated DevOps Environment

In the context of this project, the "DevOps Environment" (`environment.py`) serves as the biological substrate—the specific conditions the stem agent must adapt to. Rather than hooking a local, experimental LLM into a live production cluster, we use a deterministic Python simulation that models a standard microservices topology (Frontend -> API Gateway -> Checkout -> DB/Cache). 

**How we use it:** The environment acts as a mock infrastructure API. It exposes standard SRE tooling to the agent via an MCP-inspired registry, allowing the agent to query metrics, trace service dependencies, check recent deployments, and actuate state changes (e.g., rolling back services or scaling caches).

**Why we use it:**
1. **Reproducibility for Evaluation:** To measure cognitive evolution objectively, the environment must be deterministic. It injects randomized underlying faults (e.g., a Database lock vs. a Cache OOM) that trigger the exact same surface-level alert. This ensures the agent learns a diagnostic *process*, not just a static answer.
2. **Safety and Apoptosis:** It acts as a strict referee. If the agent hallucinates or executes a destructive action (like rolling back a healthy database), the environment instantly returns a `CRITICAL FAILURE`. This triggers our Apoptosis safeguard, rejecting the episode and preventing the agent's memory pool from being poisoned by bad operational habits.
3. **Enforcing the "Stem" Metaphor:** A stem cell requires environmental signals to differentiate. By forcing the undifferentiated agent to query this specific mock architecture using standard observability tools, it learns the unique topology of *this* system, gradually transforming into a specialist tuned exclusively for this environment's failure modes.

Instead of hardcoding a state machine, the agent utilizes a multi-phase "ontogeny" loop:
* **The Progenitor Phase:** The agent explores the environment using Chain-of-Thought reasoning. Its system prompt binds it to a generic tool (`search_runbooks`). It reads the runbook, executes observability tools (`query_metrics`, `trace_dependencies`), and actuates fixes.
* **Episodic Memory Buffer:** The agent records its successful diagnostic pathways (Thought -> Action -> Observation).
* **Differentiation (Crystallization):** After consecutive successes, a `try_crystallize` meta-prompt analyzes the episodic memory to find diagnostic patterns. The agent synthesizes a new procedural rule to bypass the runbook entirely.
* **Safeguards (Apoptosis):** If the agent executes a destructive action (e.g., rolling back a healthy database), the environment returns a `CRITICAL FAILURE`. This triggers "Apoptosis," aborting the task and preventing the agent from crystallizing a dangerous rule into its memory.

## Experiments and Evaluation Method

To measure evolution objectively, I built an evaluation harness (`main.py`) that runs the agent through continuous simulated outages. The underlying root cause randomizes (Database Lock vs. Cache OOM), but the surface-level alert remains the same. 

The suite tracks four metrics to compare the Progenitor and Specialist phases:
1.  **Success Rate:** Proper resolution without triggering Apoptosis.
2.  **Steps per Task:** Diagnostic speed (Efficiency).
3.  **Runbook Reliance:** How often it queried documentation (Autonomy).
4.  **Critical Failures:** Execution of harmful actions.

**Before/After Comparison**
*Simulation run using local `llama3.1:8b` via Ollama.*

| Metric | Progenitor Phase (Initial) | Specialist Phase (Evolved) |
| :--- | :--- | :--- |
| **Total Episodes** | 4 | 6 |
| **Success Rate** | 75.0% | **16.7%** |
| **Steps / Task** | 4.5 | 4.8 |
| **Runbook Reliance** | 0.2 reads/task | 0.2 reads/task |

## Engineering Journey: Challenges & Solutions

**Challenge 1: Logic Ceilings and Syntax Failures**
I initially tested the loop on a 3-billion parameter model (`qwen2.5-coder:3b`). Its limited context window caused it to fail under complex reasoning. It generated valid thoughts but output malformed JSON (missing delimiters, wrapping JSON in markdown), crashing the pipeline. 
*Solution:* I built a markdown-safe regex extractor (`extract_json`) using a stack-based bracket counting method to tackle malformed outputs. Ultimately, I scaled to `llama3.1:8b`, which provided better adherence to JSON schemas while retaining the ability to navigate the environment.

**Challenge 2: Hallucinating the Architecture**
The early agent guessed at infrastructure. It hallucinated tool names (e.g., `run_diagnostic`) or guessed service names (querying `checkout` instead of `checkout-service`), leading to infinite cognitive loops where it checked the same broken metrics.
*Solution:* I implemented a strict `KNOWN SERVICES` registry injected directly into the system prompt and added explicit anti-looping guardrails. Grounding the LLM's reality reduced these hallucinations, but did not completely.

**Challenge 3: Runbook Ambiguity**
During the simulation, the database would lock up due to a bad checkout deployment. The runbook originally stated: *"If DB EXHAUSTED, check deployments and rollback."* The agent tried to roll back the database itself, worsening the outage.
*Solution:* I rewrote the environment runbooks to be deterministic, mimicking how SRE teams write strict Standard Operating Procedures (SOPs). This failure also proved the efficacy of the Apoptosis safety mechanism, as it successfully caught the critical failure and prevented the agent from learning a bad path.

## Analysis: What Failed and Why

While the experiment successfully proved the *mechanism* of evolution (the agent successfully triggered memory consolidation and wrote a rule), the Specialist Phase suffered a notable drop in reliability, succeeding only 16.7% of the time.

This highlighted a fundamental limitation in local 8B parameter models. The model lacked the reasoning capacity to apply its newly formed rule without the grounding context of the runbook. In the Progenitor phase, reading the runbook provided the model with exact string parameters (e.g., `checkout-service`). In the Specialist phase, attempting to act autonomously based purely on a single-sentence crystallized rule caused the model to hallucinate arguments or target the wrong services.

## What Surprised Me

I was surprised by how the model attempted to invent parameters during the memory consolidation phase. When analyzing its own successful episodes to create a procedural rule, the model would hallucinate arbitrary thresholds (e.g., `"if MAX > 90"` or `"latency > 500ms"`) that never existed in the raw JSON logs. This showed that Stem Agents require highly rigid, few-shot prompting to prevent their "differentiation" phase from generating fictional conditions. 

## What I Would Do With More Time

1. **Upgrade the Cognitive Engine:** The architecture requires a model with better instruction-following and JSON-schema constraints (e.g., GPT-4o with Structured Outputs) to navigate the Specialist phase without context degradation.
2. **Implement Skill Pruning (Negative Feedback):** Currently, the agent can write a skill, but it cannot unlearn it. I would implement a mechanism where if a crystallized skill triggers Apoptosis multiple times, the agent deletes the skill and reverts to a Progenitor state.
3. **Dynamic Tool Discovery:** Instead of hardcoding the Tool Registry, I would allow the agent to query a simulated API gateway to discover available tools dynamically, further aligning with the concept of an agent reading its environment before transforming.
4. **Read relevant research literature:** I found the very recent research paper "STEM Agent: A Self-Adapting, Tool-Enabled, Extensible Architecture for Multi-Protocol AI Agent Systems" (https://arxiv.org/pdf/2603.22359), which explores this exact concept of STEM Agents, and it could be perhaps the inspiration for the task. The agent they built consists of multiple production-level layers, which are currently out of my scope. However, I can try to adapt the STEM Cognitive Pipeline algorithm that they provided.
5. **Expand the environment:** Currently, the model works in a sandbox environment, and the interactions are very artificial for the project to be an actual agent. With more time, maybe I could establish a real database and a pipeline of simple tasks that the agent should monitor and act upon.
