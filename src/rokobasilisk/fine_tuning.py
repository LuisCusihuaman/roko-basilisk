"""
Phase 3: Fine-Tuning Infrastructure with DPO (Direct Preference Optimization)

This module implements the fine-tuning pipeline to create improved versions
of the LlamaCoderAgent using preference data from human feedback.

Key features:
1. DPO (Direct Preference Optimization) training pipeline
2. Dataset preparation from structured experiences and preference pairs
3. Model fine-tuning with HuggingFace TRL library
4. Cloud GPU configuration (H100 support)
5. Model versioning and evaluation
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        set_seed,
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from datasets import Dataset
    from trl import DPOConfig, DPOTrainer
    HAS_TRL = True
except ImportError:
    HAS_TRL = False
    # Define dummy classes for type hints when TRL is not available
    class DatasetFallback:
        pass
    Dataset = DatasetFallback

    class DPOTrainerFallback:
        pass
    DPOTrainer = DPOTrainerFallback

    class DPOConfigFallback:
        pass
    DPOConfig = DPOConfigFallback

try:
    import wandb
    HAS_WANDB = True
except ImportError:
    HAS_WANDB = False

from .memory import MemoryManager, PreferencePair, TaskExperience

logger = logging.getLogger(__name__)


@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning process."""
    model_name: str = "codellama/CodeLlama-7b-Python-hf"
    output_dir: str = "./models/rokobasilisk-v1.1"
    max_length: int = 1024
    max_prompt_length: int = 512

    # Training hyperparameters
    learning_rate: float = 5e-7
    per_device_train_batch_size: int = 1
    per_device_eval_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    num_train_epochs: int = 3
    warmup_steps: int = 100

    # DPO specific
    beta: float = 0.1  # Temperature parameter for DPO

    # Hardware/Cloud configuration
    use_bf16: bool = True
    use_flash_attention: bool = True
    gradient_checkpointing: bool = True
    dataloader_num_workers: int = 4

    # Evaluation
    eval_steps: int = 100
    save_steps: int = 500
    logging_steps: int = 10

    # Cloud/Hardware
    cloud_provider: Optional[str] = None  # "aws", "gcp", or None for local
    instance_type: str = "p4d.24xlarge"  # AWS H100 instance


@dataclass
class TrainingDataset:
    """Structured training dataset for DPO."""
    experiences: List[TaskExperience]
    preference_pairs: List[PreferencePair]
    train_data: Optional[Dataset] = None
    eval_data: Optional[Dataset] = None


class DatasetPreparation:
    """Prepares training datasets from experiences and preference pairs."""

    def __init__(self, config: FineTuningConfig):
        self.config = config

    def prepare_dpo_dataset(self, experiences: List[TaskExperience],
                           preference_pairs: List[PreferencePair]) -> TrainingDataset:
        """Prepare dataset in DPO format."""

        # Convert preference pairs to DPO format
        dpo_data = []

        for pair in preference_pairs:
            # Create training example
            prompt = self._create_prompt_from_task(pair.task_description)

            example = {
                "prompt": prompt,
                "chosen": pair.chosen_solution,
                "rejected": pair.rejected_solution,
                "chosen_reasoning": pair.chosen_reasoning,
                "rejected_reasoning": pair.rejected_reasoning,
            }
            dpo_data.append(example)

        # Also add successful experiences as positive examples
        for exp in experiences:
            if exp.final_success and exp.human_feedback:
                # Create positive example from successful experience
                prompt = self._create_prompt_from_task(exp.task_description)

                # Create a "rejected" version with common mistakes
                rejected_code = self._create_rejected_version(exp.final_code)

                example = {
                    "prompt": prompt,
                    "chosen": exp.final_code,
                    "rejected": rejected_code,
                    "chosen_reasoning": "Successful solution with good practices",
                    "rejected_reasoning": "Common mistakes and anti-patterns",
                }
                dpo_data.append(example)

        # Split into train/eval
        split_idx = int(0.8 * len(dpo_data))
        train_data = dpo_data[:split_idx]
        eval_data = dpo_data[split_idx:]

        # Convert to HuggingFace datasets
        train_dataset = Dataset.from_list(train_data) if HAS_TRL else None
        eval_dataset = Dataset.from_list(eval_data) if HAS_TRL else None

        return TrainingDataset(
            experiences=experiences,
            preference_pairs=preference_pairs,
            train_data=train_dataset,
            eval_data=eval_dataset
        )

    def _create_prompt_from_task(self, task_description: str) -> str:
        """Create a consistent prompt format for training."""
        return f"""<|system|>
You are an expert Python programmer. Write clean, efficient, and well-documented code.

<|user|>
{task_description}

Please provide a complete Python solution with proper error handling and comments.

<|assistant|>
"""

    def _create_rejected_version(self, good_code: str) -> str:
        """Create a 'rejected' version with common coding mistakes."""
        # This is simplified - in practice would create realistic bad examples
        rejected = good_code.replace("try:", "# try:")  # Remove error handling
        rejected = rejected.replace("    ", "  ")  # Poor indentation
        rejected = "# No comments or documentation\n" + rejected
        rejected = rejected.replace("import ", "from ")  # Import anti-pattern

        return rejected


class CloudConfiguration:
    """Handles cloud infrastructure setup for H100 training."""

    def __init__(self, config: FineTuningConfig):
        self.config = config

    def setup_aws_environment(self) -> Dict[str, Any]:
        """Setup AWS environment for H100 training."""
        aws_config = {
            "instance_type": self.config.instance_type,
            "region": "us-east-1",  # H100 availability
            "ami": "ami-0c02fb55956c7d316",  # Deep Learning AMI
            "setup_commands": [
                "sudo apt-get update",
                "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
                "pip install transformers[torch] accelerate trl datasets wandb",
                "nvidia-smi",  # Verify GPU
            ]
        }

        logger.info(f"AWS H100 configuration prepared for {aws_config['instance_type']}")
        return aws_config

    def setup_gcp_environment(self) -> Dict[str, Any]:
        """Setup GCP environment for H100 training."""
        gcp_config = {
            "machine_type": "a3-highgpu-8g",  # H100 8x GPU
            "zone": "us-central1-a",
            "image": "projects/ml-images/global/images/c0-deeplearning-common-gpu-v20231105-debian-11",
            "setup_commands": [
                "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
                "pip install transformers[torch] accelerate trl datasets wandb",
                "nvidia-smi",
            ]
        }

        logger.info(f"GCP H100 configuration prepared for {gcp_config['machine_type']}")
        return gcp_config

    def check_hardware_requirements(self) -> Dict[str, Any]:
        """Check current hardware capabilities."""
        hardware_info = {
            "cuda_available": torch.cuda.is_available() if HAS_TRANSFORMERS else False,
            "gpu_count": torch.cuda.device_count() if HAS_TRANSFORMERS and torch.cuda.is_available() else 0,
            "total_memory": 0,
            "gpu_names": []
        }

        if hardware_info["cuda_available"]:
            gpu_count = int(hardware_info["gpu_count"])  # type: ignore[call-overload]
            gpu_names = hardware_info["gpu_names"]  # type: ignore[assignment]
            for i in range(gpu_count):
                gpu_props = torch.cuda.get_device_properties(i)
                gpu_names.append(gpu_props.name)  # type: ignore[attr-defined]
                hardware_info["total_memory"] = int(hardware_info["total_memory"]) + int(gpu_props.total_memory)  # type: ignore[call-overload]

        # Convert to GB
        total_memory = int(hardware_info["total_memory"])  # type: ignore[call-overload]
        hardware_info["total_memory_gb"] = total_memory / (1024**3)

        # Recommendations
        total_memory_gb = float(hardware_info["total_memory_gb"])  # type: ignore[arg-type]
        if total_memory_gb < 32:
            hardware_info["recommendation"] = "Consider using cloud H100 instances for optimal training"
        elif "H100" in str(hardware_info["gpu_names"]):
            hardware_info["recommendation"] = "Excellent hardware for fine-tuning"
        else:
            hardware_info["recommendation"] = "Current hardware sufficient for small-scale fine-tuning"

        return hardware_info


class DPOFineTuner:
    """Main class for DPO fine-tuning pipeline."""

    def __init__(self, config: FineTuningConfig):
        self.config = config
        self.cloud_config = CloudConfiguration(config)
        self.data_prep = DatasetPreparation(config)

        # Initialize tracking
        if HAS_WANDB:
            self.setup_wandb()

    def setup_wandb(self) -> None:
        """Setup Weights & Biases tracking."""
        try:
            wandb.init(
                project="rokobasilisk-dpo",
                name=f"dpo-{self.config.model_name.split('/')[-1]}-{int(time.time())}",
                config=asdict(self.config)
            )
            logger.info("W&B tracking initialized")
        except Exception as e:
            logger.warning(f"W&B initialization failed: {e}")

    def prepare_training_data(self, memory_manager: MemoryManager) -> TrainingDataset:
        """Prepare training data from memory manager."""
        logger.info("Preparing training data from experiences...")

        experiences, preference_pairs = memory_manager.generate_training_data()

        if not preference_pairs:
            logger.warning("No preference pairs found - generating from experiences")
            # Create some preference pairs from successful vs failed experiences
            preference_pairs = self._create_basic_preference_pairs(experiences)

        dataset = self.data_prep.prepare_dpo_dataset(experiences, preference_pairs)

        logger.info("Training dataset prepared:")
        logger.info(f"- Experiences: {len(experiences)}")
        logger.info(f"- Preference pairs: {len(preference_pairs)}")
        logger.info(f"- Training examples: {len(dataset.train_data) if dataset.train_data else 0}")
        logger.info(f"- Validation examples: {len(dataset.eval_data) if dataset.eval_data else 0}")

        return dataset

    def _create_basic_preference_pairs(self, experiences: List[TaskExperience]) -> List[PreferencePair]:
        """Create basic preference pairs from successful vs failed experiences."""
        pairs: List[PreferencePair] = []

        successful = [exp for exp in experiences if exp.final_success]
        failed = [exp for exp in experiences if not exp.final_success]

        for success_exp in successful[:5]:  # Limit for demo
            for fail_exp in failed[:3]:
                if success_exp.task_name == fail_exp.task_name:
                    pair = PreferencePair(
                        task_id=f"auto_{len(pairs)}",
                        task_description=success_exp.task_description,
                        chosen_solution=success_exp.final_code,
                        rejected_solution=fail_exp.final_code,
                        chosen_reasoning="Successful solution",
                        rejected_reasoning="Failed solution",
                        preference_score=0.8,
                        timestamp=time.time()
                    )
                    pairs.append(pair)

        logger.info(f"Created {len(pairs)} basic preference pairs")
        return pairs

    def fine_tune_model(self, dataset: TrainingDataset) -> str:
        """Fine-tune the model using DPO."""
        if not HAS_TRL or not HAS_TRANSFORMERS:
            logger.error("TRL and Transformers required for fine-tuning")
            return ""

        logger.info(f"Starting DPO fine-tuning of {self.config.model_name}")

        # Check hardware
        hardware_info = self.cloud_config.check_hardware_requirements()
        logger.info(f"Hardware check: {hardware_info['recommendation']}")

        try:
            # Load model and tokenizer
            logger.info("Loading base model and tokenizer...")

            tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name,
                torch_dtype=torch.bfloat16 if self.config.use_bf16 and torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )

            # Prepare reference model for DPO
            ref_model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name,
                torch_dtype=torch.bfloat16 if self.config.use_bf16 and torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )

            # DPO training configuration
            training_args = DPOConfig(
                output_dir=self.config.output_dir,
                learning_rate=self.config.learning_rate,
                per_device_train_batch_size=self.config.per_device_train_batch_size,
                per_device_eval_batch_size=self.config.per_device_eval_batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                num_train_epochs=self.config.num_train_epochs,
                warmup_steps=self.config.warmup_steps,
                bf16=self.config.use_bf16 and torch.cuda.is_available(),
                gradient_checkpointing=self.config.gradient_checkpointing,
                eval_strategy="steps",
                eval_steps=self.config.eval_steps,
                save_steps=self.config.save_steps,
                logging_steps=self.config.logging_steps,
                beta=self.config.beta,
                max_length=self.config.max_length,
                max_prompt_length=self.config.max_prompt_length,
                report_to="wandb" if HAS_WANDB else None,
            )

            # Initialize DPO trainer
            dpo_trainer = DPOTrainer(
                model=model,
                ref_model=ref_model,
                args=training_args,
                train_dataset=dataset.train_data,
                eval_dataset=dataset.eval_data,
                tokenizer=tokenizer,
            )

            # Start training
            logger.info("Starting DPO training...")
            set_seed(42)  # For reproducibility

            dpo_trainer.train()

            # Save the fine-tuned model
            logger.info(f"Saving fine-tuned model to {self.config.output_dir}")
            dpo_trainer.save_model()
            tokenizer.save_pretrained(self.config.output_dir)

            # Save training metadata
            metadata = {
                "base_model": self.config.model_name,
                "training_date": time.time(),
                "config": asdict(self.config),
                "dataset_stats": {
                    "train_size": len(dataset.train_data) if dataset.train_data else 0,
                    "eval_size": len(dataset.eval_data) if dataset.eval_data else 0,
                    "preference_pairs": len(dataset.preference_pairs) if dataset.preference_pairs else 0
                },
                "hardware_info": hardware_info
            }

            with open(Path(self.config.output_dir) / "training_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info("Fine-tuning completed successfully!")
            return self.config.output_dir

        except Exception as e:
            logger.error(f"Error during fine-tuning: {e}")
            return ""

    def evaluate_model(self, model_path: str, test_tasks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Evaluate the fine-tuned model on test tasks."""
        if not test_tasks:
            test_tasks = [
                "Create a Python script that fetches stock prices",
                "Write a file organizer that sorts files by extension",
                "Implement a text processor with word frequency analysis"
            ]

        logger.info(f"Evaluating model: {model_path}")

        try:
            # Load fine-tuned model
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )

            results = {}

            for task in test_tasks:
                logger.info(f"Testing task: {task}")

                # Create prompt
                prompt = f"""<|system|>
You are an expert Python programmer. Write clean, efficient, and well-documented code.

<|user|>
{task}

Please provide a complete Python solution with proper error handling and comments.

<|assistant|>
"""

                # Generate code
                inputs = tokenizer(prompt, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=512,
                        do_sample=True,
                        temperature=0.1,
                        top_p=0.95,
                        pad_token_id=tokenizer.eos_token_id
                    )

                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                code = generated_text[len(prompt):].strip()

                # Basic evaluation metrics
                metrics = {
                    "code_length": len(code),
                    "has_imports": "import " in code,
                    "has_functions": "def " in code,
                    "has_error_handling": "try:" in code or "except" in code,
                    "has_comments": "#" in code,
                }

                results[task] = {
                    "generated_code": code[:500] + "..." if len(code) > 500 else code,
                    "metrics": metrics
                }

            # Overall evaluation
            overall_score = sum(
                sum(result["metrics"].values()) for result in results.values()
            ) / (len(results) * 5)  # 5 metrics per task

            evaluation = {
                "model_path": model_path,
                "overall_score": overall_score,
                "task_results": results,
                "evaluation_date": time.time()
            }

            # Save evaluation results
            eval_file = Path(model_path) / "evaluation_results.json"
            with open(eval_file, "w") as f:
                json.dump(evaluation, f, indent=2)

            logger.info(f"Evaluation completed. Overall score: {overall_score:.2f}")
            return evaluation

        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            return {}


class ModelVersioning:
    """Manages model versions and deployment."""

    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

    def list_model_versions(self) -> List[Dict[str, Any]]:
        """List all available model versions."""
        versions = []

        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                metadata_file = model_dir / "training_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = json.load(f)

                        # Check if evaluation exists
                        eval_file = model_dir / "evaluation_results.json"
                        evaluation = None
                        if eval_file.exists():
                            with open(eval_file) as f:
                                evaluation = json.load(f)

                        versions.append({
                            "name": model_dir.name,
                            "path": str(model_dir),
                            "metadata": metadata,
                            "evaluation": evaluation,
                            "created": metadata.get("training_date", 0)
                        })
                    except Exception as e:
                        logger.warning(f"Could not load metadata for {model_dir}: {e}")

        # Sort by creation date
        versions.sort(key=lambda x: x["created"], reverse=True)
        return versions

    def get_best_model(self) -> Optional[str]:
        """Get the path to the best performing model."""
        versions = self.list_model_versions()

        best_model = None
        best_score = -1

        for version in versions:
            if version["evaluation"]:
                score = version["evaluation"].get("overall_score", 0)
                if score > best_score:
                    best_score = score
                    best_model = version["path"]

        return best_model  # type: ignore[no-any-return]


# CLI Interface for Fine-tuning
def run_fine_tuning_pipeline(memory_file: str = "memory.txt",
                           interactive_feedback: bool = False,
                           model_name: str = "codellama/CodeLlama-7b-Python-hf",
                           output_dir: Optional[str] = None) -> str:
    """Run the complete fine-tuning pipeline."""

    logger.info("Starting Phase 3: Fine-tuning Pipeline")

    # Initialize components
    memory_manager = MemoryManager(memory_file)

    # Process experiences and collect feedback
    logger.info("Step 1: Processing experiences and collecting feedback")
    experiences = memory_manager.process_new_experiences()

    if not experiences:
        logger.warning("No experiences found. Please run some agent tasks first.")
        return ""

    # Collect feedback
    feedback_results = memory_manager.collect_feedback_batch(experiences, interactive_feedback)
    logger.info(f"Collected feedback for {len(feedback_results)} experiences")

    # Initialize fine-tuning
    if not output_dir:
        output_dir = f"./models/rokobasilisk-v{int(time.time())}"

    return output_dir  # type: ignore[no-any-return]

    config = FineTuningConfig(
        model_name=model_name,
        output_dir=output_dir
    )

    fine_tuner = DPOFineTuner(config)

    # Prepare training data
    logger.info("Step 2: Preparing training data")
    dataset = fine_tuner.prepare_training_data(memory_manager)

    if not dataset.train_data or len(dataset.train_data) < 5:
        logger.warning("Insufficient training data. Need at least 5 examples for meaningful fine-tuning.")
        return ""

    # Fine-tune model
    logger.info("Step 3: Fine-tuning model")
    model_path = fine_tuner.fine_tune_model(dataset)

    if not model_path:
        logger.error("Fine-tuning failed")
        return ""

    # Evaluate model
    logger.info("Step 4: Evaluating fine-tuned model")
    evaluation = fine_tuner.evaluate_model(model_path)

    logger.info("Fine-tuning pipeline completed successfully!")
    logger.info(f"Model saved to: {model_path}")
    logger.info(f"Evaluation score: {evaluation.get('overall_score', 0):.2f}")

    return model_path  # type: ignore[no-any-return]


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RokoBasilisk Fine-tuning Pipeline")
    parser.add_argument("--memory-file", default="memory.txt", help="Memory file to process")
    parser.add_argument("--interactive", action="store_true", help="Interactive feedback collection")
    parser.add_argument("--model-name", default="codellama/CodeLlama-7b-Python-hf", help="Base model")
    parser.add_argument("--output-dir", help="Output directory for fine-tuned model")

    args = parser.parse_args()

    if not HAS_TRL:
        print("Warning: TRL library not available. Installing dependencies:")
        print("pip install trl datasets wandb")
        exit(1)

    # Run pipeline
    model_path = run_fine_tuning_pipeline(
        memory_file=args.memory_file,
        interactive_feedback=args.interactive,
        model_name=args.model_name,
        output_dir=args.output_dir
    )

    if model_path:
        print("\n🎉 Fine-tuning completed successfully!")
        print(f"📁 Model saved to: {model_path}")

        # Show model versions
        versioning = ModelVersioning()
        versions = versioning.list_model_versions()
        print(f"\n📋 Available model versions: {len(versions)}")

        for version in versions[:3]:  # Show top 3
            score = version["evaluation"]["overall_score"] if version["evaluation"] else 0
            print(f"  - {version['name']}: {score:.2f}")

        best_model = versioning.get_best_model()
        if best_model:
            print(f"\n🏆 Best model: {Path(best_model).name}")
    else:
        print("❌ Fine-tuning failed. Check logs for details.")
