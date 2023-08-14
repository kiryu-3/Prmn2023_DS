import streamlit as st
import pandas as pd
import requests

list_runsco = []
list_A=[]
list_B=[]
n = 0
i=0

list_kekka = ["得点", "ミス"]
list_syurui = ["DS", "BT", "SS", "PS", "NM", "7MT"]
list_iti = ["右", "左", "中"]
list_kosu = ["右上","右中", "右下", "左上","左中", "左下","中上","中中","中下"]

st.title("スコア分析")

def nyuuryoku():
    global list_runsco, n, list_A, list_B,i
    unique_key_teamserect = f"teamserect_{len(list_runsco)}"
    unique_key_sebanngou = f"sebanngou_{len(list_runsco)}"
    unique_key_sokkou = f"sokkou_{len(list_runsco)}"
    unique_key_kekka = f"kekka_{len(list_runsco)}"
    unique_key_iti = f"iti_{len(list_runsco)}"
    unique_key_syurui = f"syurui_{len(list_runsco)}"
    unique_key_kosu = f"kosu_{len(list_runsco)}"
    unique_key_senntaku = f"senntaku_{len(list_runsco)}"

    teamserect = st.selectbox(label='どちらのチームに入力しますか？',
                      options=("A","B"),
                      key=unique_key_teamserect)

    sebanngou = st.number_input("背番号", 1, 100, 1, key=unique_key_sebanngou)

    sokkou = st.radio(label='速攻かどうか',
                      options=("FB", "QS", "なし"),
                      key=unique_key_sokkou)

    kekka = st.radio(label="結果を選択してください",
                           options=list_kekka,
                           key=unique_key_kekka)

    iti = st.selectbox(label="シュート位置を入力してください",
                         options=list_iti,key=unique_key_iti)

    syurui = st.selectbox(label="シュートの種類を選択してください",
                            options=list_syurui,key=unique_key_syurui)

    kosu = st.selectbox(label="コースを選択してください",
                          options=list_kosu,key=unique_key_kosu)

    senntaku = st.radio(label='入力を続けますか？',
                        options=("終了","続ける"),key=unique_key_senntaku)

    data = [teamserect,sebanngou, sokkou, kekka, iti, syurui, kosu]
    list_runsco.append(data)

    if list_runsco[i][0]=="A":
        list_A.append(list_runsco[i])

    if list_runsco[i][0]=="B":
        list_B.append(list_runsco[i])

    df_A = pd.DataFrame(list_A, columns=["チーム", "背番号", "速攻", "結果", "位置", "種類", "コース"])
    df_B = pd.DataFrame(list_B, columns=["チーム", "背番号", "速攻", "結果", "位置", "種類", "コース"])
    i=i+1

    if senntaku == "終了":
        n = 2
        st.write(list_A)
        st.write(list_B)
       
    return df_A,df_B

def bunnseki(x):
    team_name=(x == "A").sum().sum()
    if team_name>0:
        team_name ="A"
    else:
      team_name="B"

    i=0
    tokutenn = (x == "得点").sum().sum()
    kogekikaisuu = len(x)
    of_seikouritu = tokutenn/kogekikaisuu

    class score_bunnseki:
        def __init__(self, midasi, team,  name,  kaisuu, tokutenn, seikouritu):
           self.midasi = midasi
           self.team = team
           self.name = name
           self.kaisuu = kaisuu
           self.tokutenn = tokutenn
           self.seikouritu = seikouritu

        def output(self):
              st.write("{}{}{}は{}本中{}本で{}です。".format(self.midasi, self.team, self.name, self.kaisuu ,self.tokutenn, self.seikouritu))

    zenntai = score_bunnseki( "全体のOF成功率・・・" ,team_name,"チーム", kogekikaisuu, tokutenn, of_seikouritu)
    zenntai.output()

    while i<20:
      if ((x['背番号'] == i).sum() > 0):
        banngou = i
        sebanngou_tokutenn = ((x['背番号'] == i) & (x['結果'] =="得点")).sum()
        sebanngou_kogekikaisuu = (x['背番号'] == i).sum()
        sebanngou_tokutennritu = sebanngou_tokutenn / sebanngou_kogekikaisuu
        sebanngougoto = score_bunnseki( "背番号ごとの決定率・・・" ,team_name,banngou, sebanngou_kogekikaisuu, sebanngou_tokutenn, sebanngou_tokutennritu)
        sebanngougoto.output()
      i=i+1

    i=0
    while i<6:
      if ((x['種類'] == list_syurui[i]).sum() > 0):
        syurui = list_syurui[i]
        syurui_tokutenn = ((x['種類'] == list_syurui[i]) & (x['結果'] =="得点")).sum()
        syurui_kougekikaisuu = (x['種類'] == list_syurui[i]).sum()
        syurui_ketteiritu = syurui_tokutenn / syurui_kougekikaisuu
        syuruigoto = score_bunnseki("シュート種別ごとの決定率・・・" ,team_name,syurui, syurui_kougekikaisuu, syurui_tokutenn, syurui_ketteiritu)
        syuruigoto.output()
      i=i+1
          
while n <1:
    A,B=nyuuryoku()
st.write(A)
st.write(B)
bunnseki(A)
bunnseki(B)
