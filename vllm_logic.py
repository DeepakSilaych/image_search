import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

class VisualLLM:
    def __init__(self):
        print("--- Loading Moondream2 (Visual LLM) ---")
        self.model_id = "vikhyatk/moondream2"
        
        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, 
            trust_remote_code=True
        ).to(self.device)
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        print(f"--- Moondream Loaded on {self.device} ---")

    def encode(self, image_input):
        """
        Run ONLY the heavy vision encoder.
        Returns: Image Embeddings (Tensor)
        """
        if isinstance(image_input, str):
            image = Image.open(image_input)
        else:
            image = image_input # Assume PIL

        # This is the Slow Step (10s+)
        with torch.no_grad():
            return self.model.encode_image(image)

    def ask(self, encoded_image, prompt):
        """
        Run ONLY the text generation.
        Returns: String answer
        """
        # This is the Fast Step (1-2s)
        return self.model.answer_question(encoded_image, prompt, self.tokenizer)

if __name__ == "__main__":
    v = VisualLLM()
    img = Image.open("img/8.jpg")
    encoded = v.encode(img)

    answer = v.ask(encoded, "Describe this image in detail.")
    print("Answer:", answer)