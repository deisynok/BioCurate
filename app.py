import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import cv2

st.set_page_config(page_title="BioCurate", layout="centered")
st.title("📦 BioCurate - Leitor de Exsicatas")

st.markdown("""
Bem-vindo ao **BioCurate**, desenvolvido pelo Herbário HUAM.  
Este aplicativo permite ler códigos de barras ou QR codes de exsicatas e consultar os dados associados em uma planilha no formato **Darwin Core (DwC)**.
""")

# Upload da base de dados
st.subheader("📁 Enviar base de dados (.csv) no formato Darwin Core")
uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Base carregada com {df.shape[0]} registros.")
    st.dataframe(df.head())

    # Upload da imagem com código
    st.subheader("📷 Ler código de barras ou QR Code")
    img_file = st.file_uploader("Envie uma imagem (PNG, JPG)", type=["png", "jpg", "jpeg"])

    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Imagem enviada", use_column_width=True)

        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        decoded_objects = decode(img_cv)

        if decoded_objects:
            for obj in decoded_objects:
                code_data = obj.data.decode("utf-8")
                st.success(f"Código lido: `{code_data}`")

                result = df[df.apply(lambda row: row.astype(str).str.contains(code_data), axis=1)]

                if not result.empty:
                    st.markdown("### 🗃️ Resultado encontrado:")
                    st.dataframe(result)
                else:
                    st.warning("⚠️ Código não encontrado na base.")
        else:
            st.error("Nenhum código foi detectado na imagem.")
