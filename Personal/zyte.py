import requests
from bs4 import BeautifulSoup
import time

api_response = requests.post(
    "https://api.zyte.com/v1/extract",
    auth=("867cfbf9cf314ecc892f2583a1a6dc36", ""),
    json={
        "url": "https://www.magazineluiza.com.br/smartphone-samsung-galaxy-a06-128gb-4gb-ram-azul-escuro-67-cam-dupla-selfie-8mp/p/238657700/te/ga06/",
        "browserHtml": True,
    },
)
browser_html: str = api_response.json()["browserHtml"]

# Extrair o preço do HTML
soup = BeautifulSoup(browser_html, 'html.parser')

# Buscar o elemento com data-testid="price-value"
price_element = soup.find('p', {'data-testid': 'price-value'})

if price_element:
    # Extrair o texto do elemento
    price_text = price_element.get_text(strip=True)
    print(f"Preço encontrado: {price_text}")
    
    # Limpar o preço (remover "R$" e espaços)
    price_clean = price_text.replace('R$', '').replace(' ', '').strip()
    print(f"Preço limpo: {price_clean}")
else:
    print("Preço não encontrado no HTML")

