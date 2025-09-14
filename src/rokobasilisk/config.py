"""
Agent Configuration System

Provides configuration management for the self-modifying AI agent including:
- Model settings (Llama 3 70B, local models, API endpoints)
- Cloud infrastructure configuration (AWS, GCP)
- Security and sandbox settings
- Task definitions and evaluation criteria
- Performance thresholds and improvement targets
"""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


@dataclass
class ModelConfig:
    """Configuration for AI models."""
    name: str = "codellama/CodeLlama-7b-Python-hf"
    device: str = "auto"  # "auto", "cpu", "cuda", "mps"
    torch_dtype: str = "float16"  # "float16", "float32", "bfloat16"
    max_tokens: int = 512
    temperature: float = 0.1
    top_p: float = 0.95
    do_sample: bool = True
    trust_remote_code: bool = True
    use_cache: bool = True
    local_model_path: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None


@dataclass
class CloudConfig:
    """Configuration for cloud infrastructure."""
    provider: str = "aws"  # "aws", "gcp", "azure", "local"
    region: str = "us-west-2"
    instance_type: str = "p4d.24xlarge"  # For H100 GPUs
    storage_bucket: Optional[str] = None
    credentials_file: Optional[str] = None
    project_id: Optional[str] = None  # For GCP

    # GPU configuration
    gpu_count: int = 8
    gpu_type: str = "H100"
    gpu_memory: str = "80GB"

    # Networking
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None
    security_group_id: Optional[str] = None


@dataclass
class SandboxConfig:
    """Configuration for code execution sandbox."""
    use_docker: bool = True
    container_image: str = "rokobasilisk:sandbox"
    memory_limit: str = "512m"
    cpu_limit: str = "1.0"
    network_access: bool = False
    execution_timeout: int = 30
    max_file_size: int = 1024 * 1024  # 1MB
    allowed_packages: List[str] = field(default_factory=lambda: [
        "requests", "pandas", "numpy", "matplotlib", "pytest",
        "csv", "json", "datetime", "os", "sys", "pathlib"
    ])
    blocked_modules: List[str] = field(default_factory=lambda: [
        "subprocess", "os.system", "eval", "exec", "compile",
        "socket", "urllib", "ftplib", "smtplib"
    ])


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_human_oversight: bool = True
    require_approval_for_modifications: bool = True
    max_modification_size: int = 1000  # Max lines of code that can be modified
    backup_before_modification: bool = True
    enable_rollback: bool = True
    log_all_executions: bool = True
    encrypt_model_cache: bool = False
    access_control_enabled: bool = True


@dataclass
class PerformanceConfig:
    """Performance and optimization configuration."""
    cache_enabled: bool = True
    cache_directory: str = ".rokobasilisk_cache"
    max_cache_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    parallel_execution: bool = True
    max_workers: int = 4
    benchmark_enabled: bool = True
    profiling_enabled: bool = False

    # Improvement thresholds
    min_improvement_threshold: float = 0.05  # 5% minimum improvement
    max_modification_attempts: int = 5
    convergence_patience: int = 3  # Stop if no improvement for N iterations


@dataclass
class TaskConfig:
    """Configuration for agent tasks and evaluation."""
    task_directory: str = "tasks"
    results_directory: str = "results"
    evaluation_timeout: int = 60
    success_threshold: float = 0.8

    # Default task categories
    task_categories: List[str] = field(default_factory=lambda: [
        "data_processing", "api_integration", "algorithm_optimization",
        "testing", "documentation", "debugging"
    ])

    # Evaluation metrics
    metrics: List[str] = field(default_factory=lambda: [
        "execution_time", "memory_usage", "code_quality",
        "test_coverage", "correctness", "robustness"
    ])


@dataclass
class AgentConfig:
    """Main configuration class for the AI agent."""
    # Core configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    cloud: CloudConfig = field(default_factory=CloudConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    tasks: TaskConfig = field(default_factory=TaskConfig)

    # Agent metadata
    agent_name: str = "RokoBasilisk-Agent"
    agent_version: str = "4.0.0"
    creation_timestamp: Optional[str] = None
    last_modified: Optional[str] = None

    # Logging and monitoring
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_telemetry: bool = True
    monitoring_endpoint: Optional[str] = None


class ConfigManager:
    """Manages configuration loading, saving, and validation."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = Path(config_path) if config_path else Path("config.yaml")
        self.config: Optional[AgentConfig] = None

    def load_config(self, config_path: Optional[Union[str, Path]] = None) -> AgentConfig:
        """Load configuration from file."""
        if config_path:
            self.config_path = Path(config_path)

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    if self.config_path.suffix.lower() == '.json':
                        data = json.load(f)
                    else:  # Default to YAML
                        data = yaml.safe_load(f)

                # Convert nested dicts to dataclasses
                config_dict = self._dict_to_config(data)
                self.config = AgentConfig(**config_dict)

            except Exception as e:
                print(f"Error loading config from {self.config_path}: {e}")
                print("Using default configuration")
                self.config = AgentConfig()
        else:
            print(f"Config file {self.config_path} not found, using defaults")
            self.config = AgentConfig()

        return self.config

    def save_config(self, config: Optional[AgentConfig] = None,
                   config_path: Optional[Union[str, Path]] = None) -> None:
        """Save configuration to file."""
        if config:
            self.config = config
        if config_path:
            self.config_path = Path(config_path)

        if not self.config:
            raise ValueError("No configuration to save")

        # Convert to dictionary
        config_dict = asdict(self.config)

        # Create directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, 'w') as f:
                if self.config_path.suffix.lower() == '.json':
                    json.dump(config_dict, f, indent=2)
                else:  # Default to YAML
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)

            print(f"Configuration saved to {self.config_path}")

        except Exception as e:
            print(f"Error saving config to {self.config_path}: {e}")

    def _dict_to_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert nested dictionaries to appropriate dataclass instances."""
        result: Dict[str, Any] = {}

        for key, value in data.items():
            if key == 'model' and isinstance(value, dict):
                result[key] = ModelConfig(**value)
            elif key == 'cloud' and isinstance(value, dict):
                result[key] = CloudConfig(**value)
            elif key == 'sandbox' and isinstance(value, dict):
                result[key] = SandboxConfig(**value)
            elif key == 'security' and isinstance(value, dict):
                result[key] = SecurityConfig(**value)
            elif key == 'performance' and isinstance(value, dict):
                result[key] = PerformanceConfig(**value)
            elif key == 'tasks' and isinstance(value, dict):
                result[key] = TaskConfig(**value)
            else:
                result[key] = value

        return result

    def get_env_config(self) -> Dict[str, Any]:
        """Get configuration from environment variables."""
        env_config: Dict[str, Any] = {}

        # Model configuration
        if os.getenv('ROKO_MODEL_NAME'):
            env_config.setdefault('model', {})['name'] = os.getenv('ROKO_MODEL_NAME')
        if os.getenv('ROKO_MODEL_DEVICE'):
            env_config.setdefault('model', {})['device'] = os.getenv('ROKO_MODEL_DEVICE')
        if os.getenv('ROKO_API_KEY'):
            env_config.setdefault('model', {})['api_key'] = os.getenv('ROKO_API_KEY')

        # Cloud configuration
        if os.getenv('ROKO_CLOUD_PROVIDER'):
            env_config.setdefault('cloud', {})['provider'] = os.getenv('ROKO_CLOUD_PROVIDER')
        if os.getenv('ROKO_CLOUD_REGION'):
            env_config.setdefault('cloud', {})['region'] = os.getenv('ROKO_CLOUD_REGION')
        if os.getenv('AWS_ACCESS_KEY_ID'):
            env_config.setdefault('cloud', {})['credentials_file'] = 'aws_credentials'

        # Security configuration
        if os.getenv('ROKO_ENABLE_HUMAN_OVERSIGHT'):
            env_val = os.getenv('ROKO_ENABLE_HUMAN_OVERSIGHT')
            if env_val:
                env_config.setdefault('security', {})['enable_human_oversight'] = \
                    env_val.lower() == 'true'

        return env_config

    def validate_config(self, config: Optional[AgentConfig] = None) -> List[str]:
        """Validate configuration and return list of issues."""
        if not config:
            config = self.config

        if not config:
            return ["No configuration loaded"]

        issues = []

        # Validate model configuration
        if config.model.name and not config.model.api_endpoint:
            # Check if it's a valid HuggingFace model name
            if '/' not in config.model.name and not Path(config.model.name).exists():
                issues.append(f"Invalid model name or path: {config.model.name}")

        # Validate cloud configuration
        valid_providers = ["aws", "gcp", "azure", "local"]
        if config.cloud.provider not in valid_providers:
            issues.append(f"Invalid cloud provider: {config.cloud.provider}")

        # Validate security settings
        if config.security.max_modification_size < 1:
            issues.append("max_modification_size must be positive")

        # Validate performance settings
        if config.performance.max_workers < 1:
            issues.append("max_workers must be positive")

        return issues

    def create_sample_config(self, filename: str = "config_sample.yaml") -> None:
        """Create a sample configuration file."""
        sample_config = AgentConfig()

        # Add some example values
        sample_config.model.name = "codellama/CodeLlama-13b-Python-hf"
        sample_config.cloud.provider = "aws"
        sample_config.cloud.instance_type = "p4d.24xlarge"
        sample_config.security.enable_human_oversight = True
        sample_config.performance.cache_enabled = True

        config_path = Path(filename)
        with open(config_path, 'w') as f:
            yaml.dump(asdict(sample_config), f, default_flow_style=False, indent=2)

        print(f"Sample configuration created: {config_path}")


def load_default_config() -> AgentConfig:
    """Load the default configuration."""
    manager = ConfigManager()
    return manager.load_config()


def create_cloud_config(provider: str = "aws",
                       instance_type: str = "p4d.24xlarge") -> CloudConfig:
    """Create cloud configuration for specific provider."""
    config = CloudConfig()
    config.provider = provider
    config.instance_type = instance_type

    if provider == "aws":
        config.region = "us-west-2"
        config.gpu_type = "H100"
    elif provider == "gcp":
        config.region = "us-central1"
        config.project_id = "your-project-id"
        config.gpu_type = "H100"
    elif provider == "azure":
        config.region = "West US 2"
        config.gpu_type = "H100"

    return config


def create_development_config() -> AgentConfig:
    """Create configuration optimized for development."""
    config = AgentConfig()

    # Use smaller model for development
    config.model.name = "codellama/CodeLlama-7b-Python-hf"
    config.model.max_tokens = 256

    # Local execution
    config.cloud.provider = "local"

    # Relaxed security for development
    config.security.require_approval_for_modifications = False

    # Enhanced logging
    config.log_level = "DEBUG"
    config.performance.profiling_enabled = True

    return config


def create_production_config() -> AgentConfig:
    """Create configuration optimized for production."""
    config = AgentConfig()

    # Production model
    config.model.name = "meta-llama/Llama-3-70b-hf"  # Would need actual model path
    config.model.max_tokens = 1024

    # Cloud execution
    config.cloud.provider = "aws"
    config.cloud.instance_type = "p4d.24xlarge"

    # Enhanced security
    config.security.enable_human_oversight = True
    config.security.require_approval_for_modifications = True
    config.security.log_all_executions = True

    # Performance optimization
    config.performance.cache_enabled = True
    config.performance.parallel_execution = True
    config.performance.max_workers = 8

    return config


# Example usage
if __name__ == "__main__":
    # Create configuration manager
    manager = ConfigManager()

    # Create sample configurations
    manager.create_sample_config("config_sample.yaml")

    # Save development and production configs
    dev_config = create_development_config()
    manager.save_config(dev_config, "config_development.yaml")

    prod_config = create_production_config()
    manager.save_config(prod_config, "config_production.yaml")

    # Load and validate configuration
    config = manager.load_config("config_sample.yaml")
    issues = manager.validate_config(config)

    if issues:
        print("Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration is valid")

    print(f"Loaded configuration for agent: {config.agent_name}")
    print(f"Model: {config.model.name}")
    print(f"Cloud provider: {config.cloud.provider}")
    print(f"Security oversight: {config.security.enable_human_oversight}")
