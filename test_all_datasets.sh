#!/bin/bash
set -euo pipefail

CONFIG="config.yaml"
PRED_ROOT="/root/data-tmp/preds_test"
SAVE_ROOT="/root/data-tmp/results_test"
CKPT=""
N_THREADS=4
DATASETS=("CAMO" "COD10K" "NC4K")

usage() {
    echo "Usage: bash test_all_datasets.sh -c CONFIG [--ckpt CKPT] [--pred_root DIR] [--save_root DIR] [--n_threads N]"
    echo "Example:"
    echo "  bash test_all_datasets.sh -c configs/pvt_v2_b0_escnet_litemod_512_structkd.yaml --ckpt /root/data-tmp/ESCNet/checkpoints/pvt_v2_b0_escnet_litemod_512_structkd/epoch_120.pth"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--config)
            CONFIG="$2"
            shift 2
            ;;
        --ckpt)
            CKPT="$2"
            shift 2
            ;;
        --pred_root)
            PRED_ROOT="$2"
            shift 2
            ;;
        --save_root)
            SAVE_ROOT="$2"
            shift 2
            ;;
        --n_threads)
            N_THREADS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
done

if [[ ! -f "$CONFIG" ]]; then
    echo "Config file not found: $CONFIG"
    exit 1
fi

TMP_DIR="$(mktemp -d /tmp/cod_eval_configs.XXXXXX)"
cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

MODEL_NAME="$(python - "$CONFIG" <<'PY'
import sys
import yaml
from pathlib import Path

config_path = Path(sys.argv[1])
with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)
print(cfg.get("name") or config_path.stem)
PY
)"

echo "Base config: $CONFIG"
echo "Model name: $MODEL_NAME"
echo "Prediction root: $PRED_ROOT/$MODEL_NAME"
echo "Result root: $SAVE_ROOT/$MODEL_NAME"

for DATASET in "${DATASETS[@]}"; do
    TEST_DIR="/root/data-tmp/COD/Test/$DATASET"
    if [[ ! -d "$TEST_DIR/Image" || ! -d "$TEST_DIR/GT_Object" ]]; then
        echo "Dataset folder is invalid: $TEST_DIR"
        exit 1
    fi

    DATASET_CONFIG="$TMP_DIR/${MODEL_NAME}_${DATASET}.yaml"
    python - "$CONFIG" "$DATASET_CONFIG" "$TEST_DIR" <<'PY'
import sys
import yaml

src, dst, test_dir = sys.argv[1:4]
with open(src, "r") as f:
    cfg = yaml.safe_load(f)

cfg["test_dir"] = test_dir

with open(dst, "w") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
PY

    DATASET_PRED_ROOT="$PRED_ROOT/$MODEL_NAME/$DATASET"
    DATASET_SAVE_DIR="$SAVE_ROOT/$MODEL_NAME/$DATASET"

    mkdir -p "$DATASET_PRED_ROOT" "$DATASET_SAVE_DIR"

    echo "========================================"
    echo "Testing dataset: $DATASET"
    echo "Test dir: $TEST_DIR"
    echo "Pred root: $DATASET_PRED_ROOT"
    echo "Save dir: $DATASET_SAVE_DIR"
    echo "========================================"

    if [[ -n "$CKPT" ]]; then
        python test.py --config "$DATASET_CONFIG" --ckpt "$CKPT" --pred_root "$DATASET_PRED_ROOT"
    else
        python test.py --config "$DATASET_CONFIG" --pred_root "$DATASET_PRED_ROOT"
    fi

    python eval.py \
        --config "$DATASET_CONFIG" \
        --pred_root "$DATASET_PRED_ROOT" \
        --save_dir "$DATASET_SAVE_DIR" \
        --n_threads "$N_THREADS"
done

echo "All dataset tests finished."
echo "Predictions: $PRED_ROOT/$MODEL_NAME"
echo "Results: $SAVE_ROOT/$MODEL_NAME"
