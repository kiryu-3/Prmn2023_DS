import streamlit as st

##モジュールのインポート
import cv2
#import google.colab
import matplotlib
import numpy as np
import requests

#PIL試導入
from PIL import Image


#文章
st.title("画像加工Web(仮)")
st.caption("openCVを利用して簡易的な画像加工ができます。")
#st.header("ヘッダーを表示")
#st.subheader("サブヘッダーを表示")
#st.text("テキストを表示")

st.header("Upload File")
files = st.file_uploader(
    label='ファイルをアップロードしてください',
    accept_multiple_files=False, #複数不可
    type='png'
)

#画像を表示
if files is not None:
    st.write(f"アップロードされたファイル名：{files.name}", )
    orig=Image.open(files,)
    if orig is None:
      st.write("ファイルが見つかりません")
    src=np.array(orig,dtype=np.uint8)
    st.image(src)



    #座標の入力
    #st.title('指定した箇所の色を検出します')
    h,w,_=src.shape
    st.write(f"画像のサイズ：[{w},{h}]")

    pos_x = st.number_input(
      label="x座標を入力してください",
      min_value = 0,
      max_value = w,
      value = 1,
    )

    pos_y = st.number_input(
      label="y座標を入力してください",
      min_value = 0,
      max_value = h,
      value = 1,
    )




    #指定箇所の色の検出
    def hex2(num):
      code = hex(num).replace('0x', '')
      if len(code)==1:
        code = "0"+code
      return code


    orig_color=src[pos_y,pos_x]
    r = orig_color[0]
    g = orig_color[1]
    b = orig_color[2]
    a = orig_color[3]
    color_code = '#{}{}{}'.format(hex2(r), hex2(g), hex2(b))
    color_code = color_code.replace('0x', '')
    st.color_picker('座標の色',color_code)

    st.write(f"指定座標[{pos_x},{pos_y}]=RGBA{orig_color}")





    #上限
    st.header("スライダー")

    min_R,max_R = st.slider(
        label = "R",
        min_value = 0,
        max_value = 255,
        value=(0,orig_color[0])
    )
    st.write(f'選択された値: {min_R}-{max_R}')

    min_G,max_G = st.slider(
        label = "G",
        min_value = 0,
        max_value = 255,
        value=(0,orig_color[1])
    )
    st.write(f'選択された値: {min_G}-{max_G}')

    min_B,max_B = st.slider(
        label = "B",
        min_value = 0,
        max_value = 255,
        value=(0,orig_color[2])
    )
    st.write(f'選択された値: {min_B}-{max_B}')

    max_code = '#{}{}{}'.format(hex2(max_R), hex2(max_G), hex2(max_B))
    max_code = max_code.replace('0x', '')
    st.color_picker('上限',max_code)
    st.write(max_code)

    min_code = '#{}{}{}'.format(hex2(min_R), hex2(min_G), hex2(min_B))
    min_code = min_code.replace('0x', '')
    st.color_picker('下限',min_code)
    st.write(min_code)


    #透過処理
    go = st.radio(
      label='加工方法を選択してください',
      options=("透過","塗りつぶし(未実装)","差し替え(未実装)"),
      index=0,
      horizontal=True,
    )

    def mask2():
      if st.button(label='実行'):
        max_color = (max_R,max_G,max_B,255)
        min_color = (min_R,min_G,min_B,0)
        src_mask = cv2.inRange(src, min_color , max_color)
        #src_mask = cv2.inRange(src_mask, 0,0)
        src_bool = cv2.bitwise_not(src, src, mask=src_mask)
        #cv2.imwrite('out.png', src_bool)
        st.image(src_bool)
      return

    if go=='透過':
      if st.button(label='実行'):
        max_color = (max_R,max_G,max_B,255)
        min_color = (min_R,min_G,min_B,0)
        src_mask = cv2.inRange(src, min_color , max_color)
        #src_mask = cv2.inRange(src_mask, 0,0)
        src_bool = cv2.bitwise_not(src, src, mask=src_mask)
        #cv2.imwrite('out.png', src_bool)
        st.image(src_bool)

#ダウンロード
        img = src_bool.copy()
        img=Image.fromarray(img)
        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
                    label='ダウンロード',
                    data=byte_im,
                    file_name='smple_image.png',
                    mime='image/png',
        )



    elif go=='塗りつぶし(未実装)':
      mask2()
      mask_code=st.color_picker('置換色',)
      mask_R=int(mask_code[1:3],16)
      mask_G=int(mask_code[3:5],16)
      mask_B=int(mask_code[5:7],16)
      mask_color=[mask_R,mask_G,mask_B,255]
      st.write(f"選択された値[{mask_R},{mask_G},{mask_B}]")
      blank = np.zeros((h,w,4))
      blank[:,:,0:4] = [mask_R,mask_G,mask_B,255]
      if st.button(label='表示'):
        st.write(f"選択された値[{mask_R},{mask_G},{mask_B},255]")
        st.image(blank)

    elif go=='差し替え(未実装)':
      st.subheader("差し替え画像")

      if st.button(label='実行'):
        max_color = (max_R,max_G,max_B,255)
        min_color = (min_R,min_G,min_B,0)
        src_mask = cv2.inRange(src, min_color , max_color)
        img_AND = cv2.bitwise_and(src, src_mask)
        src_bool= cv2.addWeighted(src1=img_AND,alpha=1,src2=src,beta=1,gamma=0)
        st.image(src_bool)
