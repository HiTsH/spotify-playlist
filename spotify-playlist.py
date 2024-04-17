import os
import time
import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By

# TODO 1: create user interface for the application
# TODO 2: Notify user to put the email and password of their spotify account for authentication
# TODO 3: Notify user that no data is collected
# TODO 4: Update Billboard URL scraping to allow use to choose region if possible
# TODO 5: Update Billboard URL scraping to capture the artist name
# TODO 6: Update the playlist to include artist name along with song name and convert from list to dict


# Constants
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']

# Create a SpotifyOAuth object and authenticate the user
spoauth = SpotifyOAuth(
    scope="playlist-modify-private",
    redirect_uri=REDIRECT_URI,
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    show_dialog=True,
    open_browser=True,
    cache_path="token.txt"
)

# Redirect the user to the Spotify authorization page
auth_url = spoauth.get_authorize_url()

# webbrowser.open(auth_url, new=0, autoraise=True)
print("Please authorize your app", auth_url)

# Define derivers and redirect to auth url for auto code collection
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
# url = webbrowser.open(url=auth_url,new=0, autoraise=True)
driver.get(auth_url)

# User email and password input for spotify
email = input("enter your email:  ")
password = input("enter your password: ")

# Fill out email/password and redirect to authenticated page
try:
    email_input = driver.find_element(by=By.ID, value='login-username')
    password_input = driver.find_element(by=By.ID, value='login-password')
    email_input.send_keys(email)
    password_input.send_keys(password)
    login_button = driver.find_element(by=By.ID, value='login-button')
    login_button.click()
    print('page found, login')
except:
    print('trying signing in...')
else:
    time.sleep(3)
    auth_button = driver.find_element(by=By.XPATH, value='/html/body/div/div/div[2]/main/div/main/section/div/div/div[5]/button')
    auth_button.click()
    print('button clicked')

# Capture the authenticated page URL
time.sleep(3)
currnet_url = driver.current_url
# print(currnet_url)

# Get the authorization code from the user
code = currnet_url.split('=')[1]
print(code)
    # driver.quit()

# Get the authorization code from the user
# code = input("Enter the authorization code: ")

# Exchange the authorization code for an access token
spoauth.get_access_token(code)

# Create a Spotify object using the access token
sp = spotipy.Spotify(auth_manager=spoauth)

# Get the current user ID
user_id = sp.current_user()["id"]


# Get user date for desired 100 top songs
user_date = input('Which year do you want to travel to? (YYYY-MM-DD): ')
year = user_date.split('-')[0]

# Webscraping billboard for the top 100 songs 
URL = f'https://www.billboard.com/charts/hot-100/{user_date}/'
response = requests.get(URL)
website_html = response.text

soup = BeautifulSoup(website_html, 'html.parser')
song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]

# create songs file and save the songs list.
with open(f'songs of {year}.text', 'w') as file:
    for song in song_names:
        file.write(f'{song}\n')

# Create a new playlist and obtain it's id
playlist_id = sp.user_playlist_create(user=user_id, name=f'Taste of year {year}', public=False, description='most popular hits for that year')

song_uris = []
for song in song_names:
    result = sp.search(q=f"track:{song}, year:{year}", type="track")
    # print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
        print(uri)
        
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Add songs to the playlist created
sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id['id'], tracks=song_uris)
print("Tracks successfully added to playlist.")
