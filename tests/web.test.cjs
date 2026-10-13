"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { evaluateAudit } = require("../web/app.js");

const valid = {
  task_id: "TASK-1", target_identifier: "SAMPLE-1",
  primary_metric: 10, secondary_metric: 2,
  status_descriptor: "NOMINAL", is_critical_flag: false
};

test("routine demonstration remains routine", () => {
  const result = evaluateAudit(valid);
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
  assert.ok(!("audit_hash" in result));
});

test("browser matches Python worker cutoffs", () => {
  const elevated = evaluateAudit({ ...valid, primary_metric: 25.01,
    secondary_metric: 12.01, status_descriptor: "DISCORDANT" });
  assert.equal(elevated.total_alerts, 3);
  assert.equal(elevated.overall_urgency, "ELEVATED_RISK");
  const critical = evaluateAudit({ ...valid, is_critical_flag: true });
  assert.equal(critical.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(critical.critical_alerts_count, 1);
});

test("reject non-finite values and blank metrics", () => {
  for (const invalid of [NaN, Infinity, ""]) {
    assert.throws(() => evaluateAudit({ ...valid, primary_metric: invalid }));
  }
});

test("reject identifiers that appear to contain PHI", () => {
  assert.throws(() => evaluateAudit({ ...valid, task_id: "MRN-123456" }));
  assert.throws(() => evaluateAudit({ ...valid, target_identifier: "john@example.com" }));
});

test("reject malformed identifiers and critical flags", () => {
  assert.throws(() => evaluateAudit({ ...valid, task_id: "" }));
  assert.throws(() => evaluateAudit({ ...valid, task_id: "X".repeat(129) }));
  assert.throws(() => evaluateAudit({ ...valid, is_critical_flag: "False" }));
});
