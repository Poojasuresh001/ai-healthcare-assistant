---
title: Claims Process Guide
document_type: claims_workflow
version: 1.0
classification: fictional_training_material
---

# Claims Process Guide

> **Synthetic training material.** Northstar Benefit Services, all claim identifiers, workflow steps, and examples in this document are fictional. This guide is not medical advice, a coverage determination, or a real claims adjudication policy.

## Purpose and boundary

This document explains a sample administrative claims workflow used by the project. Claim outcomes in the training database are already-recorded sample values. The AI assistant may summarize retrieved records but must not make, change, or predict an eligibility or claim decision.

## Sample workflow

1. **Receive:** Assign a synthetic claim ID and record the source-file batch identifier and received timestamp.
2. **Validate identifiers:** Check that the member ID, group ID, provider ID, and claim-line keys are present in the training data.
3. **Check period references:** Compare the service date with the synthetic member coverage period and plan period in the database. Route missing or conflicting records for human review.
4. **Validate claim-line data:** Check required dates, procedure-code placeholders, billed amounts, and duplicate line keys. This is a data-quality step, not a medical-necessity review.
5. **Route:** Send complete records through the fictional adjudication workflow. Records with missing or inconsistent inputs receive a pending status and a reason code.
6. **Record outcome:** Store the resulting status, processed date, and explanation code supplied by the training workflow.
7. **Correct:** Corrections are entered through a separately reviewed workflow and retained in the audit history.

## Example status values

| Status | Meaning in this synthetic dataset |
| --- | --- |
| `RECEIVED` | The claim entered the sample intake queue. |
| `PENDED_ELIGIBILITY` | A coverage-period or member-reference check needs review. |
| `PENDED_DOCUMENTATION` | A required sample input is missing or inconsistent. |
| `PROCESSED` | A sample workflow outcome has been recorded. |
| `DENIED` | A sample workflow recorded a denial outcome; consult the stored explanation code. |

These labels describe example records only. They do not define real benefit coverage or explain how a real claim should be adjudicated.

## Data access and assistant behavior

- Claim-level answers must come from the authorized structured-data tool, not from document similarity alone.
- If no matching claim is returned, say that no matching synthetic record was found; do not invent a claim or infer a denial.
- Do not ask users to paste real member identifiers, dates of birth, addresses, or medical details into this learning application.
- The assistant can explain the sample workflow and summarize fields it actually retrieved. It cannot provide clinical advice or change a stored status.
