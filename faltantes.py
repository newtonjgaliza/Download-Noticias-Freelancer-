import scrapy
import os
import csv
import requests

class FaltantesSpider(scrapy.Spider):
    name = "faltantes"
    allowed_domains = ["veramendes.pi.gov.br"]

    def __init__(self, *args, **kwargs):
        super(FaltantesSpider, self).__init__(*args, **kwargs)
        
        # Lê os links do arquivo txt e armazena na lista de URLs a serem processadas
        with open("links.txt", "r", encoding="utf-8") as file:
            self.start_urls = [line.strip() for line in file.readlines() if line.strip()]
        
        # Inicializa o arquivo CSV e escreve o cabeçalho
        with open("faltantes.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Titulo", "Data_Publicacao", "Autor", "Link", "Textos", "Imagens"])

    def parse(self, response):
        # Para cada link que foi carregado da lista de URLs
        yield response.follow(response.url, callback=self.parse_noticias, meta={'url': response.url})

    def parse_noticias(self, response):
        # Extrai o título
        title = response.xpath('//h1[@class="entry-title"]/text()').get()
        print("Título:", title)

        # Extrai a data
        data = response.xpath('//time[@class="entry-date published"]/text()').get()
        print('Data:', data)

        # Extrai o Autor da noticia
        autor = response.xpath('//*//*[starts-with(@id, "post-")]/div/header/div/span[2]/span/a/span').get()
        print('Autor', autor)

        # Extrai o link da notícia da meta
        link = response.meta['url']
        print('Link:', link)

        # Extrai os textos dos parágrafos
        paragraph_texts = response.xpath('//*[starts-with(@id, "post-")]/div/div[2]/p/text()').getall()
        full_text = " ".join(paragraph_texts)
        print("Textos:", full_text)

        # Extrai os links das imagens dentro da div "inside-article"
        image_urls = response.xpath('//div[contains(@class, "inside-article")]//img/@src').getall()
        print("Imagens:", image_urls)

        # Baixa e salva as imagens em uma pasta com o título da notícia
        if title:
            title_sanitized = "".join(x for x in title if x.isalnum() or x in " _-").strip()
            image_folder = f"images/{title_sanitized}"
            os.makedirs(image_folder, exist_ok=True)

            for idx, img_url in enumerate(image_urls, start=1):
                self.download_image(img_url, image_folder, idx)

        # Escreve os dados no CSV
        with open("faltantes.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([title, data, autor, link, full_text, ", ".join(image_urls)])

    def download_image(self, url, folder, idx):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                image_path = os.path.join(folder, f"{idx}.jpg")
                with open(image_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Imagem {idx} salva em {image_path}")
            else:
                print(f"Erro ao baixar a imagem: {url}")
        except Exception as e:
            print(f"Erro ao baixar a imagem {url}: {e}")
