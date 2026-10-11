# SE-AI-DATA-001 — Rights and Publication Gate

STATUS = `HUMAN_REVIEW_REQUIRED`

AUTO_PUBLISH_X = `NO`

AUTO_PUBLISH_ZHIHU = `NO`

DATASET_PUBLICATION = `PROHIBITED_WITHOUT_SEPARATE_AUTHORIZATION`

PRIVATE_DATA_INCLUDED = `NO`

OUTREACH_AUTHORIZED = `NO`

## Current rights boundary

The observation ledger and drafts use StructEvidence-authored normalized facts,
claim identifiers, states, timestamps, bounded factual paraphrases and links to
public sources. They do not copy full third-party articles, paywalled text,
customer data, private evidence or the complete Temporal Evidence dataset.

Public accessibility is not treated as permission to redistribute a complete
third-party work. Existing `SE_TEMPORAL_EVAL_SAMPLE/RIGHTS_AND_RELEASE.md`
continues to block external release of the dataset pending owner confirmation.

## Source checks for this cycle

| Material | Intended use | Public access checked | Distribution treatment |
| --- | --- | --- | --- |
| Chindata operator publication | Evidence link and short factual paraphrase | YES | Link and bounded paraphrase only |
| Siemens / Reinhausen release | Negative-boundary review | YES | Link and bounded paraphrase only |
| CATL public releases | Evidence links and short factual paraphrases | YES | Link and bounded paraphrase only |
| WHO DON620 | Evidence link and short factual paraphrase | YES | Link and bounded paraphrase only; no medical inference beyond source boundary |
| StructEvidence case pages | Link to public case state | YES | Link only |

## Mandatory human gate

Before any X or Zhihu publication, a human must approve all of the following for
the exact draft being published:

1. exact text and title;
2. factual claims and evidence cutoff;
3. rights treatment and source links;
4. destination account;
5. timing and whether publication should be skipped.

Approval of one item does not authorize another item, dataset publication,
private outreach, paid research or production changes.

X_DRAFTS = `PENDING_HUMAN_APPROVAL`

ZHIHU_DRAFT = `PENDING_HUMAN_APPROVAL`

PUBLICATIONS_MADE = `0`
