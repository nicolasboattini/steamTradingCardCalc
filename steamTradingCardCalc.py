"""
Copyriht R @nicoboattini alias deydade 2023
Steam Community Market Trading Cards Price Extractor
Useful to easily calculate rentability of selling trading cards for appid input game
"""
import requests
from prettytable import PrettyTable

# ID de la etiqueta de la aplicación de Steam del juego en cuestión
tag_app = "728880"
appid = tag_app

# ID de la moneda y prefijo para la representación de precios
currency_id = "34"  # ARS
currency_prefix = "ARS$"

# Obtener el nombre del juego con la ID de la aplicación de Steam
url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=ar"
response = requests.get(url)
if response.status_code == 200:
    data = response.json().get(str(appid))
    if data.get("success"):
        gamename = data.get("data").get("name")        
        precio = float((data.get("data").get("price_overview").get("final_formatted")).replace(f"{currency_prefix} ", "").replace(".", "").replace(",", "."))        
        

# Obtener los nombres y market_hash_name de los cromos
response = requests.get(f"https://steamcommunity.com/market/search/render/?query=trading+card&start=0&count=100&norender=1&appid=753&category_753_Game%5B%5D=tag_app_{tag_app}")

if response.status_code == 200:
    data = response.json()["results"]
    items = []
    if data:
        # Extraer el nombre de cada cromo y agregarlo a una lista
        items = [(item["hash_name"], item["sell_listings"]) for item in data]               
        obtenibles = (((1+len(items))/2)/2)
    else:
        print("No se encontraron resultados")
else:
    print(f"Error en la solicitud: {response.status_code}")
    items = []

article_data = {}
# Obtener los datos de cada cromo
for hash_name, sell_listings in items:
    response = requests.get("https://steamcommunity.com/market/priceoverview/",
                            params={"appid": 753,
                                    "currency": currency_id,
                                    "market_hash_name": hash_name})
    data = response.json()    
    if data:
        # Extraer los precios y la cantidad disponible para cada cromo
        min_price = float(data["lowest_price"].replace(f"{currency_prefix} ", "").replace(",", "."))
        avg_price = float(data["median_price"].replace(f"{currency_prefix} ", "").replace(",", "."))
        max_price = min_price * int(data["volume"])   
        volume = int(data["volume"])
        stock = sell_listings     
        article_data[hash_name] = {"min_price": min_price, "avg_price": avg_price, "max_price": max_price, "volume": volume, "stock": stock}
    else:
        print("fail")

# Imprimir los datos de los artículos ordenados por cantidad y precio promedio
def print_table(article_data):
    table = PrettyTable()
    table.field_names = ["Nombre", "Precio Min", "Precio Mid", "Precio Max", "24hs Sells", "Stock"]
    
    for name, data in sorted(article_data.items(), key=lambda x: (x[1]["max_price"], x[1]["avg_price"])):
        table.add_row([name, f"{data['min_price']} {currency_prefix}", f"{data['avg_price']} {currency_prefix}",
                       f"{data['max_price']} {currency_prefix}", data['volume'], data['stock']])
    print(f"         JUEGO: {gamename} Precio: {currency_prefix}{precio} Cromos Obtenibles: {round(obtenibles)}                         ")             
    print(table)
print_table(article_data)
print("¡El archivo se ejecutó correctamente!")