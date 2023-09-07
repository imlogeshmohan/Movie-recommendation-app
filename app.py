from flask import Flask, render_template, request
import pandas as pd
import pickle
import requests

app = Flask(__name__)

API = '798ed7f43336f360f4e1be7b3b90e92e'

def fetch_details(movie_id):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API}&language=en-US")
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie details: {e}")
        return None


def recommendation(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_movies_detail = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        data = fetch_details(movie_id)
        recommended_movies_detail.append(data)
        poster = "https://image.tmdb.org/t/p/w500/" + data["poster_path"]
        recommended_posters.append(poster)
    return recommended_movies, recommended_posters, recommended_movies_detail

movie_dict = pickle.load(open("movies_dict.pkl", 'rb'))
movies = pd.DataFrame(movie_dict)

similarity = pickle.load(open("similarity.pkl", 'rb'))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        selected_movie_name = request.form.get('selected_movie_name')
        recommended_movie_names, recommended_movie_posters, recommended_movie_details = recommendation(selected_movie_name)
    else:
        selected_movie_name = None
        recommended_movie_names = []
        recommended_movie_posters = []
        recommended_movie_details = []

    return render_template('index.html', title="Movie Recommender System", selected_movie_name=selected_movie_name, recommended_movie_names=recommended_movie_names, recommended_movie_posters=recommended_movie_posters, movies=movies, recommended_movie_details=recommended_movie_details)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
