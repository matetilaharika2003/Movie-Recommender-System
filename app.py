import pickle
import streamlit as st
import requests
import pandas as pd
import time


# Function to fetch movie poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=78bcc3ec35343e1059efeb86562f0bc7&language=en-US"
    for _ in range(3):  # Retry up to 3 times
        try:
            data = requests.get(url).json()
            if data.get('poster_path'):
                return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"
        except requests.ConnectionError as e:
           # st.warning("Connection error. Retrying...")
            time.sleep(2)  # Wait for 2 seconds before retrying
    return "https://via.placeholder.com/500x750?text=No+Image"


# Function to fetch movie details (overview, release date, etc.)
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=78bcc3ec35343e1059efeb86562f0bc7&language=en-US"
    for _ in range(3):  # Retry up to 3 times
        try:
            data = requests.get(url).json()
            details = {
                "Title": data.get("title", "N/A"),
                "Overview": data.get("overview", "N/A"),
                "Release Date": data.get("release_date", "N/A"),
                "Vote Average": data.get("vote_average", "N/A"),
                "Popularity": data.get("popularity", "N/A")
            }
            return details
        except requests.ConnectionError as e:
            # st.warning("Connection error. Retrying...")
            time.sleep(2)  # Wait for 2 seconds before retrying
    return {
        "Title": "N/A",
        "Overview": "N/A",
        "Release Date": "N/A",
        "Vote Average": "N/A",
        "Popularity": "N/A"
    }


# The rest of your code remains unchanged...


# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []
    for i in distances[1:9]:  # Get top 8 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_ids.append(movie_id)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids


# Streamlit App
st.header('🎬 Movie Recommender System')
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Session state to manage selections and details
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False
if 'movie_details' not in st.session_state:
    st.session_state.movie_details = None
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None

# Left column for recommendations
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation') or st.session_state.show_recommendations:
    st.session_state.show_recommendations = True
    selected_movie_id = movies[movies['title'] == selected_movie].iloc[0].movie_id
    st.session_state.selected_movie_id = selected_movie_id
    selected_movie_poster = fetch_poster(selected_movie_id)

    # Fetch details for the selected movie and display them initially
    st.session_state.movie_details = fetch_movie_details(selected_movie_id)

    # Display selected movie and details
    st.subheader(f"Selected Movie: {selected_movie}")
    # st.image(selected_movie_poster, caption=selected_movie, use_column_width=True)
    st.image(
        selected_movie_poster,  # URL of the selected movie's poster
        caption=selected_movie,  # Caption with the movie title
        width=300,  # Set a fixed width for consistency
        use_column_width=False,  # Disable auto-adjusting to column width
        clamp=False,  # No clamping of colors
        channels='RGB',  # Standard RGB channel
        output_format='auto'  # Automatically determine the output format
    )

    # Display movie details
    if st.session_state.movie_details:
        st.subheader(f"Details for {st.session_state.movie_details['Title']}")
        st.write(f"*Overview*: {st.session_state.movie_details['Overview']}")
        st.write(f"*Release Date*: {st.session_state.movie_details['Release Date']}")
        st.write(f"*Vote Average*: {st.session_state.movie_details['Vote Average']}")
        st.write(f"*Popularity*: {st.session_state.movie_details['Popularity']}")

    # Get recommendations
    recommended_movie_names, recommended_movie_posters, recommended_movie_ids = recommend(selected_movie)

    st.subheader("Recommended Movies:")

    # Display recommended movies
    cols = st.columns(4)  # Create 5 columns for recommended movies
    for idx, col in enumerate(cols):
        if idx < len(recommended_movie_names):  # Ensure there are movies to display
            with col:
                st.image(recommended_movie_posters[idx], width=140, caption=recommended_movie_names[idx])
                # Create a unique key by combining the movie name with its index
                if st.button(f"Details", key=f"{recommended_movie_names[idx]}_{idx}_details"):
                    # Fetch and display the details of the recommended movie
                    recommended_movie_details = fetch_movie_details(recommended_movie_ids[idx])
                    st.subheader(f"Details for {recommended_movie_names[idx]}")
                    st.write(f"*Overview*: {recommended_movie_details['Overview']}")
                    st.write(f"*Release Date*: {recommended_movie_details['Release Date']}")
                    st.write(f"*Vote Average*: {recommended_movie_details['Vote Average']}")
                    st.write(f"*Popularity*: {recommended_movie_details['Popularity']}")