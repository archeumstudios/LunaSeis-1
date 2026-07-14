# Reproducibility guide

## Supported environment

The complete experiment was tested on Apple Silicon with Python 3.12. Exact packages are recorded in `requirements-lock.txt`. Cross-platform Colab/Linux verification remains a release gate.

## Environment

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-lock.txt
```

Use `python -m pip` after moving the repository because virtual-environment launcher shebangs contain absolute paths.

## Fast verification

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q lunaseis scripts tests
ruby -e 'require "yaml"; Dir["configs/**/*.yaml"].each { |f| YAML.load_file(f) }'
git diff --check
```

## Data reconstruction

Raw files are not committed. The major steps are recorded as scripts rather than one opaque notebook:

```bash
.venv/bin/python scripts/download_catalog.py
.venv/bin/python scripts/download_shallow_plan.py
.venv/bin/python scripts/download_nonshallow_batch.py --batch-id 1
```

Large positive-waveform batches total about 7.11 GiB. Consult `docs/CURRENT_STATUS.md` and each checksum plan before downloading. Do not blindly run every historical experiment on limited storage.

## Selected model

The four release checkpoints are:

```text
models/checkpoints/compact_model_suite_v0.1/depthwise_cnn_holdout_S12.pt
models/checkpoints/compact_model_suite_v0.1/depthwise_cnn_holdout_S14.pt
models/checkpoints/compact_model_suite_v0.1/depthwise_cnn_holdout_S15.pt
models/checkpoints/compact_model_suite_v0.1/depthwise_cnn_holdout_S16.pt
```

Rebuild the architecture comparison with:

```bash
.venv/bin/python scripts/train_compact_model_suite.py
```

This is deterministic under the pinned local environment but can take several minutes on CPU.

## Inference smoke test

```bash
.venv/bin/python scripts/predict_lunaseis.py \
  data/raw/apollo_pse_v1.0/data/xa/continuous_waveform/s15/1972/114/xa.s15.00.mhz.1972.114.0.mseed \
  --station S15 --output /tmp/lunaseis_predictions.json
```

## Evidence boundaries

- `continuous_scanning_results_v0.1.json` and `v0.2.json` are immutable consumed-test evidence.
- The depthwise model was selected later on development data and must not be presented as having passed those tests.
- Re-running consumed frames is allowed only for software reproducibility, never model/threshold selection.
