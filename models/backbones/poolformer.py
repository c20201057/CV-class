import timm


def poolformer_s12():
    return timm.create_model(
        "poolformer_s12.sail_in1k",
        pretrained=False,
        features_only=True,
        out_indices=(0, 1, 2, 3),
    )
