import streamlit as st
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# === ✅ セットアップ ===
st.set_page_config(page_title="社内RAGチャットボット", layout="wide")
st.title("📘 社内ルール相談チャットボット")

# === ✅ モデルとデータの読み込み ===
@st.cache_resource
def load_model_and_data():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    with open("vector_store.pkl", "rb") as f:
        data = pickle.load(f)
    return model, data

model, manual_data = load_model_and_data()

# === ✅ OpenAIキーの読み込み（secrets.toml 経由） ===
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# === ✅ ユーザー入力 ===
query = st.text_input("💬 質問を入力してください")

if st.button("回答を生成") and query:
    # === ✅ 類似検索 ===
    query_vec = model.encode(query)
    docs = manual_data
    manual_embeddings = [model.encode(d['body']) for d in docs]
    similarities = np.dot(manual_embeddings, query_vec) / (
        np.linalg.norm(manual_embeddings, axis=1) * np.linalg.norm(query_vec)
    )
    top_k = np.argsort(similarities)[-3:][::-1]

    # === ✅ プロンプト作成 ===
    retrieved = "\n".join(
        f"{docs[i]['title']}（{docs[i]['article']}）: {docs[i]['body']}" for i in top_k
    )
    prompt = f"""以下のマニュアルに基づき、質問に丁寧に答えてください。

マニュアル抜粋:
{retrieved}

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
