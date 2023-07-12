import streamlit as st
import xlwings as xw

def excel_to_pdf(excel_file, pdf_file):
    # Excelアプリケーションを起動
    app = xw.App(visible=False)
    
    # Excelファイルを開く
    wb = app.books.open(excel_file)
    
    # PDFファイルに変換
    wb.export(pdf_file, "PDF")
    
    # ファイルを閉じてExcelを終了
    wb.close()
    app.quit()

def main():
    st.title("Excel to PDF Converter")
    
    # アップロードされたExcelファイルを取得
    excel_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])
    
    if excel_file is not None:
        # ダウンロードボタンを表示
        download_button_str = f"Download PDF"
        download_file = False
        
        if st.button(download_button_str):
            # 一時的なファイル名を生成
            pdf_file = f"temp.pdf"
            
            # ExcelをPDFに変換
            excel_to_pdf(excel_file, pdf_file)
            
            # ダウンロード用のリンクを生成
            download_file = True
        
        if download_file:
            with open(pdf_file, "rb") as f:
                st.download_button(label=download_button_str, data=f, file_name="converted.pdf")
    
if __name__ == "__main__":
    main()
