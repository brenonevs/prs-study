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

def get_existing_desired_price(user_id: str, url: str) -> Decimal | None:
    """Busca o desired_price existente para user_id+url. Retorna Decimal ou None."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT desired_price FROM monitors WHERE user_id = %s AND url = %s", (user_id, url))
        row = cursor.fetchone()
        if row and row[0] is not None:
            try:
                return Decimal(str(row[0]))
            except Exception:
                return None
        return None
    except Exception:
        return None
    finally:
        cursor.close()
        conn.close()

def get_latest_price_from_history(monitor_id: int) -> Decimal | None:
    """Busca o preço mais recente do histórico para um monitor específico"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT price FROM price_history 
        WHERE monitor_id = %s 
        ORDER BY created_at DESC 
        LIMIT 1
        """
        cursor.execute(query, (monitor_id,))
        row = cursor.fetchone()
        
        if row and row[0] is not None:
            return Decimal(str(row[0]))
        return None
        
    except Exception:
        return None
    finally:
        cursor.close()
        conn.close()

def save_price_to_history(monitor_id: int, price: Decimal, store: str):
    """Salva um novo preço no histórico"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        insert_query = """
        INSERT INTO price_history (monitor_id, price, store) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (monitor_id, price, store))
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar histórico de preços: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def save_price_to_db(user_id: str, url: str, store: str, price: Decimal, name: str | None = None, *, desired_price: Decimal | None = None, notification_platform: str | None = None):
    """Salva ou atualiza dados do monitor para user_id+url. Atualiza apenas colunas recebidas."""
    print(f"Iniciando salvamento no banco: URL={url}, Store={store}, Price={price}, Name={name}")
    
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

        monitor_id = None
        if existing_record:
            monitor_id = existing_record[0]
            print(f"Registro existente encontrado (ID: {monitor_id}). Atualizando...")
            
            # Verificar se houve mudança de preço
            if price is not None:
                latest_price = get_latest_price_from_history(monitor_id)
                if latest_price is None or latest_price != price:
                    print(f"Preço alterado de {latest_price} para {price}. Salvando no histórico.")
                    save_price_to_history(monitor_id, price, store)
                else:
                    print(f"Preço mantido em {price}. Não salvando no histórico.")
            
            # Atualiza o registro existente com colunas enviadas
            set_parts = [
                "last_mined_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'",
                "next_mine_at = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour'",
                "updated_at = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'",
            ]
            params: list[object] = []

            if price is not None:
                set_parts.append("price = %s")
                params.append(price)
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
            conn.commit()
            print("Registro atualizado com sucesso")
        else:
            print("Nenhum registro existente. Inserindo novo registro...")
            # Insere novo registro com timestamps embutidos na query
            base_columns = ["user_id", "url", "store", "price", "name"]
            base_placeholders = ["%s", "%s", "%s", "%s", "%s"]
            values = [user_id, url, store, price, name]

            optional_cols = []
            optional_vals = []
            if desired_price is not None:
                optional_cols.append("desired_price")
                optional_vals.append(desired_price)
                if is_below is not None:
                    optional_cols.append("is_below_desired_price")
                    optional_vals.append(is_below)
            if notification_platform is not None:
                optional_cols.append("notification_platform")
                optional_vals.append(notification_platform)

            all_columns = base_columns + optional_cols
            all_placeholders = base_placeholders + ["%s"] * len(optional_cols)

            insert_query = f"""
            INSERT INTO monitors ({', '.join(all_columns)}, last_mined_at, next_mine_at, created_at) 
            VALUES ({', '.join(all_placeholders)}, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') + INTERVAL '1 hour', CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
            RETURNING id
            """
            cursor.execute(insert_query, tuple(values + optional_vals))
            new_record = cursor.fetchone()
            
            # Commit do monitor primeiro para garantir que o ID existe no banco
            conn.commit()
            
            if new_record:
                monitor_id = new_record[0]
                print(f"Novo registro inserido com sucesso (ID: {monitor_id})")
                
                # Salvar preço inicial no histórico
                if price is not None:
                    print(f"Salvando preço inicial {price} no histórico.")
                    save_price_to_history(monitor_id, price, store)
            else:
                print("Novo registro inserido com sucesso")
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
        name = request_json.get('name')
        desired_price_raw = request_json.get('desired_price')
        notification_platform = request_json.get('notification_platform')
        desired_price_decimal = None
        print(f"URL recebida: {url}")
        
        try:
            print("Criando instância do MagaluScraper")
            scraper = MagaluScraper(url)
            
            print("Executando scraping do preço")
            price = scraper.run()
            
            print("Criando tabela monitors (se não existir)")
            create_monitors_table()
            
            if desired_price_raw is not None:
                try:
                    desired_price_decimal = Decimal(str(desired_price_raw))
                except Exception:
                    desired_price_decimal = None
            else:
                desired_price_decimal = get_existing_desired_price(user_id, url)

            print("Salvando preço no banco de dados")
            save_success = save_price_to_db(
                user_id, url, 'magalu', price,
                name=name,
                desired_price=desired_price_decimal,
                notification_platform=notification_platform
            )
            
            response = {
                'price': float(price) if price else None,
                'url': url,
                'name': name,
                'desiredPrice': float(desired_price_decimal) if desired_price_decimal is not None else None,
                'notificationPlatform': notification_platform,
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
