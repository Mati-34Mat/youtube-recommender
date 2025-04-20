# YouTube Recommender

Un script en Python que personaliza las recomendaciones de YouTube usando la YouTube Data API v3 y Machine Learning. Busca videos según categorías (ciencia, creatividad, programación, etc.), los rankea por engagement (likes/views) y relevancia (TF-IDF), y los agrega a una playlist personalizada.

## Características
- **Categorías predefinidas**: Ciencia y Tecnología, Creatividad, Programación, y más.
- **Ranking inteligente**: Combina likes/views con similitud de texto para recomendar videos relevantes.
- **Interfaz gráfica**: GUI simple con `tkinter` para elegir categorías.
- **Playlist personalizada**: Crea "Recomendaciones Personalizadas" en tu cuenta de YouTube.

## Instalación
1. **Requisitos**:
   - Python 3.8+
   - Linux (testado en Ubuntu) con `python3-tk` instalado:
     sudo apt install python3-tk
   - Clonar el repositorio:
     git clone https://github.com/tu-usuario/youtube-recommender.git
cd youtube-recommender
   - Crear entorno virtual:
     python -m venv venv
     source venv/bin/activate
   - Instalar dependencias:
     pip install google-api-python-client google-auth-oauthlib pandas scikit-learn
   - Configurar la API:
     Crea un proyecto en Google Cloud Console.
     Activa la YouTube Data API v3.
     Genera credenciales OAuth 2.0 (Desktop app) y descarga client_secret.json en la carpeta raíz.
     Agrega tu email como tester en OAuth Consent Screen.

## Uso
   - Crea el script:
      python recommender.py
   - En la GUI elige una cateogría, por ejemplo, Ciencia y Tecnología
   - Revisa la playlist "Recomendaciones Personalizadas" en YouTube.

## Notas
- Impacto: Los videos se agregan en segundos; el feed de YouTube mejora en 1-2 semanas.
- Cuotas: La API tiene un límite de ~10,000 unidades/día (~100 búsquedas).
- Mejoras futuras: Más peso a vistas, categorías personalizadas.

## Autor
Matías Berardo - Estudiante en el Instituto Politécnico Superior Gral. San Martín, apasionado por IA y ciencia

## Licencia
Este proyecto está licenciado bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
