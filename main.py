# -*- coding: utf-8 -*-
"""
moodmusic
"""

# #@title setup
# !pip install transformers librosa git+https://github.com/openai/whisper.git langchain-openai spotipy
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import torch
import librosa
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor

#@title analyze emotion
def load_audio(file_name):
    speech, _ = librosa.load(file_name, sr=16000, mono=True)
    return speech

# Load an audio file
file_name = "sad.m4a" #@param {type: "string"}
speech = load_audio(file_name)

model = Wav2Vec2ForSequenceClassification.from_pretrained("superb/wav2vec2-base-superb-er")
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/wav2vec2-base-superb-er")

# Compute attention masks and normalize the waveform if needed
inputs = feature_extractor(speech, sampling_rate=16000, padding=True, return_tensors="pt")

logits = model(**inputs).logits
predicted_ids = torch.argmax(logits, dim=-1)
labels = [model.config.id2label[_id] for _id in predicted_ids.tolist()]

print(labels)

#@title create playlist
def create_playlist(mood):
    # Authenticate with Spotify
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="",
                                                   client_secret="",
                                                   redirect_uri="localhost:8080",
                                                   scope="playlist-modify-public"))

    # Search for playlists that match the mood
    results = sp.search(q=f'playlist:{mood}', type='playlist', limit=1)
    playlist_id = results['playlists']['items'][0]['id']

    # Get tracks from the playlist
    tracks = sp.playlist_tracks(playlist_id)
    track_uris = [track['track']['uri'] for track in tracks['items']]

    # Create a new playlist with the tracks
    user_id = sp.me()['id']
    new_playlist = sp.user_playlist_create(user_id, f"{mood} Mood Playlist", public=True)
    sp.playlist_add_items(new_playlist['id'], track_uris)

    print(f"Playlist created: {new_playlist['external_urls']['spotify']}")

create_playlist("anger")