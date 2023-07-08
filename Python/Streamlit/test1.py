import streamlit as st
import subprocess

# ファイルのアップロード
uploaded_file = st.file_uploader("Upload LaTeX File", type="tex")

if uploaded_file is not None:
    # テキストファイルの内容を取得
    tex_content = uploaded_file.getvalue().decode()

    # LaTeXファイルを一時ファイルとして保存
    temp_file_path = "/tmp/temp.tex"
    with open(temp_file_path, "w") as f:
        f.write(tex_content)

    # pdflatexコマンドを使用してPDFに変換
    subprocess.run(["pdflatex", "-interaction=batchmode", temp_file_path])

    # 変換後のPDFを表示
    pdf_file_path = temp_file_path.replace(".tex", ".pdf")
    st.download_button("Download PDF", pdf_file_path, file_name="output.pdf", mime="application/pdf")
