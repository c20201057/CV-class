#!/usr/bin/env bash
set -e

bash run.sh -c configs/pvt_v2_b0_escnet_litemod_512_ablate_no_ts.yaml
bash run.sh -c configs/pvt_v2_b0_escnet_litemod_512_ablate_no_aetp.yaml
bash run.sh -c configs/pvt_v2_b0_escnet_litemod_512_ablate_no_patch.yaml
bash run.sh -c configs/pvt_v2_b0_escnet_litemod_512_ablate_no_decoder_edge.yaml
bash run.sh -c configs/pvt_v2_b0_escnet_litemod_512_ablate_no_mta_laplace.yaml
