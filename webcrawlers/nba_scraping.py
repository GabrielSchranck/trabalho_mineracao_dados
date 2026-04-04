from bs4 import BeautifulSoup
from loguru import logger
import pandas as pd
import requests
import json
import re
#import missingno as msmo

from utils import (
    normalize_text,
    normalize_value
)


class NBAScraping():
    def __init__(self, url: str):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        }
        
        self.url = url
        self.data = []
        self.categorias = self.extract_menu_item()
    
    def _get(self, url: str, params = None, data = None, headers: dict = None, cookies: dict = None):
        return requests.get(
            url, 
            params=params, 
            headers=headers or self.headers, 
            cookies=cookies
        )
    
    def extract_menu_item(self):
        """
            Extrai os itens de navegação do menu principal a partir do JSON embutido
        no HTML da página.

        Returns:
            list[dict]: Lista de itens de navegação extraídos do menu.
        """
        response = self._get(self.url)
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*</script>', response.text, re.S)
        
        if not match:
            return []
        
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return []
        
        menu = data.get("Navigation", {}).get("menu", [])
        nav_items = []

        for item in menu:
            children = item.get("children", [])

            if children:
                for child in children:
                    name = child.get("name")
                    path = child.get("url")

                    if name and path:
                        nav_items.append({
                            "name": name,
                            "path": path
                        })
            else:
                name = item.get("name")
                path = item.get("url")

                if name and path:
                    nav_items.append({
                        "name": name,
                        "path": path
                    })

        return nav_items
    
    
    def extract_data(self):
        """
            Realiza o scraping de produtos a partir das categorias disponíveis.
            
            Observações:
                - Ignora produtos sem atributo `href`.
                - Depende do método `_get` para requisições HTTP.
                - O parsing dos dados é feito externamente via `parse_data`.
        """
        for categoria in self.categorias:
            logger.info(f'Coletando produtos da categoria: {categoria['name']}')
            
            page = 1
            while True:
                response = self._get(f'{self.url}{categoria['path']}&page={page}')
                soup = BeautifulSoup(response.text, 'html.parser')
                
                product_div = soup.find('div', {'class':'product-list__items'})
                
                if not product_div:
                    logger.warning(
                        f"Nenhuma lista de produtos encontrada na categoria "
                        f"{categoria['name']} - página {page}"
                    )
                    break
                
                product_list = product_div.find_all('a')
                
                for product in product_list:
                    product_path = product.get("href")
                    if not product_path:
                        continue
                    
                    url = f'{self.url}{product_path}'
                    response = self._get(url)
                    self.parse_data(response.text, url)
                
                pagination = soup.find(class_='product-list__pagination')
                
                if pagination:
                    page += 1
                else:
                    break
    
    
    def parse_data(self, html: str, url: str):
        """
        Extrai os dados de um produto a partir do HTML da página.

        Observações:
            - Campos ausentes recebem valor padrão quando possível.
            - Atributos do produto são adicionados dinamicamente ao dicionário.
            - Tamanhos podem vir como tamanho único ou como lista de opções.

        Parâmetros:
            html (str): HTML da página do produto.
            url (str): URL do produto.
        """
        soup = BeautifulSoup(html, "html.parser")
        product = {}

        # SKU
        sku_tag = soup.find("p", {"class": "product-reference"})
        product["sku"] = (
            normalize_text(sku_tag.text).replace("Ref.:", "")
            if sku_tag
            else ""
        )

        # Atributos
        attributes_container = soup.find("ul", {"class": "features--attributes"})
        if attributes_container:
            attributes = attributes_container.find_all("li")
            for attr in attributes:
                parts = str(attr.text).split(":", 1)
                if len(parts) == 2:
                    key = normalize_text(parts[0])
                    value = normalize_text(parts[1])
                    product[key] = value

        # Cor
        color_tag = soup.find("span", {"class": "label--color"})
        product["color"] = normalize_text(color_tag.text) if color_tag else ""

        # Preço
        value_tag = soup.find("span", {"class": "saleInCents-value"})
        product["value"] = normalize_value(value_tag.text) if value_tag else 0

        # Descrição
        description_tag = soup.find("p", {"class": "features--description"})
        product["description"] = (
            normalize_text(description_tag.text) if description_tag else ""
        )

        # Média de avaliação
        rating_tag = soup.find("div", {"class": "link__average"})
        rating_text = normalize_text(rating_tag.text) if rating_tag else "0"

        try:
            product["media_rating"] = float(rating_text)
        except (ValueError, TypeError):
            product["media_rating"] = 0.0

        # Quantidade de avaliações
        reviews_tag = soup.find("p", {"class": "link__infos--number-of-reviews"})
        reviews_text = normalize_text(reviews_tag.text) if reviews_tag else ""
        reviews_match = re.search(r"Ler (\d+) avaliações", reviews_text)

        product["number_reviews"] = int(reviews_match.group(1)) if reviews_match else 0

        # Tamanho
        unique_size_tag = soup.find("span", {"class": "unique-size"})
        if unique_size_tag:
            product["size"] = normalize_text(unique_size_tag.text)
        else:
            size_list = []
            sizes = soup.find_all("li", {"class": "size-list__item"})
            for size in sizes:
                size_text = normalize_text(size.text)
                if size_text:
                    size_list.append(size_text)

            product["size"] = ", ".join(size_list)

        # Imagens
        image_list = []
        images = soup.find_all("figure", {"class": "carousel-item-figure"})
        for image in images:
            img_tag = image.find("img")
            if img_tag and img_tag.get("src"):
                image_list.append(img_tag["src"])

        product["images"] = "; ".join(image_list)

        # URL
        product["url_product"] = url

        self.data.append(product)
    
    def analyze_data(self):
        df = pd.DataFrame(self.data)

        logger.info(f"Total de registros: {len(df)}")

        missing = (df.isnull().mean() * 100).sort_values(ascending=False)
        logger.info(f"Valores faltantes (%):\n{missing}")

        if 'sku' in df.columns:
            duplicados = df.duplicated(subset='sku').sum()
            logger.info(f"Duplicatas encontradas (SKU): {duplicados}")

        if 'value' in df.columns:
            outliers = df[df['value'] <= 0]
            logger.info(f"Outliers de preço (<=0): {len(outliers)}")


    def clean_data(self):
        df = pd.DataFrame(self.data)

        logger.info(f"Dados antes da limpeza: {len(df)} registros")

        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        logger.info("Iniciando limpeza do campo SKU...")
        df['sku'] = (
            df['sku']
            .fillna('')
            .str.replace(r'[^A-Za-z0-9\-]', '', regex=True)
            .str.upper()
        )

        antes_tratamento = len(df)
        df = df[df['sku'] != '']           
        df = df.drop_duplicates('sku')
        depois_tratamento = len(df)

        logger.info(f"Duplicadas removidas: {antes_tratamento - depois_tratamento} registros")

        logger.info("Removendo espaços e padronizando texto...")
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip().str.title()

        logger.info("Convertendo dados numéricos...")
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0)

        if 'media_rating' in df.columns:
            df['media_rating'] = pd.to_numeric(df['media_rating'], errors='coerce').fillna(0.0)

        if 'number_reviews' in df.columns:
            df['number_reviews'] = pd.to_numeric(df['number_reviews'], errors='coerce').fillna(0).astype(int)

        if 'value' in df.columns:
            outliers = df[df['value'] <= 0]
            logger.info(f"Produtos com preço inválido (<=0): {len(outliers)}")

        df = df.reset_index(drop=True)

        logger.info(f"Total de registros após limpeza: {len(df)}")

        self.data = df.to_dict(orient='records')



    def upload_product(self):
        df = pd.DataFrame(self.data)
        
        df.to_csv('product.csv', encoding='utf-8', sep=';')
        
        print("Arquivo CSV criado com sucesso!")