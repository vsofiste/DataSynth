import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import base64
from io import BytesIO
from cryptography.fernet import Fernet
import hashlib
import random
import string

# Função para gerar ruído branco usando Box-Muller
def gerar_ruido_branco(tamanho):
    U1 = np.random.uniform(0, 1, tamanho)
    U2 = np.random.uniform(0, 1, tamanho)
    Z0 = np.sqrt(-2 * np.log(U1)) * np.cos(2 * np.pi * U2)
    return Z0

# Função para plotar ruído branco com média e desvio padrão
def plot_ruido_branco(ruido, ruido_nivel):
    media_ruido = np.mean(ruido)
    desvio_padrao_ruido = np.std(ruido)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(ruido, bins=30, kde=True, ax=ax)
    ax.axvline(media_ruido, color='r', linestyle='--', label=f'Média do Ruído: {media_ruido:.2f}')
    ax.axvline(desvio_padrao_ruido, color='g', linestyle='--', label=f'Desvio Padrão do Ruído: {desvio_padrao_ruido:.2f}')
    ax.set_xlabel('Valor')
    ax.set_ylabel('Frequência')
    ax.set_title(f'Ruído Branco Gaussiano Gerado (Nível de Ruído = {ruido_nivel})')
    ax.legend()
    st.pyplot(fig)

def plot_ruido_branco_tempo_discreto(ruido):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(ruido, label='Ruído Branco Gaussiano')
    ax.set_xlabel('Amostras')
    ax.set_ylabel('Valor')
    ax.set_title('Ruído Branco Gaussiano em Tempo Discreto')
    ax.legend()
    st.pyplot(fig)

# Função para calcular a autocorrelação
def calcular_autocorrelacao(ruido):
    autocorr = np.correlate(ruido, ruido, mode='full')
    autocorr = autocorr[autocorr.size // 2:]
    return autocorr

# Função para plotar a autocorrelação
def plot_autocorrelacao(autocorr):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(autocorr, label='Autocorrelação')
    ax.set_xlabel('Lag')
    ax.set_ylabel('Autocorrelação')
    ax.set_title('Autocorrelação do Ruído Branco Gaussiano')
    ax.legend()
    st.pyplot(fig)

# Função para derivar chave a partir da senha
def derivar_chave(senha):
    kdf_salt = b'some_salt_'  # Isso deve ser armazenado de maneira segura
    kdf_iterations = 100000
    chave = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac('sha256', senha.encode(), kdf_salt, kdf_iterations, dklen=32))
    return chave

# Função para adicionar ruído branco e encriptar os dados originais
def adicionar_ruido_branco_e_encriptar(dados, coluna, chave, ruido_nivel=1):
    tamanho = len(dados)
    Z0 = gerar_ruido_branco(tamanho)
    dados[coluna] = dados[coluna].apply(lambda x: float(str(x).replace(',', '.')) if isinstance(x, str) else x)
    ruido = Z0 * ruido_nivel
    dados_sinteticos = dados.copy()
    dados_sinteticos[coluna] += ruido

    # Encriptar os dados originais
    fernet = Fernet(chave)
    dados['Encrypted_' + coluna] = dados[coluna].apply(lambda x: fernet.encrypt(str(x).encode()).decode())
    return dados_sinteticos, dados

# Função para gerar imagem de ruído branco
def gerar_imagem_ruido(branco=True):
    largura, altura = 50, 50
    array_ruido = np.random.randint(0, 255, (altura, largura), dtype=np.uint8)
    img_ruido = Image.fromarray(array_ruido)
    buffer = BytesIO()
    img_ruido.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    return f'<img src="data:image/png;base64,{img_b64}" width="50" height="50">'

# Função para anonimizar dados textuais com ruído branco
def anonimizar_texto_com_ruido(dados, colunas_texto, chave):
    dados_anonimizados = dados.copy()
    fernet = Fernet(chave)
    for coluna in colunas_texto:
        dados_anonimizados['Encrypted_' + coluna] = dados_anonimizados[coluna].apply(lambda x: fernet.encrypt(str(x).encode()).decode())
        dados_anonimizados[coluna] = gerar_imagem_ruido()
    return dados_anonimizados

# Função para ajustar estilo CSS
def ajustar_estilo():
    st.markdown(
        """
        <style>
        .reportview-container .main .block-container {
            max-width: 80%;
            margin: auto;
            padding: 2rem;
        }
        .dataframe {
            width: 100%;
            overflow-x: auto;
            display: block;
            white-space: nowrap;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Função para formatar colunas do dataframe
def formatar_colunas(dados):
    dados['Codigo_Autorizacao'] = dados['Codigo_Autorizacao'].astype(int)
    dados['Valor_Transacao'] = dados['Valor_Transacao'].apply(lambda x: f'{x:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    return dados

# Função para gerar uma senha aleatória
def gerar_senha_aleatoria(tamanho=12):
    caracteres = string.ascii_letters + string.digits
    senha = ''.join(random.choice(caracteres) for i in range(tamanho))
    return senha

# Função para decriptar os dados
def decriptar_dados(dados, chave, colunas_texto):
    fernet = Fernet(chave)
    for coluna in dados.columns:
        if coluna.startswith('Encrypted_'):
            original_coluna = coluna.replace('Encrypted_', '')
            if original_coluna in colunas_texto:
                try:
                    dados[original_coluna] = dados[coluna].apply(lambda x: fernet.decrypt(x.encode()).decode())
                except Exception as e:
                    st.write(f"Erro ao decriptar a coluna {coluna}: {e}")
            else:
                try:
                    dados[original_coluna] = dados[coluna].apply(lambda x: float(fernet.decrypt(x.encode()).decode()))
                except Exception as e:
                    st.write(f"Erro ao decriptar a coluna {coluna}: {e}")
    # Remover colunas encriptadas após decriptação
    colunas_encriptadas = [col for col in dados.columns if col.startswith('Encrypted_')]
    dados.drop(columns=colunas_encriptadas, inplace=True)
    return dados

# Função para converter strings com vírgulas para float
def converter_para_float(valor):
    try:
        if isinstance(valor, str):
            valor = valor.replace('.', '').replace(',', '.')
        return float(valor)
    except ValueError:
        return np.nan

# Interface do Streamlit
ajustar_estilo()

st.title("DataSynth - Demonstração de Anonimização de Dados Financeiros")
st.write("Veja como os dados sensíveis são anonimizados para proteger a privacidade dos clientes.")

# Inicializa a senha e chave usando o estado do Streamlit
if 'senha_aleatoria' not in st.session_state:
    st.session_state.senha_aleatoria = None

if 'chave' not in st.session_state:
    st.session_state.chave = None

if 'uploaded_file_buffer' not in st.session_state:
    st.session_state.uploaded_file_buffer = None

# Botão para gerar nova sessão
def gerar_nova_sessao():
    st.session_state.senha_aleatoria = None
    st.session_state.chave = None
    st.session_state.uploaded_file_buffer = None
    st.experimental_rerun()

# Carregar banco de dados de um arquivo CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
if uploaded_file is not None:
    # Verifica se o arquivo carregado é novo
    uploaded_file_buffer = uploaded_file.getvalue()
    if uploaded_file_buffer != st.session_state.uploaded_file_buffer:
        # Limpa o estado atual
        st.session_state.uploaded_file_buffer = uploaded_file_buffer
        
        # Geração da senha aleatória após o upload do CSV
        st.session_state.senha_aleatoria = gerar_senha_aleatoria()

        # Geração da chave secreta após o upload do CSV
        st.session_state.chave = derivar_chave(st.session_state.senha_aleatoria)

        # Limpa as tabelas e entradas de senha
        st.session_state['banco_dados_transacoes'] = None
        st.session_state['banco_dados_anonimizados'] = None
        st.session_state['banco_dados_sinteticos'] = None
        st.session_state['banco_dados_encriptados'] = None
        st.session_state['senha_input'] = None

    fernet = Fernet(st.session_state.chave)

    st.write(f"Senha para decriptar: {st.session_state.senha_aleatoria}")

    banco_dados_transacoes = pd.read_csv(BytesIO(st.session_state.uploaded_file_buffer))
    banco_dados_transacoes['Valor_Transacao'] = banco_dados_transacoes['Valor_Transacao'].apply(converter_para_float)
    banco_dados_transacoes = formatar_colunas(banco_dados_transacoes)

    # Armazenar os dados no estado
    st.session_state['banco_dados_transacoes'] = banco_dados_transacoes

    # Adiciona o botão "Gerar Nova Sessão" logo abaixo do upload do CSV
    st.button("Gerar Nova Sessão", on_click=gerar_nova_sessao)
    
    # Exibir dados originais
    st.write("### Dados Originais")
    st.write(st.session_state['banco_dados_transacoes'].head())

    # Anonimizar dados textuais com ruído branco
    colunas_texto = ['Nome_Cliente', 'Numero_Cartao', 'Email_Cliente', 'Telefone_Cliente', 'Endereco_IP']
    banco_dados_anonimizados = anonimizar_texto_com_ruido(st.session_state['banco_dados_transacoes'], colunas_texto, st.session_state.chave)
    banco_dados_anonimizados['Valor_Transacao'] = banco_dados_anonimizados['Valor_Transacao'].apply(converter_para_float)
    banco_dados_anonimizados = formatar_colunas(banco_dados_anonimizados)

    # Armazenar os dados anonimizados no estado
    st.session_state['banco_dados_anonimizados'] = banco_dados_anonimizados

    # Aplicar ruído branco e encriptar os dados originais
    ruido_nivel = st.slider("Nível de Ruído", min_value=0, max_value=1000, value=1, step=1)
    banco_dados_sinteticos, banco_dados_encriptados = adicionar_ruido_branco_e_encriptar(st.session_state['banco_dados_anonimizados'], 'Valor_Transacao', st.session_state.chave, ruido_nivel)
    banco_dados_sinteticos = formatar_colunas(banco_dados_sinteticos)

    # Armazenar os dados sinteticos e encriptados no estado
    st.session_state['banco_dados_sinteticos'] = banco_dados_sinteticos
    st.session_state['banco_dados_encriptados'] = banco_dados_encriptados

    # Remover colunas encriptadas dos dados sintéticos
    colunas_encriptadas = [col for col in st.session_state['banco_dados_sinteticos'].columns if col.startswith('Encrypted_')]
    banco_dados_sinteticos_sem_encriptacao = st.session_state['banco_dados_sinteticos'].drop(columns=colunas_encriptadas)

    # Exibir dados anonimizados com ruído branco aplicado com controle deslizante horizontal
    st.write("### Dados Anonimizados com Ruído Branco Aplicado")
    st.write('<div style="overflow-x: auto;">' + banco_dados_sinteticos_sem_encriptacao.head(5).to_html(escape=False, index=False) + '</div>', unsafe_allow_html=True)

    # Botão para exportar dados encriptados
    csv_encriptado = banco_dados_encriptados.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Exportar Dados Encriptados",
        data=csv_encriptado,
        file_name='dados_encriptados.csv',
        mime='text/csv'
    )

    # Verificação de senha e decriptação de dados
    senha_input = st.text_input("Insira a senha para decriptar os dados", type="password")
    decriptar_btn = st.button("Decriptar Dados", key="decriptar_btn")
    if decriptar_btn and senha_input == st.session_state.senha_aleatoria:
        banco_dados_decriptados = decriptar_dados(st.session_state['banco_dados_encriptados'], st.session_state.chave, colunas_texto)
        st.write("### Dados Decriptados")
        st.write('<div style="overflow-x: auto;">' + banco_dados_decriptados.head(5).to_html(escape=False, index=False) + '</div>', unsafe_allow_html=True)
    elif decriptar_btn:
        st.write("Senha incorreta. Por favor, tente novamente.")

    # Visualizar os dados originais e sintéticos
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].hist(st.session_state['banco_dados_transacoes']['Valor_Transacao'], bins=30, alpha=0.6, color='blue', label='Original')
    ax[0].set_title('Dados Originais')
    ax[0].set_xlabel('Valor Transação')
    ax[0].set_ylabel('Frequência')

    ax[1].hist(st.session_state['banco_dados_sinteticos']['Valor_Transacao'].apply(lambda x: float(str(x).replace('.', '').replace(',', '.'))), bins=30, alpha=0.6, color='green', label='Sintético')
    ax[1].set_title(f'Dados Sintéticos (Nível de Ruído = {ruido_nivel})')
    ax[1].set_xlabel('Valor Transação')
    ax[1].set_ylabel('Frequência')

    st.pyplot(fig)

    # Geração de ruído branco gaussiano e visualização em tempo discreto
    ruido = gerar_ruido_branco(len(banco_dados_transacoes))
    ruido = ruido * ruido_nivel
    st.write("### Ruído Branco Gaussiano Gerado")
    plot_ruido_branco_tempo_discreto(ruido)

    # Visualização do histograma do ruído branco
    st.write("### Ruído Branco Gaussiano Gerado")
    plot_ruido_branco(ruido, ruido_nivel)

    st.write("### Autocorrelação do Ruído Branco Gaussiano")
    autocorr = calcular_autocorrelacao(ruido)
    plot_autocorrelacao(autocorr)

else:
    st.write("Por favor, carregue um arquivo CSV para continuar.")
