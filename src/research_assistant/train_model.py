from dataclasses import dataclass, field
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer
from pathlib import Path
import torch

# Train configuration
@dataclass
class Config:
    output_root_dir: Path

    # Model
    model_name: str = "Qwen/Qwen3.5-4B"
    use_4bit: bool = True   # For QLoRA
    use_8bit: bool = False

    # QLoRA hyperparameters
    lora_r: int = 4
    lora_alpha: int = 8
    lora_dropout:float = 0.05

    lora_target_modules: str = "all-linear"
    # If specific modules are needed, use the following line
    # lora_target_modules: list[str] = field(default_factory=lambda: ["q_proj", "v_proj"]) # ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

    # Training
    num_train_epochs: int = 3
    per_device_train_batch: int = 1
    gradient_accumulation_steps: int = 8 # effective batch: 1x8
    learning_rate: float = 2e-4
    warmup_steps: float = 8
    max_length: int = 2048 # 4096 - 16384 - 8192 - 4096 - 32768
    lr_scheduler_type: str = "cosine"
    fp16: bool = not torch.cuda.is_bf16_supported()
    bf16: bool = torch.cuda.is_bf16_supported()
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 100

    def __post_init__(self):
        out_dir: Path = self.output_root_dir / f"model_{self.lora_r}_{self.lora_alpha}"
        out_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir: str = str(out_dir)


def train(dataset_path: Path, output_dir: Path):
    config = Config(output_dir)

    # Load dataset
    paper_dataset = load_dataset("json", data_files={"train": str(dataset_path / "train.jsonl"), "validation": str(dataset_path / "val.jsonl")})

    # Load model
    bnb_config = None
    if config.use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16 if config.bf16 else torch.float16,
            bnb_4bit_use_double_quant=True
        )
    elif config.use_8bit:
        bnb_config = BitsAndBytesConfig(load_in_8bit=True)

    model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16 if config.bf16 else torch.float16
    )

    tokenizer = AutoTokenizer.from_pretrained(config.model_name)

    if config.use_4bit or config.use_8bit:
        model = prepare_model_for_kbit_training(model)

    # LoRA adapter
    peft_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        task_type="CAUSAL_LM",
        target_modules=config.lora_target_modules
    )

    training_args = SFTConfig(
        output_dir=config.output_dir,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch,
        per_device_eval_batch_size=config.per_device_train_batch,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_steps=config.warmup_steps,
        lr_scheduler_type=config.lr_scheduler_type,
        bf16=config.bf16,
        fp16=config.fp16,
        gradient_checkpointing=True,
        max_length=config.max_length,

        optim="paged_adamw_8bit",
        activation_offloading=True,
        loss_type="chunked_nll",

        # Evaluation/checkpoints
        eval_strategy="epoch",
        save_strategy="epoch",

        # Logging
        logging_steps=config.logging_steps
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        processing_class=tokenizer,
        train_dataset=paper_dataset["train"],
        eval_dataset=paper_dataset["validation"],
        peft_config=peft_config
    )

    trainer.model.print_trainable_parameters() # Sanity check. Currently trainable params: 8,116,224 || all params: 4,213,867,520 || trainable%: 0.1926

    print("Starting training...")
    trainer.train()
    
    trainer.model.save_pretrained(config.output_dir)
