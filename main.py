from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import time

# the playlist you want to copy
print('REMEMBER TO MAKE YOUR SPOTIFY PLAYLIST PUBLIC')
SPOTIFY_PLAYLIST_ID = input("Spotify Playlist ID: ")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://open.spotify.com/playlist/' + SPOTIFY_PLAYLIST_ID)

time.sleep(3)

playlist_title = driver.find_element(By.CSS_SELECTOR, 'h1.Type__TypeElement-goli3j-0').text

# clicks the accept cookies button
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()

# zooms out on the page (we do this to get more songs to load on the page)
driver.execute_script("document.body.style.zoom='25%'")

# the children of this object is the tracks div
track_parent = driver.find_element(By.CSS_SELECTOR, '#main > div > div.Root__top-container > div.Root__main-view > div.main-view-container > div.os-host.os-host-foreign.os-theme-spotify.os-host-resize-disabled.os-host-scrollbar-horizontal-hidden.main-view-container__scroll-node.os-host-transition.os-host-overflow.os-host-overflow-y > div.os-padding > div > div > div.main-view-container__scroll-node-child > main > div > section > div.rezqw3Q4OEPB1m4rmwfw > div:nth-child(3) > div > div.JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2)')

# here is the tracks
tracks = track_parent.find_elements(By.XPATH, '*')

# here will the songs get stored
songs = []

# searching through the track div to find the right data
for track in tracks:
    # getting the name of the track
    song_name = track.find_element(By.XPATH, '*').find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[1].find_element(By.XPATH, '*').text

    # getting the artist
    artist = track.find_element(By.XPATH, '*').find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[1].find_element(By.XPATH, '*').text

    # If song is explicit search for the right artist name
    if artist == 'E':
        artist = track.find_element(By.XPATH, '*').find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[2].find_element(By.XPATH, '*').text

    songs.append({'title': song_name, 'artist': artist})


# scrolls down on the page so every track loads
body = driver.find_element(By.CSS_SELECTOR, 'body')
body.click()
body.send_keys(Keys.PAGE_DOWN)

# wait for every track to load
time.sleep(2)

track_parent = driver.find_element(By.CSS_SELECTOR, '#main > div > div.Root__top-container > div.Root__main-view > div.main-view-container > div.os-host.os-host-foreign.os-theme-spotify.os-host-resize-disabled.os-host-scrollbar-horizontal-hidden.main-view-container__scroll-node.os-host-transition.os-host-overflow.os-host-overflow-y > div.os-padding > div > div > div.main-view-container__scroll-node-child > main > div > section > div.rezqw3Q4OEPB1m4rmwfw > div:nth-child(3) > div > div.JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2)')

# gives a div of the track
tracks = track_parent.find_elements(By.XPATH, '*')

# searching through the track div to find the right data
for track in tracks:
    # getting the name of the track
    song_name = track.find_element(By.XPATH, '*').find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[1].find_element(By.XPATH, '*').text

    # getting the artist
    artist = track.find_element(By.XPATH, '*').find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[1].find_element(By.XPATH, '*').text

    # If song is explicit (fix the search)
    if artist == 'E':
        artist = track.find_element(By.XPATH, '*').find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[1].find_elements(By.XPATH, '*')[2].find_element(By.XPATH, '*').text

    songs.append({'title': song_name, 'artist': artist})

# here is the list of the not dupĺicated songs
no_duplicates_songs = [] 
for i in songs: 
    if i not in no_duplicates_songs: 
        no_duplicates_songs.append(i) 

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

client_secrets_file = "client_secret_CLIENTID.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_console()

def createPlaylist(title, description):
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": title,
            "description": description,
            # "tags": [
            #   "sample playlist",
            #   "API call"
            # ],
            "defaultLanguage": "en"
          },
          "status": {
            "privacyStatus": "private"
          }
        }
    )
    response = request.execute()

    return response['id']

# NOT EDITED
def add_to_playlist(playlist_id, video_id):

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": playlist_id,
            "position": 0,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": video_id
            }
          }
        }
    )
    response = request.execute()


playlist_id = createPlaylist(playlist_title, 'Created with \'Spotify Playlist To Youtube\' https://github.com/szoid007/spotify-to-youtube')

for i, song in enumerate(no_duplicates_songs):

    song['title'] = song['title'].replace(' ', '+')

    song['artist'] = song['artist'].replace(' ', '+')

    driver.get('https://www.youtube.com/results?search_query=' + song['title'] + '+' + song['artist'])

    time.sleep(3)

    if i == 0:
        driver.find_element(By.CSS_SELECTOR, 'ytd-button-renderer.ytd-consent-bump-v2-lightbox:nth-child(2) > a:nth-child(1)').click()
        continue

    full_link = driver.find_element(By.CSS_SELECTOR, 'html body ytd-app div#content.style-scope.ytd-app ytd-page-manager#page-manager.style-scope.ytd-app ytd-search.style-scope.ytd-page-manager div#container.style-scope.ytd-search ytd-two-column-search-results-renderer.style-scope.ytd-search div#primary.style-scope.ytd-two-column-search-results-renderer ytd-section-list-renderer.style-scope.ytd-two-column-search-results-renderer div#contents.style-scope.ytd-section-list-renderer ytd-item-section-renderer.style-scope.ytd-section-list-renderer div#contents.style-scope.ytd-item-section-renderer ytd-video-renderer.style-scope.ytd-item-section-renderer div#dismissible.style-scope.ytd-video-renderer ytd-thumbnail.style-scope.ytd-video-renderer a#thumbnail.yt-simple-endpoint.inline-block.style-scope.ytd-thumbnail').get_attribute('href')
    video_id = driver.find_element(By.CSS_SELECTOR, 'html body ytd-app div#content.style-scope.ytd-app ytd-page-manager#page-manager.style-scope.ytd-app ytd-search.style-scope.ytd-page-manager div#container.style-scope.ytd-search ytd-two-column-search-results-renderer.style-scope.ytd-search div#primary.style-scope.ytd-two-column-search-results-renderer ytd-section-list-renderer.style-scope.ytd-two-column-search-results-renderer div#contents.style-scope.ytd-section-list-renderer ytd-item-section-renderer.style-scope.ytd-section-list-renderer div#contents.style-scope.ytd-item-section-renderer ytd-video-renderer.style-scope.ytd-item-section-renderer div#dismissible.style-scope.ytd-video-renderer ytd-thumbnail.style-scope.ytd-video-renderer a#thumbnail.yt-simple-endpoint.inline-block.style-scope.ytd-thumbnail').get_attribute('href').split('=')[1]

    print(str(i) + '. ' + 'Added: ' + full_link + ' to playlist')
    add_to_playlist(playlist_id, video_id)

driver.quit()
