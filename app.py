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
