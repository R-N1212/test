# RAG_QuizBot_txt-yaml
# 2025-07-23 18:00

import yaml

# 入力・出力ファイルパス（適宜変更可能）
input_path = r"C:\Users\ryotaro\Desktop\RAG\RAG_コンプラクイズ_用語.txt"
output_path = "compliance_quiz.yaml"


def parse_quiz_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = [block.strip() for block in raw.split("---") if block.strip()]
    quiz_list = []

    for block in blocks:
        lines = block.splitlines()
        question = ""
        answer = ""
        choices = []

        for line in lines:
            if line.startswith("Q:"):
                question = line[2:].strip()
            elif line.startswith("A:"):
                answer = line[2:].strip()
                choices.append(answer)  # 正解も選択肢に含める
            elif line.startswith("C:"):
                choice = line[2:].strip()
                if choice != answer:  # 重複を避けたければこの条件を外す
                    choices.append(choice)

        quiz_list.append({
            "question": question,
            "answer": answer,
            "choices": choices
        })

    return quiz_list


def save_as_yaml(data, yaml_path):
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)


if __name__ == "__main__":
    quiz_data = parse_quiz_txt(input_path)
    save_as_yaml(quiz_data, output_path)
    print(f"✅ YAMLファイルに変換完了: {output_path}")
