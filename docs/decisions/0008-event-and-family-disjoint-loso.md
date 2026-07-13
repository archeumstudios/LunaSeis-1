# 0008 - Event/family-disjoint station-held-out evaluation

Date: 2026-07-13

Status: accepted protocol constraint.

Leave-one-station-out evaluation must also exclude the held-out station's physical test events from training at other stations. Otherwise the model could see the same impact or moonquake at a training station and appear to generalize to a new station. Deep-moonquake family IDs are indivisible groups across all splits. Validation is chronological/grouped within training stations; the final test station and its event groups remain untouched until the protocol is frozen.
