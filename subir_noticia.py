# -*- coding: utf-8 -*- 
import scrapy 
import csv 
from selenium import webdriver 
from webdriver_manager.firefox import GeckoDriverManager 
from selenium.webdriver.firefox.service import Service 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import Select 
import pandas as pd 
from datetime import datetime 
import os 
import unicodedata 
import re 
from selenium.webdriver.common.keys import Keys  # Importando a classe Keys

# Função para formatar a data
def formatar_data(data_texto):
    meses = {
        "janeiro": "01", "fevereiro": "02", "março": "03",
        "abril": "04", "maio": "05", "junho": "06",
        "julho": "07", "agosto": "08", "setembro": "09",
        "outubro": "10", "novembro": "11", "dezembro": "12"
    }
    partes = data_texto.split()
    mes = meses[partes[0].lower()]
    dia = partes[1].replace(",", "")
    dia = dia.zfill(2)  # Adiciona um zero à esquerda se o dia for menor que 10
    ano = partes[2]
    agora = datetime.now()
    hora = agora.strftime("%H")
    minuto = agora.strftime("%M")
    data_formatada = f"{dia}/{mes}/{ano} {hora}:{minuto}"
    return data_formatada

# Função para normalizar o texto, removendo acentos, hífens, e caracteres especiais
def normalizar_texto(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = texto.replace('—', '-')
    texto = re.sub(r'[^a-zA-Z\s-]', '', texto)
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto.lower()

# Função para extrair parte do título antes do primeiro hífen
def extrair_parte_inicial(titulo):
    match = re.split(r' - ', titulo)
    return match[0].strip() if match else titulo

# Lendo o arquivo CSV
print('#LENDO O ARQUIVO CSV#')
df = pd.read_csv('./faltantes.csv')
nome_pasta = os.path.basename(os.getcwd())
nome_pasta_normalizado = normalizar_texto(nome_pasta)
print(f"Nome da pasta normalizado: '{nome_pasta_normalizado}'")

# Busca do título correspondente
titulo_noticia = None
for titulo in df['Titulo']:
    titulo_inicial = extrair_parte_inicial(titulo).strip()
    titulo_normalizado = normalizar_texto(titulo_inicial)
    nome_pasta_inicial = extrair_parte_inicial(nome_pasta_normalizado).strip()
    print(f"Comparando título: '{titulo_normalizado}' com nome da pasta: '{nome_pasta_inicial}'")
    if titulo_normalizado == nome_pasta_inicial:
        titulo_noticia = titulo
        print(f"Título correspondente encontrado: {titulo_noticia}")
        break

if titulo_noticia is None:
    print("Nenhum título correspondente encontrado!")
    exit()

print(f'Título encontrado: {titulo_noticia}')

data_publicacao = formatar_data(df[df['Titulo'] == titulo_noticia]['Data_Publicacao'].iloc[0])
texto_noticia = df[df['Titulo'] == titulo_noticia]['Textos'].iloc[0]
autor_noticia = df[df['Titulo'] == titulo_noticia]['Autor'].iloc[0]

print('PASTA:', nome_pasta)

# Iniciando o Navegador
print('#INICIANDO O NAVEGADOR#')
servico = Service(GeckoDriverManager().install())
navegador = webdriver.Firefox(service=servico)

# Acessando o CMS e fazendo login
print('#ACESSANDO O CMS#')
navegador.get('https://veramendes.maximatecnologia.com.br/cms')
navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[1]/input').send_keys('endereço do CMS')
navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[2]/input').send_keys('senha')
navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()

# Função para aguardar e clicar no elemento
def esperar_e_clicar(xpath):
    try:
        elemento = WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elemento.click()
        print(f"Elemento clicado: {xpath}")
    except Exception as e:
        print(f"Erro ao clicar no elemento {xpath}: {e}")

# Cadastrando a notícia
print('#CLICANDO NO MENU NOTICIAS#')
esperar_e_clicar('/html/body/div[1]/aside/div/section/ul/li[2]/a')

print('#CLICANDO EM CADASTRAR NOTICIA#')
esperar_e_clicar('/html/body/div/div/section[2]/div/div/div/div[1]/div[1]/a')

# Setando a categoria e preenchendo os campos
print("--DATA FORMATADA: "+ data_publicacao + ' --')
navegador.find_element(By.XPATH, '//*[@id="category_contents_id"]').send_keys('Secretária de Saúde')
navegador.find_element(By.XPATH, '//*[@id="title"]').send_keys(titulo_noticia)

# Limpar o campo de data antes de inserir nova data
campo_data = navegador.find_element(By.XPATH, '//*[@id="publication_date"]').clear()
campo_data2 = navegador.find_element(By.XPATH, '//*[@id="publication_date"]')
campo_data2.click()  # Clique para focar no campo
campo_data2.send_keys(data_publicacao)  # Insere a data formatada

# Simulando o pressionamento da tecla TAB para mover o foco para o próximo campo (autor)
navegador.find_element(By.XPATH, '//*[@id="author"]').send_keys(autor_noticia)

# Selecionando a Secretaria no dropdown
#print('SELECIONANDO A SECRETARIA')
#ddelement = Select(navegador.find_element(By.XPATH, '//*[@id="secretaria"]'))
#ddelement.select_by_index(7)

# Adicionando o texto da notícia
print('#ADICIONANDO O TEXTO DA NOTICIA#')
navegador.find_element(By.XPATH, '/html/body/div[1]/div/section[2]/form/div[1]/div[1]/div/div[7]/div/div/div[3]/div[3]').send_keys(texto_noticia)

# ENVIANDO A IMAGEM PRINCIPAL "1.jpg"
print('#ADICIONANDO IMAGEM PRINCIPAL#')
imagem_principal = os.path.join(os.getcwd(), '1.jpg')
campo_imagem_principal = navegador.find_element(By.XPATH, '//*[@id="file"]')
campo_imagem_principal.send_keys(imagem_principal)
print("Imagem principal '1.jpg' enviada com sucesso.")

'''
# Clicando em ativar galeria
print('#CLICANDO EM ATIVAR GALERIA#')
navegador.find_element(By.XPATH, '//*[@id="galery"]').click()

# Clicando em salvar e ir para galeria
print('#CLICANDO EM SALVAR E IR PARA GALERIA#')
navegador.find_element(By.XPATH, '//*[@id="btn-submit"]').click()

# Carregar e enviar todas as imagens presentes na pasta onde o script está rodando
print("#INICIANDO O ENVIO DAS FOTOS#")

# Listar arquivos de imagem na pasta atual e ordenar numericamente
imagens = sorted([f for f in os.listdir() if f.endswith(('.jpg', '.jpeg', '.png')) and f != '1.jpg'], key=lambda x: int(re.findall(r'\d+', x)[0]))

# Função para enviar imagens em lotes de 10
def enviar_imagens_em_lotes(imagens):
    while imagens:
        lote = imagens[:10]  # Pega o primeiro lote de até 10 imagens
        imagens = imagens[10:]  # Remove as imagens já enviadas

        for imagem in lote:
            caminho_imagem = os.path.abspath(imagem)
            try:
                print(f"Enviando imagem: {imagem}")
                campo_upload = WebDriverWait(navegador, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[starts-with(@id, "ajax-upload-id")]'))
                )
                campo_upload.send_keys(caminho_imagem)
                WebDriverWait(navegador, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//img[contains(@src, "{imagem}")]'))
                )
                print(f"Imagem {imagem} enviada com sucesso.")
            except Exception as e:
                print(f"Erro ao enviar a imagem {imagem}: {e}")

# Enviar as imagens em lotes
enviar_imagens_em_lotes(imagens)
'''

# Clicar no botão submit para finalizar o envio e salvar a notícia
print('#CICANDO EM SUBMIT PARA FINALIZAR O ENVIO#')
navegador.find_element(By.XPATH, '//*[@id="btn-submit"]').click()

# Fechar o navegador após completar a execução
print('#FECHANDO O NAVEGADOR#')
navegador.quit()
