# Continuous scanning result v0.1

Date: 2026-07-14

Status: frozen untouched pilot evaluation; negative result; not a final paper-performance claim.

## Protocol execution

Before reading any scan score, the pipeline reconstructed one operating threshold per method and held-out-station fold from the original training-station chronological validation data. The primary threshold was the highest validation-only score retaining at least 90% validation event recall. The untouched frame then produced 152,986 scores per method. Positive windows were assigned an inferred reference at window start plus 120 seconds, merged within 300 seconds, and matched one-to-one against collapsed station/time catalog references. Primary matching uses ±180 seconds; ±60 and ±300 seconds are frozen sensitivities.

The denominator is the previously frozen 2,591.4667-hour union of locally integrity-qualified time. Six catalog events were eligible for untouched recall. Triggers matched to other catalog references are protected from false-alarm counting but cannot contribute to untouched recall or precision.

## Primary ±180-second results

| Method | Triggers | Recall | False triggers | FP h⁻¹ | FP day⁻¹ | Precision* | Retained duration |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tiny CNN | 2,979 | 1/6 (0.167) | 2,932 | 1.131 | 27.154 | 0.00034 | 75.50% |
| Logistic | 319 | 1/6 (0.167) | 313 | 0.121 | 2.899 | 0.00318 | 40.28% |
| STA/LTA | 742 | 0/6 (0.000) | 732 | 0.282 | 6.779 | 0.00000 | 97.92% |

\*Precision excludes protected non-eligible catalog triggers from both numerator and denominator.

The CNN and logistic trigger matched `levent-10093` at +120 and +180 seconds respectively. Given thousands/hundreds of false triggers and only one match, this cannot be interpreted confidently as causal detection. At ±60 seconds no method recalls an eligible event. At ±300 seconds, CNN remains 1/6, logistic reaches 2/6, and STA/LTA remains 0/6; the broader logistic match at -240 seconds is especially vulnerable to coincidence.

## Station and error audit

CNN false triggers per hour are S12 2.348, S14 0.079, S15 1.056, and S16 1.082. Logistic rates are 0.025, 0.080, 0.275, and 0.098. These rates alone conceal persistent activation: CNN marks 99.995% of qualified S14 windows positive, logistic marks 100% of S14 windows positive, and STA/LTA marks 85.8–99.9% positive depending on station. Trigger merging collapses long runs, making retention and positive-window fractions mandatory companions to trigger rate.

Score-gap correlations are generally weak to moderate rather than sufficient to explain failure. The largest are STA/LTA at S12 (0.353) and CNN at S14 (0.284). Visual review of the nine highest-scoring false cases shows steps, long ringing transients, saturation-like plateaus, isolated impulses, and persistent high-frequency texture. Some false runs last nearly a full day. The model outputs saturate at 1.0 on several noncatalogued artifact windows.

## Scientific conclusion

The current operating system fails the operational research objective. The lightweight CNN does not outperform the logistic baseline under continuous scanning, all methods have unacceptable retention and/or false-trigger behavior, and H1 is not supported. This is useful evidence that balanced-window F1 did not transfer to continuous operation.

No threshold will be retuned on this frame. Continuous frame v0.1 is now consumed and may be used only for error analysis and transparent reporting. Subsequent development must use separate continuous validation days from training stations; a new untouched frame will be required for any final claim.
