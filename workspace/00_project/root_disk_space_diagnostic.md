# Root Disk Space Diagnostic

更新时间：2026-06-13T18:27:32Z

## Current Evidence

- `df -h / /root/data-tmp`: root overlay is 879G total, 838G used, 0 available; `/root/data-tmp` has about 1.2T available.
- `df -ih /`: inode use is only about 10%, so the immediate problem is not inode exhaustion.
- `du -xhd1 /`: visible files on the root filesystem total about 27G.
- Largest visible root-side directories are `/root/miniconda3` about 12G, `/usr` about 8.5G, `/root/.vscode-server` about 4.3G, and `/opt` about 1.5G.
- Open deleted fd scan found VS Code/Codex log handles and NCCL shared-memory handles. The largest sampled deleted fd is about 7.4MB, so deleted files do not explain the 800G-scale `df`/`du` gap.
- Root is an overlay filesystem with Docker overlay lower/upper dirs. The overlay accounting or host quota appears to be the likely source of the mismatch, but the backing upperdir is not a safe project artifact to manipulate from this workflow.

## Operational Decision

- Do not move or delete `/root/miniconda3`, `/usr`, `/opt`, or live VS Code server state while training jobs are active.
- Keep new experiment code, checkpoints, predictions, logs, temporary files, and paper artifacts under `/root/data-tmp/workspace` or `/root/data-tmp/tmp`.
- Treat `/root/ESCNet` as a dirty source tree/legacy observation location only; do not write new paper evidence there.
