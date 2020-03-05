from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib import messages

import requests

from geopy.geocoders import Nominatim

import spotipy 
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

from random import randint


def Initial(request):
    index_view = 'page.html'
    return render(request, index_view)


def ReturnWithError(request, message):
    messages.error(request, message)
    return redirect('initial')


def Consult(request):
    if request.POST['address'] == " ":
        message = 'Preencha o endereço'
        return ReturnWithError(request, message)

    elif request.POST['address'] != " ":
        address_name = request.POST['address']
        datas_resul = GetTemperature(request, address_name)

        if datas_resul == "geolocalization error":
            message_error = "Não foi possível encontrar as coordenadas geográficas"
            return ReturnWithError(request, message_error)

        elif datas_resul == "weather error":
            message_error = "Não foi possível encontrar dados climáticos"
            return ReturnWithError(request, message_error)


        if datas_resul['temperature'] > 30:
            style = "party"
            datas_resul['music_style'] = 'Party'
        
        elif datas_resul['temperature'] <= 30 and datas_resul['temperature'] >= 15:
            style = "pop"
            datas_resul['music_style'] = 'Pop'

        elif datas_resul['temperature'] < 15 and datas_resul['temperature'] >= 10:
            style = "rock"
            datas_resul['music_style'] = 'Rock'
         
        elif datas_resul['temperature'] < 10:
            style = "classical music"
            datas_resul['music_style'] = 'Classical Music'

        tracks_list = GetPlaylistSpotify(request, style)

        if tracks_list == "spotify api don't connected":
            message_error = "Não foi possível encontrar playlist adequada para seu 'Clima'!"
            return ReturnWithError(request, message_error) 

        elif tracks_list == "none playlist selected":
            message_error = "Houve um erro no momento de selecionar as músicas!"
            return ReturnWithError(request, message_error)

        tracks = TransformDataSpotify(tracks_list)   

        return render(request, 'playlist.html', {"playlists": tracks, "datas_weaher": datas_resul})


# This function extract tracks from selected playlist
def TransformDataSpotify(tracks_list):
    tracks_data = []
    for track in tracks_list:
        new_track = dict()
        new_track['music'] = track['track']['album']['name']
        if track['track']['album']['external_urls']:
            new_track['music_link'] = track['track']['album']['external_urls']['spotify']
        for artist in track['track']['album']['artists']:
            new_track['name'] = artist['name']
        for image in track['track']['album']['images']:
            new_track['image_link'] = image['url']
            break
        tracks_data.append(new_track) 
    return tracks_data;


# This function get data about weather using api OpenWeather
def GetTemperature(request, address_name):
    geolocalization = GetCoordinates(request, address_name);

    if geolocalization is None:
        type_error = "geolocalization error"
        return type_error

    api_weather_data = ('http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid=aa6df645abaebf0db52dfe1e1965b4a0&units=metric' .format(geolocalization.latitude, geolocalization.longitude))
    resul_api_weather = requests.get(api_weather_data)

    if resul_api_weather is None:
        return "weather error";

    datas_converted = ConvertData(resul_api_weather)
    return datas_converted


# Convert data from api OpenWeather to object 
def ConvertData(resul_api_weather):

    weather_data_json = resul_api_weather.json()

    temperature_data = weather_data_json['main']

    data_from_city = ({
        "name_city": weather_data_json['name'],
        "temperature": (float(temperature_data['temp'])),
        "temperature_max": (float(temperature_data['temp_max'])),
        "temperature_min": (float(temperature_data['temp_min'])),
    })

    return data_from_city


# This function get the coordinates of address passed 
def GetCoordinates(request, address):
    
    geolocator = Nominatim()

    geolocalization = geolocator.geocode(address)

    return geolocalization


# This function connect with spotify api
def ConnectSpotify():
    
    id = 'e4ee65ef097b4474932ce77b371808a1'

    secret = '64302df18d87452ea13389e40acf212e'
    
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=id, client_secret=secret)   
        spotipy_api = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
        return spotipy_api
    except:
        type_error = "spotify api don't connected"
        return type_error


# Get random number and select playlist based on that number
def GetPlaylistSpotify(request, style):
    spotipy = ConnectSpotify()

    if spotipy == "spotify api don't connected":
        return spotipy

    playlist_list = spotipy.search(q=('{0}-releases'.format(style)), type='playlist', limit=50)
    playlists = playlist_list['playlists']['items']
    id_playlist = playlists[randint(0, len(playlist_list))]['id']
    playlist_selected = spotipy.playlist(id_playlist)
    tracks = playlist_selected['tracks']['items']

    if tracks is None:
        type_error = "none playlist selected"
        return type_error
    return tracks

