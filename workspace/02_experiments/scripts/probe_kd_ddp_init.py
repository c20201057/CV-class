import argparse
import os
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()

    sys.path.insert(0, args.repo)
    from config import load_config
    from dataset import MyData
    from models.ESCNet import ESCNet

    config = load_config(args.config)
    rank = int(os.environ["LOCAL_RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    device_id = config.device_ids[rank]
    torch.cuda.set_device(device_id)
    dist.init_process_group(backend="nccl", init_method="env://")

    if rank == 0:
        print(f"config={Path(args.config)}")
        print(f"world_size={world_size} device_ids={config.device_ids}")

    dataset = MyData(
        config,
        dataset_dir=config.train_dir,
        image_size=config.img_size,
        is_train=True,
    )
    if rank == 0:
        print(f"dataset_len={len(dataset)}")

    model = ESCNet(config, pretrained=config.bb_pretrained).to(device_id)
    model = nn.SyncBatchNorm.convert_sync_batchnorm(model)
    model = DDP(model, device_ids=[device_id])
    dist.barrier()
    if rank == 0:
        print("kd_ddp_init=ok")
    del model
    dist.destroy_process_group()


if __name__ == "__main__":
    main()
