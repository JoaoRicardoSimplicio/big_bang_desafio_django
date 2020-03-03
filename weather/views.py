from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
import requests
from geopy.geocoders import Nominatim
import spotipy 
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from random import randint

# Create your views here.

def Initial(request):
    return render(request, 'page.html')



def ReturnWithError(request, message):
    messages.error(request, message);
    return redirect('initial');




def Consultar(request):
    if request.POST['address'] == "":
        
        message = 'Preencha o endereço';

        return ReturnWithError(request, message)

    elif request.POST['address'] != "":
        address_name = request.POST['address']

        datas_resul = GetTemperature(request, address_name)

        if datas_resul == "error1":
            message_error = "Não foi possível encontrar as coordenadas geográficas"
            return ReturnWithError(request, message_error)

        elif datas_resul == "error2":
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

        if tracks_list == "error3":
            message_error = "Não foi possível encontrar playlist adequada para seu 'Clima'!"
            return ReturnWithError(request, message_error) 
        elif tracks_list == "error4":
            message_error = "Houve um erro no momento de selecionar as músicas!"
            return ReturnWithError(request, message_error)

        tracks = TransformDataSpotify(tracks_list)   

        return render(request, 'playlist.html', { "playlists" : tracks, "datas_weaher" : datas_resul })




def TransformDataSpotify(tracks_list):
    tracks_data = []
    for track in tracks_list:
        new_track = dict()
        new_track['music'] = track['track']['album']['name']
        print(track['track']['album'], "\n")
        print(track['track']['album']['external_urls'], "\n\n\n")
        if track['track']['album']['external_urls']['spotify']:
            new_track['music_link'] = track['track']['album']['external_urls']['spotify']
        for artist in track['track']['album']['artists']:
            new_track['name'] = artist['name']
        for image in track['track']['album']['images']:
            new_track['image_link'] = image['url']
            break
        tracks_data.append(new_track)
    
    return tracks_data;




def GetTemperature(request, address_name):

    # Coordenadas Geográficas
    location = GetCoordinates(request, address_name)

    if location is None or location == "connection_error":
        return "error1"

    api_weather_data = ('http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid=aa6df645abaebf0db52dfe1e1965b4a0&units=metric' .format(location.latitude, location.longitude))

    resul_api = requests.get(api_weather_data)

    if resul_api is None or resul_api == " ":
        return "error2";

    # Filtra os dados que serão retornados
    datas_converted = ConvertData(resul_api)
    return datas_converted




def ConvertData(resul_api):

    resul_api_json = resul_api.json()

    temp_main = resul_api_json['main']

    

    datas_converted = ({
        "name_city" : resul_api_json['name'],
        "temperature" : (float(temp_main['temp'])),
        "temperature_max" : (float(temp_main['temp_max'])),
        "temperature_min" : (float(temp_main['temp_min'])),
    })

    return datas_converted




def GetCoordinates(request, address):
    
    geolocator = Nominatim()

    location = geolocator.geocode(address)

    return location




def ConnectSpotify():
    
    id = 'e4ee65ef097b4474932ce77b371808a1'

    secret = '64302df18d87452ea13389e40acf212e'
    
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=id, client_secret=secret)
        
        sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

        return sp
        
    except:
        return "error3"




def GetPlaylistSpotify(request, style):
    
    spotipy = ConnectSpotify()

    if spotipy == 'error3':
        return spotipy

    result = spotipy.search(q=('{0}-releases' .format(style)), type='playlist', limit=50)

    items_result = result['playlists']['items']

    id_playlist = items_result[randint(0, 49)]['id']

    playlist = spotipy.playlist(id_playlist)

    tracks = playlist['tracks']['items']

    if tracks is None or tracks == " ":
        return "error4"

    return tracks

