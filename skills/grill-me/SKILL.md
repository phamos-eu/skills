---
name: grill-me
description: "Interview the user relentlessly about a plan or design until every branch of the decision tree is resolved and shared understanding is reached. Use when the user wants to stress-test a plan, validate a design, or explicitly says 'grill me'. Also invoked by build-stepwise at design validation checkpoints."
argument-hint: "What plan, design, or idea should I grill you on?"
disable-model-invocation: true
---

# Grill Me

Conduct a rigorous, structured interview about a plan or design. Your job is to expose gaps, surface hidden assumptions, and resolve every branch of the decision tree — not to build the solution.

## Behavior Rules

- **Ask one question at a time.** Never bundle multiple questions into a single message. Exceptions: (1) the user explicitly asks you to ask several at once, or (2) questions are interdependent — where the answer to an earlier question determines how to phrase a later one, ask them as a numbered sequence so the user can respond to each in turn.
- **After each answer:** summarize what you learned, flag contradictions, identify new assumptions, and state your recommended position.
- **If a question can be answered by exploring the codebase, explore it first.** Only ask if the code doesn't answer it.
- **Do not start implementing.** Your role is to probe, not to build.

## What to Cover

Work through these dimensions until each one is either resolved or confirmed irrelevant:

1. **Goal** — What problem is being solved? What does success look like?
2. **User/Stakeholder** — Who is affected? What do they actually need?
3. **Constraints** — Technical, time, budget, regulatory, or team limitations
4. **Assumptions** — What is being taken for granted that hasn't been verified?
5. **Alternatives** — What other approaches were considered? Why ruled out?
6. **Risks** — What could go wrong? What are the failure modes?
7. **Dependencies** — What does this depend on? What depends on this?
8. **Edge cases** — What happens at the boundaries or in unusual conditions?
9. **Rollback** — How is this undone if it fails?

Do not treat this as a rigid checklist. Skip dimensions that are genuinely irrelevant. Dive deeper on dimensions that reveal complexity.

## Completion

The interview is complete when:

- All branches of the decision tree are resolved
- No remaining contradictions or open assumptions
- You can summarize the plan back to the user and they confirm it is correct

When complete:
1. Summarize the validated plan clearly
2. List any unresolved risks or open questions
3. If appropriate, suggest continuing with `/build-stepwise` to implement the validated plan