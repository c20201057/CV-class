import os

import torch
import torch.distributed as dist


def main():
    rank = int(os.environ["LOCAL_RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    torch.cuda.set_device(rank)
    dist.init_process_group(backend="nccl", init_method="env://")
    tensor = torch.ones(1, device=f"cuda:{rank}") * (rank + 1)
    dist.all_reduce(tensor)
    torch.cuda.synchronize(rank)
    if rank == 0:
        print(f"world_size={world_size} all_reduce_sum={tensor.item():.1f}")
    dist.destroy_process_group()


if __name__ == "__main__":
    main()
