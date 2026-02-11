#!/usr/bin/env python3
"""
Embedding Builder Module

Core logic for building embeddings for paragraphs and code entries.
Used by the main implementation script.

Author: Jonathan Paige
Date: 2025
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("sentence-transformers not installed. Install with: pip install sentence-transformers")

try:
    import faiss
except ImportError:
    raise ImportError("faiss not installed. Install with: pip install faiss-cpu")


class EmbeddingBuilder:
    """Build embeddings for paragraphs and codebook entries."""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize embedding builder.
        
        Args:
            model_name: Name of sentence-transformers model to use
        """
        print(f"  Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"  ✓ Model loaded (dimension: {self.embedding_dim})")
        
    def create_paragraph_embeddings(self, paragraphs: List[Dict], batch_size: int = 32) -> np.ndarray:
        """
        Create embeddings for paragraphs.
        
        Args:
            paragraphs: List of paragraph dictionaries
            batch_size: Batch size for embedding generation
            
        Returns:
            Numpy array of embeddings
        """
        print(f"  Creating embeddings for {len(paragraphs)} paragraphs...")
        
        # Extract texts
        texts = [p['text'] for p in paragraphs]
        
        # Create embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"  ✓ Created {len(embeddings)} embeddings")
        
        return embeddings
    
    def create_code_embeddings(self, codes: List[Dict], 
                              fields_to_embed: List[str] = None,
                              custom_queries: Dict[str, str] = None) -> np.ndarray:
        """
        Create embeddings for code entries.
        
        Args:
            codes: List of code dictionaries
            fields_to_embed: Which fields to concatenate for embedding
            custom_queries: Optional dict mapping code_id to custom query text
            
        Returns:
            Numpy array of embeddings
        """
        if fields_to_embed is None:
            fields_to_embed = ['definition', 'inclusion_criteria', 'typical_exemplars']
        
        print(f"  Creating embeddings for {len(codes)} code entries...")
        
        texts = []
        for code in codes:
            code_id = code['code_id']
            
            # Check for custom query override
            if custom_queries and code_id in custom_queries:
                text = custom_queries[code_id]
            else:
                # Concatenate specified fields
                parts = []
                for field in fields_to_embed:
                    if field in code and code[field]:
                        parts.append(code[field])
                text = " ".join(parts)
            
            texts.append(text)
        
        # Create embeddings
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"  ✓ Created {len(embeddings)} code embeddings")
        
        return embeddings
    
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Build FAISS index for embeddings.
        
        Args:
            embeddings: Numpy array of embeddings
            
        Returns:
            FAISS index
        """
        dimension = embeddings.shape[1]
        
        # Use flat index for exact search
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        return index
