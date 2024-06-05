from flask import Flask, render_template, request, redirect, url_for, session
import requests
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16) 

JIKAN_API_BASE_URL = "https://api.jikan.moe/v4"
GENRE_PARAM = "genres"
TYPE_PARAM = "type"
SORT_PARAM = "sort"

class JikanAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_genres(self):
        try:
            response = requests.get(f"{self.base_url}/genres/anime")
            response.raise_for_status()
            return response.json()['data']
        except requests.RequestException as e:
            print(f"Error fetching genres: {e}")
            return []

    def fetch_anime_by_criteria(self, genre_id, anime_type, popularity):
        params = {
            GENRE_PARAM: genre_id,
            TYPE_PARAM: anime_type,
            SORT_PARAM: "desc"
        }
        try:
            response = requests.get(f"{self.base_url}/anime", params=params)
            response.raise_for_status()
            return response.json()['data']
        except requests.RequestException as e:
            print(f"Error fetching anime: {e}")
            return []

    def fetch_anime_details(self, anime_id):
        try:
            response = requests.get(f"{self.base_url}/anime/{anime_id}")
            response.raise_for_status()
            return response.json()['data']
        except requests.RequestException as e:
            print(f"Error fetching anime details: {e}")
            return None

jikan_api = JikanAPI(JIKAN_API_BASE_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    if request.method == 'POST':
        genre = request.form.get('genre')
        anime_type = request.form.get('type')
        popularity = request.form.get('popularity')
        return redirect(url_for('results', genre=genre, anime_type=anime_type, popularity=popularity))
    
    genres = jikan_api.fetch_genres()
    return render_template('questionnaire.html', genres=genres)

@app.route('/results')
def results():
    genre = request.args.get('genre')
    anime_type = request.args.get('type')
    popularity = request.args.get('popularity')
    
    if 'animes' not in session:
        animes = jikan_api.fetch_anime_by_criteria(genre, anime_type, popularity)
        session['animes'] = animes
    else:
        animes = session['animes']
    
    if animes:
        recommended_anime = random.choice(animes)  # Choose a random anime from the list
        anime_details = jikan_api.fetch_anime_details(recommended_anime['mal_id'])
        return render_template('results.html', anime=anime_details, back_url=url_for('questionnaire'))
    else:
        return render_template('results.html', anime=None, back_url=url_for('questionnaire'))


if __name__ == '__main__':
    app.run(debug=True)