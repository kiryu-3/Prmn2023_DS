import streamlit as st
import pandas as pd
from pdfdocument import PDFDocument

def excel_to_pdf(excel_file, pdf_file):
    # エクセルファイルを読み込む
    df = pd.read_excel(excel_file)

    # PDFファイルを作成する
    pdf = PDFDocument(pdf_file)
    pdf.init_report()
    pdf.h1('Excel to PDF Conversion')
    pdf.h2('Data')
    pdf.p(str(df))
    pdf.generate()

    # 作成したPDFファイルを返す
    return pdf_file

# Streamlitアプリケーションの設定
st.title('Excel to PDF Converter')
excel_file = st.file_uploader('Upload Excel File', type=['xlsx'])
if excel_file is not None:
    pdf_file = excel_file.name.replace('.xlsx', '.pdf')
    st.write('Converting to PDF...')
    converted_file = excel_to_pdf(excel_file, pdf_file)
    st.success('Conversion completed!')
    st.download_button('Download PDF', converted_file)
