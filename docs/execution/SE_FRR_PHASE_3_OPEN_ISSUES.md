# SE-FRR-001 Phase 3 Open Issues

Date: 2026-09-26

1. The production public projection remains intentionally empty. Publishing genuine canonical Subjects, States, Changes, Evidence, and Branches still requires the approved Proposal → validation → human review → repository materialization → commit pipeline.
2. The local preview uses explicit test-only fixtures. They are never a production or staging default and must not be presented as genuine public records.
3. Visual explanation, video onboarding, and general-audience simplification are intentionally deferred until after Phase 4A demand validation.
4. Telemetry is observable through privacy-safe Worker events but has no external analytics sink or dashboard in Phase 3.
5. Customer-specific Request-status authorization remains administrator Access pending a reviewed ownership identity design.
6. D1 migration `0002_se_api_v1.sql` remains unapplied remotely.
7. Full third-party OpenAPI linting, edge performance measurement, and `jsonschema.RefResolver` migration remain deferred.

None of these issues authorizes production deployment, live data access, payment, Discord, recruitment, or external research.
