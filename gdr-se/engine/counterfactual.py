from __future__ import annotations


REQUIRED_FIELDS = ["falsifiers", "no_action_consequence", "rejected_alternative", "discriminating_evidence"]


def build_counterfactual(context) -> dict:
    return {
        "falsifiers": [
            f"New primary records contradict the current {context.display_label} finding.",
            "A correction or supersession record invalidates a material source or calculation.",
        ],
        "no_action_consequence": "Historical research may remain available, but current release or paid delivery remains blocked until runtime gates resolve.",
        "rejected_alternative": f"The alternative that {context.evidence_state} should be treated as release authorization was rejected.",
        "discriminating_evidence": [
            "Independently captured primary artifacts with stable hashes.",
            "Targeted counter-evidence addressing the leading alternative hypotheses.",
        ],
    }


def validate_counterfactual(counterfactual: dict) -> bool:
    return all(counterfactual.get(field) for field in REQUIRED_FIELDS)
