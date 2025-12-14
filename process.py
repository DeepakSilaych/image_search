import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

class VisualLLM:
    def __init__(self):
        print("--- Loading Moondream2 (Visual LLM) ---")
        self.model_id = "vikhyatk/moondream2"
        # Explicitly pinning revision to a stable commit hash is also a good safety practice
        # But downgrading transformers is the primary fix here.
        
        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        # Load Model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, 
            trust_remote_code=True  # Required for Moondream
        ).to(self.device)
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        print(f"--- Moondream Loaded on {self.device} ---")

    def analyze(self, image_input, prompt):
        try:
            # 1. Handle Input
            if isinstance(image_input, str):
                image = Image.open(image_input)
            else:
                image = image_input # Assume PIL
            
            # 2. Run Inference
            enc_image = self.model.encode_image(image)
            answer = self.model.answer_question(enc_image, prompt, self.tokenizer)
            
            return answer

        except Exception as e:
            print(f"Error in VLLM: {e}")
            return ""

if __name__ == "__main__":
    v = VisualLLM()
    # Should print a description now
    print(v.analyze("img/3.jpg", "Describe this image."))