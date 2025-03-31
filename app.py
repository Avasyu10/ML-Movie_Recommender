import streamlit as st
import pickle
import pandas as pd
import requests


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url).json()
    
    poster_url = "https://image.tmdb.org/t/p/w500/" + response.get('poster_path', '')
    imdb_rating = response.get('vote_average', 'N/A')

    # Fetch trailer
    video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8"
    video_response = requests.get(video_url).json()
    trailer_key = next((video["key"] for video in video_response.get("results", []) if video["type"] == "Trailer"), None)
    trailer_link = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else "No trailer available"

    return poster_url, imdb_rating, trailer_link
    return poster_url, imdb_rating
    
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_ratings = []
    recommended_movies_trailers = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster, rating, trailer = fetch_movie_details(movie_id)  

        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(poster)
        recommended_movies_ratings.append(rating)
        recommended_movies_trailers.append(trailer)

    return recommended_movies, recommended_movies_posters, recommended_movies_ratings, recommended_movies_trailers


moviedict=pickle.load(open('moviedict.pkl','rb'))
movies=pd.DataFrame(moviedict)

similarity=pickle.load(open('similarity.pkl','rb'))


st.title("Movie Recommender System")
selected_movie = st.selectbox("Select your movie",movies['title'].values)

if st.button("Recommend"):
    names, posters, ratings, trailers = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)

    for i, col in enumerate([col1, col2, col3, col4, col5]):
        with col:
            st.text(names[i])
            st.image(posters[i])
            st.write(f"⭐ IMDb Rating: {ratings[i]}")
            st.markdown(f"[🎥 Watch Trailer]({trailers[i]})", unsafe_allow_html=True)



