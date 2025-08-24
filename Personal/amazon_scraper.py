import requests
from bs4 import BeautifulSoup
import functions_framework
import psycopg2
from datetime import datetime
import os


class AmazonScraper:
    def __init__(self, url: str):
        self.url = url

    def fetch_product_html_via_scraperapi(self) -> str:
        payload = {
            "api_key": "9f5a0cdc28ed693568ca66e8a7baac2d",
            "url": self.url
        }
        response = requests.get("https://api.scraperapi.com/", params=payload, timeout=60)
        response.raise_for_status()
        return response.text

    def extract_price_from_html(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")

        preferred = soup.select_one(
            "#apex_offerDisplay_desktop .a-price .a-offscreen"
        )
        if preferred and preferred.get_text(strip=True):
            return preferred.get_text(strip=True)
        
        alt_core = soup.select_one("#corePrice_feature_div .a-price .a-offscreen")
        if alt_core and alt_core.get_text(strip=True):
            return alt_core.get_text(strip=True)
        
        for span in soup.select("span.a-offscreen"):
            text = span.get_text(strip=True)
            if text and ("R$" in text or "," in text):
                return text
        
        return None
    
    def run(self) -> str | None:
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
        price VARCHAR(100),
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

def save_price_to_db(url: str, store: str, price: str, product_name: str = None):
    """Salva ou atualiza o preço no banco de dados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        check_query = "SELECT id FROM monitors WHERE url = %s"
        cursor.execute(check_query, (url,))
        existing_record = cursor.fetchone()
        
        if existing_record:
            update_query = """
            UPDATE monitors 
            SET price = %s, product_name = %s, last_mined_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', 
                next_mine_at = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour', updated_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo' 
            WHERE url = %s
            """
            cursor.execute(update_query, (price, product_name, url))
        else:
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
def amazon_scraper(request):
    """Google Cloud Function para extrair preços da Amazon"""
    request_json = request.get_json(silent=True)
    
    if request_json and 'url' in request_json:
        url = request_json['url']
        scraper = AmazonScraper(url)
        price = scraper.run()
        
        create_monitors_table()
        
        save_success = save_price_to_db(url, 'amazon', price)
        
        return {
            'price': price,
            'url': url,
            'store': 'amazon',
            'saved_to_db': save_success,
            'timestamp': datetime.now().isoformat()
        }
    
    return {'error': 'URL não fornecida'}, 400
