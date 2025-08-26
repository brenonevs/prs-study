import requests
from bs4 import BeautifulSoup
import functions_framework
import psycopg2
from datetime import datetime
import os
from decimal import Decimal
import re


class AliexpressScraper:
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
        
        price_element = soup.find("span", class_="price-default--current--F8OlYIo")
        
        if price_element:
            text = price_element.get_text().strip()
            clean = re.sub(r'[R$\s]', '', text)
            if ',' in clean:
                clean = clean.replace('.', '').replace(',', '.')
            match = re.search(r'\d+(?:\.\d{1,2})?', clean)
            if match:
                try:
                    return Decimal(match.group())
                except Exception:
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
    """Cria a tabela monitors se ela não existir (com colunas opcionais e is_below_desired_price)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS monitors (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        url TEXT NOT NULL,
        store VARCHAR(50) NOT NULL,
        price DECIMAL(10,2),
        product_name VARCHAR(500),
        name VARCHAR(255),
        desired_price DECIMAL(10,2),
        notification_platform VARCHAR(50),
        is_below_desired_price BOOLEAN,
        last_mined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        next_mine_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 hour',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user_id, url)
    );
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def save_price_to_db(user_id: str, url: str, store: str, price: Decimal | None, product_name: str | None = None, *, name: str | None = None, desired_price: Decimal | None = None, notification_platform: str | None = None):
    """Salva ou atualiza dados do monitor para user_id+url. Atualiza apenas colunas recebidas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verifica se já existe um registro para este user_id+url
        check_query = "SELECT id FROM monitors WHERE user_id = %s AND url = %s"
        cursor.execute(check_query, (user_id, url))
        existing_record = cursor.fetchone()
        
        is_below: bool | None = None
        if desired_price is not None and price is not None:
            try:
                is_below = price < desired_price
            except Exception:
                is_below = None

        if existing_record:
            # Atualiza somente colunas enviadas
            set_parts = [
                "last_mined_at = CURRENT_TIMESTAMP",
                "next_mine_at = CURRENT_TIMESTAMP + INTERVAL '1 hour'",
                "updated_at = CURRENT_TIMESTAMP",
            ]
            params: list[object] = []

            if price is not None:
                set_parts.append("price = %s")
                params.append(price)
            if product_name is not None:
                set_parts.append("product_name = %s")
                params.append(product_name)
            if name is not None:
                set_parts.append("name = %s")
                params.append(name)
            if desired_price is not None:
                set_parts.append("desired_price = %s")
                params.append(desired_price)
                if is_below is not None:
                    set_parts.append("is_below_desired_price = %s")
                    params.append(is_below)
            if notification_platform is not None:
                set_parts.append("notification_platform = %s")
                params.append(notification_platform)

            update_query = f"""
            UPDATE monitors 
            SET {', '.join(set_parts)}
            WHERE user_id = %s AND url = %s
            """
            params.extend([user_id, url])
            cursor.execute(update_query, tuple(params))
        else:
            # Insere novo registro
            columns = ["user_id", "url", "store", "price", "product_name", "last_mined_at", "next_mine_at", "created_at"]
            values = [user_id, url, store, price, product_name,
                      "CURRENT_TIMESTAMP",
                      "CURRENT_TIMESTAMP + INTERVAL '1 hour'",
                      "CURRENT_TIMESTAMP"]
            placeholders = ["%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"]

            optional_cols = []
            optional_vals = []
            if name is not None:
                optional_cols.append("name")
                optional_vals.append(name)
            if desired_price is not None:
                optional_cols.append("desired_price")
                optional_vals.append(desired_price)
                if is_below is not None:
                    optional_cols.append("is_below_desired_price")
                    optional_vals.append(is_below)
            if notification_platform is not None:
                optional_cols.append("notification_platform")
                optional_vals.append(notification_platform)

            all_columns = columns + optional_cols
            all_placeholders = placeholders + ["%s"] * len(optional_cols)

            insert_query = f"""
            INSERT INTO monitors ({', '.join(all_columns)}) 
            VALUES ({', '.join(all_placeholders)})
            """
            cursor.execute(insert_query, tuple(values + optional_vals))
        
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
def aliexpress_scraper(request):
    """Google Cloud Function para extrair preços do AliExpress"""
    request_json = request.get_json(silent=True)
    
    if request_json and 'url' in request_json and 'userId' in request_json:
        url = request_json['url']
        user_id = request_json['userId']
        name = request_json.get('name')
        desired_price_raw = request_json.get('desiredPrice')
        notification_platform = request_json.get('notificationPlatform')
        desired_price_decimal = None
        scraper = AliexpressScraper(url)
        price = scraper.run()
        
        create_monitors_table()
        if desired_price_raw is not None:
            try:
                desired_price_decimal = Decimal(str(desired_price_raw))
            except Exception:
                desired_price_decimal = None
        
        save_success = save_price_to_db(
            user_id, url, 'aliexpress', price,
            name=name,
            desired_price=desired_price_decimal,
            notification_platform=notification_platform
        )
        
        return {
            'price': float(price) if price else None,
            'url': url,
            'name': name,
            'desiredPrice': float(desired_price_decimal) if desired_price_decimal is not None else None,
            'notificationPlatform': notification_platform,
            'userId': user_id,
            'store': 'aliexpress',
            'saved_to_db': save_success,
            'timestamp': datetime.now().isoformat()
        }
    
    return {'error': 'URL e/ou userId não fornecidos'}, 400
