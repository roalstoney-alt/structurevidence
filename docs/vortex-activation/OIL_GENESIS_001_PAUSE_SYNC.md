# OIL-GENESIS-001 Pause Synchronization for VORTEX Activation

## Imported authority

The complete paused OIL artifact set is imported from the frozen worktree identified by the 2026-10-03 handoff. The transferred handoff documents match these source hashes:

```ini
HANDOFF_MD_SHA256 = 9383d1995e5373fc5b34549ac438a5c30ee54015ee1acca891e0f759fa34f79e
HANDOFF_JSON_SHA256 = 97e6952d295edc6c86c58a0811e9602b9d279ce8674b64a07c0a4c46c19a73ca
HANDOFF_SHA256_INVENTORY_SHA256 = 9ad318e08c5cf9d03afeafc71a88e36a975defb28408235771bcd4bf6d68e02c
```

## Synchronized control state

```ini
EXPERIMENT = OIL-GENESIS-001
CURRENT_STATUS = PAUSED
LAST_COMPLETED_NODE = STAGE_3_HUMAN_SEND_DECISION
SEND_AUTHORIZED = NO
MESSAGES_ACTUALLY_SENT = 0
FIRST_REALITY_BOUNDARY_T0 = null
RESPONSE_WINDOWS_STARTED = 0
NEXT_ACTION = UNSET — awaiting human redesign of supplier participation approach
AUTOMATIC_RESUME_ALLOWED = NO
STAGE_4_ALLOWED = NO
```

All Provider, Evidence, VCF, Demand, Outcome, and Reuse counters remain zero.

## VORTEX separation rule

Open Evidence Gap challenges are a new public evidence channel, not OIL supplier outreach. A challenge submission or review event:

- does not contact an OIL candidate;
- does not reactivate any historical supplier send approval;
- does not establish OIL `T0` or start a response window;
- does not create an OIL Provider, Evidence item, VCF, Demand, Outcome, or Reuse record;
- does not advance OIL to Stage 4;
- does not automatically change a StructEvidence claim or gap state.

Human-reviewed public challenge outcomes may become input to a later redesign decision. That later use requires an explicit human gate and an updated authoritative OIL tracker/handoff first.

## Synchronization direction

OIL remains authoritative for OIL state. VORTEX stores only the read-only projection in `data/vortex-activation/oil-genesis-001-pause-sync.json`. Runtime VORTEX activity must never mutate OIL state directly.
