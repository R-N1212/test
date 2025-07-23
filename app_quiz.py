# RAG_QuizBot_prototype1
# 2025-07-23 18:20

import streamlit as st
import yaml
import random

# === ✅ 設定 ===
st.set_page_config(page_title="コンプライアンス クイズボット", layout="centered")
st.title("📝 コンプライアンス理解度チェック")

# === ✅ クイズデータ読み込み ===


@st.cache_data
def load_quiz_data(yaml_file="compliance_quiz.yaml"):
    with open(yaml_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


quiz_data = load_quiz_data()

# === ✅ セッション状態の初期化 ===
if "quiz_order" not in st.session_state:
    st.session_state.quiz_order = random.sample(quiz_data, k=5)
    st.session_state.current_question = 0
    st.session_state.answers = []
    st.session_state.correct_count = 0
    st.session_state.finished = False

# === ✅ クイズを進行 ===
if not st.session_state.finished:
    q_index = st.session_state.current_question
    quiz = st.session_state.quiz_order[q_index]

    st.subheader(f"問題 {q_index + 1} / 5")
    st.write(quiz["question"])
    user_choice = st.radio("選択肢を選んでください：", quiz["choices"], key=f"q{q_index}")

    if st.button("次へ"):
        is_correct = user_choice == quiz["answer"]
        st.session_state.answers.append(
            (quiz["question"], user_choice, quiz["answer"], is_correct))
        if is_correct:
            st.session_state.correct_count += 1

        st.session_state.current_question += 1

        if st.session_state.current_question >= 5:
            st.session_state.finished = True
            st.rerun()

else:
    # === ✅ 結果表示 ===
    total = len(st.session_state.quiz_order)
    correct = st.session_state.correct_count
    st.subheader("📊 結果発表")
    st.markdown(f"**{correct} / {total} 正解**（正答率：{(correct/total)*100:.1f}%）")

    if correct == total:
        st.success("🎉 完了です！お疲れ様でした。")
    else:
        st.warning("🤔 もう一度チャレンジしてみませんか？")

    # 不正解の詳細表示
    with st.expander("不正解の内容を確認する"):
        for q_text, user_ans, correct_ans, is_correct in st.session_state.answers:
            if not is_correct:
                st.markdown(f"**Q:** {q_text}")
                st.markdown(f"あなたの回答: ❌ {user_ans}")
                st.markdown(f"正解: ✅ {correct_ans}")
                st.markdown("---")

    if st.button("🔁 もう一度挑戦"):
        # セッション初期化
        st.session_state.quiz_order = random.sample(quiz_data, k=5)
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.session_state.correct_count = 0
        st.session_state.finished = False
        st.rerun()
