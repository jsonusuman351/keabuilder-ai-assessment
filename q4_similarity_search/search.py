"""
Q4: Face & Text Similarity Search System for KeaBuilder
Find similar images, templates, and user inputs using embeddings
"""

import json
import numpy as np
from datetime import datetime


class EmbeddingGenerator:
    """Generate embeddings for images and text"""
    
    def generate_text_embedding(self, text):
        """
        In production: use SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(text)
        """
        np.random.seed(hash(text) % 2**32)
        return np.random.rand(384).tolist()
    
    def generate_image_embedding(self, image_path):
        """
        In production: use CLIP model
        image = preprocess(Image.open(image_path))
        embedding = clip_model.encode_image(image)
        """
        np.random.seed(hash(image_path) % 2**32)
        return np.random.rand(512).tolist()


class VectorStore:
    """Simple vector database for similarity search"""
    
    def __init__(self):
        self.vectors = []  # In production: Pinecone / ChromaDB
    
    def add(self, id, embedding, metadata):
        self.vectors.append({
            "id": id,
            "embedding": np.array(embedding),
            "metadata": metadata
        })
    
    def search(self, query_embedding, top_k=5, threshold=0.75):
        query = np.array(query_embedding)
        results = []
        
        for item in self.vectors:
            # Cosine similarity
            similarity = np.dot(query, item["embedding"]) / (
                np.linalg.norm(query) * np.linalg.norm(item["embedding"])
            )
            if similarity >= threshold:
                results.append({
                    "id": item["id"],
                    "similarity": round(float(similarity), 4),
                    "metadata": item["metadata"]
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]


class KeaBuilderSearch:
    """Similarity search system for KeaBuilder assets"""
    
    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self.image_store = VectorStore()
        self.text_store = VectorStore()
    
    def index_image(self, asset_id, image_path, metadata):
        """Store image embedding when user uploads"""
        embedding = self.embedder.generate_image_embedding(image_path)
        self.image_store.add(asset_id, embedding, metadata)
    
    def index_text(self, asset_id, text, metadata):
        """Store text embedding for templates/content"""
        embedding = self.embedder.generate_text_embedding(text)
        self.text_store.add(asset_id, embedding, metadata)
    
    def find_similar_images(self, query_image_path, top_k=5):
        """Find images similar to given image"""
        query_embedding = self.embedder.generate_image_embedding(query_image_path)
        return self.image_store.search(query_embedding, top_k, threshold=0.5)
    
    def find_similar_text(self, query_text, top_k=5):
        """Find templates/content similar to query"""
        query_embedding = self.embedder.generate_text_embedding(query_text)
        return self.text_store.search(query_embedding, top_k, threshold=0.5)
    
    def search_by_text_for_images(self, text_query, top_k=5):
        """Search images using text description (CLIP-based)"""
        # In production: CLIP can match text to images
        query_embedding = self.embedder.generate_image_embedding(text_query)
        return self.image_store.search(query_embedding, top_k, threshold=0.5)


if __name__ == "__main__":
    search = KeaBuilderSearch()
    
    # Index some sample assets
    sample_assets = [
        {"id": "img_001", "path": "blue_marketing_banner.png", "meta": {"type": "banner", "color": "blue", "user": "user_1"}},
        {"id": "img_002", "path": "red_sales_banner.png", "meta": {"type": "banner", "color": "red", "user": "user_1"}},
        {"id": "img_003", "path": "product_photo_1.jpg", "meta": {"type": "product", "user": "user_1"}},
        {"id": "img_004", "path": "team_headshot.jpg", "meta": {"type": "headshot", "user": "user_1"}},
        {"id": "img_005", "path": "blue_funnel_template.png", "meta": {"type": "template", "color": "blue", "user": "user_1"}}
    ]
    
    for asset in sample_assets:
        search.index_image(asset["id"], asset["path"], asset["meta"])
    
    # Index text templates
    templates = [
        {"id": "tpl_001", "text": "High converting sales funnel template", "meta": {"category": "sales"}},
        {"id": "tpl_002", "text": "Lead capture landing page design", "meta": {"category": "leads"}},
        {"id": "tpl_003", "text": "Email marketing campaign template", "meta": {"category": "email"}},
        {"id": "tpl_004", "text": "Webinar registration funnel page", "meta": {"category": "webinar"}}
    ]
    
    for tpl in templates:
        search.index_text(tpl["id"], tpl["text"], tpl["meta"])
    
    # Search similar images
    print("=== Find Similar Images ===")
    results = search.find_similar_images("blue_marketing_banner.png")
    print(json.dumps(results, indent=2))
    
    # Search similar text
    print("\n=== Find Similar Templates ===")
    results = search.find_similar_text("sales funnel landing page")
    print(json.dumps(results, indent=2))
