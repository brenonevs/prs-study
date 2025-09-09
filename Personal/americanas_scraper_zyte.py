import requests
from bs4 import BeautifulSoup
import functions_framework
import psycopg2
from datetime import datetime
import os
import re
from decimal import Decimal


class AmericanasScraper:
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
        
        price_element = soup.find("div", class_="ProductPrice_productPrice__vpgdo")
        
        if price_element:
            price_text = price_element.get_text().strip()
            price_text = " ".join(price_text.split())
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
        name VARCHAR(500),
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
            
            # Verifica se o preço mudou comparando com o histórico mais recente
            if price is not None:
                latest_price = get_latest_price_from_history(monitor_id)
                if latest_price is None or latest_price != price:
                    # Preço mudou ou é o primeiro registro, salva no histórico
                    save_price_to_history(monitor_id, price, store)
            
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
            # Para updates, commit no final
            conn.commit()
        else:
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
            result = cursor.fetchone()
            
            # Commit do monitor primeiro para garantir que o ID existe no banco
            conn.commit()
            
            if result and price is not None:
                monitor_id = result[0]
                # Primeiro registro sempre vai para o histórico
                save_price_to_history(monitor_id, price, store)
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar no banco: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def send_email_notification(user_email: str, user_name: str, user_id: str, product_name: str, current_price: Decimal, desired_price: Decimal, product_url: str, store: str):
    """Envia notificação por e-mail quando preço fica abaixo do desejado"""
    try:
        email_data = {
            "user_email": user_email,
            "user_name": user_name,
            "user_id": user_id,
            "product_name": product_name,
            "current_price": float(current_price),
            "desired_price": float(desired_price),
            "product_url": product_url,
            "store": store
        }
        
        response = requests.post(
            "https://tagfy-resend-email-575184900812.southamerica-east1.run.app",
            json=email_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"E-mail de notificação enviado com sucesso para {user_email}")
            return True
        else:
            print(f"Erro ao enviar e-mail: Status {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro inesperado ao enviar e-mail de notificação: {e}")
        return False

@functions_framework.http
def americanas_scraper(request):
    """Google Cloud Function para extrair preços das Americanas"""
    request_json = request.get_json(silent=True)
    
    if request_json and 'url' in request_json and 'userId' in request_json:
        url = request_json['url']
        user_id = request_json['userId']
        name = request_json.get('name')
        desired_price_raw = request_json.get('desired_price')
        notification_platform = request_json.get('notification_platform')
        user_email = request_json.get('user_email')
        user_name = request_json.get('user_name')
        desired_price_decimal = None
        
        try:
            scraper = AmericanasScraper(url)
            price = scraper.run()
            
            create_monitors_table()
            if desired_price_raw is not None:
                try:
                    desired_price_decimal = Decimal(str(desired_price_raw))
                except Exception:
                    desired_price_decimal = None
            else:
                desired_price_decimal = get_existing_desired_price(user_id, url)

            save_success = save_price_to_db(
                user_id, url, 'americanas', price,
                name=name,
                desired_price=desired_price_decimal,
                notification_platform=notification_platform
            )
            
            # Verificar se deve enviar notificação por e-mail
            email_sent = False
            if (price is not None and desired_price_decimal is not None and 
                price < desired_price_decimal and user_email and user_name and 
                notification_platform == 'email'):
                email_sent = send_email_notification(
                    user_email=user_email,
                    user_name=user_name,
                    user_id=user_id,
                    product_name=name or "Produto Americanas",
                    current_price=price,
                    desired_price=desired_price_decimal,
                    product_url=url,
                    store='americanas'
                )
            
            return {
                'price': float(price) if price else None,
                'url': url,
                'name': name,
                'desiredPrice': float(desired_price_decimal) if desired_price_decimal is not None else None,
                'notificationPlatform': notification_platform,
                'userId': user_id,
                'store': 'americanas',
                'saved_to_db': save_success,
                'email_sent': email_sent,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na API do Zyte: {str(e)}"
            print(error_msg)
            return {
                'error': error_msg,
                'url': url,
                'store': 'americanas',
                'timestamp': datetime.now().isoformat()
            }, 502
            
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            print(error_msg)
            return {
                'error': error_msg,
                'url': url,
                'store': 'americanas',
                'timestamp': datetime.now().isoformat()
            }, 500
    
    return {'error': 'URL e/ou userId não fornecidos'}, 400