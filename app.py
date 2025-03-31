import streamlit as st
import pickle
import pandas as pd
import requests

# Load CSS for styling
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state for watchlist and ratings
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'ratings' not in st.session_state:
    st.session_state.ratings = {}

# Fetch movie details from TMDb API
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url).json()
    poster_url = "https://image.tmdb.org/t/p/w500/" + response.get('poster_path', '')
    imdb_rating = round(response.get('vote_average', 0), 1)
    
    video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8"
    video_response = requests.get(video_url).json()
    trailer_key = next((video["key"] for video in video_response.get("results", []) if video["type"] == "Trailer"), None)
    trailer_link = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else "No trailer available"
    
    return poster_url, imdb_rating, trailer_link

# Fetch streaming platforms
def fetch_streaming_platforms(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key=8265bd1679663a7ea12ac168da84d2e8"
    response = requests.get(url).json()
    
    for country in ["IN", "US", "GB", "CA"]:
        providers = response.get("results", {}).get(country, {}).get("flatrate", [])
        if providers:
            return [provider["provider_name"] for provider in providers]
    
    return ["Not Available"]

# Recommend movies based on similarity and user ratings
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies, posters, ratings, trailers, streaming = [], [], [], [], []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster, rating, trailer = fetch_movie_details(movie_id)
        platforms = fetch_streaming_platforms(movie_id)
        
        if movie in st.session_state.ratings:
            rating += st.session_state.ratings[movie] / 10  # Adjust based on user rating

        recommended_movies.append(movies.iloc[i[0]].title)
        posters.append(poster)
        ratings.append(round(rating, 1))
        trailers.append(trailer)
        streaming.append(platforms)
    
    return recommended_movies, posters, ratings, trailers, streaming

# Load movie data
moviedict = pickle.load(open('moviedict.pkl', 'rb'))
movies = pd.DataFrame(moviedict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("🎬 Movie Recommender System")
selected_movie = st.selectbox("Select your movie", movies['title'].values)

if st.button("Recommend"):
    names, posters, ratings, trailers, streaming = recommend(selected_movie)
    cols = st.columns(5)

    for i, col in enumerate(cols):
        with col:
            st.text(names[i])
            st.image(posters[i])
            st.write(f"⭐ IMDb Rating: {ratings[i]}")
            st.markdown(f"[🎥 Watch Trailer]({trailers[i]})", unsafe_allow_html=True)
            st.write("📺 **Available On:**")
            for platform in streaming[i]:
                st.markdown(f"- {platform}", unsafe_allow_html=True)
            
            if st.button(f"Save {names[i]} to Watchlist", key=f"watchlist_{i}"):
                st.session_state.watchlist.append(names[i])
                st.success(f"Added {names[i]} to Watchlist!")
            
            user_rating = st.slider(f"Rate {names[i]}", 0.0, 10.0, 5.0, key=f"rating_{i}")
            if st.button(f"Submit Rating for {names[i]}", key=f"submit_{i}"):
                st.session_state.ratings[names[i]] = user_rating
                st.success(f"Rating for {names[i]} saved!")

# Display Watchlist
st.sidebar.title("📌 Your Watchlist")
if st.session_state.watchlist:
    for movie in st.session_state.watchlist:
        st.sidebar.write(f"🎥 {movie}")
else:
    st.sidebar.write("No movies added to watchlist yet!")





