#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ROOT="${RUN_ROOT:-/root/data-tmp/escnet_runs}"
CKPT="${CKPT:-checkpoints/escnet/epoch_120.pth}"
QUANT_MODEL="${RUN_ROOT}/quantized/escnet_epoch120_dynamic.pt"

cd "${ROOT_DIR}"

mkdir -p \
  "${RUN_ROOT}/logs" \
  "${RUN_ROOT}/quantized" \
  "${RUN_ROOT}/float_cod10k_preds" \
  "${RUN_ROOT}/float_camo_preds" \
  "${RUN_ROOT}/float_nc4k_preds" \
  "${RUN_ROOT}/quant_dynamic_cod10k_preds" \
  "${RUN_ROOT}/quant_dynamic_camo_preds" \
  "${RUN_ROOT}/quant_dynamic_nc4k_preds"

echo "== ESCNet quantization night run =="
date
echo "root: ${ROOT_DIR}"
echo "run root: ${RUN_ROOT}"
echo "checkpoint: ${CKPT}"
git status --short --branch

echo
echo "== Environment =="
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("cuda version:", torch.version.cuda)
PY
nvidia-smi || true

run_float() {
  local name="$1"
  local config="$2"
  local pred_root="${RUN_ROOT}/float_${name}_preds"
  local save_dir="${RUN_ROOT}/float_${name}_results"

  echo
  echo "== Float inference/eval: ${name} =="
  python test.py \
    --config "${config}" \
    --ckpt "${CKPT}" \
    --pred_root "${pred_root}"
  python eval.py \
    --config "${config}" \
    --pred_root "${pred_root}" \
    --save_dir "${save_dir}" \
    --model_lst epoch_120
}

run_quant() {
  local name="$1"
  local config="$2"
  local pred_root="${RUN_ROOT}/quant_dynamic_${name}_preds"
  local save_dir="${RUN_ROOT}/quant_dynamic_${name}_results"
  local method="escnet_epoch120_dynamic"

  echo
  echo "== Quantized inference/eval: ${name} =="
  python test_quant.py \
    --config "${config}" \
    --model "${QUANT_MODEL}" \
    --pred_root "${pred_root}" \
    --method "${method}"
  python eval.py \
    --config "${config}" \
    --pred_root "${pred_root}" \
    --save_dir "${save_dir}" \
    --model_lst "${method}"
}

run_float cod10k config.yaml
run_float camo config.camo.yaml
run_float nc4k config.nc4k.yaml

echo
echo "== Build dynamic quantized model =="
python quantize.py \
  --config config.yaml \
  --ckpt "${CKPT}" \
  --output "${QUANT_MODEL}" \
  --mode dynamic \
  --smoke-test

run_quant cod10k config.yaml
run_quant camo config.camo.yaml
run_quant nc4k config.nc4k.yaml

echo
echo "== Result files =="
find "${RUN_ROOT}" -name result.txt -print -exec cat {} \;

echo
echo "== Model sizes =="
du -h "${CKPT}" "${QUANT_MODEL}"

echo
echo "== Done =="
date
