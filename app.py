# -----------------------------------------------
# BioCurate – Curation and Identification of Botanical Specimens
# Developed with Streamlit
#
# Author: Deisy Saraiva
# Institution: Federal University of Amazonas (UFAM)
# Program: PhD in Biodiversity and Biotechnology – BIONORTE
# Contact: deisysaraiva@ufam.edu.br
#
# Creation date: 2025-06-25
# Last updated: 2026-06-18
# -----------------------------------------------

import os
import re
import io
import time
import streamlit as st
import pandas as pd
import numpy as np
import cv2
import requests
import plotly.express as px

from io import BytesIO
from PIL import Image, ImageOps
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu


# -----------------------------------------------
# General Configuration
# -----------------------------------------------

st.set_page_config(page_title="BioCurate",  
    page_icon="favicon.png",
    layout="centered"
    )

# Toggle for language selection (PT as default)
col1, col2, col3 = st.columns([5, 1, 1])
with col3:
    is_en = st.toggle("PT / EN", value=False)

# If the selected language is English, redirect to the translated page
if is_en:
    from en_app import run as run_en
    run_en()
    st.stop()  # Stop execution of the code below

# Session variables
if 'df' not in st.session_state:
    st.session_state.df = None
if 'barcode_col' not in st.session_state:
    st.session_state.barcode_col = 'collectionCode'
if 'img_folder' not in st.session_state:
    st.session_state.img_folder = ''

# -----------------------------------------------
# Responsive horizontal menu
# -----------------------------------------------

# Create horizontal navigation bar
selected = option_menu(
    None,
    ["Início", "Base", "Relatório", "Busca", "Imagem"],
    icons=["house", "database", "bar-chart", "search", "image"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
    "container": {
        "padding": "0!important",
        "background-color": "#00A8A8"  # Azul esverdeado - lateral da logo
    },
    "icon": {
        "color": "#FFFFFF",
        "font-size": "20px"
    },
    "nav-link": {
        "font-size": "18px",
        "text-align": "center",
        "margin": "0px",
        "color": "#FFFFFF",
        "--hover-color": "#B2DFDB"  # Verde-água suave
    },
    "nav-link-selected": {
        "background-color": "#388E3C"  # Verde escuro
    },
},
)

# -----------------------------------------------
# Home Page
# -----------------------------------------------
if selected == "Início":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("logo.png", width=200)
    with col2:
        st.markdown("""
            O **BioCurate** é uma ferramenta voltada à curadoria de coleções biológicas, com ênfase em herbários.  
            Melhora a acessibilidade e a precisão na organização de dados, permitindo o cruzamento de informações por leitura de códigos de barras ou entrada manual.  
            Também integra visualização de imagens e consultas externas a bases como GBIF, Reflora e SpeciesLink.
            """)
    
    st.markdown("""
        ##### Recursos do BioCurate

        1. **📦 Base de Dados**  
        Carregue automaticamente a planilha oficial do HUAM ou envie sua própria base em formato CSV (padrão Darwin Core). Ela será usada em todas as buscas.

        2. **📊 Relatório**  
        Gere relatórios por família, gênero ou espécie, com contagem de amostras, lista de táxons e locais de armazenamento.

        3. **📋 Buscar Dados**  
        Consulte dados detalhados da amostra pelo número de tombo ou código de barras: nome científico, local de coleta e armazenamento.

        4. **📷 Buscar Imagem**  
        Visualize a exsicata e envie para o Pl@ntNet para identificação automática da espécie. Funciona apenas com amostras do HUAM, vinculadas ao Google Drive institucional.      
    """)
       
    st.markdown("""
        ### Sobre o BioCurate
        Este projeto é uma iniciativa do **Herbário da Universidade Federal do Amazonas (HUAM)** e faz parte da pesquisa de doutorado de **Deisy Saraiva**, vinculada ao **Programa de Pós-Graduação BIONORTE – Rede de Biodiversidade e Biotecnologia da Amazônia Legal**. A pesquisa foca no uso de tecnologias para ampliar o acesso e a curadoria de coleções científicas, principalmente do Herbário do HUAM.

        Contato: deisysaraiva@ufam.edu.br

        - [Acesse o site do HUAM](http://huam.site)
        - [A Coleção no site institucional da UFAM](https://www.icb.ufam.edu.br/colecoes/huam.html)

        ---

        ### Sobre a Identificação Automática com Pl@ntNet

        BioCurate integra a identificação automática de espécies por imagem via API Pl@ntNet.  
        Os resultados são gerados por inteligência artificial e devem ser validados por um especialista.  
        Mais informações em plantnet.org.  

        ---

        ### Sobre o padrão Darwin Core

        O **Darwin Core** é um padrão internacional para compartilhamento de dados sobre biodiversidade. Ele define termos recomendados que garantem consistência e interoperabilidade entre bases de dados.

        - [Repositório Darwin Core](https://github.com/tdwg/dwc)
        - [Padrão Darwin Core](https://dwc.tdwg.org/terms)
        - [Modelo de Cabeçalho Darwin Core](https://splink.cria.org.br/digir/darwin2.xsd)
        - [Vídeo explicativo (YouTube)](https://www.youtube.com/embed/YC0DfctXs5Q)
    """)

    with st.expander("Descrição dos Metadados Necessária na Base"):
        st.markdown("""
            A base de dados a ser carregada deve seguir o padrão **Darwin Core**, adotando campos fundamentais para curadoria:

            - **collectionCode:** Código único da coleção (número do tombo HUAM).
            - **catalogNumber:** Número de catálogo interno da amostra.
            - **recordedBy:** Nome do coletor principal responsável pela amostra.
            - **addCollector:** Coletores adicionais envolvidos na coleta.
            - **recordNumber:** Número atribuído pelo coletor à amostra.
            - **dayCollected / monthCollected / yearCollected:** Datas exatas de coleta da amostra.
            - **family:** Família botânica a que pertence a amostra.
            - **scientificName:** Nome científico completo (gênero + espécie + infraespécie, se aplicável).
            - **genus:** Nome do gênero botânico.
            - **specificEpithet:** Epíteto específico (nome da espécie).
            - **scientificNameAuthorship:** Autoridade taxonômica que descreveu o táxon.
            - **dynamicProperties:** Localização física da amostra na coleção (ex.: armário, prateleira).

            Esses campos garantem que a base de dados seja compatível com padrões de intercâmbio, como **GBIF**, **SpeciesLink** e **Reflora**, e viabilizam sua utilização em **sistemas digitais** como o BioCurate.
        """)
    
    #Supported by
    st.markdown("---")
    st.markdown(" ##### Apoio")
    st.image("SupportedBy.png", use_container_width=True)

# -----------------------------------------------
# Data Base Page
# -----------------------------------------------
elif selected == "Base":
    st.subheader("📦 Base de Dados")
    st.subheader("Conexão automática com Base de Dados HUAM")

    # Automatic connection to the HUAM huam
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_base = conn.read(worksheet="Metadata", ttl="10m")
        
    st.session_state.df = df_base
    st.success("✔️ Base de Dados do Herbário HUAM carregada!")
    st.write(df_base.head())

    # Upload CSV to overwrite existing data
    st.subheader("Ou envie sua própria base em formato DarwinCore")
    file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
    if file:
        df_base = pd.read_csv(file)
        st.session_state.df = df_base
        st.success("Arquivo CSV carregado! Base atualizada.")
        st.write(df_base.head())

# -----------------------------------------------
# Report Page
# -----------------------------------------------
elif selected == "Relatório":
    st.subheader("📊 Relatório de Dados")
    st.write(
        "Gere relatórios a partir da base de dados carregada na aba **BASE**. "
        "Informe o nome de uma **família**, **gênero** ou **espécie** e clique em **Buscar** para visualizar o número de amostras, "
        "a localização na coleção, a lista de táxons relacionados e os registros completos disponíveis."
    )

    # Load the database
    if st.session_state.df is None:
        st.warning("⚠️ A base de dados precisa ser carregada na aba **BASE**!")	
    else:
        df = st.session_state.df.copy()

        # Show all botanical families in the dataset
        if st.button("Listar Todas as Famílias Botânicas"):
            contagem_familias = df["family"].value_counts().sort_values(ascending=True)
            st.session_state["contagem_familias"] = contagem_familias  # salva na sessão

            st.success(f"**Total de famílias encontradas:** {len(contagem_familias)}")
            st.write(", ".join(contagem_familias.index.tolist()))

        # Show chart button (only if data is available)
        if "contagem_familias" in st.session_state:
            if st.button("📊 Exibir Gráfico Interativo por Família"):
                contagem_familias = st.session_state["contagem_familias"]
                df_plot = contagem_familias.reset_index()
                df_plot.columns = ["Família", "Amostras"]

                fig = px.bar(
                    df_plot,
                    x="Amostras",
                    y="Família",
                    orientation="h",
                    title="Amostras por Família",
                    labels={"Amostras": "Quantidade de Amostras", "Família": "Família"},
                    color_discrete_sequence=["#388E3C"],
                    height=max(400, len(df_plot) * 20)  # ajusta altura
                )

                st.plotly_chart(fig, use_container_width=True)        

        # Family Report
        st.subheader("Consultar por Família")
        familia = st.text_input("Digite o nome da família:")
        if st.button("🔍 Buscar Família"):
            if familia:
                df_fam = df[df["family"].str.upper() == familia.upper()]
                num_material = len(df_fam)
                generos = df_fam["genus"].dropna().unique()
                especies = df_fam["scientificName"].dropna().unique()
                locs = df_fam["dynamicProperties"].dropna().unique()

                if len(locs) > 0:
                    locs_str = ", ".join(sorted(map(str, locs)))
                    st.info(f"**Localização na coleção:** {locs_str}")

                st.info(f"**Total de amostras:** {num_material}")
                st.info(f"**Total de gêneros:** {len(generos)}")
                st.write("**Gêneros encontrados:**")
                st.write(", ".join(sorted(map(str, generos))))

                st.info(f"**Total de espécies:** {len(especies)}")
                st.write("**Espécies encontradas:**")
                st.write(", ".join(sorted(map(str, especies))))
            else:
                st.warning("Digite o nome da família antes de buscar.")

        # Genus Report
        st.subheader("Consultar por Gênero")
        genero = st.text_input("Digite o nome do gênero:")
        
        if st.button("🔍 Buscar Gênero"):
            if genero:
                df_gen = df[df["genus"].str.upper() == genero.upper()]
                total_amostras = len(df_gen)
                so_genero = df_gen[df_gen["scientificName"].isna() | (df_gen["scientificName"].str.strip() == "")]
                especies_por_genero = df_gen["scientificName"].dropna().unique()
                locs = df_gen["scientificName"].dropna().unique()
                familias = df_gen["family"].dropna().unique()

                if len(locs) > 0:
                    locs_str = ", ".join(sorted(map(str, locs)))
                    st.info(f"**Localização na coleção:** {locs_str}")

                st.info(f"**Família:** {', '.join(sorted(map(str, familias)))}")
                st.info(f"**Amostras do gênero:** {total_amostras}")
                st.info(f"**Espécies dentro do gênero:** {len(especies_por_genero)}")
                st.write("**Espécies encontradas:**")
                st.write(", ".join(sorted(map(str, especies_por_genero))))
            else:
                st.warning("Digite o nome do gênero antes de buscar.")

        # Species Report
        st.subheader("Consultar por Espécie")
        especie = st.text_input("Digite o nome científico da espécie:")
       
        if st.button("🔍 Buscar Espécie"):
            if especie:
                df_esp = df[df["scientificName"].str.upper() == especie.upper()]
                total_especie = len(df_esp)
                locs = df_esp["dynamicProperties"].dropna().unique()
                familias = df_esp["family"].dropna().unique()

                if len(locs) > 0:
                    locs_str = ", ".join(sorted(map(str, locs)))
                    st.info(f"**Localização na coleção:** {locs_str}")

                st.info(f"**Família:** {', '.join(sorted(map(str, familias)))}")
                st.info(f"**Total de amostras da espécie:** {total_especie}")

                if total_especie > 0:
                    st.write("**Detalhe das amostras encontradas:**")
                    st.dataframe(df_esp, use_container_width=True)
                else:
                    st.warning("Nenhuma amostra encontrada para essa espécie.")
            else:
                st.warning("Digite o nome da espécie antes de buscar.")

# -----------------------------------------------
# Data Search Page
# -----------------------------------------------
elif selected == "Busca":
    st.subheader("📋 Buscar Dados")
    st.write(
        "Consulte informações detalhadas das amostras a partir do número de tombo. "
        "Digite o código manualmente ou faça a leitura do QR Code para visualizar dados taxonômicos, "
        "local de armazenamento, coletores e outras informações relevantes."
    )

    # -------------------------------------------------
    # Funções auxiliares
    # -------------------------------------------------
    def normalizar_codigo(valor):
        """
        Normaliza o código lido manualmente ou por QR Code.
        Aceita códigos como HUAM001245, 1245 ou URLs contendo o código.
        """
        if valor is None:
            return ""

        texto = str(valor).strip().upper()

        # Caso o QR Code contenha uma URL, tenta extrair HUAM + números
        match_huam = re.search(r"HUAM\s*0*\d+", texto)
        if match_huam:
            return match_huam.group(0).replace(" ", "")

        # Caso contenha apenas números
        match_num = re.search(r"\d+", texto)
        if match_num:
            return match_num.group(0)

        return texto


    def buscar_por_tombo(df, codigo_busca):
        """
        Busca o tombo na base.
        Prioriza collectionCode, mas aceita barcode se existir.
        """
        codigo_busca = normalizar_codigo(codigo_busca)

        colunas_possiveis = ["collectionCode", "barcode", "catalogNumber"]

        col = None
        for c in colunas_possiveis:
            if c in df.columns:
                col = c
                break

        if col is None:
            st.error(
                "A base não possui coluna de tombo reconhecida. "
                "Esperado: collectionCode, barcode ou catalogNumber."
            )
            return pd.DataFrame(), None

        df = df.copy()
        df[col] = df[col].fillna("").astype(str).str.upper().str.strip()

        result = df[
            df[col].eq(codigo_busca) |
            df[col].str.endswith(codigo_busca) |
            df[col].str.endswith(codigo_busca.zfill(6))
        ]

        return result, col


    def ler_qrcode(uploaded_image):
        """
        Decodifica QR Code a partir da imagem capturada por st.camera_input.
        """
        file_bytes = np.asarray(bytearray(uploaded_image.getvalue()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return None

        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if data:
            return data.strip()

        return None


    def mostrar_dados_amostra(result):
        """
        Exibe os dados principais da amostra encontrada.
        """
        if result.empty:
            st.error("Código não encontrado.")
            return

        first = result.iloc[0]
        
        #sci modificado para retornar somente genus+species
        #sci = first.get("scientificName", "")
        #sci = sci if isinstance(sci, str) and sci.strip() else "Indeterminada"
        genus = first.get("genus", "")
        specific_epithet = first.get("specificEpithet", "")
        
        genus = genus.strip() if isinstance(genus, str) else ""
        specific_epithet = (
            specific_epithet.strip()
            if isinstance(specific_epithet, str)
            else ""
        )
        
        if genus and specific_epithet:
            sci = f"{genus} {specific_epithet}"
        elif genus:
            sci = genus
        else:
            sci = "Indeterminada"
        

        auth = first.get("scientificNameAuthorship", "")
        if not isinstance(auth, str) or not auth.strip():
            auth = ""

        if auth:
            st.markdown(
                f"<div style='font-size: 24px; font-weight: bold;'><i>{sci}</i> {auth}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='font-size: 24px; font-weight: bold;'><i>{sci}</i></div>",
                unsafe_allow_html=True
            )

        fam = first.get("family")
        if pd.notna(fam):
            st.markdown(
                f"<div style='font-size: 18px;'>Família: {fam}</div>",
                unsafe_allow_html=True
            )

        loc = first.get("dynamicProperties")
        if pd.notna(loc):
            st.markdown(
                f"<b>Localização na coleção:</b> {loc}",
                unsafe_allow_html=True
            )

        coll = first.get("recordedBy")
        addcoll = first.get("addCollector")
        number = first.get("recordNumber")

        collected = f"{number or ''}".strip()
        if coll or collected or addcoll:
            st.markdown(
                f"<b>Coletor(s):</b> {coll or ''} <b>nº</b> {collected} <b>&</b> {addcoll or ''}",
                unsafe_allow_html=True
            )

        date_parts = []
        for f in ["dayCollected", "monthCollected", "yearCollected"]:
            val = first.get(f)
            if pd.notna(val):
                try:
                    date_parts.append(str(int(float(val))))
                except Exception:
                    date_parts.append(str(val))

        if date_parts:
            st.markdown(
                f"<b>Data de coleta:</b> {'/'.join(date_parts)}",
                unsafe_allow_html=True
            )

        field_number = first.get("fieldNumber")
        if pd.notna(field_number) and str(field_number).strip():
            st.markdown(
                f"<b>Número interno (bloco):</b> {field_number}",
                unsafe_allow_html=True
            )

        st.dataframe(result, use_container_width=True)

        nome_busca = ""
        if isinstance(sci, str) and sci.strip() and sci != "Indeterminada":
            nome_busca = sci.strip().replace(" ", "+")
        elif isinstance(fam, str) and fam.strip():
            nome_busca = fam.strip().replace(" ", "+")

        st.markdown(
            """
            ### 📤 Pesquisar o nome em bases científicas:
            <div style='display: flex; flex-wrap: wrap; gap: 10px;'>
                <a href='https://www.gbif.org/search?q=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>GBIF</a>
                <a href='https://floradobrasil.jbrj.gov.br/reflora/listaBrasil/ConsultaPublicaUC/BemVindoConsultaPublicaConsultar.do?nomeCompleto=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>Reflora Lista</a>
                <a href='https://floradobrasil.jbrj.gov.br/reflora/herbarioVirtual/ConsultaPublicoHVUC/BemVindoConsultaPublicaHVConsultar.do?nomeCientifico=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>Reflora HV</a>
                <a href='https://www.worldfloraonline.org/search?query=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>World Flora</a>
                <a href='https://powo.science.kew.org/results?q=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>POWO</a>
                <a href='https://www.ipni.org/search?q=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>IPNI</a>
                <a href='https://plants.jstor.org/search?filter=name&so=ps_group_by_genus_species+asc&Query=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>JSTOR Plants</a>
                <a href='https://specieslink.net/search/' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>SpeciesLink</a>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------------------------------
    # Verificar base
    # -------------------------------------------------
    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("⚠️ A base de dados precisa ser carregada na aba **BASE**!")

    else:
        df = st.session_state.df.copy()

        # -------------------------------------------------
        # Busca manual por tombo
        # -------------------------------------------------
        st.subheader("🔎 Busca manual por tombo")

        codigo = st.text_input(
            "Digite o número do tombo",
            value="",
            placeholder="Ex.: HUAM001245 ou somente 1245"
        )

        if st.button("🔍 Buscar por tombo"):
            if not codigo:
                st.warning("Digite o número do tombo antes de buscar.")

            else:
                code = normalizar_codigo(codigo)
                result, col_usada = buscar_por_tombo(df, code)

                if col_usada:
                    st.caption(f"Busca realizada na coluna: {col_usada}")

                st.session_state["last_codigo"] = code
                mostrar_dados_amostra(result)

        st.markdown("---")

        # -------------------------------------------------
        # Busca por número interno / bloco
        # -------------------------------------------------
        st.subheader("🔍 Buscar por número interno")

        num_interno = st.text_input(
            "Digite o número interno (Número de Bloco)",
            value="",
            placeholder="Ex.: 321"
        )

        if st.button("🔍 Buscar por bloco"):
            if "fieldNumber" not in df.columns:
                st.warning("⚠️ Sua base de dados não possui a coluna 'fieldNumber'.")

            else:
                df["fieldNumber"] = df["fieldNumber"].astype(str).str.strip()
                num_interno = num_interno.strip()
                resultado_bloco = df[df["fieldNumber"] == num_interno]

                if not resultado_bloco.empty:
                    st.success(
                        f"{len(resultado_bloco)} amostra(s) encontrada(s) com Número interno '{num_interno}'."
                    )
                    st.dataframe(resultado_bloco, use_container_width=True)
                else:
                    st.warning("Nenhuma amostra encontrada com esse número interno.")
                    
        # -------------------------------------------------
        # Leitura por QR Code
        # -------------------------------------------------
        st.subheader("📷 Ler QR Code")

        st.info(
            "Aponte a câmera para o QR Code da exsicata. "
            "O QR Code deve conter o tombo, por exemplo HUAM001245."
        )

        qr_image = st.camera_input("Capturar QR Code")

        if qr_image is not None:
            qr_text = ler_qrcode(qr_image)

            if qr_text:
                codigo_lido = normalizar_codigo(qr_text)

                st.success(f"QR Code lido: {qr_text}")
                st.info(f"Código interpretado para busca: {codigo_lido}")

                result, col_usada = buscar_por_tombo(df, codigo_lido)

                if col_usada:
                    st.caption(f"Busca realizada na coluna: {col_usada}")

                st.session_state["last_codigo"] = codigo_lido
                mostrar_dados_amostra(result)

            else:
                st.warning(
                    "Não foi possível ler o QR Code. "
                    "Tente aproximar a câmera, melhorar a iluminação ou centralizar melhor o código."
                )

        st.markdown("---")

# -----------------------------------------------
# Image Lookup + Pl@ntNet
# -----------------------------------------------
elif selected == "Imagem":
    st.subheader("📷 Buscar Imagem")
    st.write(
        "Busque imagens das amostras do HUAM vinculadas à base de dados e utilize o serviço "
        "**Pl@ntNet** para realizar sugestões automáticas de identificação botânica. "
        "Informe o número do tombo para visualizar a imagem da exsicata e receber a lista de espécies prováveis."
    )

    # -------------------------------------------------
    # Configurações gerais
    # -------------------------------------------------
    DRIVE_TIMEOUT = (10, 30)
    PLANTNET_TIMEOUT = (10, 60)
    MAX_TENTATIVAS = 3
    PLANTNET_PROJECT = "all"
    PLANTNET_URL = f"https://my-api.plantnet.org/v2/identify/{PLANTNET_PROJECT}"

    # -------------------------------------------------
    # Carregar base
    # -------------------------------------------------
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Image", ttl="10m")

    df = df[~df["Subpasta"].astype(str).str.contains("Fotos exsicatas Mike", na=False)]

    # -------------------------------------------------
    # Funções auxiliares
    # -------------------------------------------------
    def redigir_api_key(texto):
        """
        Remove a API key de qualquer mensagem de erro antes de exibir na interface.
        """
        if texto is None:
            return ""

        texto = str(texto)
        texto = re.sub(r"(api-key=)[^&\s]+", r"\1[REMOVIDA]", texto)
        texto = re.sub(r'("api-key"\s*:\s*")[^"]+(")', r'\1[REMOVIDA]\2', texto)
        return texto


    def drive_link_to_file_id(link):
        """
        Extrai o file_id de um link do Google Drive.
        Aceita links no formato /file/d/ID/view, /d/ID ou URLs com ?id=.
        """
        if not isinstance(link, str):
            return None

        try:
            if "/d/" in link:
                return link.split("/d/")[1].split("/")[0]

            if "id=" in link:
                return link.split("id=")[1].split("&")[0]

        except Exception:
            return None

        return None


    def download_drive_image(file_id):
        """
        Faz download da imagem do Google Drive com timeout explícito.
        """
        url = f"https://drive.google.com/uc?export=view&id={file_id}"

        try:
            response = requests.get(url, timeout=DRIVE_TIMEOUT)

        except requests.exceptions.Timeout:
            raise RuntimeError("Timeout ao baixar a imagem do Google Drive.")

        except requests.exceptions.RequestException:
            raise RuntimeError("Erro de rede ao acessar o Google Drive.")

        if response.status_code != 200:
            raise RuntimeError(
                f"Não foi possível carregar a imagem do Drive. Status HTTP: {response.status_code}"
            )

        content_type = response.headers.get("Content-Type", "")

        if "image" not in content_type.lower():
            raise RuntimeError(
                "O link do Google Drive não retornou uma imagem válida. "
                "Verifique se o arquivo está compartilhado publicamente ou acessível pelo app."
            )

        return response.content


    def preparar_imagem_para_plantnet(image_bytes, max_size_mb=45):
        """
        Abre a imagem, corrige orientação EXIF, converte para RGB e gera JPEG.
        Mantém margem de segurança abaixo do limite de 50 MB aceito pelo Pl@ntNet.
        """
        try:
            img = Image.open(BytesIO(image_bytes))
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")

        except Exception:
            raise RuntimeError("Erro ao abrir ou converter a imagem.")

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90, optimize=True)
        prepared_bytes = buffer.getvalue()

        max_size_bytes = max_size_mb * 1024 * 1024

        if len(prepared_bytes) > max_size_bytes:
            img.thumbnail((2500, 2500))
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            prepared_bytes = buffer.getvalue()

        if len(prepared_bytes) > 50 * 1024 * 1024:
            raise RuntimeError("A imagem excede 50 MB, limite máximo aceito pelo Pl@ntNet.")

        return img, prepared_bytes


    def identificar_com_plantnet(image_bytes, organ="auto"):       
        try:
            API_KEY = st.secrets["plantnet"]["api_key"]
        except KeyError:
            raise RuntimeError("API key do Pl@ntNet não encontrada em st.secrets.")

        params = {
            "api-key": API_KEY,
            "nb-results": 5,
            "lang": "en"
        }

        data = None
        if organ and organ != "auto":
            data = {
                "organs": [organ]
            }

        ultimo_erro_tipo = None

        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                # Recriar BytesIO e files a cada tentativa.
                # Isso evita que o arquivo seja reenviado vazio após uma falha.
                files = [
                    ("images", ("image.jpg", BytesIO(image_bytes), "image/jpeg"))
                ]

                response = requests.post(
                    PLANTNET_URL,
                    params=params,
                    files=files,
                    data=data,
                    timeout=PLANTNET_TIMEOUT
                )

                return response

            except requests.exceptions.ConnectTimeout:
                ultimo_erro_tipo = "ConnectTimeout"
                st.warning(f"Tentativa {tentativa}: timeout de conexão com o Pl@ntNet.")

            except requests.exceptions.ReadTimeout:
                ultimo_erro_tipo = "ReadTimeout"
                st.warning(f"Tentativa {tentativa}: o Pl@ntNet conectou, mas demorou para responder.")

            except requests.exceptions.ConnectionError:
                ultimo_erro_tipo = "ConnectionError"
                st.warning(f"Tentativa {tentativa}: erro de conexão com o Pl@ntNet.")

            except requests.exceptions.RequestException:
                ultimo_erro_tipo = "RequestException"
                st.warning(f"Tentativa {tentativa}: falha na requisição ao Pl@ntNet.")

            time.sleep(3 * tentativa)

        raise RuntimeError(
            f"Não foi possível conectar ao Pl@ntNet após {MAX_TENTATIVAS} tentativas. "
            f"Tipo do último erro: {ultimo_erro_tipo}."
        )


    def mostrar_resultados_plantnet(response):
        """
        Exibe os resultados retornados pela API Pl@ntNet.
        """
        if response.status_code != 200:
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text

            error_detail = redigir_api_key(error_detail)

            st.error(f"Erro na API Pl@ntNet: {response.status_code}")
            with st.expander("Detalhes técnicos"):
                st.write(error_detail)

            return

        resultado_json = response.json()
        results = resultado_json.get("results", [])

        best_match = resultado_json.get("bestMatch")
        predicted_organs = resultado_json.get("predictedOrgans", [])
        version = resultado_json.get("version")
        remaining = resultado_json.get("remainingIdentificationRequests")

        if best_match:
            st.write(f"**Melhor correspondência:** *{best_match}*")

        if predicted_organs:
            organ_pred = predicted_organs[0].get("organ")
            organ_score = predicted_organs[0].get("score")

            if organ_pred is not None and organ_score is not None:
                st.write(f"**Órgão detectado:** {organ_pred} ({organ_score:.2%})")
            elif organ_pred is not None:
                st.write(f"**Órgão detectado:** {organ_pred}")

        if version:
            st.caption(f"Versão do motor Pl@ntNet: {version}")

        if remaining is not None:
            st.caption(f"Requisições restantes hoje: {remaining}")

        if not results:
            st.info("Nenhuma correspondência encontrada.")
            return

        st.subheader("Resultados da identificação com a API do Pl@ntNet")

        for res in results:
            species_data = res.get("species", {})
            family_data = species_data.get("family", {})

            species_name = species_data.get("scientificName", "Nome não disponível")
            species_name_without_author = species_data.get(
                "scientificNameWithoutAuthor",
                "Nome não disponível"
            )
            family_name = family_data.get("scientificNameWithoutAuthor", "Família não disponível")
            score = res.get("score", 0)

            nome_busca = species_name_without_author.strip().replace(" ", "+")

            st.write(
                f"- **{species_name}** — {family_name} — Confiança: {score:.2%} | "
                f"[Conferir táxon no GBIF](https://www.gbif.org/search?q={nome_busca})"
            )


    def mostrar_logo_plantnet():
        """
        Exibe o logo de atribuição do Pl@ntNet ao final da página.
        Coloque o arquivo powered-by-plantnet.png na mesma pasta do app.py
        ou dentro de uma pasta assets/.
        """
        st.divider()

        caminhos_possiveis = [
            "powered-by-plantnet.png",
            "assets/powered-by-plantnet.png",
            "images/powered-by-plantnet.png"
        ]

        logo_path = None

        for caminho in caminhos_possiveis:
            if os.path.exists(caminho):
                logo_path = caminho
                break

        if logo_path:
            col_logo, _ = st.columns([1, 4])
            with col_logo:
                st.image(logo_path, width=180)
        else:
            st.caption("Powered by Pl@ntNet")


    # -------------------------------------------------
    # Busca por tombo
    # -------------------------------------------------
    st.subheader("🔍 Busca por Tombo")

    codigo = st.text_input(
        "Digite o número do tombo",
        value="",
        placeholder="Ex.: HUAM001245 ou somente 1245",
        key="tombo_input"
    )

    organ_option = st.selectbox(
        "Órgão vegetal para envio ao Pl@ntNet",
        options=["auto", "leaf", "flower", "fruit", "bark"],
        index=0,
        help=(
            "Use 'auto' para exsicata inteira. Use 'leaf', 'flower', 'fruit' ou 'bark' "
            "quando a imagem estiver claramente recortada para esse órgão."
        )
    )

    if st.button("🔍 Buscar por Tombo", key="buscar_tombo", use_container_width=True):
        if not codigo:
            st.warning("Digite um número de tombo para buscar.")

        else:
            col_codigo = "barcode"
            df[col_codigo] = df[col_codigo].astype(str).str.upper()
            codigo_busca = codigo.strip().upper()

            resultado = df[
                df[col_codigo].eq(codigo_busca) |
                df[col_codigo].str.endswith(codigo_busca) |
                df[col_codigo].str.endswith(codigo_busca.zfill(6))
            ]

            if resultado.empty:
                st.session_state.result_image = None
                st.warning(f"Nenhuma exsicata encontrada para o tombo: {codigo_busca}")

            else:
                st.session_state.result_image = resultado
                st.success(f"{len(resultado)} resultado(s) encontrado(s):")

                for _, row in st.session_state.result_image.iterrows():
                    file_id = drive_link_to_file_id(row.get("UrlExsicata"))

                    if not file_id:
                        st.warning("Link do Drive inválido.")
                        continue

                    try:
                        image_raw_bytes = download_drive_image(file_id)
                        img, image_prepared_bytes = preparar_imagem_para_plantnet(image_raw_bytes)

                    except Exception as e:
                        st.error(f"Erro ao carregar/preparar a imagem: {redigir_api_key(e)}")
                        continue

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.subheader("Imagem da Exsicata")
                        st.image(
                            img,
                            caption=row.get("ArchiveName", "Imagem da exsicata"),
                            use_container_width=True
                        )

                    with col2:
                        st.subheader("Informações da Amostra")
                        st.write(f"**Tombo:** {row.get('barcode', 'Não informado')}")
                        st.write(f"**Arquivo:** {row.get('ArchiveName', 'Não informado')}")

                        if "family" in row.index and pd.notna(row.get("family")):
                            st.write(f"**Família:** {row.get('family')}")

                        if "scientificName" in row.index and pd.notna(row.get("scientificName")):
                            st.write(f"**Nome:** *{row.get('scientificName')}*")

                        st.write(f"**URL:** [Abrir imagem original]({row.get('UrlExsicata')})")

                    st.info("Enviando para Pl@ntNet...")

                    try:
                        plantnet_response = identificar_com_plantnet(
                            image_prepared_bytes,
                            organ=organ_option
                        )

                        mostrar_resultados_plantnet(plantnet_response)

                    except Exception as e:
                        st.error(f"Erro ao conectar/processar a resposta do Pl@ntNet: {redigir_api_key(e)}")


    # -------------------------------------------------
    # Busca por táxon
    # -------------------------------------------------
    st.subheader("🌿 Busca por Táxon")

    taxon_input = st.text_input(
        "Digite o nome da família ou espécie",
        placeholder="Ex.: Fabaceae ou Mimosa pudica",
        key="taxon_input"
    )

    if st.button("Buscar por Táxon", key="buscar_taxon", use_container_width=True):
        if not taxon_input:
            st.warning("Digite um nome de família ou espécie para buscar.")

        else:
            taxon_busca = taxon_input.strip().upper()

            resultado_taxon = df[
                (df["family"].astype(str).str.upper() == taxon_busca) |
                (df["scientificName"].astype(str).str.upper() == taxon_busca) |
                (df["family"].astype(str).str.upper().str.contains(taxon_busca, na=False)) |
                (df["scientificName"].astype(str).str.upper().str.contains(taxon_busca, na=False))
            ]

            if resultado_taxon.empty:
                st.warning(f"Nenhuma imagem encontrada para o táxon: {taxon_input}")

            else:
                st.success(f"{len(resultado_taxon)} imagem(ns) encontrada(s) para o táxon: {taxon_input}")

                st.subheader("Dados do Táxon")

                col_stat1, col_stat2 = st.columns(2)

                with col_stat1:
                    especies_unicas = resultado_taxon["scientificName"].nunique()
                    st.metric("Nomes diferentes", especies_unicas)

                with col_stat2:
                    st.metric("Total de imagens", len(resultado_taxon))

                if especies_unicas > 0:
                    st.write("**Nomes encontrados:**")
                    especies_lista = resultado_taxon["scientificName"].dropna().unique()
                    especies_texto = ""

                    for especie in sorted(especies_lista):
                        especies_texto += f"• {especie}\n"

                    st.text(especies_texto)

                st.subheader("Galeria de Imagens")

                items = list(resultado_taxon.iterrows())

                for i in range(0, len(items), 4):
                    cols = st.columns(4)

                    for j in range(4):
                        if i + j >= len(items):
                            continue

                        _, row = items[i + j]
                        file_id = drive_link_to_file_id(row.get("UrlExsicata"))

                        with cols[j]:
                            if not file_id:
                                st.warning("Link inválido")
                                continue

                            try:
                                image_raw_bytes = download_drive_image(file_id)
                                img, _ = preparar_imagem_para_plantnet(image_raw_bytes)

                                st.image(
                                    img,
                                    caption=f"{row.get('barcode', '')}",
                                    use_container_width=True
                                )

                                st.caption(f"**{row.get('barcode', '')}**")

                                if pd.notna(row.get("family")):
                                    st.caption(f"Fam: {row.get('family')}")

                                if pd.notna(row.get("scientificName")):
                                    st.caption(f"*{row.get('scientificName')}*")

                                st.markdown(
                                    f"[Abrir original]({row.get('UrlExsicata')})",
                                    unsafe_allow_html=True
                                )

                            except Exception:
                                st.error("Erro ao carregar imagem")

    # -------------------------------------------------
    # Atribuição Pl@ntNet
    # -------------------------------------------------
    mostrar_logo_plantnet()
