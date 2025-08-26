import requests
from bs4 import BeautifulSoup
import functions_framework
import psycopg2
from datetime import datetime
import os
import re
from decimal import Decimal


class MagaluScraper:
    def __init__(self, url: str):
        self.url = url
    
    def fetch_product_html_via_zyte(self) -> str:
        try:
            api_response = requests.post(
                "https://api.zyte.com/v1/extract",
                auth=("867cfbf9cf314ecc892f2583a1a6dc36", ""),
                json={
                    "url": self.url,
                    "browserHtml": True,
                },
                timeout=3600  
            )
            
            # Log do status da resposta para debug
            print(f"Zyte API Status: {api_response.status_code}")
            
            if api_response.status_code != 200:
                print(f"Zyte API Error Response: {api_response.text}")
                raise requests.exceptions.RequestException(f"Zyte API returned status {api_response.status_code}: {api_response.text}")
            
            response_json = api_response.json()
            
            if "browserHtml" not in response_json:
                raise KeyError("browserHtml not found in Zyte API response")
                
            return response_json["browserHtml"]
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTPError from Zyte API: {e}")
            print(f"Response content: {api_response.text if 'api_response' in locals() else 'No response'}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request error to Zyte API: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error with Zyte API: {e}")
            raise
    
    def extract_price_from_html(self, html: str) -> Decimal | None:
        soup = BeautifulSoup(html, "html.parser")
        
        price_element = soup.find("p", attrs={"data-testid": "price-value"})
        
        if price_element:
            price_text = price_element.get_text().strip()
            if price_text.startswith("ou "):
                price_text = price_text[3:].strip()
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
        html = self.fetch_product_html_via_zyte()
        return self.extract_price_from_html(html)


def get_db_connection():
    """Estabelece conexão com o banco Neon PostgreSQL"""
    connection_string = "postgresql://neondb_owner:npg_MQphA3BFf0gP@ep-wispy-bonus-acat1phz-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    return psycopg2.connect(connection_string)

def create_monitors_table():
    """Cria a tabela monitors se ela não existir (com user_id e chave única user_id+url)."""
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
        last_mined_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
        next_mine_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour',
        created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
        updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
        UNIQUE (user_id, url)
    );
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def save_price_to_db(user_id: str, url: str, store: str, price: Decimal, product_name: str = None):
    """Salva ou atualiza o preço no banco de dados para user_id+url."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verifica se já existe um registro para este user_id+url
        check_query = "SELECT id FROM monitors WHERE user_id = %s AND url = %s"
        cursor.execute(check_query, (user_id, url))
        existing_record = cursor.fetchone()
        
        if existing_record:
            # Atualiza o registro existente
            update_query = """
            UPDATE monitors 
            SET price = %s, product_name = %s, last_mined_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', 
                next_mine_at = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour', updated_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo' 
            WHERE user_id = %s AND url = %s
            """
            cursor.execute(update_query, (price, product_name, user_id, url))
        else:
            # Insere novo registro
            insert_query = """
            INSERT INTO monitors (user_id, url, store, price, product_name, last_mined_at, next_mine_at, created_at) 
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour', CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
            """
            cursor.execute(insert_query, (user_id, url, store, price, product_name))
        
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
def magalu_scraper(request):
    """Google Cloud Function para extrair preços do Magazine Luiza"""
    request_json = request.get_json(silent=True)
    
    if request_json and 'url' in request_json and 'userId' in request_json:
        url = request_json['url']
        user_id = request_json['userId']
        
        try:
            scraper = MagaluScraper(url)
            price = scraper.run()
            
            create_monitors_table()
            save_success = save_price_to_db(user_id, url, 'magalu', price)
            
            return {
                'price': float(price) if price else None,
                'url': url,
                'userId': user_id,
                'store': 'magalu',
                'saved_to_db': save_success,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na API do Zyte: {str(e)}"
            print(error_msg)
            return {
                'error': error_msg,
                'url': url,
                'store': 'magalu',
                'timestamp': datetime.now().isoformat()
            }, 502
            
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            print(error_msg)
            return {
                'error': error_msg,
                'url': url,
                'store': 'magalu',
                'timestamp': datetime.now().isoformat()
            }, 500
    
    return {'error': 'URL e/ou userId não fornecidos'}, 400
