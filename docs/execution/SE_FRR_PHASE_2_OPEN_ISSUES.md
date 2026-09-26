# SE-FRR-001 Phase 2 Open Issues

Date: 2026-09-26

No issue blocks Phase 2 acceptance or Phase 3 entry.

## Deferred items

1. The v1 production public projection is intentionally empty until a later authorized publication pipeline supplies real public canonical objects. Test fixtures are never production defaults.
2. D1 migration `0002_se_api_v1.sql` is committed but was not applied remotely because production deployment is forbidden in Phase 2.
3. Request-status access currently uses the existing administrative Cloudflare Access boundary. Customer-specific identity/ownership authorization requires a separate reviewed identity design before external self-service.
4. API proposal validation is intentionally preliminary. Repository chain verification remains mandatory, and API approval alone cannot materialize.
5. The custom OpenAPI contract validator verifies operation parity, statuses, and input allowlists; broader standards linting can be added without changing the frozen API contract.
6. Local latency measurements exclude network, Cloudflare edge, Access, and D1 latency and must not be presented as production performance.
7. `TECH_DEBT_SE_001` remains: migrate historical `jsonschema.RefResolver` usage to `referencing`.

Payments, Discord, production deployment, live user recruitment, and external-agent credentials remain explicitly out of scope.
