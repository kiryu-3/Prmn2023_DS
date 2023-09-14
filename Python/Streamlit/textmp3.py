import streamlit as st
from gtts import gTTS
import os
import base64
import langdetect


text_area = st.empty()
button_area = st.empty()


def tomp3():
    # 言語を自動検出して言語コードを取得
    detected_language = langdetect.detect(st.session_state["input_text"])
    
    # gTTSインスタンスの作成
    text2speech = gTTS(st.session_state["input_text"], lang=detected_language)
    
    # 一時的なファイル名を生成
    tmp_filename = "temp.mp3"
    
    # MP3ファイルを保存
    text2speech.save(tmp_filename)

    saisei_area = st.empty()
    download_area = st.empty()
    
    # MP3ファイルを再生
    saisei_area.audio(tmp_filename, format="audio/mp3")
    
    # MP3ファイルをダウンロードボタンとして表示
    with open(tmp_filename, "rb") as f:
        download_area.download_button(
            label="MP3ファイルをダウンロード",
            data=f.read(),
            file_name="output.mp3",
            key="download_button",
        )
    
    # 一時ファイルを削除
    os.remove(tmp_filename)

# テキストエリア
input_text = text_area.text_area(label="翻訳する文を入力してください", key="input_text", height=200)
button_area.button(label="Go!", on_click=tomp3)


