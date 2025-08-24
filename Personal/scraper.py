import requests
from bs4 import BeautifulSoup
import time


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

        # Seleção preferencial: preço dentro do container principal de ofertas
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
        with open("html_amazon.html", "w", encoding="utf-8") as f:
            f.write(html)
        return self.extract_price_from_html(html)
    

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
    
    def extract_price_from_html(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        
        price_element = soup.find("span", class_="price-default--current--F8OlYIo")
        
        if price_element:
            return price_element.get_text().strip()
        
        return None
        
    def run(self) -> str | None:
        html = self.fetch_product_html_via_scraperapi()
        with open("html_aliexpress.html", "w", encoding="utf-8") as f:
            f.write(html)
        return self.extract_price_from_html(html)
    

class MercadoLivreScraper:
    def __init__(self, url: str):
        self.url = url
    
    def fetch_product_html_via_scraperapi(self) -> str:
        payload = {
            "api_key": "9f5a0cdc28ed693568ca66e8a7baac2d",
            "url": self.url,
        }
        response = requests.get("https://api.scraperapi.com/", params=payload, timeout=60)
        response.raise_for_status()
        return response.text
    
    def extract_price_from_html(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        
        # Busca pelo elemento que contém o preço no Mercado Livre
        price_element = soup.find("span", class_="andes-money-amount__fraction")
        cents_element = soup.find("span", class_="andes-money-amount__cents")
        
        if price_element:
            price_text = price_element.get_text().strip()
            if cents_element:
                cents_text = cents_element.get_text().strip()
                return f"R$ {price_text},{cents_text}"
            return f"R$ {price_text}"
        
        return None
    
    def run(self) -> str | None:

        html = self.fetch_product_html_via_scraperapi()
        with open("html_mercadolivre.html", "w", encoding="utf-8") as f:
            f.write(html)
        return self.extract_price_from_html(html)
    
class MagaluScraper:
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
    
    def extract_price_from_html(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        
        price_element = soup.find("p", attrs={"data-testid": "price-value"})
        
        if price_element:
            price_text = price_element.get_text().strip()
            if price_text.startswith("ou "):
                price_text = price_text[3:].strip()
            return price_text
        
        return None
    
    def run(self) -> str | None:
        html = self.fetch_product_html_via_scraperapi()
        with open("html_magalu.html", "w", encoding="utf-8") as f:
            f.write(html)
        return self.extract_price_from_html(html)
    
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
    
    def extract_price_from_html(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        
        price_element = soup.find("span", attrs={"data-testid": "price-value"})
        
        if price_element:
            price_text = price_element.get_text().strip()
            price_text = price_text.strip()
            if price_text:
                return f"R$ {price_text}"
        
        return None
    
    def run(self) -> str | None:
        html = self.fetch_product_html_via_scraperapi()
        with open("html_fastshop.html", "w", encoding="utf-8") as f:
            f.write(html)
        return self.extract_price_from_html(html)
    
class AmericanasScraper:
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
    
    def extract_price_from_html(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        
        price_element = soup.find("div", class_="ProductPrice_productPrice__vpgdo")
        
        if price_element:
            price_text = price_element.get_text().strip()
            price_text = " ".join(price_text.split())
            return price_text
        
        return None
    
    def run(self) -> str | None:
        html = self.fetch_product_html_via_scraperapi()
        with open("html_americanas.html", "w", encoding="utf-8") as f:
            f.write(html)
        return self.extract_price_from_html(html)
    
class CeAScraper:
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
    
    def extract_price_from_html(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        
        price_element = soup.find("p", class_="cea-cea-store-theme-2-x-spotPriceShelf__price")
        
        if price_element:
            return price_element.get_text().strip()
        
        return None
    
    def run(self) -> str | None:
        html = self.fetch_product_html_via_scraperapi()
        with open("html_ceasa.html", "w", encoding="utf-8") as f:
            f.write(html)
        return self.extract_price_from_html(html)
    


AMAZON_PRODUCT_URL = (
    "https://www.amazon.com.br/DUX-HUMAN-HEALTH-Suplementos-Suplementa%C3%A7%C3%A3o/dp/B09LQL2TR8/ref=sr_1_5_pp?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=IKUUZ5QNB2OD&dib=eyJ2IjoiMSJ9.SMINSj8NzjEBnYM_86KrcbQsqYYW3NQmvy40uJuaUGsq7s0IjoV70cqSCO9d4rw5dA7V9CnwT2b7Fubhqt-f5tmdqj6E2lPS6D8nAC20Ypo3BudIvWM-wmFyG6ihTALDAXVz-xl9CPtTHhHCuOkPIeQASofTfNPBf2KsniKRBt1w7arB7LqZ1wQzgbCBPjZoAYMWHMNVOo6s3RT6kkvDpBwA8XVGNRhY2JQZNoDBvK3h-5bRVppnDuSh9PV_36Wb6_Im32OGe3TcUGf8F6km9-QRJZ5KaRtyamZqrnzml8w.oWL4SJ2LWWqq3TOXaQKEN7kSv_u19CB6j_lGhm-Dzcw&dib_tag=se&keywords=whey&qid=1754965924&sprefix=whye%2Caps%2C236&sr=8-5&ufe=app_do%3Aamzn1.fos.6a09f7ec-d911-4889-ad70-de8dd83c8a74"
)

ALIEXPRESS_PRODUCT_URL = ( 
    "https://pt.aliexpress.com/item/1005009349573153.html?spm=a2g0o.productlist.main.1.71ac4WlK4WlKD2&algo_pvid=1b3c3b36-1d59-4473-bf09-0d991941609b&algo_exp_id=1b3c3b36-1d59-4473-bf09-0d991941609b-0&pdp_ext_f=%7B%22order%22%3A%222018%22%2C%22eval%22%3A%221%22%7D&pdp_npi=6%40dis%21BRL%214199.00%213774.00%21%21%214199.00%213774.00%21%402101c5a417556355055756732e4163%2112000048832529295%21sea%21BR%210%21ABX%211%210%21n_tag%3A-29910%3Bd%3A9671c48%3Bm03_new_user%3A-29895%3BpisId%3A5000000179929387&curPageLogUid=NxX1VxuWFm4r&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005009349573153%7C_p_origin_prod%3A"
)

MERCADO_LIVRE_PRODUCT_URL = (
    "https://www.mercadolivre.com.br/escova-modeladora-britnia-bec04-2-em-1-cor-branco/p/MLB19686524?pdp_filters=item_id:MLB5477039608#wid=MLB5477039608&sid=search&is_advertising=true&searchVariation=MLB19686524&backend_model=search-backend&position=2&search_layout=grid&type=pad&tracking_id=d7cf2c07-1a78-43d9-a7e6-8270408cfdee&is_advertising=true&ad_domain=VQCATCORE_LST&ad_position=2&ad_click_id=MzYyYjI4MTYtNzBiZi00M2NlLWFlZjItMTQzNzM3ZGIyMTM4"
)

MAGALU_PRODUCT_URL = (
    "https://www.magazineluiza.com.br/escrivaninha-maclavi-moveis-mesa-para-escritorio-industrial-mdf-de-150cm-x-60cm-branco/p/fe67f17581/mo/meav/"
)

FASTSHOP_PRODUCT_URL = (
    "https://site.fastshop.com.br/apple-watch-se--gps--44-mm--caixa-de-aluminio-meia-noite-pulseira-esportiva-meia-noite-aemxek3beapto_prd/p"
)

AMERICANAS_PRODUCT_URL = (
    "https://www.americanas.com.br/monitor-gamer-27-1ms-100hz-ips-amd-freesync-full-hd-hdmi-dp-frameless-hq-premium-hq27ip10-7513253891/p?idsku=662048"
)

CEA_PRODUCT_URL = (
    "https://www.cea.com.br/calca-jeans-wide-leg-slim-cintura-alta-azul-1067527-jeans-esc/p??pfm=rec"
)


if __name__ == "__main__":
    cea_scraper = CeAScraper(CEA_PRODUCT_URL)
    print("Preço do CEA:", cea_scraper.run())



