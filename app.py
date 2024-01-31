from flask import Flask, render_template, json, redirect, url_for
import plotly.express as px
import pandas as  pd
import matplotlib.pyplot as plt
from datetime import datetime


app = Flask(__name__)

# Assume que `data` é o JSON carregado de merged_files.json
with open('merged_files.json', 'r') as file:
    data = json.load(file)




def convert_dates_to_datetime(items):
    for item in items:
        if 'date' in item:
            # Converter date string para datetime object
            item['date'] = datetime.strptime(item['date'], '%Y/%m/%d')

# Dicionário auxiliar para mapear nomes originais para nomes renomeados
name_mapping = {}

def get_renamed_categories(data):
    unique_categories = set()
    renamed_categories = {}

    for category_name, items in data.items():
        category_display_name = category_name  # Use o nome original como padrão

        if items and 'name' in items[0]:
            category_display_name = items[0]['name'].split(',')[0].strip()

        # Verifica se o nome da categoria já está no conjunto
        while category_display_name in unique_categories:
            # Adiciona um sufixo para torná-lo único
            category_display_name += "_duplicate"

        unique_categories.add(category_display_name)
        renamed_categories[category_display_name] = {
            'category_name': category_name,
            'items': items
        }

        # Mapeia o nome original para o nome renomeado
        name_mapping[category_name] = category_display_name

    return renamed_categories

@app.route('/')
def index():
    renamed_categories = get_renamed_categories(data)
    return render_template('index.html', categories=renamed_categories, data=data)

@app.route('/categoria/<category_name>')
def categoria(category_name):
    # Tenta obter o nome renomeado usando o mapeamento
    renamed_name = name_mapping.get(category_name)

    # Se o nome renomeado está presente no mapeamento, redirecione para a rota original
    if renamed_name and renamed_name in data:
        return redirect(url_for('categoria', category_name=renamed_name))

    # Se o nome renomeado não estiver no mapeamento, exiba a categoria como de costume
    items = data.get(category_name, [])
    # Encontrar a entrada mais recente
    most_recent_entry = max(items, key=lambda x: x['date']) if items else None

    return render_template('category.html', category_name=category_name, items=items, most_recent_entry=most_recent_entry, categories=data)

@app.route('/categoria/<category_name>/detalhes')
def categoria_detalhes(category_name):
    items = data.get(category_name, [])

    if not items:
        return "Category not found"
    convert_dates_to_datetime(items)
    items.sort(key=lambda x: x['date'])
    items.sort(key=lambda x: x['date'])
    fig_istore = px.scatter(items, x='date', y='price_istore', title=f'Prices - iStore')
    graph_json_istore = fig_istore.to_json()

    fig_chip7 = px.scatter(items, x='date', y='price_chip7', title=f'Prices - Chip7')
    graph_json_chip7 = fig_chip7.to_json()

    fig_radiopop = px.scatter(items, x='date', y='price_radiopop', title=f'Prices - Radio Popular')
    graph_json_radiopop = fig_radiopop.to_json()

    return render_template('category_details.html',
                           category_name=category_name,
                           graph_json_istore=graph_json_istore,
                           graph_json_chip7=graph_json_chip7,
                           graph_json_radiopop=graph_json_radiopop, categories=data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
