import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, CALENDAR_ID, EVENT_DURATION_HOURS


class CalendarManager:
    def __init__(self):
        self.service = None
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self):
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        if os.path.exists(GOOGLE_TOKEN_FILE):
            with open(GOOGLE_TOKEN_FILE, 'rb') as token:
                self.credentials = pickle.load(token)
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
                    print(f"❌ Error: No se encontró el archivo {GOOGLE_CREDENTIALS_FILE}")
                    print("📋 Para obtener las credenciales:")
                    print("1. Ve a https://console.developers.google.com/")
                    print("2. Crea un nuevo proyecto o selecciona uno existente")
                    print("3. Habilita la Google Calendar API")
                    print("4. Crea credenciales OAuth 2.0")
                    print("5. Descarga el archivo JSON y renómbralo como 'credentials.json'")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CREDENTIALS_FILE, SCOPES)
                self.credentials = flow.run_local_server(port=0)
            with open(GOOGLE_TOKEN_FILE, 'wb') as token:
                pickle.dump(self.credentials, token)
        try:
            self.service = build('calendar', 'v3', credentials=self.credentials)
            print("✅ Autenticación con Google Calendar exitosa")
        except Exception as e:
            print(f"❌ Error al conectar con Google Calendar: {e}")
    
    def create_event(self, title, start_date, description="", duration_hours=EVENT_DURATION_HOURS):
        if not self.service:
            print("❌ No se pudo conectar con Google Calendar")
            return None
        try:
            end_date = start_date + timedelta(hours=duration_hours)
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_date.isoformat(),
                    'timeZone': 'Europe/Madrid',
                },
                'end': {
                    'dateTime': end_date.isoformat(),
                    'timeZone': 'Europe/Madrid',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 60},
                    ],
                },
            }
            event_result = self.service.events().insert(
                calendarId=CALENDAR_ID, 
                body=event
            ).execute()
            
            print(f"✅ Evento creado: {title}")
            print(f"   📅 Fecha: {start_date.strftime('%d/%m/%Y %H:%M')}")
            print(f"   🔗 Enlace: {event_result.get('htmlLink')}")
            
            return event_result
            
        except HttpError as error:
            print(f"❌ Error al crear evento: {error}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None
    
    def create_events_from_assignments(self, assignments):
        created_events = []
        for assignment in assignments:
            nombre = assignment.get('nombre', 'Actividad sin nombre')
            fecha_completa = assignment.get('fecha_completa', '')
            curso = assignment.get('curso', '')
            url = assignment.get('url', '')
            fecha_timestamp = None
            if fecha_completa and fecha_completa != "No encontrada":
                try:
                    fecha_timestamp = datetime.strptime(fecha_completa, '%d/%m/%Y %H:%M')
                except ValueError:
                    try:
                        fecha_timestamp = datetime.strptime(fecha_completa, '%d/%m/%Y')
                    except ValueError:
                        print(f"⚠️ No se pudo parsear la fecha: {fecha_completa}")
                        continue
            if not fecha_timestamp:
                print(f"⚠️ Saltando actividad '{nombre}': fecha no válida")
                continue
            title = f"📝 {nombre}"
            description_parts = []
            if curso:
                description_parts.append(f"📚 Curso: {curso}")
            if url:
                description_parts.append(f"🔗 Enlace: {url}")
            description_parts.append(f"\n📅 Fecha de entrega: {fecha_completa}")
            description = "\n".join(description_parts)
            event = self.create_event(title, fecha_timestamp, description)
            if event:
                created_events.append(event)
        
        return created_events
    
    def list_upcoming_events(self, max_results=10):
        if not self.service:
            print("❌ No se pudo conectar con Google Calendar")
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                print("📅 No hay eventos próximos")
                return []
            
            print(f"📅 Próximos {len(events)} eventos:")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                title = event.get('summary', 'Sin título')
                print(f"   • {title} - {start}")
            
            return events
            
        except HttpError as error:
            print(f"❌ Error al listar eventos: {error}")
            return []

