# 0011 — Use one event-level candidate registry with source-specific QA status

Date: 2026-07-13

## Decision

Represent each physical positive candidate once in the unified registry. Merge the 28 corrected legacy shallow records into their exact PDS identities and add the 46 KO records once. Replace the conservative PDS shallow subset with all 74 corrected discovery-catalog events while preserving inherited PDS grades and Onodera-specific provenance. Do not equate PDS positive visibility with audited waveform usability.

Evaluation grouping is the deep repeating family where assigned, the KO-SMQ-26/KO-SMQ-40 repeating pair where applicable, and otherwise the physical event.

## Rationale

Appending catalogs would duplicate 28 physical events and inflate class counts. Expanding shallow candidates is scientifically traceable to a corrected peer-reviewed discovery analysis, whereas silently labeling the added events as PDS A/B would be false. Event-level grouping also prevents multi-station observations and known repeating sources from crossing splits.

## Consequences

The registry contains 1,314 candidates but is not a training manifest. All 1,240 nonshallow candidates still require waveform QA. Background sampling and split assignment remain prohibited until candidate QA and grouping checks are complete.
