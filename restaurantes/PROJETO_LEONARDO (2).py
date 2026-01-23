import time
import traceback
from multiprocessing import Pool, Manager
import pandas as pd
import requests
import urllib3
import warnings

warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

with open("TENTATIVAS.txt", 'r') as file:
    TENTA = int(file.read())

LATITUDE_PESQUISA = "-23.48511167789553"
LONGITUDE_PESQUISA = "-46.352385881847496"

HEADERS = {
    'Host': 'marketplace.ifood.com.br',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not(A:Brand";v="24", "Chromium";v="122"',
    'app_version': '9.102.44',
    'browser': 'Windows',
    'accept-language': 'pt-BR,pt;q=1',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'x-client-application-key': '41a266ee-51b7-4c37-9e9d-5cd331f280d5',
    'Accept': 'application/json, text/plain, */*',
    'Cache-Control': 'no-cache, no-store',
    'X-Ifood-Session-Id': '9304c3b5-350c-46b7-b97f-9fce88b2a252',
    'x-device-model': 'Windows Chrome',
    'platform': 'Desktop',
    'sec-ch-ua-platform': '"Windows"',
    'Origin': 'https://www.ifood.com.br',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.ifood.com.br/',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
}

CATEGORY_STRUCTURE = {
    "HOME_FOOD_DELIVERY": (1, 0),
    "MERCADO_BEBIDAS": (0, 4),
    "HOME_MERCADO_BR": (0, 5),
    "MERCADO_FARMACIA": (0, 6),
    "MERCADO_PETSHOP": (0, 5),
    "SHOPPING_OFICIAL": (0, 5)
}


def process_restaurant(ID, LATITUDE_PESQUISA, LONGITUDE_PESQUISA, dados_restaurantes):
    try:
        URL = f'https://marketplace.ifood.com.br/v1/merchant-info/graphql?latitude={LATITUDE_PESQUISA}&longitude={LONGITUDE_PESQUISA}&channel=IFOOD'
        PAYLOAD = {
            "query": "query ($merchantId: String!) { merchant (merchantId: $merchantId, required: true) { available availableForScheduling contextSetup { catalogGroup context regionGroup } currency deliveryFee { originalValue type value } deliveryMethods { catalogGroup deliveredBy id maxTime minTime mode originalValue priority schedule { now shifts { dayOfWeek endTime interval startTime } timeSlots { availableLoad date endDateTime endTime id isAvailable originalPrice price startDateTime startTime } } subtitle title type value state } deliveryTime distance features id mainCategory { code name } minimumOrderValue name paymentCodes preparationTime priceRange resources { fileName type } slug tags takeoutTime userRating } merchantExtra (merchantId: $merchantId, required: false) { address { city country district latitude longitude state streetName streetNumber timezone zipCode } categories { code description friendlyName } companyCode configs { bagItemNoteLength chargeDifferentToppingsMode nationalIdentificationNumberRequired orderNoteLength } deliveryTime description documents { CNPJ { type value } MCC { type value } } enabled features groups { externalId id name type } id locale mainCategory { code description friendlyName } merchantChain { externalId id name } metadata { ifoodClub { banner { action image priority title } } } minimumOrderValue name phoneIf priceRange resources { fileName type } shifts { dayOfWeek duration start } shortId tags takeoutTime test type userRatingCount } }",
            "variables": {"merchantId": f"{ID}"}
        }
        response = requests.post(URL, headers=HEADERS, json=PAYLOAD, verify=False)
        data = response.json()['data']
        merchant = data.get('merchant', {})
        merchant_extra = data.get('merchantExtra', {})
        address = merchant_extra.get('address', {})
        documents = merchant_extra.get('documents', {})
        cnpj = documents.get('CNPJ', {})

        SUPER_R = data.get('tags', '')
        SUPER = "SIM" if "SUPER_RESTAURANT" in SUPER_R else "NÃO"

        PRECO_MEDIO = merchant.get('priceRange', '')
        PRECO = {
            "CHEAPEST": "$",
            "CHEAP": "$$",
            "MODERATE": "$$$",
            "EXPENSIVE": "$$$$",
            "MOST_EXPENSIVE": "$$$$$"
        }.get(PRECO_MEDIO, PRECO_MEDIO)

        nova_linha = {
            "NOME": merchant.get('name', ''),
            "RUA": address.get('streetName', ''),
            "NUMERO": address.get('streetNumber', ''),
            "BAIRRO": address.get('district', ''),
            "CIDADE": address.get('city', ''),
            "CEP": address.get('zipCode', ''),
            "LATITUDE": address.get('latitude', ''),
            "LONGITUDE": address.get('longitude', ''),
            "CNPJ": cnpj.get('value', ''),
            "PRECO MEDIO": PRECO,
            "VALOR MINIMO": merchant_extra.get('minimumOrderValue', ''),
            "CATEGORIA": merchant.get('mainCategory', {}).get('name', ''),
            "AVALIACAO": merchant.get('userRating', ''),
            "TEMPO ENTREGA": merchant.get('deliveryTime', ''),
            "VALOR ORIGINAL": merchant.get('deliveryFee', {}).get('originalValue', ''),
            "SUPER RESTAURANTE": SUPER,
        }
        dados_restaurantes.append(nova_linha)
        print(f'PESQUISANDO CADA RESTAURANTE: {len(dados_restaurantes)}', end='\r')
    except:
        pass


def worker(params):
    ID, LATITUDE_PESQUISA, LONGITUDE_PESQUISA, dados_restaurantes = params
    process_restaurant(ID, LATITUDE_PESQUISA, LONGITUDE_PESQUISA, dados_restaurantes)


def fetch_ids(category_alias, LATITUDE_PESQUISA, LONGITUDE_PESQUISA):
    try:
        LISTA_ID = []
        URL = f'https://marketplace.ifood.com.br/v2/home?latitude={LATITUDE_PESQUISA}&longitude={LONGITUDE_PESQUISA}&channel=IFOOD&size=100&alias={category_alias}'
        PAYLOAD = {
            "supported-headers": ["OPERATION_HEADER"],
            "supported-cards": ["MERCHANT_LIST", "CATALOG_ITEM_LIST", "CATALOG_ITEM_LIST_V2", "CATALOG_ITEM_LIST_V3",
                                "FEATURED_MERCHANT_LIST", "CATALOG_ITEM_CAROUSEL", "CATALOG_ITEM_CAROUSEL_V2",
                                "CATALOG_ITEM_CAROUSEL_V3", "BIG_BANNER_CAROUSEL", "IMAGE_BANNER",
                                "MERCHANT_LIST_WITH_ITEMS_CAROUSEL", "SMALL_BANNER_CAROUSEL", "NEXT_CONTENT",
                                "MERCHANT_CAROUSEL", "MERCHANT_TILE_CAROUSEL", "SIMPLE_MERCHANT_CAROUSEL", "INFO_CARD",
                                "MERCHANT_LIST_V2", "ROUND_IMAGE_CAROUSEL", "BANNER_GRID", "MEDIUM_IMAGE_BANNER",
                                "MEDIUM_BANNER_CAROUSEL", "RELATED_SEARCH_CAROUSEL", "ADS_BANNER"],
            "supported-actions": ["catalog-item", "merchant", "page", "card-content", "last-restaurants",
                                  "webmiddleware", "reorder", "search", "groceries", "home-tab"],
            "feed-feature-name": "", "faster-overrides": ""
        }
        response = requests.post(URL, headers=HEADERS, json=PAYLOAD, verify=False)
        section_idx, card_idx = CATEGORY_STRUCTURE[category_alias]
        for content in response.json()['sections'][section_idx]['cards'][card_idx]['data']['contents']:
            LISTA_ID.append(content['id'])

        try:
            ACTION = str(response.json()['sections'][section_idx]['cards'][card_idx + 1]['data']['action']).split('cursor=')[1]
        except:
            print(f'{category_alias.upper()} ACHADOS: {len(LISTA_ID)}')
            return LISTA_ID
        ID_REFERENCIA = str(response.json()['sections'][section_idx]['id'])
        tenta = 0
        while True:
            time.sleep(1)
            try:
                URL = f'https://marketplace.ifood.com.br/v2/home?latitude={LATITUDE_PESQUISA}&longitude={LONGITUDE_PESQUISA}&channel=IFOOD&size=100&section={ID_REFERENCIA}&cursor={ACTION}&alias={category_alias}'
                response = requests.post(URL, headers=HEADERS, json=PAYLOAD, verify=False)
                lista_content = response.json()['sections'][section_idx]['cards'][card_idx]['data']['contents']
                ACTION = \
                str(response.json()['sections'][section_idx]['cards'][card_idx + 1]['data']['action']).split('cursor=')[
                    1]
                ID_REFERENCIA = str(response.json()['sections'][section_idx]['id'])

                for content in lista_content:
                    LISTA_ID.append(content['id'])

                print(f'{category_alias.upper()} ACHADOS: {len(LISTA_ID)}', end='\r')

                tenta = 0
            except:
                tenta += 1
                if tenta == TENTA:
                    break

        print(f'{category_alias.upper()} ACHADOS: {len(LISTA_ID)}')
        return LISTA_ID

    except Exception as e:
        traceback.print_exc()
        print(f'ERRO PLANILHA {category_alias.upper()} - CONTATE O ADM\n')
        return []


def fetch_and_process_ids(category_alias):
    TOTAL_IDS = []
    locations = [
        ("-23.44859826", "-46.38589552"),
        ("-23.4220173", "-46.32689839"),
        ("-23.47644759", "-46.2980699"),
        ("-23.47620027", "-46.32743982"),
        ("-23.47594743", "-46.35680932"),
        ("-23.50303844", "-46.35708664"),
        ("-23.44959731", "-46.26844066"),
        ("-23.44935583", "-46.29780498"),
        ("-23.44910883", "-46.3271689"),
        ("-23.44885631", "-46.35653242"),
    ]
    for lat, lon in locations:
        TOTAL_IDS.extend(fetch_ids(category_alias, lat, lon))

    TOTAL_IDS = list(set(TOTAL_IDS))
    manager = Manager()
    dados_restaurantes = manager.list()
    pool = Pool(processes=3)
    params = [(ID, LATITUDE_PESQUISA, LONGITUDE_PESQUISA, dados_restaurantes) for ID in TOTAL_IDS]
    pool.map(worker, params)
    pool.close()
    pool.join()

    print(f'GERANDO PLANILHA {category_alias.upper()}...')
    df_restaurantes = pd.DataFrame(list(dados_restaurantes), columns=[
        "NOME", "RUA", "NUMERO", "BAIRRO", "CIDADE", "CEP", "LATITUDE", "LONGITUDE", "CNPJ", "PRECO MEDIO",
        "VALOR MINIMO",
        "CATEGORIA", "AVALIACAO", "TEMPO ENTREGA", "VALOR ORIGINAL", "SUPER RESTAURANTE"
    ])
    df_restaurantes.to_excel(f"RESULTADO {category_alias.upper()} IFOOD.xlsx", index=False, engine='openpyxl')
    print(f"PLANILHA {category_alias.upper()} GERADA COM SUCESSO!\n")


def main():
    category_aliases = ["HOME_FOOD_DELIVERY"]
    for alias in category_aliases:
        fetch_and_process_ids(alias)

    input("\nPRESSIONE ENTER PARA FECHAR (ENTER):")


if __name__ == '__main__':
    main()
