import requests
import streamlit as st
import pickle
import pandas as pd

# Function to recommend anime based on name
def recommend_anime(anime_name, top_n=5):
    idx = animes[animes['name'] == anime_name].index[0]
    sim_scores = list(enumerate(overall_similarity.iloc[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n + 1]
    anime_indices = [i[0] for i in sim_scores]
    return animes[['name', 'genre', 'rating']].iloc[anime_indices]

# Function to recommend anime based on genre
def recommend_by_genre(genre_input, top_n=5):
    filtered = animes[animes['genre'].str.contains(genre_input, case=False, na=False)]
    return filtered[['name', 'genre', 'rating']].head(top_n)

# Function to fetch poster URL from AniList API
def get_anime_poster(anime_name):
    query = '''
    query ($search: String) {
      Media (search: $search, type: ANIME) {
        coverImage {
          large
        }
      }
    }
    '''
    variables = {'search': anime_name}
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        data = response.json()
        if data['data'] and data['data']['Media']:
            return data['data']['Media']['coverImage']['large']
    return None

# Load data
anime_dict = pickle.load(open('anime_dict.pkl', 'rb'))
overall_similarity = pickle.load(open('similarity.pkl', 'rb'))
animes = pd.DataFrame(anime_dict)

# Streamlit app
st.title('Anime Recommender')

search_type = st.radio("How would you like to search?", ['Search by Anime Name', 'Search by Genre'])

if search_type == 'Search by Anime Name':
    selected_anime_name = st.selectbox("Choose an anime", animes['name'].values)
    if st.button('Get Recommendations'):
        recommendations = recommend_anime(selected_anime_name)
        st.subheader("Recommended Animes:")
        for i in range(0, len(recommendations), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(recommendations):
                    anime_name = recommendations.iloc[i + j]['name']
                    with col:
                        poster_url = get_anime_poster(anime_name)
                        if poster_url:
                            st.image(poster_url, width=150)
                        else:
                            st.write("Poster not available")
                        st.write(f"**{anime_name}**")
                        st.write(f"Genre: {recommendations.iloc[i + j]['genre']}")
                        st.write(f"Rating: {recommendations.iloc[i + j]['rating']}")

elif search_type == 'Search by Genre':
    genre_input = st.text_input("Enter a genre (e.g., Action, Romance, Sci-Fi)")
    if st.button('Find by Genre'):
        genre_recommendations = recommend_by_genre(genre_input)
        if genre_recommendations.empty:
            st.warning("No anime found with this genre.")
        else:
            st.subheader("Animes from that Genre:")
            for i in range(0, len(genre_recommendations), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(genre_recommendations):
                        anime_name = genre_recommendations.iloc[i + j]['name']
                        with col:
                            poster_url = get_anime_poster(anime_name)
                            if poster_url:
                                st.image(poster_url, width=150)
                            else:
                                st.write("Poster not available")
                            st.write(f"**{anime_name}**")
                            st.write(f"Genre: {genre_recommendations.iloc[i + j]['genre']}")
                            st.write(f"Rating: {genre_recommendations.iloc[i + j]['rating']}")
