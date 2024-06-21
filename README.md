# DataSynth

![QR Code](QRCode.png)

DataSynth é uma ferramenta para anonimização de dados sensíveis de transações financeiras utilizando técnicas de ruído branco e criptografia. DataSynthDecripter é uma ferramenta complementar que permite a recuperação dos dados originais a partir dos dados encriptados.

## Descrição

DataSynth aplica ruído branco gaussiano aos dados sensíveis para anonimização e encripta os dados originais usando criptografia simétrica. DataSynthDecripter permite decriptar os dados encriptados utilizando uma chave derivada de uma senha fornecida pelo usuário.

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/DataSynth.git
2. Instale as dependências
   ```bash
   pip install -r requirements.txt

## Uso
### DataSynth

1. Para rodar o DataSynth, execute o seguinte comando:
   ```bash
   streamlit run DataSynth.py

### DataSynthDecripter

1. Para rodar o DataSynthDecripter, execute o seguinte comando:
   ```bash
    streamlit run DataSynthDecripter.py

## Contribuição

Sinta-se à vontade para contribuir com o projeto abrindo uma issue ou enviando um pull request.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
