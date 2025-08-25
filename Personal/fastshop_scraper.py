import requests
from bs4 import BeautifulSoup
import functions_framework
import psycopg2
from datetime import datetime
import os
import re
from decimal import Decimal


class FastShopScraper:
    def __init__(self, url: str):
        self.url = url
    
    def fetch_product_html_via_scraperapi(self) -> str:
        payload = {
            "api_key": "9f5a0cdc28ed693568ca66e8a7baac2d",
            "url": self.url,
            "render": "true"
        }
        response = requests.get("https://api.scraperapi.com/", params=payload, timeout=60)
        response.raise_for_status()
        return response.text
    
    def extract_price_from_html(self, html: str) -> Decimal | None:
        soup = BeautifulSoup(html, "html.parser")
        
        price_element = soup.find("span", attrs={"data-testid": "price-value"})
        
        if price_element:
            price_text = price_element.get_text().strip()
            return self._parse_price_to_decimal(price_text)
        
        return None
    
    def _parse_price_to_decimal(self, price_text: str) -> Decimal | None:
        """Converte texto de preço para valor decimal considerando formato brasileiro"""
        if not price_text:
            return None
        
        # Remove símbolos de moeda e espaços
        clean_text = re.sub(r'[R$\s]', '', price_text)
        
        # Lógica para distinguir separador de milhares vs decimais
        # Se há vírgula, ela é o separador decimal, pontos são separadores de milhares
        if ',' in clean_text:
            # Formato: 1.234,56 -> remove pontos e substitui vírgula por ponto
            clean_text = clean_text.replace('.', '').replace(',', '.')
        else:
            # Se não há vírgula, verifica se o ponto é separador decimal ou de milhares
            # Se há apenas um ponto e há exatamente 2 dígitos após ele, é decimal
            # Caso contrário, é separador de milhares
            dot_parts = clean_text.split('.')
            if len(dot_parts) == 2 and len(dot_parts[1]) == 2:
                # Formato: 1234.56 (decimal)
                pass  # mantém como está
            else:
                # Formato: 1.234 ou 1.234.567 (separadores de milhares)
                clean_text = clean_text.replace('.', '')
        
        # Extrai apenas números e ponto decimal
        price_match = re.search(r'\d+(?:\.\d{1,2})?', clean_text)
        
        if price_match:
            try:
                return Decimal(price_match.group())
            except:
                return None
        
        return None
    
    def run(self) -> Decimal | None:
        html = self.fetch_product_html_via_scraperapi()
        return self.extract_price_from_html(html)


def get_db_connection():
    """Estabelece conexão com o banco Neon PostgreSQL"""
    connection_string = "postgresql://neondb_owner:npg_MQphA3BFf0gP@ep-wispy-bonus-acat1phz-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    return psycopg2.connect(connection_string)

def create_monitors_table():
    """Cria a tabela monitors se ela não existir"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS monitors (
        id SERIAL PRIMARY KEY,
        url TEXT NOT NULL,
        store VARCHAR(50) NOT NULL,
        price DECIMAL(10,2),
        product_name VARCHAR(500),
        last_mined_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
        next_mine_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour',
        created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
        updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
    );
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def save_price_to_db(url: str, store: str, price: Decimal, product_name: str = None):
    """Salva ou atualiza o preço no banco de dados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verifica se já existe um registro para esta URL
        check_query = "SELECT id FROM monitors WHERE url = %s"
        cursor.execute(check_query, (url,))
        existing_record = cursor.fetchone()
        
        if existing_record:
            # Atualiza o registro existente
            update_query = """
            UPDATE monitors 
            SET price = %s, product_name = %s, last_mined_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', 
                next_mine_at = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour', updated_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo' 
            WHERE url = %s
            """
            cursor.execute(update_query, (price, product_name, url))
        else:
            # Insere novo registro
            insert_query = """
            INSERT INTO monitors (url, store, price, product_name, last_mined_at, next_mine_at, created_at) 
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour', CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
            """
            cursor.execute(insert_query, (url, store, price, product_name))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar no banco: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

@functions_framework.http
def fastshop_scraper(request):
    """Google Cloud Function para extrair preços da FastShop"""
    request_json = request.get_json(silent=True)
    
    if request_json and 'url' in request_json:
        url = request_json['url']
        scraper = FastShopScraper(url)
        price = scraper.run()
        
        create_monitors_table()
        save_success = save_price_to_db(url, 'fastshop', price)
        
        return {
            'price': float(price) if price else None,
            'url': url,
            'store': 'fastshop',
            'saved_to_db': save_success,
            'timestamp': datetime.now().isoformat()
        }
    
    return {'error': 'URL não fornecida'}, 400
