import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import torch
import datetime
import librosa
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor

def load_audio(file):
    speech, _ = librosa.load(file, sr=16000, mono=True)
    return speech

def analyze_emotion(speech):
    model = Wav2Vec2ForSequenceClassification.from_pretrained("superb/wav2vec2-base-superb-er")
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/wav2vec2-base-superb-er")

    inputs = feature_extractor(speech, sampling_rate=16000, padding=True, return_tensors="pt")
    logits = model(**inputs).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    labels = [model.config.id2label[_id] for _id in predicted_ids.tolist()]
    return labels

def create_playlist(mood):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="b6de56e5e2a94e048e312579af966cb8",
                                                   client_secret="c1d54a60e8cf44b1b7087a4b9cfb37dd",
                                                   redirect_uri="http://localhost:8080",
                                                   scope="playlist-modify-public"))
    results = sp.search(q=f'playlist:{mood}', type='playlist', limit=1)
    playlist_id = results['playlists']['items'][0]['id']

    tracks = sp.playlist_tracks(playlist_id)
    track_uris = [track['track']['uri'] for track in tracks['items']]

    date = datetime.datetime.now().strftime("%d-%m-%Y")
    user_id = sp.me()['id']
    new_playlist = sp.user_playlist_create(user_id, f"{mood} {str(date)}", public=True)
    sp.playlist_add_items(new_playlist['id'], track_uris)

    return f"Playlist created: {new_playlist['external_urls']['spotify']}"

def main():
    st.title("Mood Music")
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])
    create_playlist_checkbox = st.checkbox("Create Spotify playlist", value=False)

    if uploaded_file is not None:
        speech = load_audio(uploaded_file)
        mood = analyze_emotion(speech)[0]
        st.write(f"Detected mood: {mood}")

        if create_playlist_checkbox:
            playlist_url = create_playlist(mood)
            st.write(playlist_url)

if __name__ == "__main__":
    main()
