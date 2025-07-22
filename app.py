# RAG_vectorファイル二つを対象とする形式（マニュアル、FAQ）

import streamlit as st
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# === ✅ ページ設定 ===
st.set_page_config(page_title="社内RAGチャットボット", layout="wide")
st.title("📘 社内ルール相談チャットボット")

# === ✅ モデルとデータの読み込み（FAQ + マニュアル） ===
@st.cache_resource
def load_model_and_data():
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # FAQデータ
    with open("vector_store_faq.pkl", "rb") as f:
        faq_data = pickle.load(f)

    # マニュアルデータ
    with open("vector_store.pkl", "rb") as f:
        manual_data = pickle.load(f)

    return model, faq_data, manual_data

model, faq_data, manual_data = load_model_and_data()

# === ✅ OpenAIキーの読み込み（secrets.toml 経由） ===
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# === ✅ ユーザー入力欄 ===
query = st.text_input("💬 質問を入力してください")

if st.button("回答を生成") and query:
    query_vec = model.encode(query)

    # ✅ スコア付き検索関数（フィールド柔軟対応 + 類似度返却）
    def search_similar_docs(data, query_vec, top_k=3):
        for field_option in ["body", "answer"]:
            if field_option in data[0]:
                target_field = field_option
                break
        else:
            raise KeyError("対象データに 'body' または 'answer' フィールドが見つかりません")

        embeddings = [model.encode(d[target_field]) for d in data]
        similarities = np.dot(embeddings, query_vec) / (
            np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_vec)
        )
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        top_docs = [data[i] for i in top_indices]
        top_scores = [similarities[i] for i in top_indices]
        return top_docs, top_scores

    # === ✅ FAQ優先 → スコア低ければマニュアル検索へ切り替え ===
    top_faq, faq_scores = search_similar_docs(faq_data, query_vec)
    THRESHOLD = 0.6  # 類似度のしきい値（0〜1）

    if max(faq_scores) >= THRESHOLD:
        retrieved_label = "FAQ"
        retrieved_docs = top_faq
    else:
        top_manual, _ = search_similar_docs(manual_data, query_vec)
        retrieved_label = "マニュアル"
        retrieved_docs = top_manual

    # === ✅ プロンプト作成 ===
    def format_docs(label, docs):
        return f"\n--- {label} ---\n" + "\n".join(
            f"{doc.get('title', 'Q&A')}（{doc.get('article', '')}）: {doc.get('body', doc.get('answer', ''))}"
            for doc in docs
        )

    retrieved_text = format_docs(retrieved_label, retrieved_docs)

    prompt = f"""以下の社内資料に基づき、質問に丁寧に答えてください。

{retrieved_text}

質問:
{query}

回答:"""

    # === ✅ ChatGPTで回答生成 ===
    with st.spinner("回答を生成中..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは社内規定に詳しいアシスタントです。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            answer = response.choices[0].message.content
            st.success("✅ 回答はこちら")
            st.markdown(answer)
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")

elif not query:
    st.info("💬 質問を入力後、[回答を生成]をクリックしてください")
