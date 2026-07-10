# Effectiveness Guide for Agents Using the Navaia CLI

> This document outlines patterns and practices for running large language model agents effectively through the Navaia command-line interface. It is applicable across workforce types and business domains.

---

## 1. The Orchestrator Pattern

Every workforce contains an orchestrator agent. The orchestrator holds the capability map of all other agents, receives incoming tasks, parses them, and delegates sub-tasks to the appropriate domain agents. The orchestrator does not execute domain work itself; its role is routing, tracking, and escalation.

When you spawn a session through the Navaia CLI, the orchestrator is your entry point. Communicate the task clearly and let it handle decomposition and delegation. If the orchestrator asks clarifying questions, answer them — the precision gained at this step prevents wasted execution later.

---

## 2. Tool Call Discipline

The Navaia CLI mediates all tool calls between the agent and the runtime. The interaction layer between the agent and the CLI has known failure modes. Adhering to the following discipline significantly reduces the likelihood of stalled or looping sessions.

### Single-Purpose Calls

Submit one operation per tool call. A single tool call containing a multi-step script, chained commands, or conditional logic is more likely to fail serialisation. Split the work into multiple sequential calls, each responsible for one unit of work.

### Avoid Retrying the Same Call

If a tool call fails with what appears to be a parsing or serialisation error, do not retry the identical call. The failure is unlikely to resolve on repetition. Instead, change the approach: break the operation into smaller parts, use a dedicated script file, or restructure the request.

### Prefer Scripts for Complex Operations

For any operation longer than a few lines, delegate to a pre-existing script rather than inlining logic into the tool call. Script files side-step whatever serialisation boundary causes failures in the interaction layer.

### Background Execution for Long-Running Tasks

Operations that involve external API calls, data imports, or network requests may exceed the runtime's timeout threshold and cause the session to enter a blocked state. Use the background execution flag when available, and poll for completion periodically. This prevents timeouts from halting the session.

---

## 3. Handling Blocked or Looping States

If a session appears stuck — repeating the same tool call, producing the same output, or not progressing for several turns — the most likely cause is a breakdown in the interaction layer, not an error in the agent's reasoning. The session will not self-correct through continued repetition.

When you detect a loop, intervene externally: kill the session, adjust the instruction, and restart. Adjustments that help include:

- Adding explicit constraints on tool call length and structure.
- Instructing the agent to stop and escalate if the same operation fails twice.
- Pre-decomposing the task into explicit sequential steps so the agent does not need to chain operations inside a single tool call.

---

## 4. Session Initialisation

At the start of each session, the agent should be given:

1. A clear statement of the task objective, not the method.
2. Reference to any relevant documentation or playbook files it should read first.
3. A cap on the number of retries or turns before escalation.
4. The identity and scope of the orchestrator agent it is reporting to.

The initial message should be concise. Overloading the first turn with excessive context can cause the agent to lose focus on the primary objective.

---

## 5. Error Handling Philosophy

Errors during execution are expected. What matters is the agent's response to them:

- A transient API error should be retried once or twice, then reported.
- A tool call serialisation error should never be retried — the approach must change.
- A missing credential or integration should be escalated to the orchestrator, not guessed or worked around.
- If the task specification is ambiguous, the agent should ask for clarification before proceeding, not guess.

Instruct the agent explicitly about which errors to retry and which to escalate. The default assumption should be escalation.

---

## 6. Context Boundaries

The agent's context window is finite. Long sessions accumulate tool outputs, file contents, and conversational history that push out earlier instructions. If the task involves many steps, consider:

- Breaking it into multiple independent sessions rather than one long session.
- Instructing the agent to summarise progress periodically so that if context is lost, the state can be reconstructed.
- Keeping reference documents external (files on disk) rather than inline in the conversation.

---

## 7. Security and Credentials

The agent should never output credentials, tokens, or secrets into the conversation or into files that could be committed. Credentials live in environment configuration, not in agent instructions or output. If a credential is missing, the agent escalates — it does not search for, guess, or reconstruct it.

---

## Summary of Key Practices

| Area | Practice |
|------|----------|
| Tool calls | One operation per call, no chains or pipes |
| Errors | Do not retry serialisation failures; escalate after one or two transient failures |
| Loops | Kill and restart with adjusted instructions; do not wait for self-correction |
| Orchestrator | Route all tasks through the orchestrator; it delegates, not executes |
| Context | Break long tasks into sessions; summarise progress externally |
| Credentials | Never output secrets; escalate if missing |