# -----------------------------------------------
# 📚 BioCurate - Consulta e Identificação de Amostras Botânicas
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


# -----------------------------------------------
# 🚩 Configuração Geral
# -----------------------------------------------

st.set_page_config(page_title="BioCurate",  
    page_icon="favicon.png",
    layout="centered"
    )

# Variáveis de sessão
if 'df' not in st.session_state:
    st.session_state.df = None
if 'barcode_col' not in st.session_state:
    st.session_state.barcode_col = 'CollectionCode'
if 'img_folder' not in st.session_state:
    st.session_state.img_folder = ''


# -----------------------------------------------
# Menu HORIZONTAL RESPONSIVO
# -----------------------------------------------
# ✅ Cria o navbar horizontal
selected = option_menu(
    None,
    ["Início", "Base de Dados", "Relatório", "Buscar Dados", "Buscar Imagem"],
    icons=["house", "database", "bar-chart", "search", "image"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
    "container": {
        "padding": "0!important",
        "background-color": "#00A8A8"  # Azul esverdeado da lateral da logo
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
        "--hover-color": "#B2DFDB"  # Hover verde-água suave
    },
    "nav-link-selected": {
        "background-color": "#388E3C"  # Verde escuro harmônico
    },
},
)

# -----------------------------------------------
# 🏠 Página: Início
# -----------------------------------------------
if selected == "Início":
    col1, col2 = st.columns([1,2])
    with col1:
        st.image("logo.png", width=200)
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>Bem-vindo ao BioCurate</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        Ferramenta para consulta de amostras por código de barras. 
        O BioCurate foi desenvolvido para facilitar o acesso, a curadoria e o uso de dados de coleções biológicas, especialmente em herbários. 
        Ele permite que você busque informações rapidamente a partir de códigos de barras, visualize dados completos das amostras, 
        acesse imagens vinculadas (caso estejam disponíveis) e faça buscas externas em bases como GBIF, Reflora e SpeciesLink.
        Uso não comercial, apenas para fins de pesquisa científica.
    """)
    
    st.markdown("""
        ### Instruções:

        1. **📦 Base de Dados**  
        Use esta aba para carregar automaticamente os **Metadados** (vinculada à planilha oficial do HUAM - https://docs.google.com/spreadsheets/d/1Pf9Vig397BEESIo7dR9dXnBQ-B4RneIc_I3DG6vTMYw) ou enviar sua própria base de dados no formato CSV, organizada no padrão **Darwin Core**. A base importada será utilizada em todas as buscas.

        2. **📊 Relatório**
        Nesta aba, você pode gerar relatórios detalhados a partir dos dados cadastrados na base do HUAM. É possível consultar por **família**, **gênero** ou **espécie**, obtendo informações como o número total de amostras, lista de gêneros e espécies relacionadas e os registros completos encontrados. Os relatórios são úteis para análise, organização e planejamento de curadoria do acervo.
        
        3. **📋 Buscar Dados**  
        Nesta aba, você pode consultar informações detalhadas de cada amostra da base. A busca pode ser feita digitando o **número do tombo** ou capturando o **código de barras** com a câmera do dispositivo. O sistema exibe informações taxonômicas, local de armazenamento e dados de coleta.

        4. **📷 Buscar Imagem**  
        Esta aba permite buscar da imagem de uma amostra específica e enviar automaticamente a imagem vinculada para o serviço **Pl@ntNet**. Assim, você pode realizar uma **identificação automatizada da espécie**, recebendo uma lista de prováveis correspondências com nível de confiança.
        **Observação:** O cruzamento de dados e imagens funciona exclusivamente para amostras do HUAM, pois está vinculado ao Google Drive institucional, onde estão armazenadas as fotos oficiais do acervo.
        
       
    """)
       
    st.markdown("""
        ### Sobre o BioCurate
        O **BioCurate** oferece uma forma rápida e eficiente de cruzar informações da base de dados de coleções científicas por meio da leitura de códigos de barras ou entrada manual.

        Ele melhora a acessibilidade e a precisão na gestão de coleções biológicas, facilitando a organização e a utilização de dados.

        Este projeto é uma iniciativa do **Herbário da Universidade Federal do Amazonas (HUAM)** e faz parte da pesquisa de doutorado de **Deisy Saraiva**, vinculada ao **Programa de Pós-Graduação BIONORTE – Rede de Biodiversidade e Biotecnologia da Amazônia Legal**. A pesquisa foca no uso de tecnologias para ampliar o acesso e a curadoria das coleções do HUAM.

        Contato: deisysaraiva@ufam.edu.br

        - [Acesse o site do HUAM](http://huam.site)
        - [A Coleção no site institucional da UFAM](https://www.icb.ufam.edu.br/colecoes/huam.html)

        ---

        ### Sobre a Identificação Automática com Pl@ntNet

        **BioCurate** também integra a tecnologia de identificação automática de espécies por imagens através da **API Pl@ntNet**, reconhecida internacionalmente.  
        Para mais informações, acesse [Pl@ntNet](https://plantnet.org/).
        
        **Aviso:** A identificação automática é realizada utilizando a [API Pl@ntNet](https://plantnet.org/). Os resultados são gerados por um sistema de aprendizado de máquina e devem ser conferidos por um especialista.
    
        ---

        ### Sobre o padrão Darwin Core

        O **Darwin Core** é um padrão internacional para compartilhamento de dados sobre biodiversidade. Ele define termos recomendados que garantem consistência e interoperabilidade entre bases de dados.

        - [Repositório Darwin Core](https://github.com/tdwg/dwc)
        - [Padrão Darwin Core](https://dwc.tdwg.org/terms)
        - [Modelo de Cabeçalho Darwin Core](https://splink.cria.org.br/digir/darwin2.xsd)

        - [Vídeo explicativo (YouTube)](https://www.youtube.com/embed/YC0DfctXs5Q)
    """)

# -----------------------------------------------
# 📦 Página: Base de Dados
# -----------------------------------------------
elif selected == "Base de Dados":
    st.title("📦 Base de Dados")
    st.subheader("Base de Dados HUAM: Conexão automática")

    # Conexão automática com a planilha do HUAM
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_base = conn.read(worksheet="Metadata", ttl="10m")

    st.session_state.df = df_base
    st.success("Metadata da BaseHUAM carregada automaticamente.")
    st.write(df_base.head())

    # Opção para sobrescrever com upload CSV
    st.subheader("Ou envie sua própria base em formato DarwinCore")
    file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
    if file:
        df_user = pd.read_csv(file)
        st.session_state.df = df_user
        st.success("Arquivo CSV carregado! Base atualizada.")
        st.write(df_user.head())

# -----------------------------------------------
# 📊 Página: Relatório
# -----------------------------------------------
elif selected == "Relatório":
    st.title("📊 Relatório de Dados")
    st.write(
        "Nesta página, você pode gerar relatórios detalhados a partir das amostras do HUAM. "
        "Informe o nome da família, gênero ou espécie e clique em **Buscar** para obter estatísticas como quantidade de amostras, "
        "lista de gêneros ou espécies relacionadas, e visualizar os registros completos presentes na base de dados."
    )

    if st.session_state.df is None:
        st.warning("⚠️ A base de dados precisa ser carregada na aba **Base de Dados**.")
    else:
        df = st.session_state.df.copy()

        # RELATÓRIO POR FAMÍLIA
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
                    st.markdown(f"<b>📦 Armário(s):</b> <span style='color:gold;'>{', '.join(sorted(locs))}</span>", unsafe_allow_html=True)

                st.info(f"**Total de amostras:** {num_material}")
                st.info(f"**Total de gêneros:** {len(generos)}")
                st.write("**Gêneros encontrados:**")
                st.write(", ".join(sorted(generos)))

                st.info(f"**Total de espécies:** {len(especies)}")
                st.write("**Espécies encontradas:**")
                st.write(", ".join(sorted(especies)))
            else:
                st.warning("Digite o nome da família antes de buscar.")

        # RELATÓRIO POR GÊNERO
        st.subheader("Consultar por Gênero")
        genero = st.text_input("Digite o nome do gênero:")
        if st.button("🔍 Buscar Gênero"):
            if genero:
                df_gen = df[df["Genus"].str.upper() == genero.upper()]
                total_amostras = len(df_gen)
                so_genero = df_gen[df_gen["ScientificName"].isna() | (df_gen["ScientificName"].str.strip() == "")]
                num_so_genero = len(so_genero)
                especies_por_genero = df_gen["ScientificName"].dropna().unique()
                locs = df_gen["StorageLocation"].dropna().unique()

                if len(locs) > 0:
                    st.markdown(f"<b>📦 Armário(s):</b> <span style='color:gold;'>{', '.join(sorted(locs))}</span>", unsafe_allow_html=True)

                st.info(f"**Amostras do gênero:** {total_amostras}")
                st.info(f"**Apenas identificadas até gênero:** {num_so_genero}")
                st.info(f"**Espécies dentro do gênero:** {len(especies_por_genero)}")
                st.write("**Espécies encontradas:**")
                st.write(", ".join(sorted(especies_por_genero)))
            else:
                st.warning("Digite o nome do gênero antes de buscar.")

        # RELATÓRIO POR ESPÉCIE
        st.subheader("Consultar por Espécie")
        especie = st.text_input("Digite o nome científico da espécie:")
        if st.button("🔍 Buscar Espécie"):
            if especie:
                df_esp = df[df["ScientificName"].str.upper() == especie.upper()]
                total_especie = len(df_esp)
                locs = df_esp["StorageLocation"].dropna().unique()

                if len(locs) > 0:
                    st.markdown(f"<b>📦 Armário(s):</b> <span style='color:gold;'>{', '.join(sorted(locs))}</span>", unsafe_allow_html=True)

                st.info(f"**Total de amostras da espécie:** {total_especie}")

                if total_especie > 0:
                    st.write("**Detalhe das amostras encontradas:**")
                    st.dataframe(df_esp, use_container_width=True)
                else:
                    st.warning("Nenhuma amostra encontrada para essa espécie.")
            else:
                st.warning("Digite o nome da espécie antes de buscar.")
# -----------------------------------------------
# 📋 Página: Buscar Dados
# -----------------------------------------------
elif selected == "Buscar Dados":
    st.title("📋 Buscar Dados")
    st.write("Nesta página, você pode consultar informações detalhadas das amostras "
        "a partir do número de tombo. Digite ou escaneie o código para visualizar "
        "dados taxonômicos, local de armazenamento, coletores e outras informações relevantes.")
    if st.session_state.df is None:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_base = conn.read(worksheet="Metadata", ttl="10m")
        st.session_state.df = df_base
        st.success("Metadata da BaseHUAM carregada automaticamente.")
    
    #st.subheader("Buscar Amostra")
    
    # Entrada manual
    code = ""
    code = st.text_input("Digite o código:", value=code)

    # Botão de busca
    if st.button("🔍 Buscar"):
        df = st.session_state.df.copy()
        col = 'CollectionCode'
        st.session_state.barcode_col = col
        code = code.strip().upper()
        df[col] = df[col].astype(str).str.upper()
        result = df[
            df[col].str.upper().eq(code) |
            df[col].str.endswith(code.zfill(6))
        ]

        # Aqui salva o tombo na sessão!
        st.session_state["last_codigo"] = code

        if not result.empty:
            first = result.iloc[0]

            # Nome científico + autor, com fallback
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

            # Família
            fam = first.get("Family")
            if pd.notna(fam):
                st.markdown(
                    f"<div style='font-size: 18px;'>Família: {fam}</div>",
                    unsafe_allow_html=True
                )

            # Local de armazenamento
            loc = first.get("StorageLocation")
            if pd.notna(loc):
                st.markdown(
                    f"<b>Localização na coleção:</b> {loc}",
                    unsafe_allow_html=True
                )

            # Coletor + número de coleta
            coll = first.get("Collector")
            addcoll = first.get("Addcoll")
            number = first.get("CollectorNumber")
                
            collected = f"{number or ''}".strip()
            if coll or collected:
                st.markdown(
                    f"<b>Coletor:</b> {coll or ''} {addcoll or ''} — Nº {collected}",
                    unsafe_allow_html=True
                )

            # Data de coleta
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
            
            # Exibir linha completa da base
            st.dataframe(result, use_container_width=True)       
            
            # Busca externa pelo nome científico ou família
            nome_busca = ""
            if isinstance(sci, str) and sci.strip():
                nome_busca = sci.strip().replace(" ", "+")
            elif isinstance(fam, str) and fam.strip():
                nome_busca = fam.strip().replace(" ", "+")

            st.markdown("""
            ### 📤 Pesquisar o nome em bases científicas:
            <div style='display: flex; flex-wrap: wrap; gap: 10px;'>
                <a href='https://specieslink.net/search/' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>SpeciesLink</a>
                <a href='https://www.gbif.org/search?q=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>GBIF</a>
                <a href='https://floradobrasil.jbrj.gov.br/reflora/listaBrasil/ConsultaPublicaUC/BemVindoConsultaPublicaConsultar.do?nomeCompleto=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>Reflora Lista</a>
                <a href='https://floradobrasil.jbrj.gov.br/reflora/herbarioVirtual/ConsultaPublicoHVUC/BemVindoConsultaPublicaHVConsultar.do?nomeCientifico=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>Reflora HV</a>
                <a href='https://www.worldfloraonline.org/search?query=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>World Flora</a>
                <a href='https://powo.science.kew.org/results?q=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>POWO</a>
                <a href='https://www.ipni.org/search?q=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>IPNI</a>
                <a href='https://plants.jstor.org/search?filter=name&so=ps_group_by_genus_species+asc&Query=""" + nome_busca + """' target='_blank' style='background: #eee; padding: 8px 12px; border-radius: 5px; text-decoration: none;'>JSTOR Plants</a>
            </div>
            """, unsafe_allow_html=True)
                                    
        else:
            st.error("Código não encontrado.")        

# -----------------------------------------------
# 📷 Página: Buscar Imagem (Pl@ntNet)
# -----------------------------------------------
elif selected == "Buscar Imagem":
    st.title("📷 Buscar Imagem")
    st.write(
        "Nesta página, você pode buscar imagens das amostras do HUAM vinculadas à da base de dados "
        "e utilizar o serviço **Pl@ntNet** para realizar a identificação automática da espécie. "
        "Basta informar o número do tombo ou escanear o código de barras para visualizar "
        "a imagem da exsicata e receber sugestões de identificação botânica."
    )
    st.subheader("Identificação da Espécie com Pl@ntNet")

    # Conexão com a planilha
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

    # Entrada manual (pré-preenchida)
    code = ""
    codigo = st.text_input(
        "Digite o número do tombo",
        value=code,
        placeholder="Ex.: HUAM000001"
    )
    
    # Buscar e Identificar (Pl@ntNet)
    if st.button("🔍 Buscar e Identificar"):
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
            # 🚩 Mostrar o resultado Imagem se existir
            if 'result_image' in st.session_state and st.session_state.result_image is not None:
                for _, row in st.session_state.result_image.iterrows():

                #for _, row in resultado.iterrows():
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

                                    # Envia para Pl@ntNet
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
                                            st.subheader("Resultados da identificação com a API do Pl@ntnet:")
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

    
