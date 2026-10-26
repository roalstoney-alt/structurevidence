import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const reportUrl = new URL("../../../docs/implementation/SE-IREN-P0-R2-ISOLATED-RESTORE-DRILL-001-RESULT.json", import.meta.url);

test("R2 stops before mutation when native isolated restore is unsupported", async () => {
  const report = JSON.parse(await readFile(reportUrl, "utf8"));
  assert.equal(report.authorization, "R2_AUTHORIZED");
  assert.equal(report.native_capability_preflight.time_travel_bookmark_read, "PASS");
  assert.equal(report.native_capability_preflight.isolated_clone_or_fork_supported, false);
  assert.equal(report.native_capability_preflight.restore_semantics, "IN_PLACE_OVERWRITE_ONLY");
  assert.equal(report.isolation_gate.result, "BLOCKED_UNSUPPORTED_NATIVE_ISOLATED_RESTORE");
  assert.equal(report.isolation_gate.stop_before_database_create, true);
  assert.equal(report.isolation_gate.stop_before_restore, true);
  assert.equal(report.execution.result, "STOPPED_BLOCKED_BEFORE_MUTATION");
  assert.equal(report.r2_result, "BLOCKED");
});

test("R2 report preserves privacy and every prohibited-action gate", async () => {
  const reportText = await readFile(reportUrl, "utf8");
  const report = JSON.parse(reportText);
  assert.equal(report.execution.native_backup_created, false);
  assert.equal(report.execution.new_restore_database_created, false);
  assert.equal(report.execution.in_place_restore_invoked, false);
  assert.equal(report.execution.export_invoked, false);
  assert.equal(report.execution.import_invoked, false);
  assert.equal(report.execution.staging_copy_created, false);
  assert.equal(report.execution.local_copy_created, false);
  assert.equal(report.prohibited_actions.production_d1_write_count, 0);
  assert.equal(report.prohibited_actions.migration_0003_applied, false);
  assert.equal(report.prohibited_actions.worker_deployed, false);
  assert.equal(report.prohibited_actions.production_post_count, 0);
  assert.equal(report.prohibited_actions.pr_merged, false);
  assert.equal(report.prohibited_actions.public_pilot_started, false);
  assert.ok(Object.values(report.privacy).every((value) => value === false));
  assert.equal(report.ready_for_owner_production_release, false);
  assert.equal(report.validation.r2_stop_gate.failed, 0);
  assert.equal(report.validation.cloudflare_landing_node.failed, 0);
  assert.equal(report.validation.repository_python.new_failures, 0);
  assert.equal(report.validation.public_record_drift, "PASS");
  assert.equal(report.validation.internal_link_audit.result, "PASS");
  assert.equal(report.validation.new_regression_count, 0);
  assert.doesNotMatch(reportText, /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
  assert.doesNotMatch(reportText, /eyJ[A-Za-z0-9_-]{20,}/);
});
