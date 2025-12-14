import os
import cv2
import pickle
import numpy as np
from deepface import DeepFace
from scipy.spatial.distance import cosine
from collections import defaultdict

class FaceIdentifier:
    def __init__(self, known_faces_dir="known_faces"):
        self.known_faces_dir = known_faces_dir
        self.db_path = os.path.join(known_faces_dir, "known_faces_db.pkl")
        
        # Structure: { "PersonName": { "image_filename.jpg": [embedding_vector] } }
        self.known_db = defaultdict(dict) 
        
        self._load_from_disk()
        self._scan_and_update_faces()

    def _load_from_disk(self):
        """Load existing DB from pickle file if it exists."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'rb') as f:
                    loaded_data = pickle.load(f)
                    # Convert standard dict back to defaultdict for easier handling
                    self.known_db = defaultdict(dict, loaded_data)
                print(f"--- Loaded database from {self.db_path} ---")
            except Exception as e:
                print(f"Error loading DB: {e}. Starting fresh.")
        else:
            print("--- No existing database found. Starting fresh. ---")

    def _save_to_disk(self):
        """Save the current memory DB to disk."""
        try:
            with open(self.db_path, 'wb') as f:
                # Convert defaultdict to dict for pickling
                pickle.dump(dict(self.known_db), f)
            print("--- Database saved to disk ---")
        except Exception as e:
            print(f"Error saving DB: {e}")

    def _scan_and_update_faces(self):
        """
        Scans folders. Only processes images that are NOT in self.known_db.
        """
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
            return

        updates_made = False
        
        for person_name in os.listdir(self.known_faces_dir):
            person_dir = os.path.join(self.known_faces_dir, person_name)
            
            if not os.path.isdir(person_dir):
                continue
            
            # Check files in this person's folder
            for img_file in os.listdir(person_dir):
                if not img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    continue
                
                # --- INCREMENTAL CHECK ---
                # If we already have an embedding for this specific file, SKIP it.
                if img_file in self.known_db[person_name]:
                    continue 

                # If we reach here, it's a new file. Process it.
                img_path = os.path.join(person_dir, img_file)
                print(f"Processing NEW image: {img_file} for {person_name}...")
                
                try:
                    # 1. Detect
                    faces_in_img = DeepFace.extract_faces(
                        img_path=img_path,
                        detector_backend="opencv", 
                        enforce_detection=False
                    )
                    
                    if len(faces_in_img) > 1:
                        print(f"WARNING: Multiple faces in {img_file}. Using all.")

                    for face_obj in faces_in_img:
                        # 2. Embed
                        embedding = DeepFace.represent(
                            img_path=face_obj['face'],
                            model_name="ArcFace",
                            enforce_detection=False,
                            detector_backend="skip" 
                        )[0]["embedding"]
                        
                        # Save to memory DB
                        self.known_db[person_name][img_file] = embedding
                        updates_made = True

                except Exception as e:
                    print(f"Skipping {img_file}: {e}")
        
        if updates_made:
            self._save_to_disk()
        else:
            print("No new images found. Using cached data.")

    def detect_and_name(self, target_img_path):
        try:
            faces_in_image = DeepFace.extract_faces(
                img_path=target_img_path, 
                detector_backend='opencv', 
                enforce_detection=True
            )
        except:
            return []

        results = []

        for face_obj in faces_in_image:
            current_embedding = DeepFace.represent(
                img_path=face_obj['face'], 
                model_name="ArcFace", 
                enforce_detection=False,
                detector_backend="skip"
            )[0]["embedding"]

            best_match_name = "Unknown"
            best_match_score = .7

            # 3. Compare against known DB
            # Structure is now: {Name: {Filename: Embedding}}
            for name, file_dict in self.known_db.items():
                for filename, saved_emb in file_dict.items():
                    dist = cosine(saved_emb, current_embedding)
                    
                    if dist < best_match_score:
                        best_match_score = dist
                        best_match_name = name

            results.append({
                "name": best_match_name,
                "box": face_obj['facial_area'], 
                "distance": best_match_score
            })

        return results

if __name__ == "__main__":
    face_identifier = FaceIdentifier(known_faces_dir="known_faces")
    
    # Test
    test_image_path = "img/3.jpg" 
    if os.path.exists(test_image_path):
        identified_faces = face_identifier.detect_and_name(test_image_path)
        for face in identified_faces:
            print(f"Found: {face['name']} ({face['distance']:.4f})")