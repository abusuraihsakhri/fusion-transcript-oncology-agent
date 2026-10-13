"use strict";

/**
 * Browser-only mirror of agents/workers.py demonstration thresholds.
 * This is NOT fusion calling, ESCAT scoring, or a clinical classifier.
 */
(function (root) {
  const PHI = [
    /\bMRN[:#\s-]*\d{4,10}\b/i,
    /\b\d{3}-\d{2}-\d{4}\b/,
    /\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/,
    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/,
    /\b(?:DOB|Date of Birth)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b/i,
    /\b(?:Patient\s+Name|Patient)[:\s]+[A-Z][a-z]+\s+[A-Z][a-z]+\b/i
  ];
  const KEYWORDS = ["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"];

  function evaluateAudit(input) {
    const task = String(input.task_id || "").trim();
    const target = String(input.target_identifier || "").trim();
    const descriptor = String(input.status_descriptor || "NOMINAL").trim();
    if (!task || task.length > 128 || !target || target.length > 128 || descriptor.length > 64) {
      throw new Error("Task/target identifiers must be 1–128 characters; descriptor at most 64.");
    }
    if ([task, target, descriptor].some((text) => PHI.some((pattern) => pattern.test(text)))) {
      throw new Error("A possible personal identifier was detected. Use synthetic identifiers only.");
    }
    const primary = Number(input.primary_metric);
    const secondary = Number(input.secondary_metric);
    if (input.primary_metric === "" || input.secondary_metric === "" ||
        !Number.isFinite(primary) || !Number.isFinite(secondary)) {
      throw new Error("Both metrics must contain finite numeric values.");
    }
    if (typeof input.is_critical_flag !== "boolean") {
      throw new Error("The priority flag must be true or false.");
    }

    const alerts = [];
    if (primary > 25) {
      alerts.push({
        worker: "InvariantQCWorker", urgency: "ELEVATED_RISK",
        summary: "Configured Primary Threshold Exceeded",
        details: "Primary metric " + primary + " exceeds demonstration threshold 25."
      });
    }
    if (input.is_critical_flag || secondary > 12) {
      alerts.push({
        worker: "SafetyEscalationWorker",
        urgency: input.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
        summary: "Priority / Secondary Threshold Triggered",
        details: "Priority flag " + input.is_critical_flag + "; secondary metric " + secondary + "."
      });
    }
    if (KEYWORDS.some((keyword) => descriptor.toUpperCase().includes(keyword))) {
      alerts.push({
        worker: "ProtocolConformanceWorker", urgency: "ELEVATED_RISK",
        summary: "Descriptor Keyword Detected",
        details: "Descriptor matched a demonstration keyword rule."
      });
    }
    const critical = alerts.filter((a) => a.urgency === "CRITICAL_STAT_PANIC").length;
    const urgency = critical ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
    return {
      mode: "DEMONSTRATION_ONLY",
      task_id: task,
      target_identifier: target,
      overall_urgency: urgency,
      integrity_status: critical ? "RECALIBRATION_REQUIRED" :
        alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
      total_alerts: alerts.length,
      critical_alerts_count: critical,
      alerts,
      note: "Rule-based simulation. No fusion transcript detected; no actionability or therapy inferred."
    };
  }

  root.FusionDemo = { evaluateAudit };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { evaluateAudit };
  }

  if (typeof document === "undefined") return;

  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("audit-form");
    const output = document.getElementById("output");
    const error = document.getElementById("error");
    const stats = document.getElementById("tasks");
    const status = document.getElementById("status");
    const save = document.getElementById("save");
    let completed = 0;
    let latest = null;

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      error.textContent = "";
      try {
        const request = Object.fromEntries(new FormData(form).entries());
        request.is_critical_flag = document.getElementById("is_critical_flag").checked;
        latest = evaluateAudit(request);
        output.textContent = JSON.stringify(latest, null, 2);
        status.textContent = latest.overall_urgency;
        completed += 1;
        stats.textContent = String(completed);
        save.disabled = false;
      } catch (exc) {
        latest = null;
        error.textContent = exc.message;
        output.textContent = "Please correct the input to run the demonstration.";
        save.disabled = true;
      }
    });

    form.addEventListener("reset", () => {
      latest = null;
      save.disabled = true;
      error.textContent = "";
      output.textContent = "Enter synthetic example values and select Run evaluation.";
      status.textContent = "READY";
    });

    save.addEventListener("click", () => {
      if (!latest) return;
      const file = new Blob([JSON.stringify(latest, null, 2) + "\n"], { type: "application/json" });
      const url = URL.createObjectURL(file);
      const link = document.createElement("a");
      link.href = url;
      link.download = "fusion-demo-result.json";
      link.click();
      URL.revokeObjectURL(url);
    });
  });
})(typeof window !== "undefined" ? window : globalThis);
