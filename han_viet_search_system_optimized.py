# -*- coding: utf-8 -*-
"""
Hệ thống tìm kiếm Hán-Việt tối ưu hóa
Sử dụng cache và lazy loading để tăng tốc độ
"""

import torch
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModel
import unicodedata
import re
import pickle
import os
import time
from functools import lru_cache

# ========== Tiền xử lý tối ưu ==========
def preprocess_text(text):
    """Tiền xử lý text tối ưu cho 1 câu"""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'([.,!?;:]){2,}', r'\1', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    return text

# ========== Model Manager với Lazy Loading ==========
class ModelManager:
    def __init__(self):
        self.phobert_tokenizer = None
        self.phobert_model = None
        self.labse_model = None
        self.device = None
        self._models_loaded = False
    
    def load_models(self):
        """Lazy load models chỉ khi cần"""
        if self._models_loaded:
            return
            
        print("Loading models...")
        start_time = time.time()
        
        # Load device
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load PhoBERT
        print("Loading PhoBERT...")
        self.phobert_tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base')
        self.phobert_model = AutoModel.from_pretrained('vinai/phobert-base')
        self.phobert_model.to(self.device)
        self.phobert_model.eval()
        
        # Load LaBSE
        print("Loading LaBSE...")
        self.labse_model = SentenceTransformer('sentence-transformers/LaBSE', device=self.device)
        if self.device == 'cuda':
            self.labse_model.half()
        
        self._models_loaded = True
        print(f"Models loaded in {time.time() - start_time:.2f}s")
    
    @lru_cache(maxsize=1000)
    def encode_phobert(self, text):
        """Cache encoding cho PhoBERT"""
        if not self._models_loaded:
            self.load_models()
            
        with torch.no_grad():
            encoded = self.phobert_tokenizer(
                text, padding=True, truncation=True, max_length=256, return_tensors='pt'
            )
            input_ids = encoded['input_ids'].to(self.device)
            attention_mask = encoded['attention_mask'].to(self.device)
            outputs = self.phobert_model(input_ids=input_ids, attention_mask=attention_mask)
            last_hidden = outputs.last_hidden_state
            mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
            summed = torch.sum(last_hidden * mask, 1)
            counts = torch.clamp(mask.sum(1), min=1e-9)
            mean_pooled = summed / counts
            return mean_pooled.cpu()
    
    @lru_cache(maxsize=1000)
    def encode_labse(self, text):
        """Cache encoding cho LaBSE"""
        if not self._models_loaded:
            self.load_models()
            
        with torch.no_grad():
            embedding = self.labse_model.encode(text, convert_to_tensor=True, device=self.device)
            return embedding

# ========== VectorStore tối ưu ==========
class OptimizedHanVietVectorStore:
    def __init__(self, data_path=None):
        self.data_path = data_path
        self.df = None
        self.han_embeddings_phobert = None
        self.han_embeddings_labse = None
        self.model_manager = ModelManager()
        self._embeddings_loaded = False
        
    def load_data(self):
        """Load data từ CSV file"""
        if self.df is not None:
            return self.df
            
        print("Loading data...")
        start_time = time.time()
        self.df = pd.read_csv(self.data_path)
        print(f"Loaded {len(self.df)} records in {time.time() - start_time:.2f}s")
        return self.df
    
    def create_embeddings(self):
        """Tạo embeddings cho tất cả câu tiếng Hán"""
        if self._embeddings_loaded:
            return
            
        print("Creating embeddings...")
        start_time = time.time()
        
        # Load models
        self.model_manager.load_models()
        
        # Tiền xử lý
        han_sentences = [preprocess_text(str(s)) for s in self.df['Câu tiếng Hán'].tolist()]
        
        # Encode bằng PhoBERT
        print("Encoding with PhoBERT...")
        phobert_embeddings = []
        batch_size = 64
        for i in range(0, len(han_sentences), batch_size):
            batch = han_sentences[i:i+batch_size]
            batch_embeddings = []
            for text in batch:
                embedding = self.model_manager.encode_phobert(text)
                batch_embeddings.append(embedding)
            phobert_embeddings.extend(batch_embeddings)
        self.han_embeddings_phobert = torch.cat(phobert_embeddings, dim=0)
        
        # Encode bằng LaBSE
        print("Encoding with LaBSE...")
        labse_embeddings = []
        for i in range(0, len(han_sentences), batch_size):
            batch = han_sentences[i:i+batch_size]
            batch_embeddings = self.model_manager.labse_model.encode(
                batch, convert_to_tensor=True, device=self.device
            )
            labse_embeddings.append(batch_embeddings)
        self.han_embeddings_labse = torch.cat(labse_embeddings, dim=0)
        
        self._embeddings_loaded = True
        print(f"Embeddings created in {time.time() - start_time:.2f}s")
        
    def save_vectorstore(self, save_path="han_viet_vectorstore_optimized.pkl"):
        """Lưu vectorstore tối ưu"""
        print(f"Saving optimized vectorstore...")
        vectorstore_data = {
            'df': self.df,
            'han_embeddings_phobert': self.han_embeddings_phobert,
            'han_embeddings_labse': self.han_embeddings_labse,
            'model_manager': self.model_manager
        }
        with open(save_path, 'wb') as f:
            pickle.dump(vectorstore_data, f)
        print("Optimized vectorstore saved!")
        
    def load_vectorstore(self, load_path="han_viet_vectorstore_optimized.pkl"):
        """Load vectorstore tối ưu"""
        print(f"Loading optimized vectorstore...")
        with open(load_path, 'rb') as f:
            vectorstore_data = pickle.load(f)
        
        self.df = vectorstore_data['df']
        self.han_embeddings_phobert = vectorstore_data['han_embeddings_phobert']
        self.han_embeddings_labse = vectorstore_data['han_embeddings_labse']
        self.model_manager = vectorstore_data['model_manager']
        self._embeddings_loaded = True
        print("Optimized vectorstore loaded!")
        
    def search(self, query_han, top_k=1):
        """Tìm kiếm tối ưu với cache"""
        start_time = time.time()
        
        # Tiền xử lý query
        query_processed = preprocess_text(query_han)
        
        # Encode query với cache
        query_embedding_phobert = self.model_manager.encode_phobert(query_processed)
        query_embedding_labse = self.model_manager.encode_labse(query_processed)
        
        # Tìm kiếm semantic
        hits_phobert = util.semantic_search(
            query_embedding_phobert, self.han_embeddings_phobert, top_k=top_k
        )[0]
        
        hits_labse = util.semantic_search(
            query_embedding_labse, self.han_embeddings_labse, top_k=top_k
        )[0]
        
        # Ensemble results
        all_hits = []
        for hit in hits_phobert:
            hit['model'] = 'phobert'
            all_hits.append(hit)
        for hit in hits_labse:
            hit['model'] = 'labse'
            all_hits.append(hit)
            
        # Sort by score và lấy top-k
        all_hits = sorted(all_hits, key=lambda x: -x['score'])[:top_k]
        
        # Get results
        results = []
        for hit in all_hits:
            idx = hit['corpus_id']
            results.append({
                'han_original': self.df.iloc[idx]['Câu tiếng Hán'],
                'translation': self.df.iloc[idx]['translation'],
                'best_match': self.df.iloc[idx]['best_match'],
                'score': hit['score'],
                'model': hit['model']
            })
        
        search_time = time.time() - start_time
        print(f"Search completed in {search_time:.3f}s")
        
        return results

# ========== Main Functions tối ưu ==========
def create_optimized_vectorstore(data_path):
    """Tạo vectorstore tối ưu"""
    vectorstore = OptimizedHanVietVectorStore(data_path)
    vectorstore.load_data()
    vectorstore.create_embeddings()
    vectorstore.save_vectorstore()
    return vectorstore

def load_and_search_optimized(query_han, vectorstore_path="han_viet_vectorstore_optimized.pkl"):
    """Load vectorstore và tìm kiếm tối ưu"""
    vectorstore = OptimizedHanVietVectorStore()
    vectorstore.load_vectorstore(vectorstore_path)
    return vectorstore.search(query_han)

# ========== Demo tối ưu ==========
def demo_optimized():
    """Demo với câu ví dụ"""
    data_path = "/Users/ntvinh120501/Documents/KHDL_K34/NLP/CK_2/Final result the align sentences with rescue hybrid.xlsx - aligned_with_rescue_hybrid_2.5-2.csv"
    
    # Tạo vectorstore tối ưu (chỉ chạy 1 lần)
    if not os.path.exists("han_viet_vectorstore_optimized.pkl"):
        print("Creating optimized vectorstore...")
        create_optimized_vectorstore(data_path)
    
    # Test tìm kiếm
    query = "鎮驚安神：天麻、茯神、遠志、棗仁、薊藤、菖蒲、丹參、麥冬、當歸、芍藥、硃砂、珍珠、燈花、童腦、金箔、童齒、麝香、袨香、安息香、茲合香、乳香、琥珀、代赭石。"
    
    print("=" * 50)
    print("OPTIMIZED DEMO SEARCH")
    print("=" * 50)
    print(f"Input (Han): {query}")
    print()
    
    results = load_and_search_optimized(query)
    
    print("Best result:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.4f} (Model: {result['model']})")
        print(f"   Han Original: {result['han_original']}")
        print(f"   Translation: {result['translation']}")
        print(f"   Best Match: {result['best_match']}")

if __name__ == '__main__':
    demo_optimized() 