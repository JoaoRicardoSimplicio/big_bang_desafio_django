from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
import requests
from geopy.geocoders import Nominatim
import spotipy 
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

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
            playlists = GetPlaylistSpotify(request, 'party')
            datas_resul['music_style'] = 'Party'
        
        elif datas_resul['temperature'] <= 30 and datas_resul['temperature'] >= 15:
            playlists = GetPlaylistSpotify(request, "pop")
            datas_resul['music_style'] = 'Pop'

        elif datas_resul['temperature'] < 15 and datas_resul['temperature'] >= 10:
            playlists = GetPlaylistSpotify(request, "rock")
            datas_resul['music_style'] = 'Rock'
         
        elif datas_resul['temperature'] < 10:
            playlists = GetPlaylistSpotify(request, 'classical music')
            datas_resul['music_style'] = 'Classical Music'

        if playlists == "error3":
            message_error = "Não foi possível encontrar playlist adequada para seu 'Clima'!"
            return ReturnWithError(request, message_error) 

        playlists_view = TransformDataSpotify(playlists)   

        return render(request, 'playlist.html', { "playlists" : playlists_view, "datas_weaher" : datas_resul })




def TransformDataSpotify(playlists):
    playlists_data = []
    for playlist in playlists.values():
        for about_playlist in (playlist.get('items')):
            items_playlist = ({
                "description" : about_playlist['description'],
                "name" : about_playlist['name'],
                "url" : about_playlist['external_urls']['spotify'],
                "image_datas" : about_playlist['images'][0]['url'],
            })
            if items_playlist['description'].find("</a>") > 1:
                string1 = items_playlist['description'].split('<a')
                string2 = string1[1].split(',')
                items_playlist['description'] = string1[0] + string2[1]
            playlists_data.append(items_playlist)
    
    return playlists_data;




def GetTemperature(request, address_name):

    # Coordenadas Geográficas
    location = GetCoordinates(request, address_name)

    if location == "error1":
        return location

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

    if location is None or location == " ":
        return "error1"
 
    return location




def ConnectSpotify():
    
    id = 'e4ee65ef097b4474932ce77b371808a1'

    secret = '64302df18d87452ea13389e40acf212e'

    client_credentials_manager = SpotifyClientCredentials(client_id=id, client_secret=secret)

    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    if sp is None or sp == " ":
        return "error3"

    return sp




def GetPlaylistSpotify(request, style):
    
    spotipy = ConnectSpotify()

    if spotipy == 'error3':
        return spotipy

    result = spotipy.search(q=style, type='playlist', limit=12)

    return result

