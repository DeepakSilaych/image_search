import chromadb
from sentence_transformers import SentenceTransformer
from embed_img import ImageEmbedder
import os
import uuid
import cv2

class SearchEngine:
    def __init__(self):
        print("--- Initializing Vector DB ---")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path="image_search_db")
        self.collection = self.client.get_or_create_collection(
            name="personal_photos",
            metadata={"hnsw:space": "cosine"}
        )
        self.metadata_generator = ImageEmbedder()

    def add_image(self, image_path):
        # Check if already exists to avoid duplicates
        existing = self.collection.get(where={"path": image_path})
        if existing['ids']:
            print(f"Skipping {image_path} (Already in DB)")
            return

        search_text, metadata_dict = self.metadata_generator.process(image_path)

        print(f"Indexing: {image_path}...")
        
        # 1. Convert text to vector
        vector = self.embedder.encode(search_text).tolist()
        
        # 2. Create valid metadata dict (ChromaDB requires dicts, not strings)
        # We store the path and a short snippet of the caption for display
        meta_payload = {
            "path": image_path,
            "scene_snippet": metadata_dict.get('image_caption', '')[:100]
        }

        # 3. Add to DB
        self.collection.add(
            documents=[search_text],       
            embeddings=[vector],           
            metadatas=[meta_payload],      # FIX: Must be a list of dicts
            ids=[str(uuid.uuid4())]        
        )
        print(" -> Saved!")

    def search(self, query_text, n_results=3):
        print(f"\n--- Searching for: '{query_text}' ---")
        
        query_vector = self.embedder.encode(query_text).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        
        return results
    

if __name__ == "__main__":
    engine = SearchEngine()
    
    img_dir = "img/"
    if os.path.exists(img_dir):
        # 1. Indexing Loop
        for img_file in os.listdir(img_dir):
            if not img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
                continue

            img_path = os.path.join(img_dir, img_file)
            img = cv2.imread(img_path)
            
            if img is None:
                print(f"Skipping {img_file} (Read Error)")
                continue
            

            engine.add_image(img_path)

        # 2. Search Test
        results = engine.search("deepak with white tshirt")
        
        # Pretty print results
        if results['ids']:
            for i in range(len(results['ids'][0])):
                print(f"\nMatch #{i+1}")
                meta = results['metadatas'][0][i]
                print(f"File: {meta['path']}")
                print(f"Snippet: {meta.get('scene_snippet', '')}...")
    else:
        print(f"Directory '{img_dir}' not found.")