#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ứng dụng dịch tiếng Hán sang tiếng Việt sử dụng model online từ Hugging Face
Cài đặt các thư viện cần thiết với câu lệnh bên dưới
Khuyến nghị chạy bằng google colab vì có GPU
!pip install torch torchvision torchaudio transformers sentence-transformers pandas numpy requests
"""

import torch
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModel
import unicodedata
import re
import pickle
import requests
import gc

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

def load_pickle_from_url():
    hf_url = "https://huggingface.co/datasets/ntvinh12052001/han_viet_vectorstore/resolve/main/han_viet_vectorstore.pkl"
    try:
        session = requests.Session()
        session.timeout = 300
        response = session.get(hf_url, stream=True, timeout=300)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            return None

        pickle_data = response.content
        data = pickle.loads(pickle_data)
        return data

    except Exception as e:
        return None

class HanVietVectorStore:
    def __init__(self):
        self.df = None
        self.han_embeddings_phobert = None
        self.han_embeddings_labse = None
        self.phobert_tokenizer = None
        self.phobert_model = None
        self.labse_model = None
        self.device = None
        self.is_loaded = False

    def load_vectorstore_from_url(self):
        vectorstore_data = load_pickle_from_url()
        if vectorstore_data is None:
            raise RuntimeError("Không thể load vectore store (file .pkl) từ Hugging Face cá nhân!")

        self.df = vectorstore_data['df']
        gc.collect()

        self.han_embeddings_phobert = vectorstore_data.get('han_embeddings_phobert')
        gc.collect()

        self.han_embeddings_labse = vectorstore_data.get('han_embeddings_labse')
        gc.collect()

        self.phobert_tokenizer = vectorstore_data.get('phobert_tokenizer')
        self.phobert_model = vectorstore_data.get('phobert_model')
        self.labse_model = vectorstore_data.get('labse_model')
        self.device = vectorstore_data.get('device', 'cpu')

        if self.phobert_model is not None:
            self.phobert_model = self.phobert_model.cpu()
        if self.labse_model is not None:
            self.labse_model = self.labse_model.cpu()

        gc.collect()
        self.is_loaded = True

    def search(self, query_han, top_k=3):
        if not self.is_loaded:
            raise RuntimeError("Vectorstore chưa được load")

        if self.han_embeddings_phobert is None and self.han_embeddings_labse is None:
            return self.simple_search(query_han, top_k)

        query_processed = preprocess_texts([query_han])[0]
        all_hits = []

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
                pass

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
                pass

        if not all_hits:
            return self.simple_search(query_han, top_k)

        all_hits = sorted(all_hits, key=lambda x: -x['score'])[:top_k]

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

    def simple_search(self, query_han, top_k=3):
        results = []
        query_lower = query_han.lower()

        for idx, row in self.df.iterrows():
            han_text = str(row['Câu tiếng Hán']).lower()

            if query_lower in han_text or han_text in query_lower:
                score = 0.8
            elif any(char in han_text for char in query_lower):
                score = 0.3
            else:
                continue

            results.append({
                'han_original': row['Câu tiếng Hán'],
                'translation': row['translation'],
                'best_match': row['best_match'],
                'score': score,
                'model': 'simple'
            })

        results = sorted(results, key=lambda x: -x['score'])[:top_k]
        return results

class HanVietTranslator:
    def __init__(self):
        self.vectorstore = HanVietVectorStore()
        self.is_initialized = False

    def initialize(self):
        if self.is_initialized:
            return

        try:
            self.vectorstore.load_vectorstore_from_url()
            self.is_initialized = True
        except Exception as e:
            raise

    def translate(self, han_text, top_k=3):
        if not self.is_initialized:
            self.initialize()

        if not han_text.strip():
            return {"error": "Vui lòng nhập câu tiếng Hán"}

        try:
            results = self.vectorstore.search(han_text, top_k=top_k)

            if not results:
                return {
                    "error": "Không tìm thấy bản dịch phù hợp",
                    "input": han_text
                }

            return {
                "success": True,
                "input": han_text,
                "results": results
            }

        except Exception as e:
            return {
                "error": f"Lỗi khi dịch: {str(e)}",
                "input": han_text
            }

def main():
    print("Hệ thống dịch Hán-Việt cho y học cổ truyền")
    translator = HanVietTranslator()

    try:
        translator.initialize()
        print("Sẵn sàng dịch")
    except Exception as e:
        print(f"Lỗi khởi tạo: {str(e)}")
        return

    while True:
        try:
            han_input = input("\nNhập câu tiếng Hán: ").strip()

            if han_input.lower() in ['quit', 'exit', 'q']:
                print("Hẹn gặp lại")
                break

            if not han_input:
                continue

            result = translator.translate(han_input, top_k=1)

            if "error" in result:
                print(f"Lỗi: {result['error']}")
            else:
                print(f"\nKết quả dịch '{result['input']}':\n")
                for i, res in enumerate(result['results'], 1):
                    if res['score'] > 0.7:
                      print(f"Score: {res['score']:.3f}")
                      print(f"{i}. Câu tiếng Hán dich sang tiếng Việt: \n{res['translation']}\n")
                      print(f"Câu tiếng Việt từ trong sách: \n{res['best_match']}")
                    else:
                      print("Không có bản dịch tiếng Hán phù hợp")

        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"Lỗi: {str(e)}")

if __name__ == '__main__':
    main()