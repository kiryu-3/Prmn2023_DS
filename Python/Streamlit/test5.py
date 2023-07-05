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
    st.session_state['mapping'] = {
        "ja": "日本語",
        "en": "英語",
        "zh": "中国語",
        "ko": "韓国語",
        "de": "ドイツ語",
        "es": "スペイン語",
        "fr": "フランス語",
        "tr": "トルコ語",
        "ar": "アラビア語",
        "it": "イタリア語",
        "pt": "ポルトガル語",
        "ru": "ロシア語",
        "nl": "オランダ語",
        "sv": "スウェーデン語",
        "pl": "ポーランド語",
        "vi": "ベトナム語",
        "th": "タイ語",
        "id": "インドネシア語",
        "hi": "ヒンディー語",
        "fi": "フィンランド語",
        "da": "デンマーク語",
        "el": "ギリシャ語",
        "no": "ノルウェー語",
        "he": "ヘブライ語",
        "cs": "チェコ語",
        "ro": "ルーマニア語",
        "hu": "ハンガリー語",
        "sk": "スロバキア語",
        "uk": "ウクライナ語",
        "af": "アフリカーンス語",
        "bg": "ブルガリア語",
        "ca": "カタロニア語",
        "cy": "ウェールズ語",
        "et": "エストニア語",
        "fa": "ペルシャ語",
        "ga": "アイルランド語",
        "hr": "クロアチア語",
        "is": "アイスランド語",
        "lt": "リトアニア語",
        "lv": "ラトビア語",
        "mk": "マケドニア語",
        "ms": "マレー語",
        "mt": "マルタ語",
        "sq": "アルバニア語",
        "sr": "セルビア語",
        "sw": "スワヒリ語",
        "tl": "タガログ語",
        "ur": "ウルドゥー語",
        "yi": "イディッシュ語"
    } 

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

st.session_state["cols"] = st.columns([3, 7])

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

if "language_code" not in st.session_state:  # 初期化
    st.session_state['language_code'] = ""

if "input_language" not in st.session_state:  # 初期化
    st.session_state['input_language'] = ""

def nlp():
    if st.session_state["input_text"] != "":
        st.session_state['input_language'] = ""
        response = comprehend.detect_dominant_language(Text=st.session_state["input_text"])
        st.session_state["language_code"] = response['Languages'][0]['LanguageCode']

        # マッピングから言語名を取得
        st.session_state["language_name"] = st.session_state["mapping"][st.session_state["language_code"]]
        st.session_state['selected_languages'] = [lang for lang in st.session_state['select_languages'] if lang != st.session_state['language_name']]         
        
    else:
        st.session_state["language_code"] = ""
        st.session_state["language_name"] = ""
        st.session_state['selected_languages'] = st.session_state['select_languages']
        st.session_state['translated_text'] = ""


def honyaku():
    reverse_mapping = {v: k for k, v in st.session_state['mapping'].items()}
    st.write(st.session_state['input_language'])
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
            VoiceId=st.session_state['voices'][st.session_state["input_language"]]
        )
        audio_stream = response['AudioStream'].read()
    
        # st.session_state["cols"][1].write(f"言語：{st.session_state['input_language']}")
        # st.session_state["cols"][1].write(f"テキスト：{st.session_state['translated_text']}")
        # # 音声をバイナリストリームとして再生する
        # st.session_state["cols"][1].audio(BytesIO(audio_stream), format='audio/mp3')

    except Exception as e:
        error_message = str(e)
        st.error(error_message)

st.text_input(label="翻訳する文を入力してください",
              key="input_text",
              on_change=nlp)
st.session_state["cols"] = st.columns([3, 7])
if st.session_state["input_text"] != "":
    st.session_state["cols"][0].selectbox(
                label="言語を選んでください",
                options=st.session_state['selected_languages'],
                key="input_language",
                on_change=honyaku
            )
if st.session_state["language_code"] != "":
    st.session_state["cols"][1].write(f"言語：{st.session_state['input_language']}")
    st.session_state["cols"][1].write(f"テキスト：{st.session_state['translated_text']}")
    # 音声をバイナリストリームとして再生する
    st.session_state["cols"][1].audio(BytesIO(audio_stream), format='audio/mp3')
