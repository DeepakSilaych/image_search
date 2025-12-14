import cv2
from PIL import Image
# Import your modules
from face_recognition import FaceIdentifier  
from caption_logic import ImageCaptioner   
from ocr import process_ocr         

class ImageProcessor:
    def __init__(self):
        # Load models once on startup
        self.face_engine = FaceIdentifier()
        self.caption_engine = ImageCaptioner()
        
    def process_image(self, image_path):
        print(f"\n--- Processing {image_path} ---")
        
        # 1. Basic Scene Description
        scene_caption = self.caption_engine.get_caption(image_path)
        
        # 2. Extract Text (OCR)
        # Note: Your process_ocr expects an OpenCV image (numpy array)
        cv_img = cv2.imread(image_path)
        ocr_text = process_ocr(cv_img)
        
        # 3. Face Detection & Body Analysis
        faces = self.face_engine.detect_and_name(image_path)
        
        people_descriptions = []
        person_names = []

        pil_img = Image.open(image_path) # Need PIL for cropping
        
        for face in faces:
            name = face['name']
            
            # If we know the person, let's describe what they are wearing
            if name != "Unknown":
                person_names.append(name)
                
                # --- The Body Crop Trick ---
                x, y, w, h = face['box']['x'], face['box']['y'], face['box']['w'], face['box']['h']
                
                # Expand box to include body (go down 3x the head height)
                img_w, img_h = pil_img.size
                body_y2 = min(img_h, y + h * 4) 
                body_x1 = max(0, x - int(w * 0.5))
                body_x2 = min(img_w, x + w + int(w * 0.5))
                
                body_crop = pil_img.crop((body_x1, y, body_x2, body_y2))
                
                # Get description of this person specifically
                body_caption = self.caption_engine.get_caption(body_crop)
                
                # Store: "Deepak is looking like a man in a blue suit"
                people_descriptions.append(f"{name} is {body_caption}")
        
        # 4. Synthesize Final Searchable Text
        # This string is what we will save to the Vector DB
        
        final_description = f"""
        Summary: {scene_caption}
        Text in image: {ocr_text}
        People Identified: {', '.join(person_names)}
        Details: {'. '.join(people_descriptions)}
        """
        
        return {
            "image_path": image_path,
            "search_text": final_description.strip(),
            "metadata": {
                "names": person_names,
                "scene": scene_caption
            }
        }

# --- Test the Full Pipeline ---
if __name__ == "__main__":
    processor = ImageProcessor()
    
    # Run on your test image
    result = processor.process_image("img/3.jpg")
    
    print("\n[FINAL SEARCHABLE DOCUMENT]")
    print(result["search_text"])