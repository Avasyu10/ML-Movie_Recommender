import streamlit as st
import pickle
import pandas as pd
import requests


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def fetch_poster(movie_id):
    response=requests.get(url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id))
    data=response.json()
    poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    imdb_rating = data.get('vote_average', 'N/A')  # TMDb provides IMDb-style ratings
    return poster_url, imdb_rating
    
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_ratings = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster, rating = fetch_movie_details(movie_id)
        
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(poster)
        recommended_movies_ratings.append(rating)
    
    return recommended_movies, recommended_movies_posters, recommended_movies_ratings


moviedict=pickle.load(open('moviedict.pkl','rb'))
movies=pd.DataFrame(moviedict)

similarity=pickle.load(open('similarity.pkl','rb'))


st.title("Movie Recommender System")
selected_movie = st.selectbox("Select your movie",movies['title'].values)

if st.button("Recommend"):
    names, posters, ratings = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])
        st.write(f"⭐ IMDb Rating: {ratings[0]}")

    with col2:
        st.text(names[1])
        st.image(posters[1])
        st.write(f"⭐ IMDb Rating: {ratings[1]}")

    with col3:
        st.text(names[2])
        st.image(posters[2])
        st.write(f"⭐ IMDb Rating: {ratings[2]}")

    with col4:
        st.text(names[3])
        st.image(posters[3])
        st.write(f"⭐ IMDb Rating: {ratings[3]}")

    with col5:
        st.text(names[4])
        st.image(posters[4])
        st.write(f"⭐ IMDb Rating: {ratings[4]}")



