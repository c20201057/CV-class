# train.py
import os
import argparse
import shutil
from datetime import timedelta
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.amp import GradScaler, autocast
from torch.distributed import barrier, init_process_group, destroy_process_group
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
import cv2

from config import Config, load_config
from dataset import MyData
from loss import EdgeDiceLoss, StructureLoss
from metrics import evaluator
from models.ESCNet import ESCNet
from utils import Logger, AverageMeter, check_state_dict, save_tensor_img, set_seed


def setup_ddp(rank: int, world_size: int):
    os.environ["RANK"] = str(rank)
    os.environ["WORLD_SIZE"] = str(world_size)
    init_process_group(
        backend="nccl",
        init_method="env://",
        timeout=timedelta(hours=6),
    )


def cleanup_ddp():
    destroy_process_group()


class Trainer:
    def __init__(self, config: Config, rank: int, world_size: int):
        self.config = config
        self.rank = rank
        self.world_size = world_size
        self.device_id = self.config.device_ids[self.rank]
        self.device = torch.device(f"cuda:{self.device_id}")

        torch.cuda.set_device(self.device_id)
        if self.config.precisionHigh:
            torch.set_float32_matmul_precision("high")
        
        os.makedirs(os.path.join(self.config.save_model_dir, self.config.name), exist_ok=True)

        self.logger = (
            Logger(config, os.path.join(self.config.save_model_dir, self.config.name, "log.txt"))
            if self.rank == 0
            else None
        )

        self.log(f"Trainer initialized on rank {self.rank} with device {self.device}.")
        self.log(f"Full config:\n{self.config.model_dump_json(indent=2)}")

        self.train_loader = self._prepare_dataloader()
        self.eval_loader = self._prepare_eval_dataloader()
        self.model, self.optimizer, self.lr_scheduler = (
            self._prepare_model_and_optimizer()
        )
        self.teacher_model = (
            self._prepare_teacher_model()
            if self.config.distillation.enabled
            else None
        )

        self.scaler = GradScaler()
        self.structure_loss = StructureLoss().to(self.device)
        self.dice_loss = EdgeDiceLoss().to(self.device)
        self.loss_log = AverageMeter()

    def log(self, message: str):
        if self.rank == 0:
            self.logger.info(message)

    def _prepare_dataloader(self) -> DataLoader:
        dataset = MyData(
            self.config,
            dataset_dir=self.config.train_dir,
            image_size=self.config.img_size,
            is_train=True,
        )
        sampler = DistributedSampler(dataset) if self.config.is_ddp else None

        loader = DataLoader(
            dataset=dataset,
            batch_size=self.config.batch_size,
            num_workers=min(self.config.num_workers, self.config.batch_size),
            pin_memory=True,
            shuffle=(sampler is None),  # DDP模式下shuffle由sampler控制
            sampler=sampler,
            drop_last=True,
        )
        self.log(f"{len(loader)} batches of train dataloader created.")
        return loader

    def _prepare_eval_dataloader(self) -> DataLoader | None:
        eval_config = self.config.eval_during_training
        if not eval_config.enabled:
            return None
        if self.rank != 0:
            return None

        dataset = MyData(
            self.config,
            dataset_dir=self.config.test_dir,
            image_size=self.config.img_size,
            is_train=False,
        )
        loader = DataLoader(
            dataset=dataset,
            batch_size=self.config.batch_size_valid,
            num_workers=min(self.config.num_workers, self.config.batch_size_valid),
            pin_memory=True,
            shuffle=False,
        )
        self.log(f"{len(loader)} batches of eval dataloader created.")
        return loader

    def _prepare_model_and_optimizer(self):
        model = ESCNet(self.config, pretrained=True).to(self.device)
        if self.config.is_ddp:
            model = nn.SyncBatchNorm.convert_sync_batchnorm(model)
            model = DDP(model, device_ids=[self.device_id])

        if self.config.compile:
            model = torch.compile(model, mode="reduce-overhead")
            self.log("Model compiled with torch.compile.")

        optimizer = optim.AdamW(
            params=model.parameters(),
            lr=self.config.lr,
            weight_decay=self.config.weight_decay,
        )
        lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=self.config.epochs, eta_min=self.config.lr / 10
        )

        self.log("Model, optimizer, and scheduler have been initialized.")
        return model, optimizer, lr_scheduler

    def _prepare_teacher_model(self):
        distill_config = self.config.distillation
        teacher_config = self.config.model_copy(deep=True)

        if distill_config.teacher_backbone:
            teacher_config.backbone = distill_config.teacher_backbone
        if distill_config.teacher_lateral_channels:
            teacher_config.lateral_channels = distill_config.teacher_lateral_channels

        teacher = ESCNet(teacher_config, pretrained=False).to(self.device)
        checkpoint = torch.load(
            distill_config.teacher_checkpoint,
            map_location=self.device,
            weights_only=True,
        )
        teacher.load_state_dict(self._extract_state_dict(checkpoint))
        teacher.eval()
        teacher.requires_grad_(False)

        self.log(
            "Teacher model loaded from "
            f"{distill_config.teacher_checkpoint} "
            f"with backbone={teacher_config.backbone}."
        )
        return teacher

    @staticmethod
    def _extract_state_dict(checkpoint):
        if isinstance(checkpoint, dict):
            for key in (
                "state_dict",
                "model",
                "model_state_dict",
                "student",
                "student_state_dict",
            ):
                value = checkpoint.get(key)
                if isinstance(value, dict):
                    checkpoint = value
                    break

        if not isinstance(checkpoint, dict):
            raise TypeError("Checkpoint does not contain a valid state dict.")

        state_dict = check_state_dict(checkpoint)
        cleaned_state_dict = {}
        for key, value in state_dict.items():
            clean_key = key
            changed = True
            while changed:
                changed = False
                for prefix in ("module.", "_orig_mod."):
                    if clean_key.startswith(prefix):
                        clean_key = clean_key[len(prefix) :]
                        changed = True
            cleaned_state_dict[clean_key] = value
        return cleaned_state_dict

    def _compute_supervised_loss(self, out_edge, out_pred_masks, gts, edges):
        loss_dice = self.dice_loss(out_edge, edges)

        loss_structure = out_edge.new_tensor(0.0)
        gts = torch.clamp(gts, 0, 1)
        factors = [0.5, 0.7, 0.9, 1.1]

        for i, pred_lvl in enumerate(out_pred_masks):
            pred_lvl_resized = F.interpolate(
                pred_lvl,
                size=gts.shape[2:],
                mode="bilinear",
                align_corners=False,
            )
            factor = factors[i] if i < len(factors) else 1.0
            loss_structure += self.structure_loss(pred_lvl_resized, gts) * factor

        return loss_structure + loss_dice, loss_structure, loss_dice

    @staticmethod
    def _soft_logit_loss(student_logits, teacher_logits, temperature):
        if teacher_logits.shape[2:] != student_logits.shape[2:]:
            teacher_logits = F.interpolate(
                teacher_logits,
                size=student_logits.shape[2:],
                mode="bilinear",
                align_corners=False,
            )

        teacher_prob = torch.sigmoid(teacher_logits.detach() / temperature)
        return (
            F.binary_cross_entropy_with_logits(
                student_logits / temperature,
                teacher_prob,
                reduction="mean",
            )
            * temperature
            * temperature
        )

    def _compute_distillation_loss(self, student_outputs, teacher_outputs):
        student_edge, student_masks = student_outputs
        teacher_edge, teacher_masks = teacher_outputs
        distill_config = self.config.distillation
        temperature = distill_config.temperature

        mask_loss = student_edge.new_tensor(0.0)
        num_levels = min(len(student_masks), len(teacher_masks))
        for student_mask, teacher_mask in zip(student_masks, teacher_masks):
            mask_loss += self._soft_logit_loss(
                student_mask, teacher_mask, temperature
            )
        if num_levels > 0:
            mask_loss = mask_loss / num_levels

        edge_loss = self._soft_logit_loss(student_edge, teacher_edge, temperature)
        total_loss = (
            distill_config.mask_loss_weight * mask_loss
            + distill_config.edge_loss_weight * edge_loss
        )
        return total_loss, mask_loss, edge_loss

    def _save_checkpoint(self, epoch: int):
        if self.rank != 0:
            return  # 只有主进程保存模型

        if (
            epoch >= self.config.epochs - self.config.save_last
            and epoch % self.config.save_step == 0
        ):

            model_state = self._unwrap_model().state_dict()
            save_path = os.path.join(self.config.save_model_dir, self.config.name, f"epoch_{epoch}.pth")
            torch.save(model_state, save_path)
            self.log(f"Checkpoint saved to {save_path}")

    def _unwrap_model(self):
        model = self.model
        while True:
            if hasattr(model, "_orig_mod"):
                model = model._orig_mod
                continue
            if isinstance(model, DDP):
                model = model.module
                continue
            return model

    @staticmethod
    def _format_score(score):
        return f"{float(score):.4f}"

    def _write_eval_result(self, epoch, scores):
        eval_config = self.config.eval_during_training
        save_dir = os.path.join(eval_config.save_dir, self.config.name)
        os.makedirs(save_dir, exist_ok=True)
        result_file = os.path.join(save_dir, "result.txt")
        header = "epoch,Smeasure,wFmeasure,meanFm,meanEm,MAE\n"
        if not os.path.exists(result_file):
            with open(result_file, "w") as f:
                f.write(header)

        row = ",".join(
            [
                str(epoch),
                self._format_score(scores["Smeasure"]),
                self._format_score(scores["wFmeasure"]),
                self._format_score(scores["meanFm"]),
                self._format_score(scores["meanEm"]),
                self._format_score(scores["MAE"]),
            ]
        )
        with open(result_file, "a") as f:
            f.write(row + "\n")
        self.log(f"Eval result appended to {result_file}")

    def _run_eval(self, epoch: int):
        eval_config = self.config.eval_during_training
        if not eval_config.enabled or self.eval_loader is None or self.rank != 0:
            return

        model = self._unwrap_model()
        was_training = model.training
        model.eval()

        method = f"epoch_{epoch}"
        pred_dir = os.path.join(eval_config.pred_root, self.config.name, method)
        if os.path.isdir(pred_dir):
            shutil.rmtree(pred_dir)
        os.makedirs(pred_dir, exist_ok=True)

        self.log(f"Running eval at epoch {epoch}. Predictions: {pred_dir}")
        gt_paths = []
        with torch.no_grad():
            for inputs, _, label_paths in self.eval_loader:
                inputs = inputs.to(self.device, non_blocking=True)
                _, scaled_preds = model(inputs)
                pred_lvl = (scaled_preds[-1].sigmoid() >= 0.5).float()

                for idx_sample in range(pred_lvl.shape[0]):
                    label_path = label_paths[idx_sample]
                    gt_paths.append(label_path)
                    gt_shape = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE).shape[:2]
                    res = F.interpolate(
                        pred_lvl[idx_sample].unsqueeze(0),
                        size=gt_shape,
                        mode="bilinear",
                        align_corners=True,
                    )
                    save_tensor_img(
                        res,
                        os.path.join(
                            pred_dir,
                            label_path.replace("\\", "/").split("/")[-1],
                        ),
                    )

        pred_paths = [
            path.replace(os.path.join(self.config.test_dir), os.path.join(eval_config.pred_root, self.config.name, method))
            .replace("/GT_Object/", "/")
            for path in gt_paths
        ]
        em, sm, fm, mae, wfm, _, _ = evaluator(
            gt_paths=gt_paths,
            pred_paths=pred_paths,
            metrics=["S", "MAE", "E", "F", "WF"],
        )
        scores = {
            "Smeasure": sm,
            "wFmeasure": wfm,
            "meanFm": fm["curve"].mean(),
            "meanEm": em["curve"].mean(),
            "MAE": mae,
        }
        self.log(
            "Eval "
            f"Epoch[{epoch}/{self.config.epochs}] | "
            f"S: {self._format_score(scores['Smeasure'])} | "
            f"wF: {self._format_score(scores['wFmeasure'])} | "
            f"meanF: {self._format_score(scores['meanFm'])} | "
            f"meanE: {self._format_score(scores['meanEm'])} | "
            f"MAE: {self._format_score(scores['MAE'])}"
        )
        self._write_eval_result(epoch, scores)

        if not eval_config.keep_predictions:
            shutil.rmtree(pred_dir, ignore_errors=True)

        if was_training:
            model.train()

    def train_epoch(self, epoch: int):
        self.model.train()
        if self.teacher_model is not None:
            self.teacher_model.eval()
        self.loss_log.reset()

        if self.config.is_ddp:
            self.train_loader.sampler.set_epoch(epoch)

        for batch_idx, (inputs, gts, edges) in enumerate(self.train_loader):
            inputs, gts, edges = (
                inputs.to(self.device),
                gts.to(self.device),
                edges.to(self.device),
            )

            with autocast(device_type="cuda", dtype=torch.float32):
                student_outputs = self.model(inputs)
                out_edge, out_pred_masks = student_outputs

                hard_loss, loss_structure, loss_dice = self._compute_supervised_loss(
                    out_edge, out_pred_masks, gts, edges
                )

                distill_loss = out_edge.new_tensor(0.0)
                distill_mask_loss = out_edge.new_tensor(0.0)
                distill_edge_loss = out_edge.new_tensor(0.0)
                hard_loss_weight = 1.0

                if self.teacher_model is not None:
                    with torch.no_grad():
                        teacher_outputs = self.teacher_model(inputs)
                    distill_loss, distill_mask_loss, distill_edge_loss = (
                        self._compute_distillation_loss(student_outputs, teacher_outputs)
                    )
                    hard_loss_weight = self.config.distillation.hard_loss_weight

                total_loss = hard_loss_weight * hard_loss + distill_loss

            self.optimizer.zero_grad()
            self.scaler.scale(total_loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()

            self.loss_log.update(total_loss.item(), inputs.size(0))

            if self.rank == 0 and batch_idx % 50 == 0:
                log_msg = (
                    f"Epoch[{epoch}/{self.config.epochs}] Iter[{batch_idx}/{len(self.train_loader)}] | "
                    f"Total Loss: {total_loss.item():.3f} | "
                    f"Hard Loss: {hard_loss.item():.3f} | "
                    f"Structure Loss: {loss_structure.item():.3f} | "
                    f"Edge Loss: {loss_dice.item():.3f}"
                )
                if self.teacher_model is not None:
                    log_msg += (
                        f" | KD Loss: {distill_loss.item():.3f}"
                        f" | KD Mask: {distill_mask_loss.item():.3f}"
                        f" | KD Edge: {distill_edge_loss.item():.3f}"
                    )
                self.log(log_msg)

        self.log(
            f"@==Final== Epoch[{epoch}/{self.config.epochs}] Avg Training Loss: {self.loss_log.avg:.3f}"
        )
        self.lr_scheduler.step()

    def train(self):
        self.log("Starting training process...")
        for epoch in range(1, self.config.epochs + 1):
            self.train_epoch(epoch)
            self._save_checkpoint(epoch)
            should_eval = (
                self.config.eval_during_training.enabled
                and (
                    epoch % self.config.eval_during_training.interval == 0
                    or (
                        self.config.eval_during_training.run_at_end
                        and epoch == self.config.epochs
                    )
                )
            )
            if should_eval:
                if self.config.is_ddp:
                    barrier()
                self._run_eval(epoch)
                if self.config.is_ddp:
                    barrier()
        self.log("Training finished.")


def main(config: Config):
    if config.is_ddp:
        rank = int(os.environ["LOCAL_RANK"])
        world_size = len(config.device_ids)
        setup_ddp(rank, world_size)
    else:
        rank, world_size = 0, 1

    trainer = Trainer(config, rank, world_size)
    trainer.train()

    if config.is_ddp:
        cleanup_ddp()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ESCNet Training Script")
    parser.add_argument(
        "--config", type=str, default="config.yaml", help="Path to the config file."
    )
    args = parser.parse_args()

    config = load_config(args.config)
    set_seed(config.rand_seed)

    if config.multi_GPU:
        os.environ["OMP_NUM_THREADS"] = "4"
        main(config)
    else:  # 单卡模式
        os.environ["CUDA_VISIBLE_DEVICES"] = str(config.device_ids[0])
        main(config)
