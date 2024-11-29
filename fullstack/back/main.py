from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

file_path = './datasets/APIMOVIES.xlsx'
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    raise Exception(f"Archivo '{file_path}' no encontrado. Verifica la ruta y el archivo.")

df.rename(columns={
    'Series_Title': 'title',
    'Genre': 'genres',
    'Released_Year': 'year',
    'No_of_Votes': 'votes'
}, inplace=True)

if 'votes' not in df.columns:
    raise Exception("El archivo cargado no contiene una columna 'No_of_Votes', necesaria para las recomendaciones.")

df['genres'] = df['genres'].fillna('').str.lower()
df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)

@app.route('/api/options/<category>', methods=['GET'])
def get_options(category):
    """
    Devuelve las opciones únicas para las categorías 'genres' o 'year'.
    """
    if category not in ['genres', 'year']:
        return jsonify({"error": f"La categoría '{category}' no es válida. Usa 'genres' o 'year'."}), 400

    options = df[category].unique()

    if category == 'year':
        options_list = sorted([int(year) for year in options if year > 0], reverse=True)
    else:
        options_list = sorted(set(options))

    return jsonify({category: options_list})

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Devuelve una lista de recomendaciones basadas en género y año,
    ordenadas por el número de votos.
    """
    data = request.get_json()

    genre = data.get('genres', '').lower()
    year = data.get('year')

    if not genre or not year:
        return jsonify({"error": "Faltan parámetros de entrada. Asegúrese de proporcionar género y año."}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({"error": "El parámetro 'year' debe ser un número entero."}), 400

    filtered_df = df[
        (df['genres'].str.contains(rf'\b{genre}\b', case=False, na=False)) &
        (df['year'] == year)
    ]

    if filtered_df.empty:
        return jsonify({"error": "No se encontraron películas que coincidan con los filtros seleccionados."}), 404

    sorted_df = filtered_df.sort_values(by='votes', ascending=False)

    recommendations = sorted_df.head(5)['title'].tolist()

    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
