import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os


class ImageCaptioner:
    def __init__(self):
        self.model_id = "Salesforce/blip-image-captioning-large"
  
        self.processor = BlipProcessor.from_pretrained(self.model_id)
        self.model = BlipForConditionalGeneration.from_pretrained(self.model_id)
        
        # Move to GPU if available (optional, runs fine on CPU)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def get_caption(self, image_input):
        """
        image_input: Can be a file path (str) OR a PIL Image object (from a crop).
        """
        try:
            if isinstance(image_input, str):
                raw_image = Image.open(image_input).convert('RGB')
            else:
                raw_image = image_input.convert('RGB')

            # 2. Process
            inputs = self.processor(raw_image, return_tensors="pt").to(self.device)

            # 3. Generate
            out = self.model.generate(**inputs, max_new_tokens=50, min_length=10)
            
            # 4. Decode
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption

        except Exception as e:
            print(f"Error in captioning: {e}")
            return ""

# --- Test Block ---
if __name__ == "__main__":
    captioner = ImageCaptioner()
    
    for img_name in os.listdir("img"):
        img_path = os.path.join("img", img_name)
        caption = captioner.get_caption(img_path)
        print(f"Image: {img_name} | Caption: {caption}")