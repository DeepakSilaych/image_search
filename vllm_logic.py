import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

class VisualLLM:
    def __init__(self):
        print("--- Loading Moondream2 (Visual LLM) ---")
        self.model_id = "vikhyatk/moondream2"
        self.revision = "2024-08-26" # Pinning version for stability
        
        self.device = "cpu"
        # If you have a Mac M1/M2/M3, use 'mps'. If NVIDIA, use 'cuda'.
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, 
            trust_remote_code=True, 
            revision=self.revision
        ).to(self.device)
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, revision=self.revision)
        print(f"--- Moondream Loaded on {self.device} ---")

    def analyze(self, image_input, prompt):
        """
        image_input: File path (str) OR PIL Image.
        prompt: The question you want to ask about the image.
        """
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

# --- Test Block ---
if __name__ == "__main__":
    vllm = VisualLLM()
    
    img_path = "img/3.jpg" # Use your selfie image
    
    # 1. Test Scene Description
    print(f"Scene: {vllm.analyze(img_path, 'Describe this image briefly.')}")
    
    # 2. Test Person Specifics (Simulating the crop)
    full_img = Image.open(img_path)
    w, h = full_img.size
    # Crop the left half (assuming Deepak is there) to test
    crop = full_img.crop((0, 0, w//2, h)) 
    
    print(f"Person Clothing: {vllm.analyze(crop, 'Describe the clothing of the person in this image. Be specific about colors.')}")