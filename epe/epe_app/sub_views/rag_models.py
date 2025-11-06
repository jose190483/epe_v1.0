# rag_models.py (import this from your views)

from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.utils import logging as hf_logging

hf_logging.set_verbosity_error()  # quiet noisy logs

MISTRAL_PATH = Path(r"C:\Users\BVM\PycharmProjects\epe_v_3.0\epe\epe_app\models\Mistral_7B_Instruct_v0.3")
DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

TOKENIZER = AutoTokenizer.from_pretrained(MISTRAL_PATH, local_files_only=True)
MODEL = AutoModelForCausalLM.from_pretrained(
    MISTRAL_PATH, local_files_only=True, device_map="auto", dtype=DTYPE
)

# be explicit to silence the pad warning
if TOKENIZER.pad_token is None:
    TOKENIZER.pad_token = TOKENIZER.eos_token
MODEL.config.pad_token_id = TOKENIZER.eos_token_id
TOKENIZER.padding_side = "left"
