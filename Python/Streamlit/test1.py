import streamlit as st
from pylatex import Document, Section, Subsection, Command

# ファイルのアップロード
uploaded_file = st.file_uploader("Upload LaTeX File", type="tex")

if uploaded_file is not None:
    # テキストファイルの内容を取得
    tex_content = uploaded_file.getvalue().decode()

    # LaTeXドキュメントを作成
    doc = Document()
    doc.append(Command('title', 'Generated PDF'))
    doc.append(Command('author', 'User'))
    doc.append(Command('date', 'Today'))
    doc.append(tex_content)

    # PDFに変換
    pdf_bytes = doc.generate_pdf()

    # 変換後のPDFをダウンロード
    st.download_button("Download PDF", pdf_bytes, file_name='output.pdf', mime='application/pdf')
