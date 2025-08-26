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
    
    def fetch_product_html_via_scraperapi(self) -> str:
        try:
            payload = {
                "api_key": "9f5a0cdc28ed693568ca66e8a7baac2d",
                "url": self.url,
                "render": "true"
            }
            
            print(f"Iniciando requisição para ScraperAPI com URL: {self.url}")
            response = requests.get("https://api.scraperapi.com/", params=payload, timeout=3600)
            
            # Log do status da resposta para debug
            print(f"ScraperAPI Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"ScraperAPI Error Response: {response.text}")
                raise requests.exceptions.RequestException(f"ScraperAPI returned status {response.status_code}: {response.text}")
            
            print(f"HTML obtido com sucesso. Tamanho: {len(response.text)} caracteres")
            return response.text
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTPError from ScraperAPI: {e}")
            print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request error to ScraperAPI: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error with ScraperAPI: {e}")
            raise
    
    def extract_price_from_html(self, html: str) -> Decimal | None:
        print("Iniciando extração de preço do HTML")
        soup = BeautifulSoup(html, "html.parser")
        
        price_element = soup.find("p", attrs={"data-testid": "price-value"})
        
        if price_element:
            price_text = price_element.get_text().strip()
            print(f"Elemento de preço encontrado: '{price_text}'")
            print(f"HTML do elemento: {price_element}")
            
            # Remove "ou " do início se existir
            if price_text.startswith("ou "):
                price_text = price_text[3:].strip()
                print(f"Texto de preço após remoção do 'ou ': '{price_text}'")
            
            parsed_price = self._parse_price_to_decimal(price_text)
            print(f"Preço parseado: {parsed_price}")
            return parsed_price
        else:
            print("Elemento de preço não encontrado no HTML")
            # Tentar seletores alternativos
            print("Tentando seletores alternativos...")
            
            # Procurar por qualquer elemento com "R$" e que pareça um preço
            all_elements = soup.find_all(string=lambda text: text and "R$" in text)
            for elem in all_elements[:5]:  # Testar os 5 primeiros
                clean_text = elem.strip()
                print(f"Testando elemento alternativo: '{clean_text}'")
                if clean_text and not any(word in clean_text.lower() for word in ["10x", "cartão", "em", "vezes"]):
                    parsed_price = self._parse_price_to_decimal(clean_text)
                    if parsed_price:
                        print(f"Preço encontrado em seletor alternativo: {parsed_price}")
                        return parsed_price
        
        return None
    
    def _parse_price_to_decimal(self, price_text: str) -> Decimal | None:
        """Converte texto de preço para valor decimal considerando formato brasileiro"""
        print(f"Parseando preço: '{price_text}'")
        
        if not price_text:
            print("Texto de preço vazio")
            return None
        
        # Remove símbolos de moeda e espaços
        clean_text = re.sub(r'[R$\s]', '', price_text)
        print(f"Texto limpo após remoção de símbolos: '{clean_text}'")
        
        # Lógica para distinguir separador de milhares vs decimais
        # Se há vírgula, ela é o separador decimal, pontos são separadores de milhares
        if ',' in clean_text:
            # Formato: 1.234,56 -> remove pontos e substitui vírgula por ponto
            clean_text = clean_text.replace('.', '').replace(',', '.')
            print(f"Formato brasileiro detectado (vírgula decimal): '{clean_text}'")
        else:
            # Se não há vírgula, verifica se o ponto é separador decimal ou de milhares
            # Se há apenas um ponto e há exatamente 2 dígitos após ele, é decimal
            # Caso contrário, é separador de milhares
            dot_parts = clean_text.split('.')
            if len(dot_parts) == 2 and len(dot_parts[1]) == 2:
                # Formato: 1234.56 (decimal)
                print(f"Formato americano detectado (ponto decimal): '{clean_text}'")
                pass  # mantém como está
            else:
                # Formato: 1.234 ou 1.234.567 (separadores de milhares)
                clean_text = clean_text.replace('.', '')
                print(f"Separadores de milhares removidos: '{clean_text}'")
        
        # Extrai apenas números e ponto decimal
        price_match = re.search(r'\d+(?:\.\d{1,2})?', clean_text)
        
        if price_match:
            try:
                final_value = Decimal(price_match.group())
                print(f"Valor final parseado: {final_value}")
                return final_value
            except Exception as e:
                print(f"Erro ao converter para Decimal: {e}")
                return None
        
        print("Nenhum padrão de preço válido encontrado")
        return None
    
    def run(self) -> Decimal | None:
        html = self.fetch_product_html_via_scraperapi()
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
    print(f"Iniciando salvamento no banco: URL={url}, Store={store}, Price={price}, Product={product_name}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verifica se já existe um registro para este user_id+url
        check_query = "SELECT id FROM monitors WHERE user_id = %s AND url = %s"
        cursor.execute(check_query, (user_id, url))
        existing_record = cursor.fetchone()
        
        if existing_record:
            print(f"Registro existente encontrado (ID: {existing_record[0]}). Atualizando...")
            # Atualiza o registro existente
            update_query = """
            UPDATE monitors 
            SET price = %s, product_name = %s, last_mined_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', 
                next_mine_at = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour', updated_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo' 
            WHERE user_id = %s AND url = %s
            """
            cursor.execute(update_query, (price, product_name, user_id, url))
            print("Registro atualizado com sucesso")
        else:
            print("Nenhum registro existente. Inserindo novo registro...")
            # Insere novo registro
            insert_query = """
            INSERT INTO monitors (user_id, url, store, price, product_name, last_mined_at, next_mine_at, created_at) 
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour', CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
            """
            cursor.execute(insert_query, (user_id, url, store, price, product_name))
            print("Novo registro inserido com sucesso")
        
        conn.commit()
        print("Transação commitada com sucesso")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar no banco: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
        print("Conexão com banco fechada")

@functions_framework.http
def magalu_scraper(request):
    """Google Cloud Function para extrair preços do Magazine Luiza"""
    print("Iniciando execução da Cloud Function magalu_scraper")
    
    request_json = request.get_json(silent=True)
    
    if request_json and 'url' in request_json and 'userId' in request_json:
        url = request_json['url']
        user_id = request_json['userId']
        print(f"URL recebida: {url}")
        
        try:
            print("Criando instância do MagaluScraper")
            scraper = MagaluScraper(url)
            
            print("Executando scraping do preço")
            price = scraper.run()
            
            print("Criando tabela monitors (se não existir)")
            create_monitors_table()
            
            print("Salvando preço no banco de dados")
            save_success = save_price_to_db(user_id, url, 'magalu', price)
            
            response = {
                'price': float(price) if price else None,
                'url': url,
                'userId': user_id,
                'store': 'magalu',
                'saved_to_db': save_success,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"Scraping concluído com sucesso: {response}")
            return response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na API do ScraperAPI: {str(e)}"
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
    
    print("Erro: URL e/ou userId não fornecidos na requisição")
    return {'error': 'URL e/ou userId não fornecidos'}, 400
