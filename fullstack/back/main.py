from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)
CORS(app)


try:
    df = pd.read_excel('./datasets/APIMOVIES.xlsx')
except FileNotFoundError:
    raise Exception("Archivo './datasets/APIMOVIES.xlsx' no encontrado. Verifica la ruta y el archivo.")


df.rename(columns={
    'Series_Title': 'title',
    'Genre': 'genres',
    'Released_Year': 'year',
    'Director': 'director',
    'Overview': 'overview'
}, inplace=True)


df['genres'] = df['genres'].fillna('').str.lower()
df['director'] = df['director'].fillna('').str.lower()
df['overview'] = df['overview'].fillna('').str.lower()
df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)


tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['overview'])


@app.route('/api/options/<category>', methods=['GET'])
def get_options(category):
    if category not in ['genres', 'director', 'year']:
        return jsonify({"error": f"La categoría '{category}' no es válida. Usa 'genres', 'director' o 'year'."}), 400


    options = df[category].unique()


    if category == 'year':
        options_list = sorted([int(year) for year in options if year > 0], reverse=True)
    else:
        options_list = sorted(set(options))

    return jsonify({category: options_list})


@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json()

    genre = data.get('genres', '').lower()
    director = data.get('director', '').lower()
    year = data.get('year')

    if not genre or not director or not year:
        return jsonify({"error": "Faltan parámetros de entrada. Asegúrese de proporcionar género, director y año."}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({"error": "El parámetro 'year' debe ser un número entero."}), 400


    filtered_df = df[
        (df['genres'].str.contains(rf'\b{genre}\b', case=False, na=False)) &
        (df['director'].str.contains(rf'\b{director}\b', case=False, na=False)) &
        (df['year'] == year)
    ]

    if filtered_df.empty:
        return jsonify({"error": "No se encontraron películas que coincidan con los filtros seleccionados."}), 404


    idx = filtered_df.index[0]
    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-6:-1][::-1]
    recommendations = df.iloc[similar_indices]['title'].tolist()

    return jsonify({"recommendations": recommendations})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
