import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const reportUrl = new URL("../../../docs/implementation/SE-IREN-P0-PRODUCTION-READONLY-AND-RESTORE-DRILL-001-R0-R1-RESULT.json", import.meta.url);

test("production R0/R1 report is read-only, aggregate-only, and bounded", async () => {
  const reportText = await readFile(reportUrl, "utf8");
  const report = JSON.parse(reportText);
  assert.equal(report.repository.pr_head, "ff1083d319c4171add34191d63413a68e0fb968d");
  assert.equal(report.repository.draft, true);
  assert.equal(report.repository.merged, false);
  assert.equal(report.r0.result, "PASS");
  assert.equal(report.r1.result, "PARTIAL");
  assert.deepEqual(report.r1.production_d1.aggregate_counts, { customers: 3, requests: 3, request_events: 5 });
  assert.equal(report.privacy.customer_rows_retrieved, false);
  assert.equal(report.privacy.private_identifiers_retrieved, false);
  assert.equal(report.privacy.secret_values_retrieved, false);
  assert.equal(report.privacy.jwt_retrieved, false);
  assert.equal(report.privacy.otp_retrieved, false);
  assert.equal(report.privacy.report_contains_only_aggregate_counts, true);
  assert.doesNotMatch(reportText, /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
  assert.doesNotMatch(reportText, /eyJ[A-Za-z0-9_-]{20,}/);
});

test("production R0/R1 report preserves every mutation and release stop gate", async () => {
  const report = JSON.parse(await readFile(reportUrl, "utf8"));
  assert.ok(Object.values(report.prohibited_actions).every((value) => value === false || value === 0));
  assert.equal(report.r1.production_d1.migration_0003, "PENDING_NOT_APPLIED");
  assert.equal(report.r1.production_d1.sqlite_master_ddl, "BLOCKED");
  assert.equal(report.r1.routes.control_plane_inventory, "BLOCKED");
  assert.equal(report.r1.production_worker.turnstile_site_key_binding_present, false);
  assert.equal(report.r1.production_worker.turnstile_secret_name_present, false);
  assert.equal(report.r1.compatibility_observation.result, "NOT_READY_FOR_RELEASE");
  assert.equal(report.r2_restore_drill, "NOT_AUTHORIZED_NOT_PERFORMED");
  assert.equal(report.production_backup_recoverability, "UNKNOWN");
  assert.equal(report.human_privacy_review, "PENDING");
  assert.equal(report.ready_for_owner_production_release, false);
  assert.equal(report.validation.production_report_guard.failed, 0);
  assert.equal(report.validation.cloudflare_landing_node.failed, 0);
  assert.equal(report.validation.repository_python.new_failures, 0);
  assert.equal(report.validation.scripts_python.new_failures_or_errors, 0);
  assert.equal(report.validation.public_record_drift, "PASS");
  assert.equal(report.validation.internal_link_audit.result, "PASS");
  assert.equal(report.validation.new_regression_count, 0);
});
