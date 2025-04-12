import tkinter as tk
from tkinter import messagebox
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import isodate

# Configuración de la API
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = 'client_secret.json'  # Asumimos que está en la carpeta raíz'

# Categorías
CATEGORIES = {
    '1': {'name': 'Ciencia y Tecnología', 'keywords': ['ciencia', 'tecnología', 'IA', 'robótica', 'física']},
    '2': {'name': 'Creatividad e Innovación', 'keywords': ['creatividad', 'innovación', 'diseño', 'emprender']},
    '3': {'name': 'Ciencia Ficción y Futurismo', 'keywords': ['ciencia ficción', 'futurismo', 'ciberpunk']},
    '4': {'name': 'Programación y Desarrollo', 'keywords': ['programación', 'Python', 'blockchain', 'desarrollo']},
    '5': {'name': 'Sostenibilidad y Medio Ambiente', 'keywords': ['sostenibilidad', 'medio ambiente', 'tecnología verde']},
    '6': {'name': 'Filosofía y Pensamiento Crítico', 'keywords': ['filosofía', 'ética IA', 'pensamiento crítico']}
}

# Autenticación
def authenticate_youtube():
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=0)
        youtube = build('youtube', 'v3', credentials=credentials)
        if not hasattr(youtube, 'videos'):
            raise ValueError("Error al crear el servicio de YouTube")
        return youtube
    except Exception as e:
        raise Exception(f"Error en autenticación: {str(e)}")

# Crear o encontrar playlist
def get_or_create_playlist(youtube):
    try:
        # Buscar si existe "Recomendaciones Personalizadas"
        request = youtube.playlists().list(
            part='snippet',
            mine=True,
            maxResults=50
        )
        response = request.execute()
        for playlist in response.get('items', []):
            if playlist['snippet']['title'] == 'Recomendaciones Personalizadas':
                return playlist['id']
        
        # Si no existe, crear una
        request = youtube.playlists().insert(
            part='snippet',
            body={
                'snippet': {
                    'title': 'Recomendaciones Personalizadas',
                    'description': 'Videos recomendados por mi script personalizado'
                }
            }
        )
        response = request.execute()
        return response['id']
    except Exception as e:
        raise Exception(f"Error al crear playlist: {str(e)}")

# Buscar y rankear videos
import isodate

def search_videos(youtube, keywords, max_results=20):
    try:
        query = ' '.join(keywords)
        request = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            maxResults=max_results,
            safeSearch='moderate'
        )
        response = request.execute()
        video_ids = [item['id']['videoId'] for item in response['items'] if 'videoId' in item['id']]
        
        if not video_ids:
            return []
        
        request = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids)
        )
        stats = request.execute()
        
        videos = []
        for item in stats['items']:
            views = int(item['statistics'].get('viewCount', 0))
            likes = int(item['statistics'].get('likeCount', 0))
            title = item['snippet']['title']
            engagement = likes / (views + 1) if views > 0 else 0
            duration_str = item['contentDetails']['duration']
            duration_sec = isodate.parse_duration(duration_str).total_seconds()
            videos.append({
                'id': item['id'],
                'title': title,
                'views': views,
                'likes': likes,
                'engagement': engagement,
                'description': item['snippet'].get('description', ''),
                'duration_sec': duration_sec
            })
        
        # ML: Similitud con keywords
        corpus = [query] + [v['title'] + ' ' + v['description'] for v in videos]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Normalizar vistas
        max_views = max(v['views'] for v in videos) if videos else 1
        for i, video in enumerate(videos):
            normalized_views = (video['views'] / max_views) if max_views > 0 else 0
            # Peso por duración
            duration_min = video['duration_sec'] / 60
            if duration_min <= 1:
                duration_weight = 0.1
            elif 6 <= duration_min <= 30:
                duration_weight = 1.0
            else:
                duration_weight = 0.5
            video['score'] = (
                0.35 * normalized_views +
                0.25 * video['engagement'] +
                0.25 * similarities[i] +
                0.15 * duration_weight
            )
        
        return sorted(videos, key=lambda x: x['score'], reverse=True)[:5]
    except Exception as e:
        raise Exception(f"Error en búsqueda: {str(e)}")

# Agregar a playlist personalizada
def add_to_playlist(youtube, playlist_id, videos):
    try:
        for video in videos:
            youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {'kind': 'youtube#video', 'videoId': video['id']}
                    }
                }
            ).execute()
    except Exception as e:
        raise Exception(f"Error al agregar videos: {str(e)}")

# Interfaz gráfica
class RecommenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Recommender")
        self.youtube = None
        
        self.status_label = tk.Label(root, text="Listo para empezar")
        self.status_label.pack(pady=5)
        
        tk.Label(root, text="Elige una categoría para mejorar tus recomendaciones:").pack(pady=10)
        
        self.category_var = tk.StringVar()
        for key, value in CATEGORIES.items():
            tk.Radiobutton(
                root,
                text=value['name'],
                variable=self.category_var,
                value=key,
                anchor='w'
            ).pack(fill='x', padx=20)
        
        tk.Button(root, text="Personalizar YouTube", command=self.run_script).pack(pady=20)
    
    def run_script(self):
        if not self.category_var.get():
            messagebox.showerror("Error", "Por favor, elegí una categoría.")
            return
        
        self.status_label.config(text="Autenticando...")
        self.root.update()
        
        try:
            if not self.youtube:
                self.youtube = authenticate_youtube()
            
            self.status_label.config(text="Creando playlist...")
            self.root.update()
            playlist_id = get_or_create_playlist(self.youtube)
            
            self.status_label.config(text="Buscando videos...")
            self.root.update()
            
            keywords = CATEGORIES[self.category_var.get()]['keywords']
            videos = search_videos(self.youtube, keywords)
            
            if not videos:
                messagebox.showwarning("Advertencia", "No se encontraron videos. Intentá de nuevo.")
                return
            
            self.status_label.config(text="Agregando a playlist...")
            self.root.update()
            
            add_to_playlist(self.youtube, playlist_id, videos)
            
            self.status_label.config(text="¡Completado!")
            messagebox.showinfo("Éxito", "¡Listo! Revisa la playlist 'Recomendaciones Personalizadas' en YouTube.")
        except Exception as e:
            self.status_label.config(text="Error")
            messagebox.showerror("Error", f"Algo salió mal: {str(e)}")

# Ejecutar app
if __name__ == "__main__":
    root = tk.Tk()
    app = RecommenderApp(root)
    root.geometry("400x300")
    root.mainloop()
