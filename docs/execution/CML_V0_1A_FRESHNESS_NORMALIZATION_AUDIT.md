# CML v0.1a Freshness Normalization Audit

CML continues to use `RDL_FRESHNESS_v0.1a` as the canonical state authority. Runtime records now separate `freshness_state`, `freshness_reason`, and `freshness_rule_type`; no compound CML-only state remains.

| Pilot | State | Reason | Rule type |
| --- | --- | --- | --- |
| Amphenol 10081811-101-07LF | `CURRENT_WITH_LIMITATIONS` | `CONFLICTING_PRIMARY_LIFECYCLE_EFFECTIVE_DATE` | `EVENT_DRIVEN` |
| NXP Radio Power 2026 | `CURRENT_WITH_LIMITATIONS` | `MANUFACTURER_INTERFACE_STATUS_CONFLICT` | `EVENT_DRIVEN` |
| Murata MYMGM5R012ELA5RND | `POLICY_NOT_CONFIGURED` | `EXACT_LIFECYCLE_EFFECTIVE_DATE_UNRESOLVED` | `UNCONFIGURED` |
| Amphenol RF 095-725-134-006 | `POLICY_NOT_CONFIGURED` | `ACTIVE_BENCHMARK_HAS_NO_EMPIRICAL_CADENCE` | `UNCONFIGURED` |

These mappings preserve the existing evidence findings. They normalize state representation and do not create a global age threshold.
