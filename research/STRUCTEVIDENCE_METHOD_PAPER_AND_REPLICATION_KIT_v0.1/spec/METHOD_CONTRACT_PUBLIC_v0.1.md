# StructureEvidence Public Method Contract v0.1

This document is the concise human-readable companion to the machine method contract.

## Purpose

StructureEvidence exists to prevent unsupported inference between **retrieval** and **decision**.

## Contract

1. A source statement is not automatically an established claim.
2. A claim is not automatically sufficient for a decision.
3. Event time and knowledge time are separate.
4. Failure to find evidence within a defined scope is not proof of non-existence.
5. One deployment is not broad adoption.
6. An order is not delivery; delivery is not commissioning; commissioning is not operating history.
7. A source's own claim is not independent validation.
8. Unknowns remain unknown until qualifying evidence resolves them.
9. Every public claim should expose what it supports and what it does not support.
10. When public evidence is sufficient, cite it and stop.
11. When public evidence is insufficient, identify the minimum missing evidence.
12. Research requires explicit authorization.
13. A customer purchases a controlled process, not a predetermined research outcome.
14. Paid evidence remains private unless it is eligible and explicitly approved for public release.
15. Public versions are append-only.

## Resolver behavior

The public resolver classifies questions as EXACT, ISOMORPHIC, PARTIAL, or NONE after intake. It may expose existing claim states and a possible next verification capability. It does not authorize research, payment, or publication.

## Public endpoints

- Method contract: `https://structurevidence.org/method-contract.json`
- Claims: `https://structurevidence.org/claims/index.json`
- Resolver: `https://api.structurevidence.org/resolve?q=...`
- Changes: `https://structurevidence.org/changes.json`
- Capabilities: `https://structevidence.com/capabilities.json`

## Challenge us

A useful challenge is not "I disagree." It identifies a concrete protocol failure: wrong match class, wrong evidence threshold, missing boundary, stale state, private/public leakage, unsupported inference, or a source that should change the state.
