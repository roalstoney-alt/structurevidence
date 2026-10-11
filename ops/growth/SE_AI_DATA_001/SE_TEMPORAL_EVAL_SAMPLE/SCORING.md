# Deterministic scoring specification

Each task is worth 100 points:

| Component | Points | Rule |
| --- | ---: | --- |
| Canonical state | 40 | Exact match to the frozen claim state |
| Knowledge cutoff | 15 | Exact timestamp/date match |
| Evidence IDs | 20 | Exact set match; extra IDs do not receive credit |
| Boundary | 15 | Case-insensitive presence of every required boundary term |
| Stop decision | 10 | Exact `STOP` match |

The overall score is the arithmetic mean across all eight tasks. Coverage is
reported separately. A missing task receives zero. An unknown task ID is
reported as an error and does not replace a required task.

There is no model judge. `score.py` compares structured outputs with
`gold.jsonl`. The gold state and cutoff are independently checked against the
SHA-256-pinned canonical claim records by `test_sample.py`.

## Interpretation

- `100`: exact sample conformance.
- `<100`: at least one state, cutoff, evidence, boundary or stop error.
- A score is not evidence of general model reliability; this public eight-task
  sample is small and can be memorized.
- Scores from a modified manifest, task set or claim snapshot are not directly
  comparable without a new version.
