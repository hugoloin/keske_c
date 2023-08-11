from flask import Flask, render_template, request
import requests
from config import MOVIE_DB_API_KEY
import os

app = Flask(__name__)

TOKEN_TMDB = os.environ.get('MOVIE_DB_API_KEY')

# Correspondance des genres de film
genre_mapping = {
    "Action": "Action",
    "Adventure": "Aventure",
    "Comedy": "Comédie",
    "Animation": "Animation",
    "Crime": "Crime",
    "Documentary": "Documentaire",
    "Drama": "Drame",
    "Family": "Familial",
    "Fantasy": "Fantastique",
    "War": "Guerre",
    "History": "Histoire",
    "Horror": "Horreur",
    "Music": "Musique",
    "Mystery": "Mystère",
    "Romance": "Romance",
    "Science Fiction": "Science-Fiction",
    "Thriller": "Thriller",
    "TV movie": "Téléfilm",
    "Western": "Western",
}

def search_movie(api_key, movie_name):
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": movie_name,
        "language": "fr-FR"
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if "results" in data:
        results = data["results"]
        if results:
            return results[0]
    return None


def get_movie_details(api_key, movie_id):
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": api_key,
        "language": "fr-FR"
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    return data

def get_top_rated_movies(api_key):
    base_url = "https://api.themoviedb.org/3/movie/top_rated"
    params = {
        "api_key": api_key,
        "language": "fr-FR"
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    return data.get("results", [])


@app.route("/result/<int:movie_id>")
def result(movie_id):
    api_key = TOKEN_TMDB
    movie_details = get_movie_details(api_key, movie_id)

    # Traitez les détails du film et préparez les données pour le rendu
    genres_list = movie_details["genres"]
    genres_french = [genre_mapping.get(genre["name"], genre["name"]) for genre in genres_list]
    # Formater la valeur du budget en dollars avec séparateurs de milliers
    budget = "${:,}".format(movie_details["budget"])

    return render_template("result.html", movie=movie_details, genres=genres_french, budget=budget, runtime=movie_details["runtime"])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        api_key = TOKEN_TMDB
        movie_name = request.form["movie_name"]

        if movie_name.strip() == "":
            api_key = TOKEN_TMDB
            top_rated_movies = get_top_rated_movies(api_key)
            return render_template("index.html", top_rated_movies=top_rated_movies)
        else:
            movie = search_movie(api_key, movie_name)
            # Créez un dictionnaire de correspondance des genres

            if movie:
                movie_id = movie["id"]
                movie_details = get_movie_details(api_key, movie_id)
                # Construction de la liste des genres en français
                genres_list = movie_details["genres"]
                genres_french = [genre_mapping.get(genre["name"], genre["name"]) for genre in genres_list]
                # Formater la valeur du budget en dollars avec séparateurs de milliers
                budget = "${:,}".format(movie_details["budget"])
                return render_template("result.html", movie=movie, genres=genres_french, budget=budget, runtime=movie_details["runtime"])
            else:
                return render_template("index.html", top_rated_movies=top_rated_movies)
    else:
        api_key = TOKEN_TMDB
        top_rated_movies = get_top_rated_movies(api_key)
        return render_template("index.html", top_rated_movies=top_rated_movies)

if __name__ == "__main__":
    app.run(debug=True)
