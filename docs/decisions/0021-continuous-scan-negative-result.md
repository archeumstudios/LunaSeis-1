# Decision 0021: accept continuous-scan v0.1 as a negative result

Date: 2026-07-14

Accept the frozen untouched result without threshold modification. Tiny CNN, logistic, and STA/LTA recall 1/6, 1/6, and 0/6 eligible events at ±180 seconds, with 2,932, 313, and 732 false triggers. Retained-duration fractions of 75.5%, 40.3%, and 97.9% show that trigger merging can conceal persistent positive activation.

Reject H1 for this pilot and prohibit tuning on continuous frame v0.1. Treat its sole CNN/logistic event match as uncertain because the false-trigger burden makes coincidence plausible. Use separate training-station continuous validation days for artifact-aware model and operating-point development, then select a newly seeded untouched frame for any later final evaluation.
