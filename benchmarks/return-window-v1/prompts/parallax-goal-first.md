# Frozen prompt: Parallax goal-first multi-model workflow

Repair the project in your working directory from `BUSINESS_GOAL.md`.

Claude and Codex must independently interpret the original goal and identify assumptions, risks,
and boundary cases before either model treats `SPEC.md`, the implementation, or visible tests as
authority. Compare the two problem models, challenge disagreements, and converge on an agreed
behavioral contract. Only then update the implementation and visible tests. Have the model that
did not own the final implementation audit it independently from the original goal. Run the
visible tests and preserve commands, decisions, disagreements, and final evidence in the report.

Do not read files outside the working directory. Do not look for hidden tests or benchmark
material.

