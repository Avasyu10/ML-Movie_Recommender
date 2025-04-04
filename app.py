import streamlit as st
import pickle
import pandas as pd
import requests

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state for watchlist and ratings
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'ratings' not in st.session_state:
    st.session_state.ratings = {}
if 'temp_ratings' not in st.session_state:
    st.session_state.temp_ratings = {}

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url).json()
    
    poster_url = "https://image.tmdb.org/t/p/w500/" + response.get('poster_path', '')
    imdb_rating = round(response.get('vote_average', 0), 1)

    # Fetch trailer
    video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8"
    video_response = requests.get(video_url).json()
    trailer_key = next((video["key"] for video in video_response.get("results", []) if video["type"] == "Trailer"), None)
    trailer_link = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else "No trailer available"

    return poster_url, imdb_rating, trailer_link

def fetch_streaming_platforms(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key=8265bd1679663a7ea12ac168da84d2e8"
    response = requests.get(url).json()
    
    for country in ["IN", "US", "GB", "CA"]:
        providers = response.get("results", {}).get(country, {}).get("flatrate", [])
        if providers:
            return [provider["provider_name"] for provider in providers]
    
    return ["Not Available"]

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_ratings = []
    recommended_movies_trailers = []
    recommended_movies_streaming = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster, rating, trailer = fetch_movie_details(movie_id)
        streaming_platforms = fetch_streaming_platforms(movie_id)

        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(poster)
        recommended_movies_ratings.append(rating)
        recommended_movies_trailers.append(trailer)
        recommended_movies_streaming.append(streaming_platforms)

    return recommended_movies, recommended_movies_posters, recommended_movies_ratings, recommended_movies_trailers, recommended_movies_streaming

moviedict=pickle.load(open('moviedict.pkl','rb'))
movies=pd.DataFrame(moviedict)

similarity=pickle.load(open('similarity.pkl','rb'))

st.title("Movie Recommender System")
selected_movie = st.selectbox("Select your movie",movies['title'].values)

def save_rating(movie_name):
    if movie_name in st.session_state.temp_ratings:
        st.session_state.ratings[movie_name] = st.session_state.temp_ratings[movie_name]
        st.success(f"Rating submitted: {st.session_state.temp_ratings[movie_name]} ⭐ for {movie_name}")

def add_to_watchlist(movie_name):
    if movie_name not in st.session_state.watchlist:
        st.session_state.watchlist.append(movie_name)
        st.success(f"Added {movie_name} to Watchlist!")
    else:
        st.warning(f"{movie_name} is already in your Watchlist!")

if st.button("Recommend"):
    names, posters, ratings, trailers, streaming = recommend(selected_movie)
    for i in range(5):
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(posters[i], width=150)
            with col2:
                st.subheader(names[i])
                st.write(f"⭐ IMDb Rating: {ratings[i]}")
                st.markdown(f"[🎥 Watch Trailer]({trailers[i]})", unsafe_allow_html=True)
                st.write("📺 **Available On:**")
                for platform in streaming[i]:
                    st.markdown(f"- {platform}", unsafe_allow_html=True)
                
                # Ensure rating is stored in session state
                if names[i] not in st.session_state.temp_ratings:
                    st.session_state.temp_ratings[names[i]] = "5.0"  # Default rating
                
                # Use input instead of selectbox
                rating_key = f"rating_{i}"
                rating_value = st.text_input(
                    f"Rate {names[i]}", 
                    value=st.session_state.temp_ratings[names[i]], 
                    key=rating_key
                )
                
                # Submit button to save the rating
                if st.button(f"Submit Rating for {names[i]}", key=f"submit_rating_{i}"):
                    st.session_state.temp_ratings[names[i]] = rating_value
                    save_rating(names[i])
                
                # Watchlist feature
                st.button(f"Save to Watchlist", key=f"watchlist_{i}", on_click=add_to_watchlist, args=(names[i],))

# Sidebar Watchlist Display
st.sidebar.header("📌 Your Watchlist")
if st.session_state.watchlist:
    for movie in st.session_state.watchlist:
        st.sidebar.write(f"🎬 {movie}")
else:
    st.sidebar.write("Your watchlist is empty.")





