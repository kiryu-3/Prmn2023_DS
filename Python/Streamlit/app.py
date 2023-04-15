import streamlit as st
import random
import datetime
import time

def judge_hit_blow(guess, answer):
    # ヒットアンドブローの判定を行う関数
    hit = 0
    blow = 0
    for i, digit in enumerate(guess):
        if digit == answer[i]:
            hit += 1
        elif digit in answer:
            blow += 1
    return hit, blow

markdown = """
【ヒットアンドブローとは】\r\n
ヒットアンドブローは、4桁の数字を当てるゲームです。\r\n
プレイヤーは、コンピュータが用意した数字を予想し、\r\n
その結果に対して、ヒット（数字と位置が一致）、ブロー（数字のみが一致）の数を教えてもらいます。\r\n
この情報をもとに、次の予想を立てて、正解を目指しましょう。\r\n

【ルール】\r\n
ゲーム開始時に、コンピュータが4桁の数字を用意します。\r\n
プレイヤーは、4桁の数字を予想し、入力します。\r\n
コンピュータは、プレイヤーの予想に対して、ヒットとブローの数を教えます。\r\n
プレイヤーは、この情報をもとに、次の予想を立てます。\r\n
ヒットが4つになるまで、3〜4を繰り返します。\r\n
ヒットが4つになったら、ゲーム終了です。\r\n
"""

st.title("ヒットアンドブロー")
with st.expander("ルールを見る"):
  st.write(markdown)

# ゲームの開始
st.write("4桁の数字を当ててください！")
guess = st.text_input("数字を入力してください", max_chars=4)
btn = st.button('送信する')

# 試行回数と答えを管理する変数
if 'count' not in st.session_state:
    st.session_state.count = 0
    # 4桁のランダムな数字を作成
    st.session_state.answer = ''.join(random.sample('0123456789', 4))

# ゲームのループ
if (guess is not None) and (len(guess) == 4) and (btn):
    st.session_state.count += 1
    print(st.session_state.answer)  # デバッグ用
    if guess == st.session_state.answer:
        st.write(f"正解！{st.session_state.count}回目の試行で当てました！")
        del st.session_state['count']  # キー'count'を削除
        st.write("15秒後に最初の画面に遷移します")
        time.sleep(15)
        st.experimental_rerun()  # 現在のスクリプトの再実行をトリガーする
    else:
        hit, blow = judge_hit_blow(guess, st.session_state.answer)
        st.write(f"{guess}: {hit}ヒット, {blow}ブロー")
elif btn:
    st.write("4桁の数字を入力してください。")
