---
title: Plan Setup Guide
document_type: plan_configuration
version: 1.0
classification: fictional_training_material
---

# Plan Setup Guide

> **Synthetic training material.** Northstar Benefit Services, all plan names, identifiers, dates, benefits, and procedures in this document are fictional. This is not a real plan description or coverage guidance.

## Purpose

This guide describes sample data checks for setting up a plan in the fictional training environment. A plan is configured only from approved source material; this guide does not authorize a plan or establish member benefits.

## Required configuration fields

Each training plan record should contain:

- Group identifier and plan identifier.
- Plan display name and plan type.
- Requested effective date and, when applicable, termination date.
- Network label and funding arrangement.
- Eligibility class mapping.
- A reference to the approved plan selection and benefit summary.
- Configuration status and the ID of the reviewer role (never a real person's credentials).

Illustrative plan row: group `ABC123`, plan `DEMO-PPO-250`, display name `Sample PPO 250`, effective date `2027-01-01`, network label `DEMO-NETWORK-A`, status `PENDING_REVIEW`. All identifiers and values are invented.

## Setup sequence

1. Confirm that the group is active in the training dataset and that the plan ID is unique for that group and effective period.
2. Match the requested effective date to the signed renewal election or approved plan amendment.
3. Confirm that the plan selection, benefit-summary reference, network label, funding arrangement, and eligibility classes are present.
4. Validate that the effective date is earlier than any termination date and that the plan period does not overlap another active version unless an approved transition explicitly allows it.
5. Save the row as `PENDING_REVIEW`; do not publish it to downstream enrollment processing.
6. Have a second reviewer compare the configured row with the approved source documents.
7. Mark the plan `READY` only after the review result is recorded. Otherwise keep it on hold with a reason.

## Validation rules

- Reject a missing group ID, plan ID, effective date, plan type, or approved source reference.
- Flag duplicate group/plan/effective-date keys for investigation.
- Hold the setup if the effective date differs from the signed instruction or the group renewal case is `NEEDS_RECONCILIATION`.
- Do not derive benefit values from a plan name. A name such as `PPO 250` is not a source of deductible, copay, or coverage details.
- Do not overwrite an existing plan version to fix a discrepancy; record a correction through the approved training workflow.

## Example outcomes

| Condition | Training outcome |
| --- | --- |
| All required fields are present and approved dates match. | `PENDING_REVIEW` until a second reviewer completes the check. |
| Group renewal has an unresolved effective-date conflict. | `ON_HOLD` with reason `GROUP_DATE_RECONCILIATION`. |
| A plan ID is already in use for the same effective period. | `REJECTED_FOR_REVIEW`; investigate the duplicate before retrying. |
