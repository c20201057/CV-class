# Gate Patch Readiness Audit

- Status: `pass`
- Findings: 0

## Gate Readiness

| Gate | State | Evidence | Required Paper Action |
| --- | --- | --- | --- |
| Gate 1 clean baseline | pending | no rows found | Keep ESCNet-B5 as historical/reference only. |
| Gate 2 KD | pending | no rows found | Keep KD as engineering route only, with no improvement claim. |
| Gate 3 controlled speed | pending | no idle profile rows found | Keep latency/FPS claims withheld. |
| Gate 4A B0 observation candidate | pending | no candidate rows or profiles found | Keep B0 as dirty-tree observation only. |
| Gate 4B MobileMamba observation candidate | pending | no candidate rows or profiles found | Keep MobileMamba-T2 as dirty-tree observation only. |

## Findings

- none

## Interpretation

- `pending` is acceptable and means the manuscript must keep the current evidence boundary.
- `ready_to_patch` means the corresponding section of `paper_gate_patch_matrix.md` can be applied.
- `partial_invalid` is unsafe: do not patch claims until metadata and integrity evidence are repaired.
