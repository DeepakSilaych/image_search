from ocr import OCR_Object
from vllm_logic import VisualLLM
from face_recognition import FaceIdentifier
from monitor import PerformanceMonitor
import cv2
from PIL import Image 
import numpy as np

class ImageEmbedder:

    def __init__(self):         
        self.ocr = OCR_Object()
        self.vllm = VisualLLM()
        self.face_identifier = FaceIdentifier()

    def _to_pil(self, img_arr):
        if isinstance(img_arr, np.ndarray):
            img_rgb = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
            return Image.fromarray(img_rgb)
        return img_arr

    def _annotate_image(self, img, faces):
        annotated_img = img.copy()
        for face in faces:
            x, y, w, h = face['box']['x'], face['box']['y'], face['box']['w'], face['box']['h']
            name = face['name']
            
            # Draw Green Box & Label
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(annotated_img, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return annotated_img

    def _flatten_metadata(self, data):
        parts = []
        if data.get('image_caption'):
            parts.append(f"Summary: {data['image_caption']}")
        
        # add person details
        if data.get('people_descriptions'):
            for person in data['people_descriptions']:
                parts.append(f"{person['name']} is {person['description']}")
        
        if data.get('ocr_text'):
            clean_ocr = " ".join(data['ocr_text'].split())[:300]
            parts.append(f"Text content: {clean_ocr}")

        return " ".join(parts)

    def process(self, img):
        monitor = PerformanceMonitor()
        final_data = {}

        # 1. OCR
        with monitor.measure("OCR"):
            final_data['ocr_text'] = self.ocr.process(img)

        # 2. Face Detection
        with monitor.measure("Face_Detection"):
            faces = self.face_identifier.detect_and_name(img)
        
        # 3. Visual Analysis
        with monitor.measure("VLLM_Pipeline"):
            # Use Annotated image
            if faces:
                marked_img = self._annotate_image(img, faces)
                pil_img = self._to_pil(marked_img)
            else:
                pil_img = self._to_pil(img)
            
            # Resize for speed (Standard Moondream resolution)
            pil_img.thumbnail((1024, 1024))

            # encode image
            print(" > Encoding Image...")
            encoded_image = self.vllm.encode(pil_img)

            # Q1: overall context
            print(" > Querying Scene...")
            scene_caption = self.vllm.ask(encoded_image, "Describe the setting and activity in this image.")
            final_data['image_caption'] = scene_caption
            
            # Que Loop: specific people
            people_descriptions = []
            
            if faces and len(faces) < 5: 
                for face in faces:
                    name = face['name']
                    print(f" > Querying {name}...")
                    
                    # since image is annotated, we refer to the LABEL
                    prompt = f"Focus ONLY on the person inside the box labeled '{name}'. Describe their clothing. Do not describe anyone else."
                    
                    desc = self.vllm.ask(encoded_image, prompt)
                    people_descriptions.append({"name": name, "description": desc})
            
            final_data['people_descriptions'] = people_descriptions

        # flattening
        final_search_string = self._flatten_metadata(final_data)
        
        perf_stats = monitor.get_summary()
        print("\n[Performance Report]")
        total_time = 0
        for task, data in perf_stats.items():
            print(f" > {task:<20}: {data['latency_sec']}s")
            total_time += data['latency_sec']
        print(f"Total Latency: {total_time:.4f}s")

        return final_search_string, final_data


if __name__ == "__main__":
    embedder = ImageEmbedder()
    img_path = "img/3.jpg"
    
    img = cv2.imread(img_path)
    final_string, result = embedder.process(img)

    import json
    print(final_string, "\n", json.dumps(result, indent=2))