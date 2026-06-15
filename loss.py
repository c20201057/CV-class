import torch
from torch import nn
import torch.nn.functional as F



class EdgeDiceLoss(nn.Module):
    def __init__(self, epsilon=1e-6):
        super(EdgeDiceLoss, self).__init__()
        self.epsilon = epsilon

    def forward(self, logits, target, valid_mask=None):
        pred = torch.sigmoid(logits)

        if valid_mask is None:
            valid_mask = torch.ones_like(target)

        # 展平张量 (B, H*W)
        pred = pred.view(pred.shape[0], -1)
        target = target.view(target.shape[0], -1)
        valid_mask = valid_mask.view(valid_mask.shape[0], -1)

        intersection = torch.sum(pred * target * valid_mask, dim=1)
        total = torch.sum((pred + target) * valid_mask, dim=1)
        dice = (2 * intersection + self.epsilon) / (total + self.epsilon)
        loss = 1 - dice
        return loss.mean()


class EdgeDiceFocalLoss(nn.Module):
    def __init__(self, alpha=0.8, gamma=2, epsilon=1e-6):
        """
        alpha: Dice Loss 权重（越大越关注边缘）
        gamma: Focal Loss 聚焦难例的程度
        """
        super().__init__()
        self.dice = EdgeDiceLoss(epsilon)
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits, target, valid_mask=None):
        dice_loss = self.dice(logits, target, valid_mask)

        # Focal Loss（直接基于 Logits 计算）
        pred = torch.sigmoid(logits)
        bce_loss = F.binary_cross_entropy_with_logits(logits, target, reduction="none")

        pt = pred * target + (1 - pred) * (1 - target)  # 计算 pt = p_t
        focal_weight = (1 - pt) ** self.gamma
        focal_loss = (focal_weight * bce_loss).mean()

        # 加权结合（确保权重和为 1）
        return self.alpha * dice_loss + (1 - self.alpha) * focal_loss


class WBCEWithLogitsLoss(nn.Module):
    def __init__(self):
        super(WBCEWithLogitsLoss, self).__init__()
        self.bce_loss = nn.BCEWithLogitsLoss(
            reduction="none"
        )  # 不进行平均，而是逐像素计算损失

    def forward(self, pred, target, weight=None):
        b = pred.shape[0]
        # 计算原始的 BCE 损失
        loss = self.bce_loss(pred, target)

        # 如果有权重，应用权重
        if weight is not None:
            # 逐像素加权损失
            loss = loss * weight

        # 返回平均损失
        return loss.mean()



class StructureLossWithWeight(torch.nn.Module):

    def __init__(self, epision=1e-6):
        super().__init__()
        self.epision = epision

    def forward(self, pred, target):
        weit = 1 + 5 * torch.abs(
            F.avg_pool2d(target, kernel_size=31, stride=1, padding=15) - target
        )
        wbce = F.binary_cross_entropy_with_logits(pred, target, reduction="none")
        wbce = (weit * wbce).sum(dim=(2, 3)) / weit.sum(dim=(2, 3))

        pred = torch.sigmoid(pred)
        inter = ((pred * target) * weit).sum(dim=(2, 3))
        union = ((pred + target) * weit).sum(dim=(2, 3))
        wiou = 1 - (inter + self.epision) / (union - inter + self.epision)

        return (wbce + wiou).mean()


class StructureLoss(torch.nn.Module):

    def __init__(self, epision=1e-6):
        super().__init__()
        self.epision = epision

    def forward(self, pred, target):
        # pdb.set_trace()
        bce = F.binary_cross_entropy_with_logits(pred, target, reduction="none")
        bce = bce.mean(dim=(2, 3))

        pred = torch.sigmoid(pred)
        inter = (pred * target).sum(dim=(2, 3))
        union = (pred + target).sum(dim=(2, 3))
        iou = 1 - (inter + self.epision) / (union - inter + self.epision)

        return (bce + iou).mean()


class BackboneFeatureDistillationLoss(nn.Module):
    def __init__(
        self,
        feature_weight=1.0,
        attention_weight=0.5,
        mask_guided_weight=0.0,
        mask_foreground_weight=2.0,
        mask_edge_weight=3.0,
        stage_weights=None,
    ):
        super().__init__()
        self.feature_weight = feature_weight
        self.attention_weight = attention_weight
        self.mask_guided_weight = mask_guided_weight
        self.mask_foreground_weight = mask_foreground_weight
        self.mask_edge_weight = mask_edge_weight
        self.stage_weights = stage_weights

    @staticmethod
    def _attention_map(feature):
        attention = feature.pow(2).mean(dim=1, keepdim=True)
        return F.normalize(attention.flatten(1), p=2, dim=1)

    def _stage_weight(self, idx):
        if self.stage_weights is None or idx >= len(self.stage_weights):
            return 1.0
        return self.stage_weights[idx]

    def _mask_guided_feature_loss(self, student_feature, teacher_feature, mask, edge):
        if self.mask_guided_weight <= 0 or mask is None:
            return student_feature.new_tensor(0.0)

        target_size = student_feature.shape[2:]
        with torch.no_grad():
            resized_mask = F.interpolate(
                mask.detach(),
                size=target_size,
                mode="bilinear",
                align_corners=False,
            ).clamp(0, 1)
            weight = 1.0 + self.mask_foreground_weight * resized_mask

            if edge is not None and self.mask_edge_weight > 0:
                resized_edge = F.interpolate(
                    edge.detach(),
                    size=target_size,
                    mode="bilinear",
                    align_corners=False,
                ).clamp(0, 1)
                weight = weight + self.mask_edge_weight * resized_edge

            weight = weight / weight.mean(dim=(2, 3), keepdim=True).clamp_min(1e-6)

        student_norm = F.normalize(student_feature, p=2, dim=1)
        teacher_norm = F.normalize(teacher_feature, p=2, dim=1)
        pixel_loss = (student_norm - teacher_norm).pow(2).mean(dim=1, keepdim=True)
        return (pixel_loss * weight).mean()

    def forward(self, student_features, teacher_features, mask=None, edge=None):
        feature_loss = student_features[0].new_tensor(0.0)
        attention_loss = student_features[0].new_tensor(0.0)
        mask_guided_loss = student_features[0].new_tensor(0.0)
        num_levels = min(len(student_features), len(teacher_features))
        weight_sum = 0.0

        for idx in range(num_levels):
            student_feature = student_features[idx]
            teacher_feature = teacher_features[idx].detach()
            stage_weight = self._stage_weight(idx)
            weight_sum += stage_weight

            if student_feature.shape[2:] != teacher_feature.shape[2:]:
                teacher_feature = F.interpolate(
                    teacher_feature,
                    size=student_feature.shape[2:],
                    mode="bilinear",
                    align_corners=False,
                )

            feature_loss = feature_loss + stage_weight * F.mse_loss(
                F.normalize(student_feature, p=2, dim=1),
                F.normalize(teacher_feature, p=2, dim=1),
            )
            attention_loss = attention_loss + stage_weight * F.mse_loss(
                self._attention_map(student_feature),
                self._attention_map(teacher_feature),
            )
            mask_guided_loss = mask_guided_loss + stage_weight * self._mask_guided_feature_loss(
                student_feature,
                teacher_feature,
                mask,
                edge,
            )

        if weight_sum > 0:
            feature_loss = feature_loss / weight_sum
            attention_loss = attention_loss / weight_sum
            mask_guided_loss = mask_guided_loss / weight_sum

        total_loss = (
            self.feature_weight * feature_loss
            + self.attention_weight * attention_loss
            + self.mask_guided_weight * mask_guided_loss
        )
        return total_loss, feature_loss, attention_loss, mask_guided_loss
