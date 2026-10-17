-- SYNTHETIC TRAINING DATA ONLY. All names, identifiers, dates and amounts are invented.
-- SQLite dialect, used by the local FastAPI demo and Docker image.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS groups (
    group_id TEXT PRIMARY KEY,
    group_name TEXT NOT NULL,
    status TEXT NOT NULL,
    industry TEXT NOT NULL,
    state_code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
    plan_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES groups(group_id),
    plan_name TEXT NOT NULL,
    plan_type TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    termination_date TEXT,
    network_label TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    member_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES groups(group_id),
    plan_id TEXT NOT NULL REFERENCES plans(plan_id),
    coverage_start TEXT NOT NULL,
    coverage_end TEXT,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS providers (
    provider_id TEXT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    provider_type TEXT NOT NULL,
    network_label TEXT NOT NULL,
    state_code TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    member_id TEXT NOT NULL REFERENCES members(member_id),
    provider_id TEXT NOT NULL REFERENCES providers(provider_id),
    service_date TEXT NOT NULL,
    received_date TEXT NOT NULL,
    processed_date TEXT,
    status TEXT NOT NULL,
    billed_amount REAL NOT NULL,
    allowed_amount REAL NOT NULL,
    paid_amount REAL NOT NULL,
    explanation_code TEXT NOT NULL,
    explanation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS renewals (
    renewal_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES groups(group_id),
    status TEXT NOT NULL,
    requested_effective_date TEXT NOT NULL,
    signed_effective_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    open_items TEXT NOT NULL,
    updated_date TEXT NOT NULL
);

INSERT OR IGNORE INTO groups (group_id, group_name, status, industry, state_code) VALUES
    ('ABC123', 'Northwind Bicycle Cooperative', 'ACTIVE', 'Retail Cooperative', 'MN'),
    ('DEF456', 'Cedar Valley Analytics', 'ACTIVE', 'Professional Services', 'OR');

INSERT OR IGNORE INTO plans
    (plan_id, group_id, plan_name, plan_type, effective_date, termination_date, network_label, status)
VALUES
    ('DEMO-PPO-250', 'ABC123', 'Sample PPO 250', 'PPO', '2026-01-01', NULL, 'DEMO-NETWORK-A', 'ACTIVE'),
    ('DEMO-HMO-500', 'ABC123', 'Sample HMO 500', 'HMO', '2027-01-01', NULL, 'DEMO-NETWORK-B', 'PENDING_REVIEW'),
    ('DEMO-EPO-750', 'DEF456', 'Sample EPO 750', 'EPO', '2026-04-01', NULL, 'DEMO-NETWORK-C', 'ACTIVE');

INSERT OR IGNORE INTO members
    (member_id, group_id, plan_id, coverage_start, coverage_end, status)
VALUES
    ('M1001', 'ABC123', 'DEMO-PPO-250', '2026-01-01', NULL, 'ACTIVE'),
    ('M1002', 'ABC123', 'DEMO-PPO-250', '2026-01-01', NULL, 'ACTIVE'),
    ('M2001', 'DEF456', 'DEMO-EPO-750', '2026-04-01', NULL, 'ACTIVE');

INSERT OR IGNORE INTO providers
    (provider_id, provider_name, provider_type, network_label, state_code, status)
VALUES
    ('P1001', 'Riverbend Family Practice', 'PRIMARY_CARE', 'DEMO-NETWORK-A', 'MN', 'ACTIVE'),
    ('P1002', 'Lakeview Imaging Center', 'IMAGING', 'DEMO-NETWORK-A', 'MN', 'ACTIVE'),
    ('P2001', 'Pine Street Pediatrics', 'PRIMARY_CARE', 'DEMO-NETWORK-C', 'OR', 'ACTIVE');

INSERT OR IGNORE INTO claims
    (claim_id, member_id, provider_id, service_date, received_date, processed_date,
     status, billed_amount, allowed_amount, paid_amount, explanation_code, explanation)
VALUES
    ('CLM5001', 'M1001', 'P1001', '2026-03-10', '2026-03-12', '2026-03-18',
     'PROCESSED', 180.00, 125.00, 100.00, 'SYN-OK', 'Synthetic sample claim processed.'),
    ('CLM5002', 'M1001', 'P1002', '2026-04-02', '2026-04-04', '2026-04-12',
     'DENIED', 420.00, 0.00, 0.00, 'SYN-INFO', 'Synthetic sample record is missing a required attachment.'),
    ('CLM6001', 'M2001', 'P2001', '2026-05-06', '2026-05-07', NULL,
     'PENDED_DOCUMENTATION', 95.00, 0.00, 0.00, 'SYN-PEND', 'Synthetic sample record is awaiting documentation review.');

INSERT OR IGNORE INTO renewals
    (renewal_id, group_id, status, requested_effective_date, signed_effective_date,
     reason, open_items, updated_date)
VALUES
    ('REN-ABC123-2027', 'ABC123', 'NEEDS_RECONCILIATION', '2027-01-01', '2027-02-01',
     'Requested renewal date differs from the signed amendment.',
     'Written Group Account Manager resolution|Confirm plan-selection worksheet date', '2026-09-15'),
    ('REN-DEF456-2027', 'DEF456', 'READY_FOR_REVIEW', '2027-04-01', '2027-04-01',
     'Sample documents agree; second-person review remains open.',
     'Second-person review', '2026-09-20');
