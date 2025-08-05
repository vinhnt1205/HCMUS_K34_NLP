# -*- coding: utf-8 -*-
"""
Hệ thống tìm kiếm Hán-Việt sử dụng align.py làm back-end
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

# ========== Tiền xử lý ==========
def preprocess_texts(texts, lower=True, remove_stopwords=False, stopwords=None, norm_unicode='NFC'):
    def clean_text(s):
        if not isinstance(s, str):
            return ""
        s = unicodedata.normalize(norm_unicode, s)
        s = re.sub(r'\s+', ' ', s.strip())
        if lower:
            s = s.lower()
        s = re.sub(r'([.,!?;:]){2,}', r'\1', s)
        s = re.sub(r'\s+([.,!?;:])', r'\1', s)
        if remove_stopwords and stopwords:
            words = s.split()
            words = [w for w in words if w not in stopwords]
            s = ' '.join(words)
        return s
    return [clean_text(t) for t in texts]

# ========== PhoBERT ==========
def load_phobert_model(device=None):
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base')
    model = AutoModel.from_pretrained('vinai/phobert-base')
    model.to(device)
    model.eval()
    return tokenizer, model, device

def phobert_encode(texts, tokenizer, model, device, batch_size=64):
    all_embeddings = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            encoded = tokenizer(batch_texts, padding=True, truncation=True, max_length=256, return_tensors='pt')
            input_ids = encoded['input_ids'].to(device)
            attention_mask = encoded['attention_mask'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            last_hidden = outputs.last_hidden_state
            mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
            summed = torch.sum(last_hidden * mask, 1)
            counts = torch.clamp(mask.sum(1), min=1e-9)
            mean_pooled = summed / counts
            all_embeddings.append(mean_pooled.cpu())
    return torch.cat(all_embeddings, dim=0)

# ========== LaBSE ==========
def load_labse_model(device=None):
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    model = SentenceTransformer('sentence-transformers/LaBSE', device=device)
    model.eval()
    if device == 'cuda':
        model.half()
    return model, device

def labse_encode(texts, model, batch_size=128):
    with torch.no_grad():
        embeddings = model.encode(texts, convert_to_tensor=True, batch_size=batch_size, device=model.device)
    return embeddings

# ========== VectorStore Class ==========
class HanVietVectorStore:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.han_embeddings_phobert = None
        self.han_embeddings_labse = None
        self.phobert_tokenizer = None
        self.phobert_model = None
        self.labse_model = None
        self.device = None
        
    def load_data(self):
        """Load data từ CSV file"""
        print("Loading data...")
        self.df = pd.read_csv(self.data_path)
        print(f"Loaded {len(self.df)} records")
        return self.df
    
    def initialize_models(self):
        """Khởi tạo các mô hình"""
        print("Initializing PhoBERT...")
        self.phobert_tokenizer, self.phobert_model, self.device = load_phobert_model()
        
        print("Initializing LaBSE...")
        self.labse_model, _ = load_labse_model(device=self.device)
        
    def create_embeddings(self):
        """Tạo embeddings cho tất cả câu tiếng Hán"""
        print("Creating embeddings for Han sentences...")
        
        # Tiền xử lý
        han_sentences = preprocess_texts(self.df['Câu tiếng Hán'].astype(str).tolist())
        
        # Encode bằng PhoBERT
        print("Encoding with PhoBERT...")
        self.han_embeddings_phobert = phobert_encode(
            han_sentences, self.phobert_tokenizer, self.phobert_model, self.device
        )
        
        # Encode bằng LaBSE
        print("Encoding with LaBSE...")
        self.han_embeddings_labse = labse_encode(han_sentences, self.labse_model)
        
        print("Embeddings created successfully!")
        
    def save_vectorstore(self, save_path="han_viet_vectorstore.pkl"):
        """Lưu vectorstore"""
        print(f"Saving vectorstore to {save_path}...")
        vectorstore_data = {
            'df': self.df,
            'han_embeddings_phobert': self.han_embeddings_phobert,
            'han_embeddings_labse': self.han_embeddings_labse,
            'phobert_tokenizer': self.phobert_tokenizer,
            'phobert_model': self.phobert_model,
            'labse_model': self.labse_model,
            'device': self.device
        }
        with open(save_path, 'wb') as f:
            pickle.dump(vectorstore_data, f)
        print("Vectorstore saved successfully!")
        
    def load_vectorstore(self, load_path="han_viet_vectorstore.pkl"):
        """Load vectorstore từ file .pkl hoặc URL"""
        print(f"Loading vectorstore from {load_path}...")
        try:
            # Thử load từ URL trước
            if load_path.startswith("http") or "huggingface" in load_path:
                print("Loading from Hugging Face URL...")
                import download_model
                vectorstore_data = download_model.load_pickle_from_url()
                if vectorstore_data is None:
                    print("Failed to load from URL, trying local file...")
                    with open(load_path, 'rb') as f:
                        vectorstore_data = pickle.load(f)
            else:
                # Load từ local file
                with open(load_path, 'rb') as f:
                    vectorstore_data = pickle.load(f)
                    
        except (ModuleNotFoundError, AttributeError) as e:
            if 'numpy._core' in str(e):
                print(f"❌ Numpy version compatibility issue: {str(e)}")
                raise RuntimeError("Không thể load file .pkl do lỗi numpy._core. Hãy tạo lại file .pkl đúng version numpy!")
            else:
                print(f"❌ Error loading pickle file: {str(e)}")
                raise
        except Exception as e:
            print(f"❌ Error loading vectorstore: {str(e)}")
            raise
            
        self.df = vectorstore_data['df']
        self.han_embeddings_phobert = vectorstore_data.get('han_embeddings_phobert')
        self.han_embeddings_labse = vectorstore_data.get('han_embeddings_labse')
        self.phobert_tokenizer = vectorstore_data.get('phobert_tokenizer')
        self.phobert_model = vectorstore_data.get('phobert_model')
        self.labse_model = vectorstore_data.get('labse_model')
        self.device = vectorstore_data.get('device', 'cpu')
        print("Vectorstore loaded successfully!")
        
    def search(self, query_han, top_k=1):
        """Tìm kiếm câu tiếng Việt tương ứng"""
        print(f"Searching for: {query_han}")
        
        # Kiểm tra xem có embeddings không
        if self.han_embeddings_phobert is None and self.han_embeddings_labse is None:
            print("⚠️  No embeddings available, using simple text search...")
            return self.simple_search(query_han, top_k)
        
        # Tiền xử lý query
        query_processed = preprocess_texts([query_han])[0]
        
        # Encode query và tìm kiếm
        all_hits = []
        
        # PhoBERT search
        if self.han_embeddings_phobert is not None and self.phobert_tokenizer is not None:
            try:
                query_embedding_phobert = phobert_encode(
                    [query_processed], self.phobert_tokenizer, self.phobert_model, self.device
                )
                hits_phobert = util.semantic_search(
                    query_embedding_phobert, self.han_embeddings_phobert, top_k=top_k
                )[0]
                for hit in hits_phobert:
                    hit['model'] = 'phobert'
                    all_hits.append(hit)
            except Exception as e:
                print(f"PhoBERT search failed: {str(e)}")
        
        # LaBSE search
        if self.han_embeddings_labse is not None and self.labse_model is not None:
            try:
                query_embedding_labse = labse_encode([query_processed], self.labse_model)
                hits_labse = util.semantic_search(
                    query_embedding_labse, self.han_embeddings_labse, top_k=top_k
                )[0]
                for hit in hits_labse:
                    hit['model'] = 'labse'
                    all_hits.append(hit)
            except Exception as e:
                print(f"LaBSE search failed: {str(e)}")
        
        # Nếu không có kết quả từ embeddings, dùng simple search
        if not all_hits:
            print("⚠️  No semantic search results, using simple text search...")
            return self.simple_search(query_han, top_k)
        
        # Sort by score
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
            
        return results
    
    def simple_search(self, query_han, top_k=1):
        """Tìm kiếm đơn giản bằng text matching"""
        print(f"Simple search for: {query_han}")
        
        results = []
        query_lower = query_han.lower()
        
        # Tìm kiếm trong DataFrame
        for idx, row in self.df.iterrows():
            han_text = str(row['Câu tiếng Hán']).lower()
            
            # Tính điểm đơn giản dựa trên độ tương đồng
            if query_lower in han_text or han_text in query_lower:
                score = 0.8  # Điểm cao cho exact match
            elif any(char in han_text for char in query_lower):
                score = 0.3  # Điểm thấp cho partial match
            else:
                continue
            
            results.append({
                'han_original': row['Câu tiếng Hán'],
                'translation': row['translation'],
                'best_match': row['best_match'],
                'score': score,
                'model': 'simple'
            })
        
        # Sort và trả về top_k kết quả
        results = sorted(results, key=lambda x: -x['score'])[:top_k]
        return results

# ========== Main Functions ==========
def create_vectorstore(data_path):
    """Tạo vectorstore từ data"""
    vectorstore = HanVietVectorStore(data_path)
    vectorstore.load_data()
    vectorstore.initialize_models()
    vectorstore.create_embeddings()
    vectorstore.save_vectorstore()
    return vectorstore

def load_and_search(query_han, vectorstore_path="han_viet_vectorstore.pkl"):
    """Load vectorstore và tìm kiếm - chỉ dùng file .pkl, lỗi là dừng"""
    if not os.path.exists(vectorstore_path):
        raise FileNotFoundError(f"Vectorstore file {vectorstore_path} not found. Hãy upload đúng file .pkl!")
    vectorstore = HanVietVectorStore(None)
    vectorstore.load_vectorstore(vectorstore_path)
    return vectorstore.search(query_han)

# ========== Demo ==========
def demo():
    """Demo với câu ví dụ của bạn"""
    # Đường dẫn file data
    data_path = "Final result the align sentences with rescue hybrid.xlsx - aligned_with_rescue_hybrid_2.5-2.csv"
    
    # Tạo vectorstore (chỉ chạy 1 lần)
    if not os.path.exists("han_viet_vectorstore.pkl"):
        print("Creating vectorstore...")
        create_vectorstore(data_path)
    
    # Tìm kiếm
    query = "鎮驚安神：天麻、茯神、遠志、棗仁、薊藤、菖蒲、丹參、麥冬、當歸、芍藥、硃砂、珍珠、燈花、童腦、金箔、童齒、麝香、袨香、安息香、茲合香、乳香、琥珀、代赭石。"
    
    print("=" * 50)
    print("DEMO SEARCH")
    print("=" * 50)
    print(f"Input (Han): {query}")
    print()
    
    results = load_and_search(query)
    
    print("Top results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.4f} (Model: {result['model']})")
        print(f"   Han Original: {result['han_original']}")
        print(f"   Translation: {result['translation']}")
        print(f"   Best Match: {result['best_match']}")

if __name__ == '__main__':
    demo() 