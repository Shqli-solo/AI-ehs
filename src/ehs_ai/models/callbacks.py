"""
训练回调函数

实现早停（Early Stopping）和模型检查点（Checkpoint）功能。
"""

import os
import json
import torch
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments


@dataclass
class EarlyStoppingConfig:
    """早停配置"""
    min_delta: float = 1e-4  # 最小改善阈值
    patience: int = 3  # 容忍 epochs
    restore_best_weights: bool = True  # 是否恢复最佳权重


class EarlyStoppingCallback(TrainerCallback):
    """
    早停回调

    当 validation loss 连续 patience 个 epochs 不下降时停止训练。
    """

    def __init__(
        self,
        patience: int = 3,
        min_delta: float = 1e-4,
        restore_best_weights: bool = True
    ):
        """
        初始化早停回调

        Args:
            patience: 容忍 epochs 数
            min_delta: 最小改善阈值
            restore_best_weights: 是否恢复最佳权重
        """
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best_weights = restore_best_weights

        self.best_loss: Optional[float] = None
        self.best_weights: Optional[Dict] = None
        self.counter: int = 0
        self.best_epoch: int = 0
        self.should_stop: bool = False

    def on_evaluate(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        metrics: Dict[str, float],
        model=None,
        **kwargs
    ):
        """评估后回调"""
        eval_loss = metrics.get("eval_loss")

        if eval_loss is None:
            return

        # 初始化最佳损失
        if self.best_loss is None:
            self.best_loss = eval_loss
            self.best_epoch = state.epoch
            if self.restore_best_weights and model:
                self.best_weights = {
                    k: v.cpu().clone() for k, v in model.state_dict().items()
                }
            return

        # 检查是否有改善
        if eval_loss < self.best_loss - self.min_delta:
            # 有改善
            self.best_loss = eval_loss
            self.best_epoch = state.epoch
            self.counter = 0
            if self.restore_best_weights and model:
                self.best_weights = {
                    k: v.cpu().clone() for k, v in model.state_dict().items()
                }
            print(f"\n✓ Validation loss improved: {eval_loss:.4f} (best: {self.best_loss:.4f})")
        else:
            # 没有改善
            self.counter += 1
            print(f"\n✗ No improvement. Patience: {self.counter}/{self.patience}")

            if self.counter >= self.patience:
                self.should_stop = True
                control.should_training_stop = True
                print(f"\n⚠ Early stopping triggered at epoch {state.epoch:.2f}")
                print(f"   Best epoch: {self.best_epoch:.2f}, Best loss: {self.best_loss:.4f}")

    def restore_best_weights(self, model) -> None:
        """恢复最佳权重"""
        if self.best_weights and model:
            model.load_state_dict(self.best_weights)
            print(f"Restored best weights from epoch {self.best_epoch:.2f}")


class CheckpointCallback(TrainerCallback):
    """
    检查点回调

    每个 epoch 保存一次模型检查点，支持断点恢复训练。
    """

    def __init__(
        self,
        output_dir: str,
        save_every_epoch: bool = True,
        save_total_limit: int = 3,
        save_optimizer: bool = True
    ):
        """
        初始化检查点回调

        Args:
            output_dir: 检查点保存目录
            save_every_epoch: 是否每个 epoch 保存
            save_total_limit: 保留的检查点数量上限
            save_optimizer: 是否保存优化器状态
        """
        self.output_dir = output_dir
        self.save_every_epoch = save_every_epoch
        self.save_total_limit = save_total_limit
        self.save_optimizer = save_optimizer

        self.checkpoint_history: List[str] = []
        self.best_eval_loss: Optional[float] = None

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

    def _save_checkpoint(
        self,
        model,
        tokenizer,
        epoch: float,
        step: int,
        eval_loss: Optional[float] = None
    ):
        """保存检查点"""
        checkpoint_name = f"checkpoint-epoch-{epoch:.2f}-step-{step}"
        checkpoint_path = os.path.join(self.output_dir, checkpoint_name)

        # 保存模型
        model.save_pretrained(checkpoint_path)
        if tokenizer:
            tokenizer.save_pretrained(checkpoint_path)

        # 保存额外信息
        extra_info = {
            "epoch": epoch,
            "step": step,
            "eval_loss": eval_loss,
        }
        with open(os.path.join(checkpoint_path, "training_info.json"), "w") as f:
            json.dump(extra_info, f, indent=2)

        self.checkpoint_history.append(checkpoint_path)
        print(f"\n✓ Checkpoint saved: {checkpoint_path}")

        # 清理旧检查点
        self._cleanup_old_checkpoints()

    def _cleanup_old_checkpoints(self):
        """清理旧的检查点"""
        if len(self.checkpoint_history) > self.save_total_limit:
            old_checkpoint = self.checkpoint_history.pop(0)
            try:
                import shutil
                shutil.rmtree(old_checkpoint)
                print(f"  Removed old checkpoint: {old_checkpoint}")
            except Exception as e:
                print(f"  Failed to remove old checkpoint: {e}")

    def on_epoch_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        model=None,
        tokenizer=None,
        metrics: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """epoch 结束时回调"""
        if not self.save_every_epoch:
            return

        eval_loss = metrics.get("eval_loss") if metrics else None
        self._save_checkpoint(
            model=model,
            tokenizer=tokenizer,
            epoch=state.epoch,
            step=state.global_step,
            eval_loss=eval_loss
        )

    def on_save(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        model=None,
        tokenizer=None,
        **kwargs
    ):
        """保存时回调（作为 on_epoch_end 的补充）"""
        # 如果 on_epoch_end 已经保存，这里可以跳过
        pass

    def get_latest_checkpoint(self) -> Optional[str]:
        """获取最新的检查点路径"""
        if not self.checkpoint_history:
            return None
        return self.checkpoint_history[-1]

    def resume_from_checkpoint(self, model, tokenizer) -> Optional[str]:
        """
        从最新检查点恢复

        Returns:
            检查点路径，如果没有检查点则返回 None
        """
        latest_checkpoint = self.get_latest_checkpoint()
        if latest_checkpoint and os.path.exists(latest_checkpoint):
            from peft import PeftModel
            # 加载 adapter
            model = PeftModel.from_pretrained(model, latest_checkpoint)
            print(f"Resumed from checkpoint: {latest_checkpoint}")

            # 加载训练信息
            info_path = os.path.join(latest_checkpoint, "training_info.json")
            if os.path.exists(info_path):
                with open(info_path) as f:
                    info = json.load(f)
                print(f"  Epoch: {info['epoch']:.2f}, Step: {info['step']}")
                if info.get('eval_loss'):
                    print(f"  Eval Loss: {info['eval_loss']:.4f}")

            return latest_checkpoint
        return None


class TrainingProgressCallback(TrainerCallback):
    """
    训练进度回调

    记录并打印训练进度信息。
    """

    def __init__(self, log_every_steps: int = 10):
        self.log_every_steps = log_every_steps
        self.epoch_losses: List[float] = []
        self.eval_losses: List[float] = []

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """日志记录回调"""
        if logs and state.global_step % self.log_every_steps == 0:
            loss = logs.get("loss", 0)
            lr = logs.get("learning_rate", 0)
            print(f"\n[Step {state.global_step}] Loss: {loss:.4f}, LR: {lr:.2e}")

    def on_evaluate(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        metrics: Dict[str, float],
        **kwargs
    ):
        """评估回调"""
        eval_loss = metrics.get("eval_loss")
        if eval_loss:
            self.eval_losses.append(eval_loss)
            print(f"\n[Epoch {state.epoch:.2f}] Eval Loss: {eval_loss:.4f}")

    def save_training_history(self, output_path: str):
        """保存训练历史"""
        import json
        history = {
            "epoch_losses": self.epoch_losses,
            "eval_losses": self.eval_losses
        }
        with open(output_path, "w") as f:
            json.dump(history, f, indent=2)
        print(f"Training history saved to: {output_path}")


def create_callbacks(
    output_dir: str,
    early_stopping_patience: int = 3,
    save_total_limit: int = 3,
    log_every_steps: int = 10
) -> List[TrainerCallback]:
    """
    创建回调列表

    Args:
        output_dir: 输出目录
        early_stopping_patience: 早停 patience
        save_total_limit: 检查点保留数量
        log_every_steps: 日志记录步数

    Returns:
        回调列表
    """
    return [
        EarlyStoppingCallback(patience=early_stopping_patience),
        CheckpointCallback(
            output_dir=output_dir,
            save_every_epoch=True,
            save_total_limit=save_total_limit
        ),
        TrainingProgressCallback(log_every_steps=log_every_steps),
    ]
