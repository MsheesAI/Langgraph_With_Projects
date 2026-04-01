# AI Workflow Types

## Linear

Linear workflows are the simplest form of AI orchestration — a sequence of steps where each task depends on the output of the one before it. Think of it as an assembly line: the model reads a document, then summarizes it, then translates that summary, and finally formats it as a report. Each stage waits for the previous one to finish before it begins. This approach is easy to reason about and debug, but it can be slow, since tasks are never processed in parallel. Linear workflows are best suited for tasks with strict dependencies, where the order of operations fundamentally shapes the outcome.

## Parallel

Parallel workflows address the speed problem by splitting independent tasks across multiple agents or model calls simultaneously. If you need to analyze five research papers, there's no reason to read them one by one — you can dispatch five concurrent requests and collect all the results at once. This can dramatically reduce latency and is particularly effective in data processing pipelines, batch document handling, and anything where subtasks share no dependencies. The challenge lies in orchestrating the final aggregation step, where all parallel outputs must be merged intelligently into a coherent result.

## Branching

Branching workflows introduce conditional logic, allowing the AI system to take different paths depending on context or intermediate outputs. A customer support system might classify an incoming query first, then route it to a specialist agent — one branch for billing issues, another for technical support, another for general inquiries. This mirrors how human teams operate, with a triage layer deciding who handles what. Branching workflows can become complex quickly, especially when branches themselves branch further, so clear state management and well-defined exit conditions are essential to prevent the system from getting lost in a maze of conditions.

## Loop / Iterative

Loop and iterative workflows are particularly powerful for tasks that require self-correction or refinement over multiple passes. An AI might draft a piece of code, run it, observe the error, revise the code, and test again — repeating until the output meets a defined standard. This kind of feedback loop mimics how humans refine their work over time and is central to agentic AI systems. The risk, however, is runaway loops where the model cycles indefinitely without converging. Robust loop workflows need clear stopping criteria, whether that's a maximum iteration count, a quality threshold, or an explicit human-in-the-loop checkpoint to break the cycle.
