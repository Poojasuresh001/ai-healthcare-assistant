---
title: Group Renewal Guide
document_type: renewal_procedure
version: 1.0
classification: fictional_training_material
---

# Group Renewal Guide

> **Synthetic training material.** Northstar Benefit Services, all group identifiers, dates, procedures, and examples in this document are fictional. This is not legal, clinical, coverage, or operational guidance.

## Purpose and scope

This guide describes a sample administrative workflow for renewing an existing employer group. It applies to the fictional Northstar Benefit Services training environment only. It does not define insurance contract terms or replace an approved business procedure.

## Renewal timeline

The dates below are planning targets measured from the requested renewal effective date. A case owner records the actual milestones in the renewal work queue.

| Target | Activity | Expected result |
| --- | --- | --- |
| 120 days before | Open the renewal case and confirm the group contact and current plan lineup. | Case is assigned and the initial document request is recorded. |
| 90 days before | Request the current enrollment roster or a signed no-change attestation, plan selections, and contribution schedule. | Required inputs are received or listed as outstanding. |
| 60 days before | Compare requested dates, plan identifiers, eligibility classes, and roster totals across the submitted materials. | Discrepancies are documented and routed to an owner. |
| 45 days before | Record the group's approved plan selections and any signed contract amendment. | An authorized decision is available for configuration. |
| 30 days before | Configure the approved renewal in the training system and run validation checks. | Configuration results are reviewed against approved documents. |
| 15 days before | Complete a second-person review and record readiness or remaining blockers. | The case is marked ready or remains on hold with a reason. |

## Required renewal documents

For this training workflow, the case checklist includes:

1. A signed renewal election or contract amendment that identifies the requested effective date and selected plan IDs.
2. A current enrollment roster, or a signed no-change attestation if the roster is unchanged.
3. An employer contribution schedule for the selected plans and eligibility classes.
4. A plan-selection worksheet that maps each selected plan ID to the requested effective date.
5. Written eligibility-class changes, if any.

The case owner records the document name, received date, and review status. A document marked missing, unsigned, or inconsistent remains an open item; the assistant must not infer or create an approval.

## Effective-date mismatch handling

Compare the requested renewal date, the date on the signed renewal election or amendment, and the dates in the plan-selection worksheet. If they do not agree:

1. Set the case status to `NEEDS_RECONCILIATION` and record the conflicting values.
2. Do not update the group or plan effective date and do not apply member changes.
3. Route the discrepancy to the assigned Group Account Manager for written resolution.
4. Resume configuration only after the approved source documents agree or a new signed instruction is recorded.

Do not choose which date is correct based on recency, a database value, or a model-generated guess.

### Fictional example: group ABC123

In this example, fictional group `ABC123` has a requested renewal date of `2027-01-01`, while its signed amendment shows `2027-02-01`. The case remains `NEEDS_RECONCILIATION`; no renewal configuration is applied until an authorized written resolution is recorded. These values are fabricated solely for the project.

## Completion checks

Before marking a case ready, confirm that all required documents are reviewed, the plan IDs exist in the approved plan lineup, dates agree across the approved materials, roster totals reconcile to the case summary, and a second reviewer has recorded the validation result.
