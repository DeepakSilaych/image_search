import cv2
import os
from PIL import Image

# Import your local modules
from vllm_logic import VisualLLM 
from face_recognition import FaceIdentifier
from ocr import process_ocr 

class ImageProcessor:
    def __init__(self):
        print("--- Initializing Processor ---")
        self.face_engine = FaceIdentifier()
        self.vllm = VisualLLM() 
        print("--- Processor Ready ---")
        
    def process_image(self, image_path):
        if not os.path.exists(image_path):
            return f"Error: File {image_path} not found."

        print(f"\n--- Processing {image_path} ---")
        
        # 1. Global Scene Description
        # We ask Moondream to describe the general scene
        scene_caption = self.vllm.analyze(image_path, "Describe the setting and the people in this image.")
        print(f"Scene: {scene_caption}")

        # 2. OCR (Text Extraction)
        cv_img = cv2.imread(image_path)
        ocr_text = process_ocr(cv_img)        
        print(f"OCR: {ocr_text}")
        
        # 3. Face Detection & Body Analysis
        faces = self.face_engine.detect_and_name(image_path)
        pil_img = Image.open(image_path).convert('RGB') # Convert to RGB to ensure cropping works
        
        people_descriptions = []
        person_names = []

        for face in faces:
            name = face['name']
            
            # Describe clothing for known people
            if name != "Unknown":
                person_names.append(name)
                
                # --- Body Cropping Logic ---
                x = face['box']['x']
                y = face['box']['y']
                w = face['box']['w']
                h = face['box']['h']
                
                # Get image dimensions to prevent out-of-bounds errors
                img_w, img_h = pil_img.size

                # Heuristic: Body is wider than head and extends down
                # 1. Expand Down: 4x the head height to get torso/legs
                body_y2 = min(img_h, y + h * 4)
                
                # 2. Expand Sides: 50% wider than the face
                body_x1 = max(0, x - int(w * 0.5))
                body_x2 = min(img_w, x + w + int(w * 0.5))
                
                # 3. Perform the Crop
                body_crop = pil_img.crop((body_x1, y, body_x2, body_y2))

                # --- Clothing Analysis ---
                # We ask Moondream specifically about this crop
                clothing_desc = self.vllm.analyze(body_crop, "Describe what this person is wearing. Focus on shirt, pants, and accessories.")
                print(f" > Analysis for {name}: {clothing_desc}")
                
                people_descriptions.append(f"{name} is wearing {clothing_desc}")
        
        # 4. Final Searchable Document Synthesis
        final_description = f"""
        Summary: {scene_caption}
        Text found: {ocr_text}
        People: {', '.join(person_names)}
        Details: {'. '.join(people_descriptions)}
        """
        
        return final_description.strip()

if __name__ == "__main__":
    processor = ImageProcessor()
    
    test_img = "img/3.jpg" 
    result = processor.process_image(test_img)
    print("\n[FINAL OUTPUT]")
    print(result)