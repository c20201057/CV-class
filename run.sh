#!/bin/bash
set -e

# 默认执行训练、测试和评估
TRAIN=true
CONFIG="config.yaml"
PRED_ROOT="preds"
SAVE_DIR="results"
NPROC_PER_NODE=""
MASTER_PORT=""

usage() {
    echo "Usage: bash run.sh [--config CONFIG] [--notrain] [--pred_root DIR] [--save_dir DIR] [--nproc_per_node N] [--master_port PORT]"
    echo "       bash run.sh -c configs/pvt_v2_b0.yaml"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--config)
            CONFIG="$2"
            shift 2
            ;;
        --notrain)
            TRAIN=false
            shift
            ;;
        --pred_root)
            PRED_ROOT="$2"
            shift 2
            ;;
        --save_dir)
            SAVE_DIR="$2"
            shift 2
            ;;
        --nproc_per_node)
            NPROC_PER_NODE="$2"
            shift 2
            ;;
        --master_port)
            MASTER_PORT="$2"
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

echo "Using config: $CONFIG"

is_multi_gpu() {
    python - "$CONFIG" <<'PY'
import sys
import yaml

with open(sys.argv[1], "r") as f:
    cfg = yaml.safe_load(f)

device_ids = cfg.get("device_ids") or []
multi_gpu = bool(cfg.get("multi_GPU", False))
print("1" if multi_gpu and len(device_ids) > 1 else "0")
PY
}

get_nproc_per_node() {
    python - "$CONFIG" <<'PY'
import sys
import yaml

with open(sys.argv[1], "r") as f:
    cfg = yaml.safe_load(f)

print(len(cfg.get("device_ids") or []))
PY
}

find_free_port() {
    python - <<'PY'
import socket

for port in range(29501, 30000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            continue
        print(port)
        break
else:
    raise SystemExit("No free port found in 29501-29999")
PY
}

# 训练部分
if [ "$TRAIN" = true ]; then
    echo "开始训练..."
    if [[ "$(is_multi_gpu)" == "1" ]]; then
        if [[ -z "$NPROC_PER_NODE" ]]; then
            NPROC_PER_NODE="$(get_nproc_per_node)"
        fi
        if [[ -z "$MASTER_PORT" ]]; then
            MASTER_PORT="$(find_free_port)"
        fi
        echo "Using torchrun master port: $MASTER_PORT"
        torchrun --nproc_per_node="$NPROC_PER_NODE" --master_port="$MASTER_PORT" train.py --config "$CONFIG"
    else
        python train.py --config "$CONFIG"
    fi
fi

# 测试部分
echo "执行测试脚本..."
python test.py --config "$CONFIG" --pred_root "$PRED_ROOT"

# 评估部分
echo "执行评估脚本..."
python eval.py --config "$CONFIG" --pred_root "$PRED_ROOT" --save_dir "$SAVE_DIR"
