# config.py
import yaml
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel, DirectoryPath, Field, FilePath, model_validator

# --- Nested Models for better structure ---

class WeightsPaths(BaseModel):
    """Defines and validates paths to backbone weights."""
    pvt_v2_b0: Optional[FilePath] = None
    pvt_v2_b1: Optional[FilePath] = None
    pvt_v2_b2: Optional[FilePath] = None
    pvt_v2_b3: Optional[FilePath] = None
    pvt_v2_b4: Optional[FilePath] = None
    pvt_v2_b5: Optional[FilePath] = None
    mobilemamba_t2: Optional[FilePath] = None
    mobilemamba_t4: Optional[FilePath] = None
    mobilemamba_s6: Optional[FilePath] = None
    mobilemamba_b1: Optional[FilePath] = None
    mobilemamba_b2: Optional[FilePath] = None
    mobilemamba_b4: Optional[FilePath] = None
    poolformer_s12: Optional[FilePath] = None


class DistillationConfig(BaseModel):
    """Teacher-Student distillation settings."""

    enabled: bool = False
    start_epoch: int = Field(1, ge=1)
    teacher_architecture: Literal[
        "escnet",
        "escnet_slim",
        "escnet_lite_modules",
        "escnet_lite_fast_modules",
        "lite_escnet",
    ] = "escnet"
    teacher_checkpoint: Optional[str] = None
    teacher_backbone: Optional[str] = None
    teacher_lateral_channels: Optional[List[int]] = None
    teacher_escnet_width: Optional[int] = Field(None, gt=0)
    teacher_lite_head_channels: Optional[int] = Field(None, gt=0)
    temperature: float = Field(1.0, gt=0)
    hard_loss_weight: float = Field(1.0, ge=0)
    mask_loss_weight: float = Field(1.0, ge=0)
    edge_loss_weight: float = Field(0.2, ge=0)
    teacher_structure_loss_weight: float = Field(0.0, ge=0)
    teacher_structure_loss_levels: Literal["final", "all"] = "final"
    teacher_structure_temperature: float = Field(1.0, gt=0)
    feature_loss_weight: float = Field(0.0, ge=0)
    feature_loss_warmup_epochs: int = Field(0, ge=0)
    feature_mse_weight: float = Field(1.0, ge=0)
    feature_attention_weight: float = Field(0.5, ge=0)
    feature_mask_guided_weight: float = Field(0.0, ge=0)
    feature_mask_foreground_weight: float = Field(2.0, ge=0)
    feature_mask_edge_weight: float = Field(3.0, ge=0)
    feature_stage_weights: Optional[List[float]] = None


class EvalDuringTrainingConfig(BaseModel):
    """Validation/evaluation settings used during training."""

    enabled: bool = False
    interval: int = Field(0, ge=0)
    pred_root: str = "preds_train"
    save_dir: str = "results_train"
    keep_predictions: bool = False
    run_at_end: bool = True


class LRSchedulerConfig(BaseModel):
    """Learning-rate schedule settings."""

    type: Literal["constant", "cosine", "linear", "poly"] = "cosine"
    step_unit: Literal["epoch", "iter"] = "epoch"
    warmup_epochs: int = Field(0, ge=0)
    warmup_start_factor: float = Field(0.1, ge=0, le=1)
    min_lr: Optional[float] = Field(None, ge=0)
    min_lr_factor: float = Field(0.1, ge=0, le=1)
    power: float = Field(0.9, gt=0)

# --- Main Configuration Class ---

class Config(BaseModel):

    batch_size: int = Field(..., gt=0, description="Batch size for training.")
    batch_size_valid: int = Field(..., gt=0, description="Batch size for validation.")
    epochs: int = Field(..., gt=0, description="Total number of training epochs.")
    lr: float = Field(..., gt=0, description="Learning rate.")
    weight_decay: float = Field(..., ge=0, description="Weight decay for the optimizer.")
    structure_loss_type: Literal["plain", "weighted"] = "plain"
    structure_loss_weight: float = Field(1.0, ge=0)
    edge_supervision_weight: float = Field(1.0, ge=0)
    mask_level_weights: Optional[List[float]] = None
    mask_edge_consistency_weight: float = Field(0.0, ge=0)
    rand_seed: int = 42
    precisionHigh: bool = True

    # --- Dataset Configuration ---
    train_dir: DirectoryPath   # Validates that the train directory exists
    test_dir: DirectoryPath    # Validates that the test directory exists
    load_all: bool = False

    # --- Model Configuration ---
    architecture: Literal[
        "escnet",
        "escnet_slim",
        "escnet_lite_modules",
        "escnet_lite_fast_modules",
        "lite_escnet",
    ] = "escnet"
    backbone: str
    img_size: int = Field(..., gt=0)
    lateral_channels: List[int]
    escnet_width: int = Field(128, gt=0)
    lite_head_channels: int = Field(64, gt=0)
    lite_use_aetp: bool = True
    lite_use_patch_guidance: bool = True
    lite_use_decoder_edge: bool = True
    lite_use_mta_laplace: bool = True
    resume: Optional[str] = None # Allows the field to be missing or empty ""
    resume_optimizer: bool = True
    resume_lr_scheduler: bool = True
    resume_scaler: bool = True
    resume_epoch: bool = True
    resume_strict: bool = True
    compile: bool = True
    distillation: DistillationConfig = Field(default_factory=DistillationConfig)
    eval_during_training: EvalDuringTrainingConfig = Field(default_factory=EvalDuringTrainingConfig)
    lr_scheduler: LRSchedulerConfig = Field(default_factory=LRSchedulerConfig)

    # --- Multi-GPU Settings ---
    device_ids: List[int]
    multi_GPU: bool = False

    # --- Save Settings ---
    save_model_dir: str 
    name: Optional[str] = None
    save_last: int = Field(..., ge=0)
    save_step: int = Field(..., gt=0)

    # --- Data Augmentation ---
    preproc_methods: List[str]

    # --- Path Settings ---
    weights: WeightsPaths

    # --- System ---
    num_workers: int = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_selected_backbone_weight(self) -> "Config":
        if not hasattr(self.weights, self.backbone):
            raise ValueError(f"No weight path configured for backbone '{self.backbone}'")
        weight_path = getattr(self.weights, self.backbone)
        if weight_path is None and not self.backbone.startswith("mobilemamba_"):
            raise ValueError(f"Weight path for backbone '{self.backbone}' is required")
        if self.eval_during_training.enabled and self.eval_during_training.interval <= 0:
            raise ValueError("eval_during_training.interval must be > 0 when eval_during_training.enabled is true")
        if self.distillation.enabled:
            teacher_checkpoint = self.distillation.teacher_checkpoint
            if not teacher_checkpoint:
                raise ValueError("distillation.teacher_checkpoint is required when distillation is enabled")
            if not Path(teacher_checkpoint).is_file():
                raise ValueError(f"Teacher checkpoint not found: {teacher_checkpoint}")
        return self
    
    # --- Helper Properties (for cleaner code in train.py) ---
    @property
    def is_ddp(self) -> bool:
        """Returns True if Distributed Data Parallel (DDP) should be used."""
        return self.multi_GPU and len(self.device_ids) > 1

    @property
    def save_path(self) -> Path:
        """
        Generates the full, unique path for saving models and logs for this run.
        It creates the directory if it doesn't exist.
        """
        path = Path(self.save_model_dir) / self.name
        path.mkdir(parents=True, exist_ok=True)
        return path


def load_config(config_path: str = "config.yaml") -> Config:
    """Loads a YAML configuration file into a validated Config object."""
    config_file = Path(config_path)
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)

    if not config_dict.get("name"):
        config_dict["name"] = config_file.stem

    # Pydantic will raise a ValidationError if the config is invalid
    return Config(**config_dict)
