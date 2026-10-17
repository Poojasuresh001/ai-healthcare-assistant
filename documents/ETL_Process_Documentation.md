---
title: Synthetic Enrollment and Claims ETL Process
document_type: etl_runbook
version: 1.0
classification: fictional_training_material
---

# Synthetic Enrollment and Claims ETL Process

> **Synthetic training material.** Northstar Benefit Services, all source names, schedules, fields, thresholds, and run procedures in this document are invented for this repository. No production connection or company extract is used.

## Purpose and sample data flow

This runbook describes a fictional batch pipeline that later project phases may represent with local sample files and a synthetic SQL database. It does not connect to a Facets environment or any real payer system.

```text
fabricated group / plan / member / claim files
    -> landing area
    -> schema and file checks
    -> staging tables
    -> key and date validation
    -> synthetic operational tables
    -> run summary and rejected-row report
```

## Schedule and dependencies

For demonstration, a daily batch is scheduled at 01:15 UTC by a fictional scheduler named `DemoTidal`. The claims load starts only after the group, plan, and member reference loads finish successfully. These values are examples and do not represent any real company's schedule.

Each run is identified by a synthetic `run_id`, business date, and input-file checksum. A retry uses the same run identity so that a successful batch is not duplicated.

## Processing steps

1. Confirm that all expected fabricated input files exist and are readable.
2. Record file name, row count, checksum, and batch date in the run log.
3. Validate headers, required columns, date formats, and supported schema version.
4. Load rows into staging tables without overwriting the prior successful batch.
5. Check required identifiers, duplicate natural keys, parent-child references, and date ordering.
6. Route invalid rows to a synthetic reject table with a stable reason code; do not silently discard them.
7. Merge valid rows into the synthetic group, plan, member, provider, and claim tables using the run key.
8. Compare input, accepted, rejected, and target counts; write a run summary and mark the batch `SUCCEEDED` or `FAILED_VALIDATION`.

## Validation examples

- Every plan row references a group ID present in the group table.
- Every member row references a group ID and plan ID that exist for the applicable sample period.
- Each claim line has a claim ID, member ID, provider ID, service date, and unique line number.
- A service date is not earlier than the sample member's effective date or later than a populated termination date.
- Duplicate claim-line keys are rejected for review rather than loaded twice.
- For each file, `input_rows = accepted_rows + rejected_rows` must hold.
- If a target count changes by more than the configured synthetic threshold of 20 percent from the prior sample run, mark the batch for review. This is a demonstration threshold, not an operational standard.

## Failure and recovery

On missing files, invalid headers, a failed dependency, or a count reconciliation failure, stop downstream loads, preserve the landing files, and record the error in the run log. Correct the fabricated input or mapping and rerun with the same run identity. The load must be idempotent: rerunning a completed input must not duplicate target rows.

## Audit fields

Synthetic target rows should retain `source_file`, `run_id`, `loaded_at_utc`, and `record_hash` where applicable. Logs should contain fabricated identifiers only and must not include real member information or credentials.
