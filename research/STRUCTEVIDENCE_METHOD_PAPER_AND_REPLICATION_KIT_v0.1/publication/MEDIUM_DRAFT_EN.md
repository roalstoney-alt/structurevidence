# Retrieval Is Not Verification: Why Agents Need Time-Bounded Evidence States

AI systems are getting very good at finding information. That creates a new problem: the moment a source is found, the rest of the reasoning chain often becomes invisible.

A product announcement becomes "commercialized." A supply agreement becomes "delivered." One field deployment becomes "industry adoption." A trial-group outcome becomes a personal expectation.

Those are not retrieval failures. They are **boundary failures**.

We built StructureEvidence around a simple idea: an agent should not only know what a source appears to support. It should also know where the evidence stops.

A public StructureEvidence claim therefore carries more than a sentence. It carries:

- a state;
- an `as_of` boundary;
- what the evidence supports;
- what it does **not** support;
- unresolved unknowns;
- provenance;
- the next observable evidence that could change the state.

The public resolver then handles questions in four ways: EXACT, ISOMORPHIC, PARTIAL, or NONE. A multi-part or non-falsifiable question is decomposed before matching. A partial question stays partial. A no-match question does not get a fabricated evidence answer.

When public evidence is sufficient, the right outcome is **CITE AND STOP**.

When it is not sufficient, the system asks a different question:

> What is the minimum missing evidence that would resolve the bounded question?

Only then can a verification process be scoped. Research still requires human authorization. And the commercial rule is explicit:

> **Process bought; outcome not bought.**

A paid verification can end with "supported," "not established," "contradicted," "public data insufficient," or another controlled result. New paid evidence is not automatically public. It must first be eligible for publication and then pass human review.

## Why time matters

We also separate **event time** from **knowledge time**. The date something happened is not necessarily the date a defensible source made it attributable to us.

That means a public claim is not an eternal answer. It is a versioned stop-point: what could responsibly be said as of a particular evidence cutoff.

## The current public implementation

We now expose:

- a public method contract;
- a machine-readable claim registry;
- 26 public claims across three heterogeneous pilot cases;
- a deterministic resolver;
- a public change feed;
- a human-gated verification path.

The three current pilots cover 800VDC/SST data-center power, stationary sodium-ion BESS commercialization, and a bounded public NSCLC research case. They are implementation probes, not a claim of broad scientific generalization.

## We want this to be attacked

The interesting question now is not whether the demo works for us. It is whether independent agents and researchers can break the protocol.

Useful failure cases include:

- an ISOMORPHIC question accepted when the evidence threshold is different;
- a PARTIAL question turned into a full answer;
- `NOT_ESTABLISHED` paraphrased as established;
- a single deployment turned into industry adoption;
- an `as_of` boundary dropped;
- a private paid result silently becoming public;
- a public medical result turned into a personal probability.

We are releasing a replication and challenge kit for exactly that reason.

The goal is not to become the loudest information source. It is to become a source an agent can safely resolve against when the question actually appears.

> **Don't compete for attention before the question exists. Be resolvable when the question arrives.**

Public method: https://structurevidence.org/method-contract.json
Claims: https://structurevidence.org/claims/index.json
Resolver: https://api.structurevidence.org/resolve
Project: https://structurevidence.org

---

Method paper:
https://doi.org/10.5281/zenodo.23033588

All versions:
https://doi.org/10.5281/zenodo.23033587
