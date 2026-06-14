from models.modules.Decoder import Decoder
from models.modules.AETP import AETP
from models.modules.Encoder import Encoder
import torch.nn as nn


# @torch.compile()
class ESCNet(nn.Module):
    def __init__(self, config, pretrained=True):
        super(ESCNet, self).__init__()
        self.channels = config.lateral_channels
        inter_channel = 128

        self.encoder = Encoder(config, pretrained)
        self.decoder = Decoder(config,inter_channel)
        self.enhanced = AETP(inter_channel)

        self.asa4 = nn.Sequential(
            nn.Conv2d(self.channels[0], inter_channel, 1, 1, 0),
            nn.BatchNorm2d(inter_channel),
            nn.ReLU(inplace=True),
        )
        self.asa3 = nn.Sequential(
            nn.Conv2d(self.channels[1], inter_channel, 1, 1, 0),
            nn.BatchNorm2d(inter_channel),
            nn.ReLU(inplace=True),
        )
        self.asa2 = nn.Sequential(
            nn.Conv2d(self.channels[2], inter_channel, 1, 1, 0),
            nn.BatchNorm2d(inter_channel),
            nn.ReLU(inplace=True),
        )
        self.asa1 = nn.Sequential(
            nn.Conv2d(self.channels[3], inter_channel, 1, 1, 0),
            nn.BatchNorm2d(inter_channel),
            nn.ReLU(inplace=True),
        )
        self.feature_adapters = self._build_feature_adapters(config)

    def _build_feature_adapters(self, config):
        distill_config = getattr(config, "distillation", None)
        if (
            distill_config is None
            or not distill_config.enabled
            or distill_config.feature_loss_weight <= 0
        ):
            return None

        teacher_channels = (
            distill_config.teacher_lateral_channels
            if distill_config.teacher_lateral_channels
            else config.lateral_channels
        )
        student_channels = list(reversed(config.lateral_channels))
        teacher_channels = list(reversed(teacher_channels))

        return nn.ModuleList(
            [
                nn.Conv2d(student_ch, teacher_ch, kernel_size=1, bias=False)
                if student_ch != teacher_ch
                else nn.Identity()
                for student_ch, teacher_ch in zip(student_channels, teacher_channels)
            ]
        )

    def _adapt_features(self, features):
        if self.feature_adapters is None:
            return features
        return tuple(adapter(feature) for adapter, feature in zip(self.feature_adapters, features))

    def forward(self, x, return_features=False):
        ########## Encoder ##########
        raw_features = self.encoder(x)  # x1,x2,x3,x4
        (x1, x2, x3, x4) = raw_features
        x4 = self.asa4(x4)
        x3 = self.asa3(x3)
        x2 = self.asa2(x2)
        x1 = self.asa1(x1)
        features = [x, x1, x2, x3, x4]

        ########## Decoder ##########
        out_edge = self.enhanced(features)  # logits

        out_mask = self.decoder(features, out_edge.sigmoid())
        if return_features:
            return out_edge, out_mask, self._adapt_features(raw_features)
        return out_edge, out_mask
