import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet
import base64
import hashlib
from io import BytesIO

# Função para derivar chave a partir da senha
def derivar_chave(senha):
    kdf_salt = b'some_salt_'  # Isso deve ser armazenado de maneira segura
    kdf_iterations = 100000
    chave = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac('sha256', senha.encode(), kdf_salt, kdf_iterations, dklen=32))
    return chave

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

# Interface do Streamlit
st.title("DataSynthDecripter - Desencriptação de Dados")

# Carregar banco de dados encriptado de um arquivo CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV encriptado", type="csv")
if uploaded_file is not None:
    banco_dados_encriptados = pd.read_csv(uploaded_file)

    # Verificação de senha e decriptação de dados
    senha_input = st.text_input("Insira a senha para decriptar os dados", type="password")
    if st.button("Decriptar Dados"):
        chave = derivar_chave(senha_input)
        try:
            banco_dados_decriptados = decriptar_dados(banco_dados_encriptados, chave, ['Nome_Cliente', 'Numero_Cartao', 'Email_Cliente', 'Telefone_Cliente', 'Endereco_IP', 'Valor_Transacao'])
            st.write("### Dados Decriptados")
            st.write(banco_dados_decriptados.head())
        except Exception as e:
            st.write(f"Erro na decriptação: {e}")
