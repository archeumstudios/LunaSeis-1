# LunaSeis-1 adversarial pre-submission review

Date: 2026-07-14

Reviewer status: internal evidence and presentation audit. This is deliberately **not** described as independent peer review; a review performed within the project cannot substitute for an unaffiliated human domain expert.

## Recommendation

The initial manuscript required major revision. After the corrections below, it is suitable as a transparent negative-result preprint and reproducibility package, but not as evidence of an operational lunar detector. External review remains desirable before journal submission.

## Major findings and resolutions

1. **Uncertainty was absent from headline event results.** Exact two-sided 95% Clopper-Pearson intervals were added for recall, and exact Poisson intervals were added for false triggers per station-hour. The manuscript now states that Poisson intervals do not represent temporal clustering.
2. **The three frozen frames could be read as directly comparable trials.** The paper now states that models, dates, label grades, and denominators differ; it prohibits pooling them into one effectiveness estimate or ranking models from the cross-frame table.
3. **The first two event denominators are extremely small.** Their broad exact intervals are reported and interpreted conservatively. Zero of three is no longer worded as zero underlying sensitivity.
4. **The Grade-C challenge could be mistaken for high-confidence ground truth.** Its weaker label status, separate role, selection rules, and inability to upgrade the operational claim are explicit in the abstract, methods, table, and limitations.
5. **Methods were not sufficiently reproducible in the paper.** The revised text includes input duration and size, robust scaling, validity mask, architecture, optimizer, hyperparameters, seed, threshold rule, scanning stride, merging, matching, protection, integrity, and exposure definitions.
6. **Background-label semantics and a detected shortcut were underreported.** The independent-day selection and S12 metric degradation are now described; catalog-negative is explicitly not equated with physical noise.
7. **The PDF silently omitted Markdown tables.** The renderer now converts Markdown tables into repeated-header ReportLab tables. The rebuilt six-page A4 PDF was rasterized and visually inspected page by page.
8. **The conclusion overgeneralized across model generations.** It now refers to the model generation assigned to each heterogeneous frame and to a failed joint recall/false-trigger/retention objective.
9. **Research ethics and source ownership were implicit.** A statement now covers robotic historical data, no human/animal participants, no competing interests, NASA/catalog attribution, and the distinction between paper authorship and archive ownership.

## Evidence checks

- `scripts/audit_manuscript_evidence.py` reads the three frozen result JSON files and asserts the primary ±180-second counts, exposure, and false-trigger rates against `paper/tables/continuous_tests.csv`.
- It writes `paper/tables/statistical_intervals.csv` and `results/predictions/manuscript_evidence_audit.json`.
- The combined exposure recomputes to 6,748.2167 station-hours.
- Grade-C primary evidence recomputes to 12/63 recall, 1,306 false triggers, and 0.867572 false triggers/hour.
- The public claim remains negative: the model is a functioning research prototype, not an operational detector.

## Residual concerns for an external reviewer

- A lunar seismologist should assess catalog timing interpretation, signal visibility, Grade-C suitability, and artifact descriptions.
- A statistical reviewer should assess the descriptive exact intervals and clustered-trigger treatment.
- A journal editor may require a different format, expanded literature review, or supplementary protocol.
- No new untouched high-confidence event-rich frame remains; the paper cannot repair this limitation through further analysis of consumed frames.

## Disposition

Internal adversarial review: **passed after major revision**.

Independent external scientific review: **not yet obtained**.

