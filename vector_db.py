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

        img = cv2.imread(image_path)
        if img is None:
            print(f"Error reading {image_path}")
            return

        # Generate descriptions
        search_text, _ = self.metadata_generator.process(img)

        print(f"Indexing: {image_path}...")
        
        # 1. Convert text to vector
        vector = self.embedder.encode(search_text).tolist()
        
        # 2. Add to DB
        self.collection.add(
            documents=[search_text],       
            embeddings=[vector],           
            metadatas=[{"path": image_path}],     
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
            
            # process image
            engine.add_image(img_path)

        # 2. Search Test
        results = engine.search("deepak with white tshirt")
        
        # Pretty print results
        if results['ids']:
            for i in range(len(results['ids'][0])):
                meta = results['metadatas'][0][i]
                print(f"File: {results['ids'][0][i]}, Path: {meta['path']}")

    else:
        print(f"Directory '{img_dir}' not found.")