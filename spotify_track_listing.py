#read playlists.json
import json
import requests
import pandas as pd
from math import ceil

print('enter your user id (e.g: https://open.spotify.com/user/captainbeefheart):')
user_id = input()

print('thank you, '+user_id+'.')

client_id = '<GET_UR_OWN_ID'
client_secret = '<GET_UR_OWN_SECRET>'

auth_url = 'https://accounts.spotify.com/api/token'

base_url = 'https://api.spotify.com/v1/'

data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
}

auth_response = requests.post(auth_url, data=data)
access_token = auth_response.json().get('access_token')


headers = {
    'Authorization': 'Bearer {}'.format(access_token),
}
#https://api.spotify.com/v1/users/116057239/playlists?limit=0&offset=100#
#we've got the access token now...
print('access token retrieved.')

##obtain total of playlists
print('obtaining total playlists')


playlists_endpoint = 'users/'+user_id+'/playlists?limit=0&offset=0'

playlists_url = ''.join([base_url,playlists_endpoint])

response = requests.get(playlists_url,headers=headers)
playlists = response.json()

playlistItems = playlists['items']
totalPlaylists = playlists['total']
print(str(totalPlaylists) +" playlists found...")
#got the playlists now...

total_calls = ceil((totalPlaylists / 20)) ## we can only get 20 playlists at a time

# put the playlists in their own data frame

playlists = {
    'href':[],
    'playlist_name':[]
}

offset = 0
p = 1
playlist_list = []
##add all the playlists to playlistsDf
while p < totalPlaylists+1: #can call up to 20 playlists at a time
    playlists_endpoint = 'users/'+str(user_id)+'/playlists?limit=20&offset='+str(offset)
    playlists_url = ''.join([base_url,playlists_endpoint])
    response = requests.get(playlists_url,headers=headers)
    playlists = response.json()
    playlistItems = playlists['items']
    i=0
    for playlists in playlistItems:
        p+=1
        playlist_list.append([playlistItems[i]['href'],playlistItems[i]['name']])
        i+=1
    offset += 20
    print('moving to next offset.. '+str(offset),end="\r")
playlistDf = pd.DataFrame(playlist_list, columns = ['href','playlist_name'])

playlistsDetailsTrimmed = {
                            'track_name':[],
                            'artist':[],
                            'album_title':[],
                            #'album_year':[],
                            'playlist_name':[],
                            'album_art':[]
    
}

df = pd.DataFrame(playlistsDetailsTrimmed)


for ind in playlistDf.index:  
    print("Extracting tracks for.........................." + playlistDf['playlist_name'][ind])
    href=playlistDf['href'][ind]
    playlist_name = playlistDf['playlist_name'][ind]
    pr = requests.get(href+'/tracks', headers=headers)
    pr_data = pr.json()
    if pr_data:
        playlist_data = pr_data['items']
        for tr in playlist_data:
            track = tr['track']
            if len(track['album']['images']) == 0:
                 album_art = ''
            else:
                album_art = track['album']['images'][0]['url']
            tracksDf = {
                'track_name':track['name'],
                'artist':track['artists'][0]['name'],
                'album_title':track['album']['name'],
                #'album_year':[],
                'playlist_name':playlist_name,
                'album_art':album_art
            }

            #print(tracksDf)
            df = pd.concat([df, pd.DataFrame([tracksDf])])
    i += 1
print("\r")
df.to_csv('Playlist_Extract_user_id_'+ user_id +'.csv',index=False)
print('finished creating extract')
playlistsDetailsTrimmed = {
                            'track_name':[],
                            'artist':[],
                            'album_title':[],
                            #'album_year':[],
                            'playlist_name':[],
                            'album_art':[]
    
}

df = pd.DataFrame(playlistsDetailsTrimmed)

