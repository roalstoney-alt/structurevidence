import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const reportUrl = new URL("../../../docs/implementation/SE-IREN-P0-R2-SYNTHETIC-RESTORE-001-RESULT.json", import.meta.url);

test("synthetic restore report proves unmodified round-trip integrity", async () => {
  const report = JSON.parse(await readFile(reportUrl, "utf8"));
  assert.equal(report.locked_head_sha, "dfa72a5935e9c5cb6e1cb06a2fd4042c5ad7ac55");
  assert.equal(report.result, "PASS_SYNTHETIC_ONLY_UNMODIFIED_ROUNDTRIP");
  assert.equal(report.resources.ids_distinct, true);
  assert.equal(report.resources.production_or_staging_id_used, false);
  assert.equal(report.resources.worker_binding_created, false);
  assert.equal(report.resources.public_route_created, false);
  assert.equal(report.export.sql_transformed, false);
  assert.equal(report.import.unmodified_export_used, true);
  assert.deepEqual(report.integrity.counts, {
    customers: 3,
    requests: 3,
    request_events: 5,
    request_consent_receipts: 3,
    request_idempotency: 3
  });
  assert.equal(report.integrity.fixture_hash_match, true);
  assert.equal(report.integrity.schema_metadata_hash_match, true);
  assert.equal(report.integrity.required_indexes_present, true);
  assert.equal(report.integrity.foreign_key_violations, 0);
  assert.equal(report.integrity.migration_ledger_match, true);
  assert.equal(report.integrity.append_only_attempts_rejected, 4);
  assert.equal(report.integrity.source_unchanged_after_export, true);
  assert.equal(report.integrity.target_unchanged_after_guard_tests, true);
});

test("synthetic restore report keeps production boundaries and cleanup closed", async () => {
  const reportText = await readFile(reportUrl, "utf8");
  const report = JSON.parse(reportText);
  assert.equal(report.recovery_measurement.rpo_synthetic, "ZERO_IN_STATIC_FIXTURE_ONLY");
  assert.equal(report.recovery_measurement.production_rpo_inferred, false);
  assert.equal(report.recovery_measurement.production_rto_inferred, false);
  assert.equal(report.cleanup.retention_policy, "DELETE_AFTER_VALIDATION");
  assert.equal(report.cleanup.source_database_deleted, true);
  assert.equal(report.cleanup.target_database_deleted, true);
  assert.equal(report.cleanup.source_and_target_absent_after_delete, true);
  assert.equal(report.cleanup.temporary_sql_deleted, true);
  assert.equal(report.cleanup.temporary_seed_deleted, true);
  assert.equal(report.cleanup.temporary_config_deleted, true);
  assert.ok(Object.values(report.prohibited_actions).every((value) => value === false || value === 0));
  assert.equal(report.ready_for_owner_production_release, false);
  assert.equal(report.validation.synthetic_restore_report_guard.failed, 0);
  assert.equal(report.validation.cloudflare_landing_node.failed, 0);
  assert.equal(report.validation.repository_python.new_failures, 0);
  assert.equal(report.validation.public_record_drift, "PASS");
  assert.equal(report.validation.internal_link_audit.result, "PASS");
  assert.equal(report.validation.new_regression_count, 0);
  assert.doesNotMatch(reportText, /[A-Z0-9._%+-]+@(?!example\.invalid\b)[A-Z0-9.-]+\.[A-Z]{2,}/i);
  assert.doesNotMatch(reportText, /eyJ[A-Za-z0-9_-]{20,}/);
});
