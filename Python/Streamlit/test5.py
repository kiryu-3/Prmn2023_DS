import boto3
import streamlit as st
from io import BytesIO

access_key = 'AKIAW7ZW5WIR5VJRHQRC'
secret_key = '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'
region_name = 'ap-northeast-1'

session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region_name)
comprehend = session.client('comprehend')
translate = session.client('translate')
polly = session.client('polly')

if 'mapping' not in st.session_state:  # 初期化
    st.session_state['mapping'] = {}

    with open("languages.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                key, value = line.split(":")  # もしくは line.split("\t")
                st.session_state['mapping'][key.strip()] = value.strip()

if 'select_languages' not in st.session_state:  # 初期化
    st.session_state['select_languages'] = [
        "日本語",
        "英語",
        "中国語",
        "韓国語",
        "ドイツ語",
        "スペイン語",
        "フランス語"
    ]

if 'selected_languages' not in st.session_state:  # 初期化
    st.session_state['selected_languages'] = st.session_state['select_languages']

if 'voices' not in st.session_state:  # 初期化
   st.session_state['voices'] = {
       "英語": "Joanna",
       "日本語": "Mizuki",
       "中国語": "Zhiyu",
       "韓国語": "Seoyeon",
       "フランス語": "Celine",
       "スペイン語": "Lucia",
       "ドイツ語": "Marlene"
   }


def nlp():
    if st.session_state["input_text"] != "":
        response = comprehend.detect_dominant_language(Text=st.session_state["input_text"])
        st.session_state["language_code"] = response['Languages'][0]['LanguageCode']

        # マッピングから言語名を取得
        try:
            st.session_state["language_name"] = st.session_state["mapping"][st.session_state["language_code"]]
        if 'select_languages' in st.session_state and 'language_name' in st.session_state:
            st.session_state['selected_languages'] = [lang for lang in st.session_state['select_languages'] if lang != st.session_state['language_name']]
        st.session_state["cols"][0].selectbox(
            label="言語を選んでください",
            options=st.session_state['selected_languages'],
            key="input_language",
            on_change=honyaku
        )
    else:
        st.session_state["language_code"] = ""
        st.session_state["language_name"] = ""
        st.session_state['selected_languages'] = st.session_state['select_languages']
        st.session_state['translated_text'] = ""


def honyaku():
    reverse_mapping = {v: k for k, v in st.session_state['mapping'].items()}
    try:
        response = translate.translate_text(
            Text=st.session_state["input_text"],
            SourceLanguageCode= st.session_state["language_code"],
            TargetLanguageCode=reverse_mapping[st.session_state["input_language"]]
        )
        st.session_state["translated_text"] = response['TranslatedText']
        response = polly.synthesize_speech(
            Text=st.session_state["translated_text"],
            OutputFormat='mp3',
            VoiceId=st.session_state['voices'][reverse_mapping[st.session_state["input_language"]]]
        )
        audio_stream = response['AudioStream'].read()
    
        st.session_state["cols"][1].write(f"言語：{st.session_state['input_language']}")
        st.session_state["cols"][1].write(f"テキスト：{st.session_state['translated_text']}")
        # 音声をバイナリストリームとして再生する
        st.session_state["cols"][1].audio(BytesIO(audio_stream), format='audio/mp3')

    except translate.exceptions.TranslateTextException as e:
        error_message = str(e)
        st.error(error_message)

st.text_input(label="翻訳する文を入力してください",
              key="input_text",
              on_change=nlp)
st.session_state["cols"] = st.columns([3, 7])
