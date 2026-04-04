from loguru import logger
import pandas as pd
import os

from utils import (
    normalize_text,
    normalize_value,
    clean_string,
    normalize_minmax,
    detect_outliers_iqr,
)

DEFAULT_PATH = os.path.dirname(os.path.abspath(__file__))


class Analyze:
    def __init__(self):
        self.path = os.path.abspath(
            os.path.join(DEFAULT_PATH, "..", "products_gross.csv")
        )
        self.output_path = os.path.abspath(
            os.path.join(DEFAULT_PATH, "..", "products.csv")
        )
        self.data = []


    def load_analyze(self):
        """Carrega dados, analisa, limpa e salva."""
        if not os.path.exists(self.path):
            logger.error(f"Arquivo não encontrado: {self.path}")
            return None

        try:
            df = pd.read_csv(self.path, encoding="utf-8", sep=";")

            self.analyze_data(df)
            df = self.clean_data(df)

            self.save_clean_data(df)
            self.data = df.to_dict(orient="records")

            return df

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return None


    def analyze_data(self, df: pd.DataFrame):
        """Resumo geral dos dados."""
        logger.info(f"Total de registros: {len(df)}")
        self.analyze_missing(df)
        self.analyze_duplicates(df)
        self.analyze_invalid_prices(df)


    def analyze_missing(self, df):
        """Percentual de nulos."""
        missing = (df.isnull().mean() * 100).sort_values(ascending=False)
        logger.info(f"Valores faltantes (%):\n{missing}")


    def analyze_duplicates(self, df):
        """Duplicatas por SKU."""
        if "sku" in df.columns:
            duplicados = df.duplicated(subset="sku").sum()
            logger.info(f"Duplicatas (SKU): {duplicados}")


    def analyze_invalid_prices(self, df):
        """Preços inválidos."""
        if "value" in df.columns:
            values = pd.to_numeric(df["value"], errors="coerce")
            invalid = df[values <= 0]
            logger.info(f"Preços inválidos (<=0): {len(invalid)}")


    def clean_data(self, df: pd.DataFrame):
        """Pipeline de limpeza."""
        logger.info(f"Antes da limpeza: {len(df)} registros")

        df = self.normalize_columns(df)
        df = self.clean_sku(df)
        df = self.clean_text(df)
        df = self.convert_values(df)
        df = self.fill_missing(df)
        df = self.remove_sparse_columns(df)
        df = self.normalize_categories(df)
        df = self.handle_outliers(df)
        df = self.create_price_range(df)
        df = self.normalize_price(df)
        df = self.clean_description(df)

        df = df.reset_index(drop=True)

        logger.info(f"Após limpeza: {len(df)} registros")
        return df


    def normalize_columns(self, df):
        """Padroniza nomes das colunas."""
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df


    def clean_sku(self, df):
        """Limpa SKU e remove duplicatas."""
        if "sku" not in df.columns:
            return df

        df["sku"] = (
            df["sku"]
            .fillna("")
            .astype(str)
            .str.replace(r"[^A-Za-z0-9\-]", "", regex=True)
            .str.upper()
        )

        before = len(df)

        df = df[df["sku"] != ""]
        df = df.drop_duplicates("sku")

        logger.info(f"Removidos por SKU: {before - len(df)}")
        return df


    def clean_text(self, df):
        """Normaliza texto."""
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(normalize_text)
        return df


    def convert_values(self, df):
        """Converte valores monetários."""
        if "value" in df.columns:
            df["value"] = df["value"].apply(normalize_value)

        if "media_rating" in df.columns:
            df["media_rating"] = pd.to_numeric(df["media_rating"], errors="coerce")

        if "number_reviews" in df.columns:
            df["number_reviews"] = pd.to_numeric(df["number_reviews"], errors="coerce")

        return df


    def fill_missing(self, df):
        """Preenche valores ausentes."""
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].replace("Nan", pd.NA)
                df[col] = df[col].fillna("Não Informado")
        return df


    def remove_sparse_columns(self, df, threshold=0.7):
        """Remove colunas muito vazias."""
        null_ratio = df.isnull().mean()
        cols = null_ratio[null_ratio > threshold].index

        if len(cols) > 0:
            df = df.drop(columns=cols)
            logger.info(f"Colunas removidas: {list(cols)}")

        return df


    def normalize_categories(self, df):
        """Padroniza categorias."""
        for col in ["marca", "categoria", "genero", "indicado_para"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower().str.strip()
        return df


    def handle_outliers(self, df):
        """Detecta outliers de preço."""
        if "value" in df.columns:
            mask = detect_outliers_iqr(df["value"])
            logger.info(f"Outliers detectados: {mask.sum()}")
        return df


    def create_price_range(self, df):
        """Cria faixa de preço."""
        if "value" in df.columns:
            bins = [0, 100, 300, 600, float("inf")]
            labels = ["barato", "medio", "caro", "premium"]

            df["faixa_preco"] = pd.cut(df["value"], bins=bins, labels=labels)
        return df


    def normalize_price(self, df):
        """Normaliza preço."""
        if "value" in df.columns:
            df["value_normalized"] = normalize_minmax(df["value"])
        return df


    def clean_description(self, df):
        """Limpa descrição."""
        if "description" in df.columns:
            df["description"] = df["description"].apply(clean_string)
        return df


    def save_clean_data(self, df):
        """Salva CSV final."""
        df.to_csv(self.output_path, index=False, sep=";", encoding="utf-8")
        logger.info("Arquivo CSV criado com sucesso!")
