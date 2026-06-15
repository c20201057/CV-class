from models.ESCNet import ESCNet
from models.LiteESCNet import LiteESCNet


def build_model(config, pretrained=True):
    architecture = getattr(config, "architecture", "escnet")
    if architecture in {"escnet", "escnet_slim"}:
        return ESCNet(config, pretrained=pretrained)
    if architecture == "lite_escnet":
        return LiteESCNet(config, pretrained=pretrained)
    raise ValueError(f"Unsupported architecture: {architecture}")
