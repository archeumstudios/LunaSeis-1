# Decision 0025: select the depthwise CNN as the release prototype

Date: 2026-07-14

Select the 2,761-parameter depthwise CNN for the public research-prototype interface. At identical mean development event recall (0.9115), it yields 421 merged triggers over 1,998.85 fold-hours (0.2106/hour), compared with 820/0.4102 for the robust tiny CNN and 911/0.4558 for the compact TCN.

This selection is development-only. A full-day S15 CLI smoke scan scored 1,418 valid windows and placed all 1,418 above the fold threshold, demonstrating persistent activation and poor retention on that day. The checkpoint is useful for reproducible research and failure analysis, but is not an operational detector.
