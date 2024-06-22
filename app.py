from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import urllib.request
from typing import Optional, Tuple
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RADIO_URL = "https://sv2.globalhostlive.com/proxy/bendistereo/stream2"  # URL da rádio fixa
SONG_HISTORY_LIMIT = 5
song_history = []  # Histórico de músicas
current_song = {"artist": "", "song": ""}

radio_monitoring_started = False  # Flag para indicar se o monitoramento já foi iniciado

def get_album_art(artist: str, song: str) -> Optional[str]:
    """Busca a capa do álbum na iTunes API."""
    try:
        response = requests.get(
            f"https://itunes.apple.com/search?term={artist}+{song}&media=music&limit=1"
        )
        response.raise_for_status() 
        data = response.json()
        if data["resultCount"] > 0:
            return data["results"][0]["artworkUrl100"].replace("100x100bb", "512x512bb")
        else:
            return None  # Retorna None se não encontrar a capa
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar capa do álbum: {e}")
        return None

def get_mp3_stream_title(streaming_url: str, interval: int) -> Optional[str]:
    needle = b'StreamTitle='
    ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'

    headers = {
        'Icy-MetaData': '1',
        'User-Agent': ua
    }

    req = urllib.request.Request(streaming_url, headers=headers)
    response = urllib.request.urlopen(req)

    meta_data_interval = None
    for key, value in response.headers.items():
        if key.lower() == 'icy-metaint':
            meta_data_interval = int(value)
            break

    if meta_data_interval is None:
        return None

    offset = 0
    while True:
        response.read(meta_data_interval)
        buffer = response.read(interval)
        title_index = buffer.find(needle)
        if title_index != -1:
            title = buffer[title_index + len(needle):].split(b';')[0].decode('utf-8')
            return title
        offset += meta_data_interval + interval

def extract_artist_and_song(title: str) -> Tuple[str, str]:
    # Remove as aspas simples extras
    title = title.strip("'")
    
    if '-' in title:
        artist, song = title.split('-', 1)
        return artist.strip(), song.strip()
    else:
        return '', title.strip()

async def monitor_radio(background_tasks: BackgroundTasks):
    global radio_monitoring_started, current_song, song_history
    if not radio_monitoring_started:
        radio_monitoring_started = True
        while True:
            title = get_mp3_stream_title(RADIO_URL, 19200)
            if title:
                artist, song = extract_artist_and_song(title)
                if artist != current_song["artist"] or song != current_song["song"]:
                    # Nova música detectada
                    if current_song["artist"] and current_song["song"]:
                        song_history.insert(0, current_song)
                        song_history = song_history[:SONG_HISTORY_LIMIT]
                    current_song = {"artist": artist, "song": song}
            await asyncio.sleep(10)

@app.get("/")
async def root():
    return {"message": "Bem vindo, estamos funcionando!"}

@app.get("/get_stream_title/")
async def get_stream_title(url: str, interval: Optional[int] = 19200):
    title = get_mp3_stream_title(url, interval)
    if title:
        artist, song = extract_artist_and_song(title)
        art_url = get_album_art(artist, song)  # Busca a capa do álbum
        return {"artist": artist, "song": song, "art": art_url}  # Retorna a URL da capa junto com as informações da música
    else:
        return {"error": "Failed to retrieve stream title"}
    
@app.get("/radio_info/")
async def get_radio_info(background_tasks: BackgroundTasks, radio_url: Optional[str] = Query(None)):
    if radio_url:
        return {
            "currentSong": "Free API Disabled",
            "currentArtist": "contact contato@jailson.es to free use"
        }
    else:
        background_tasks.add_task(monitor_radio, background_tasks)  # Inicia o monitoramento em segundo plano

        return {
            "currentSong": current_song["song"],
            "currentArtist": current_song["artist"],
            "songHistory": song_history,
        }
