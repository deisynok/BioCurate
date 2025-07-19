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
# Last updated: 2025-07-15
# -----------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import cv2
from streamlit_gsheets import GSheetsConnection
import requests
from io import BytesIO
from PIL import Image
from streamlit_option_menu import option_menu
import plotly.express as px


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
    st.session_state.barcode_col = 'CollectionCode'
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

            - **CollectionCode:** Código único da coleção (número do tombo HUAM).
            - **CatalogNumber:** Número de catálogo interno da amostra.
            - **Collector:** Nome do coletor principal responsável pela amostra.
            - **Addcoll:** Coletores adicionais envolvidos na coleta.
            - **CollectorNumberPrefix:** Prefixo que antecede o número de coleta (quando houver).
            - **CollectorNumber:** Número atribuído pelo coletor à amostra.
            - **CollectorNumberSuffix:** Sufixo complementar ao número de coleta (quando houver).
            - **DayCollected / MonthCollected / YearCollected:** Datas exatas de coleta da amostra.
            - **Family:** Família botânica a que pertence a amostra.
            - **ScientificName:** Nome científico completo (gênero + espécie + infraespécie, se aplicável).
            - **Genus:** Nome do gênero botânico.
            - **Species:** Epíteto específico (nome da espécie).
            - **ScientificNameAuthor:** Autoridade taxonômica que descreveu o táxon.
            - **StorageLocation:** Localização física da amostra na coleção (ex.: armário, prateleira).

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
            contagem_familias = df["Family"].value_counts().sort_values(ascending=True)
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
                df_fam = df[df["Family"].str.upper() == familia.upper()]
                num_material = len(df_fam)
                generos = df_fam["Genus"].dropna().unique()
                especies = df_fam["ScientificName"].dropna().unique()
                locs = df_fam["StorageLocation"].dropna().unique()

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
                df_gen = df[df["Genus"].str.upper() == genero.upper()]
                total_amostras = len(df_gen)
                so_genero = df_gen[df_gen["ScientificName"].isna() | (df_gen["ScientificName"].str.strip() == "")]
                especies_por_genero = df_gen["ScientificName"].dropna().unique()
                locs = df_gen["StorageLocation"].dropna().unique()
                familias = df_gen["Family"].dropna().unique()

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
                df_esp = df[df["ScientificName"].str.upper() == especie.upper()]
                total_especie = len(df_esp)
                locs = df_esp["StorageLocation"].dropna().unique()
                familias = df_esp["Family"].dropna().unique()

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
    st.write("Consulte informações detalhadas das amostras a partir do número de tombo. Digite o código para visualizar dados taxonômicos, local de armazenamento, coletores e outras informações relevantes.")
    
    # Load the database
    if st.session_state.df is None:
        st.warning("⚠️ A base de dados precisa ser carregada na aba **BASE**!")	
    else:
        df = st.session_state.df.copy()

    # Manual input of the code
    code = ""
    codigo = st.text_input(
        "Digite o número do tombo",
        value=code,
        placeholder="Ex.: HUAM001245 ou somente 1245"
    )

    # Lookup button
    if st.button("🔍 Buscar por tombo"):
        df = st.session_state.df.copy()
        col = 'CollectionCode'
        st.session_state.barcode_col = col
        code = codigo.strip().upper()
        df[col] = df[col].astype(str).str.upper()
        result = df[
            df[col].str.upper().eq(code) |
            df[col].str.endswith(code.zfill(6))
        ]

        # Save the specimen code to the session
        st.session_state["last_codigo"] = code

        if not result.empty:
            first = result.iloc[0]

            # Scientific name and author (with fallback)
            sci = first.get("ScientificName", "")
            sci = sci if isinstance(sci, str) and sci.strip() else "Indeterminada"

            auth = first.get("ScientificNameAuthor", "")
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

            # Family
            fam = first.get("Family")
            if pd.notna(fam):
                st.markdown(
                    f"<div style='font-size: 18px;'>Família: {fam}</div>",
                    unsafe_allow_html=True
                )

            # Storage Location
            loc = first.get("StorageLocation")
            if pd.notna(loc):
                st.markdown(
                    f"<b>Localização na coleção:</b> {loc}",
                    unsafe_allow_html=True
                )

            # Collector and collection number
            coll = first.get("Collector")
            addcoll = first.get("Addcoll")
            number = first.get("CollectorNumber")
                
            collected = f"{number or ''}".strip()
            if coll or collected:
                st.markdown(
                    f"<b>Coletor(s):</b> {coll or ''} <b>nº</b> {collected} <b>&</b> {addcoll or ''}",
                    unsafe_allow_html=True
                )

            # Collection date
            date_parts = []
            for f in ["DayCollected", "MonthCollected", "YearCollected"]:
                val = first.get(f)
                if pd.notna(val):
                    date_parts.append(str(int(val)))
            if date_parts:
                st.markdown(
                    f"<b>Data de coleta:</b> {'/'.join(date_parts)}",
                    unsafe_allow_html=True
                )
            
            # Internal Number (FieldNumber)
            field_number = first.get("FieldNumber")
            if pd.notna(field_number) and str(field_number).strip():
                st.markdown(
                    f"<b>Número interno (bloco):</b> {field_number}",
                    unsafe_allow_html=True
                )

            # View full dataset entry
            st.dataframe(result, use_container_width=True)       
            
            # External search by scientific name or family
            nome_busca = ""
            if isinstance(sci, str) and sci.strip():
                nome_busca = sci.strip().replace(" ", "+")
            elif isinstance(fam, str) and fam.strip():
                nome_busca = fam.strip().replace(" ", "+")

            st.markdown("""
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
            """, unsafe_allow_html=True)
                                    
        else:
            st.error("Código não encontrado.")
        
    st.markdown("---")

     # Entry for FieldNumber
    num_interno = st.text_input(
        "Digite o número interno (Número de Bloco)",
        value="",
        placeholder="Ex.: 321"
    )

    # Search Button
    if st.button("🔍 Buscar por bloco"):
        df = st.session_state.df.copy()

        if "FieldNumber" not in df.columns:
            st.warning("⚠️ Sua base de dados não possui a coluna 'FieldNumber'.")
        else:
            df["FieldNumber"] = df["FieldNumber"].astype(str).str.strip()
            num_interno = num_interno.strip()
            resultado_bloco = df[df["FieldNumber"] == num_interno]

            if not resultado_bloco.empty:
                st.success(f"{len(resultado_bloco)} amostra(s) encontrada(s) com Número interno '{num_interno}'.")
                st.dataframe(resultado_bloco, use_container_width=True)
            else:
                st.warning("Nenhuma amostra encontrada com esse número interno.")              

# -----------------------------------------------
# Image Lookup + Pl@ntNet
# -----------------------------------------------
elif selected == "Imagem":
    st.subheader("📷 Buscar Imagem")
    st.write(
        "Busque imagens das amostras do HUAM vinculadas à da base de dados e utilizar o serviço **Pl@ntNet** para realizar a identificação automática da espécie. "
        "Basta informar o número do tombo para visualizar a imagem da exsicata e receber sugestões de identificação botânica."
    )
    
    # Load the database
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Image", ttl="10m")
    
    def drive_link_to_direct(link):
        try:
            parts = link.split("/d/")
            if len(parts) > 1:
                file_id = parts[1].split("/")[0]
                return file_id
        except Exception:
            pass
        return None

    # Manual input of the code
    code = ""
    codigo = st.text_input(
        "Digite o número do tombo",
        value=code,
        placeholder="Ex.: HUAM001245 ou somente 1245"
    )
    
    # Search and Identify (Pl@ntNet)
    if st.button("🔍 Buscar imagens e Identificar"):
        col_codigo = 'barcode'
        df[col_codigo] = df[col_codigo].astype(str).str.upper()
        codigo = codigo.strip().upper()

        resultado = df[
            df[col_codigo].eq(codigo) |
            df[col_codigo].str.endswith(codigo) |
            df[col_codigo].str.endswith(codigo.zfill(6))
        ]

        if resultado.empty:
            st.session_state.result_image = None
            st.warning(f"Nenhuma exsicata encontrada para o tombo: {codigo}")
            
        else: 
            st.session_state.result_image = resultado
            st.success(f"{len(resultado)} resultado(s) encontrado(s):")
            
            # Show the image result, if available
            if 'result_image' in st.session_state and st.session_state.result_image is not None:
                for _, row in st.session_state.result_image.iterrows():
                    file_id = drive_link_to_direct(row['UrlExsicata'])
                    
                    if file_id:
                        url = f"https://drive.google.com/uc?export=view&id={file_id}"
                        response = requests.get(url)

                        if response.status_code == 200:
                            content_type = response.headers.get('Content-Type', '')
                            
                            if 'image' in content_type:
                                try:
                                    from PIL import Image
                                    import io

                                    img = Image.open(io.BytesIO(response.content))
                                    #img = img.rotate(-90, expand=True)
                                    st.image(img, caption=row['ArchiveName'])

                                    # Send to Pl@ntNet
                                    API_KEY = st.secrets["plantnet"]["api_key"]
                                    PLANTNET_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"

                                    files = {
                                        "images": ('image.jpg', BytesIO(response.content), 'image/jpeg'),
                                        "organs": (None, 'leaf')
                                    }

                                    st.info("Enviando para Pl@ntNet...")
                                    r = requests.post(PLANTNET_URL, files=files)

                                    if r.status_code == 200:
                                        results = r.json().get("results", [])
                                        if not results:
                                            st.info("Nenhuma correspondência encontrada.")
                                        else:
                                            st.subheader("Resultados da identificação com a API do Pl@ntnet")
                                            for res in results:
                                                species = res['species']['scientificNameWithoutAuthor']
                                                score = res['score']
                                                nome_busca = species.strip().replace(" ", "+")
                                                st.write(
                                                    f"- **{species}** — Confiança: {score:.2%} | "
                                                    f"[Ver resultados desse taxon no GBIF](https://www.gbif.org/search?q={nome_busca})"
                                                 )
                                            
                                    else:
                                        st.error(f"Erro na API Pl@ntNet: {r.status_code}")

                                except Exception as e:
                                    st.error(f"Erro ao abrir/processar a imagem: {e}")

                            else:
                                st.warning("O link não retornou uma imagem válida. Verifique o compartilhamento.")
                        else:
                            st.warning("Não foi possível carregar a imagem do Drive.")
                    else:
                        st.warning("Link do Drive inválido.")