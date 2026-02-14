from flask import Flask, request, jsonify, render_template, send_file
import openai
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

system_prompt = """
다음은 영문 의료 데이터 텍스트입니다. 한국어로 번역을 한 뒤
번역한 내용을 요약 정리합니다.
병을 진단하는 기준인 키워드와 진단 병명을 출력해 주세요.
출력 시 번역, 요약, 키워드, 진단 병명 사이에 구분 기호를 넣어주세요.
"""

results = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    user_text = request.json.get("text", "")
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        max_tokens=500,
        temperature=0
    )
    result = response.choices[0].message.content

    # Save result
    results.append({"Review": user_text, "ChatGPT_Result": result})

    # Create dynamic filename with today's date
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"analysis_results_{today}.xlsx"

    # Export to Excel
    df = pd.DataFrame(results)
    df.to_excel(filename, index=False)

    return jsonify({"result": result, "filename": filename})

@app.route("/download", methods=["GET"])
def download():
    # Always serve the latest file (based on today’s date)
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"analysis_results_{today}.xlsx"
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
    
@app.route("/reset", methods=["POST"])
def reset():
    global results
    results = []  # clear the list
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"analysis_results_{today}.xlsx"
    pd.DataFrame(results).to_excel(filename, index=False)
    return jsonify({"message": f"Results have been reset. New file: {filename}"})
