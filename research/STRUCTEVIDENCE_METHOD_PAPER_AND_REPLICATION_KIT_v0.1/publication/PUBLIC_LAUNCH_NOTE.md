# Public Launch Note — StructureEvidence Method + Replication Kit v0.1

We are releasing the first public methods and replication package for StructureEvidence.

## What is being released

- a methods paper;
- a public protocol specification;
- a machine-readable method contract;
- 26 public claim objects across three pilot domains;
- a deterministic question resolver;
- a replication test set;
- an external challenge template.

## What we are asking others to test

Please try to break the evidence boundaries.

We are especially interested in cases where an agent:

- treats a partial match as a complete answer;
- treats a single instance as broad adoption;
- loses an `as_of` boundary;
- drops a material `does_not_support` condition;
- treats absence within a search scope as proof of non-existence;
- treats source claims as independent validation;
- converts public medical evidence into a personal probability;
- initiates research or publication without authorization.

## What this release does not claim

It does not claim that StructureEvidence is already superior to other retrieval or research systems. The current system is a production implementation of a protocol, not a completed comparative benchmark.

## Public endpoints

- Project: https://structurevidence.org
- Method contract: https://structurevidence.org/method-contract.json
- Claims: https://structurevidence.org/claims/index.json
- Resolver: https://api.structurevidence.org/resolve
- Changes: https://structurevidence.org/changes.json
- Commercial capabilities: https://structevidence.com/capabilities.json

## Core principle

> Public evidence is reused. Missing evidence is scoped. Research is authorized. Outcomes are never promised.

## Frozen implementation baseline

`94ee5dc8670b8132979846c815b400f8cef17ab1`

## Scholarly record

- Exact v0.1 publication: https://doi.org/10.5281/zenodo.23033588
- All versions: https://doi.org/10.5281/zenodo.23033587
- Zenodo record: https://zenodo.org/records/23033588
