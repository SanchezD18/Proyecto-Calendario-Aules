import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from calendar_manager import CalendarManager

load_dotenv()

class AulesTimelineCrawler:
    def __init__(self, username, password):
        self.base_url = "https://aules.edu.gva.es/fp"
        self.username = username
        self.password = password
        self.driver = None
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    def login(self):
        try:
            print("🔧 Configurando ChromeDriver automáticamente...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            self.driver.implicitly_wait(10)
            
            login_url = f"{self.base_url}/login/index.php"
            print(f"🌐 Navegando a: {login_url}")
            
            self.driver.get(login_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "login"))
            )
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            username_field.clear()
            username_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)
            login_button = self.driver.find_element(By.ID, "loginbtn")
            login_button.click()
            WebDriverWait(self.driver, 15).until(
                lambda driver: 'dashboard' in driver.current_url or 'my' in driver.current_url or 'course' in driver.current_url
            )
            
            print("✅ Login exitoso")
            return True
            
        except TimeoutException:
            print("❌ Timeout durante el login")
            return False
        except Exception as e:
            print(f"💥 Error durante el login: {e}")
            return False
    
    def get_timeline_page(self):
        timeline_url = f"{self.base_url}/my/"
        try:
            print(f"🌐 Navegando a la cronología: {timeline_url}")
            self.driver.get(timeline_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "block_timeline"))
            )
            print("⏳ Esperando a que cargue el contenido dinámico de la cronología...")
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-region='event-list-content']"))
                )
                time.sleep(3)
                event_container = self.driver.find_element(By.CSS_SELECTOR, "[data-region='event-list-content']")
                
                if event_container.get_attribute('innerHTML').strip():
                    print("✅ Contenido de la cronología cargado correctamente")
                else:
                    print("⚠️ El contenedor de eventos está vacío")
                
            except TimeoutException:
                print("⚠️ Timeout esperando el contenido de la cronología")
            html_content = self.driver.page_source
            return html_content
            
        except Exception as e:
            print(f"💥 Error obteniendo la página de timeline: {e}")
            return None
    
    def extract_assignments_from_timeline(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        assignments = []
        print("🔍 Analizando estructura de la página...")
        event_container = soup.find('div', {'data-region': 'event-list-content'})
        
        if not event_container:
            print("❌ No se encontró el contenedor de eventos de la cronología")
            return []
        
        print(f"✅ Contenedor de eventos encontrado")
        event_items = event_container.find_all('div', class_='list-group-item')
        assignment_links = event_container.find_all('a', href=re.compile(r'/mod/assign/'))
        print(f"📋 Eventos encontrados: {len(event_items)} items, {len(assignment_links)} enlaces de tareas")
        processed_ids = set()
        for link in assignment_links:
            try:
                event_element = link.find_parent('div', class_='list-group-item')
                if not event_element:
                    event_element = link.find_parent(['div', 'li'])
                
                if not event_element:
                    continue
                assignment_info = self.parse_assignment_element(event_element, link)
                if assignment_info and assignment_info.get('id') not in processed_ids:
                    assignments.append(assignment_info)
                    processed_ids.add(assignment_info.get('id'))
                    
            except Exception as e:
                print(f"⚠️ Error procesando evento: {e}")
        
        return assignments
    
    def parse_assignment_element(self, element, link=None):
        try:
            if not link:
                link = element.find('a', href=re.compile(r'/mod/assign/'))
            if not link:
                return None
            id_match = re.search(r'id=(\d+)', link.get('href', ''))
            assignment_id = id_match.group(1) if id_match else None
            assignment_name = link.get_text(strip=True)
            meses_en = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                       'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
            meses_es = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                       'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}
            meses = {**meses_en, **meses_es}
            aria_label = link.get('aria-label', '')
            fecha_entrega = None
            hora = None
            fecha_timestamp = None
            fecha_pattern = r'vencerà el (\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(\d{4}),\s+(\d{1,2}):(\d{2})\s+(AM|PM)'
            fecha_match = re.search(fecha_pattern, aria_label, re.IGNORECASE)
            if fecha_match:
                dia = int(fecha_match.group(1))
                mes_nombre = fecha_match.group(2).lower()
                año = int(fecha_match.group(3))
                hora_num = int(fecha_match.group(4))
                minuto = fecha_match.group(5)
                am_pm = fecha_match.group(6).upper()
                mes_num = meses.get(mes_nombre, 1)
                if am_pm == 'PM' and hora_num != 12:
                    hora_num += 12
                elif am_pm == 'AM' and hora_num == 12:
                    hora_num = 0
                try:
                    fecha_timestamp = datetime(año, mes_num, dia, hora_num, int(minuto))
                    fecha_entrega = fecha_timestamp.strftime('%d/%m/%Y')
                    hora = fecha_timestamp.strftime('%H:%M')
                except ValueError:
                    pass
            if not fecha_timestamp:
                timestamp_container = element.find_parent('div', {'data-region': 'event-list-content-date'})
                if timestamp_container and timestamp_container.get('data-timestamp'):
                    try:
                        timestamp = int(timestamp_container.get('data-timestamp'))
                        fecha_timestamp = datetime.fromtimestamp(timestamp)
                        fecha_entrega = fecha_timestamp.strftime('%d/%m/%Y')
                        hora = fecha_timestamp.strftime('%H:%M')
                    except (ValueError, OSError):
                        pass
            if not fecha_entrega:
                text = element.get_text()
                date_pattern = r'\b(\d{1,2})\s+(?:de\s+)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+de)?\s+(\d{4})\b'
                time_pattern = r'\b(\d{1,2}):(\d{2})\b'
                date_match = re.search(date_pattern, text, re.IGNORECASE)
                time_match = re.search(time_pattern, text)
                if date_match:
                    dia = int(date_match.group(1))
                    mes_nombre = date_match.group(2).lower()
                    año = int(date_match.group(3))
                    mes_num = meses.get(mes_nombre, 1)
                    hora_num = 0
                    minuto = 0
                    if time_match:
                        hora_num = int(time_match.group(1))
                        minuto = int(time_match.group(2))
                    try:
                        fecha_timestamp = datetime(año, mes_num, dia, hora_num, minuto)
                        fecha_entrega = fecha_timestamp.strftime('%d/%m/%Y')
                        hora = fecha_timestamp.strftime('%H:%M')
                    except ValueError:
                        pass
            curso = None
            small_text = element.find('small', class_='mb-0')
            if small_text:
                curso_text = small_text.get_text(strip=True)
                if '·' in curso_text:
                    curso = curso_text.split('·')[-1].strip()
            
            return {
                'id': assignment_id,
                'nombre': assignment_name,
                'fecha_entrega': fecha_entrega or "No encontrada",
                'hora': hora or "No encontrada",
                'fecha_completa': fecha_timestamp.strftime('%d/%m/%Y %H:%M') if fecha_timestamp else "No encontrada",
                'curso': curso,
                'url': link.get('href', '') if link else ''
            }
            
        except Exception as e:
            print(f"⚠️ Error parseando elemento: {e}")
            import traceback
            traceback.print_exc()
            return None

    def crawl_assignments(self):
        try:
            if not self.login():
                print("❌ Error en el login")
                return []
            
            time.sleep(2)
            
            html = self.get_timeline_page()
            if not html:
                print("❌ No se pudo cargar la página")
                return []
            
            assignments = self.extract_assignments_from_timeline(html)
            return assignments
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Driver de Selenium cerrado")
    
    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

def main():
    USERNAME = os.getenv("AULES_USERNAME")
    PASSWORD = os.getenv("AULES_PASSWORD")
    
    if not USERNAME or not PASSWORD:
        print("❌ Error: Las variables AULES_USERNAME y AULES_PASSWORD deben estar definidas en el archivo .env")
        print("💡 Copia el archivo .env.example a .env y completa tus credenciales")
        return
    
    crawler = AulesTimelineCrawler(USERNAME, PASSWORD)
    
    print("🚀 Extrayendo entregas de Aules y agregándolas a Google Calendar...")
    
    try:
        assignments = crawler.crawl_assignments()
        
        if assignments:
            print(f"\n🎯 ENCONTRADAS {len(assignments)} ENTREGAS:")
            for i, assignment in enumerate(assignments, 1):
                print(f"   {i}. 📝 {assignment['nombre']} - 📅 {assignment['fecha_completa']}")
            
            print("\n" + "="*60)
            add_to_calendar = input("\n📅 ¿Agregar estas entregas a Google Calendar? (s/n): ").strip().lower()
            
            if add_to_calendar == 's':
                try:
                    print("\n🔐 Conectando con Google Calendar...")
                    calendar = CalendarManager()
                    
                    if calendar.service:
                        print(f"\n⏳ Creando {len(assignments)} eventos en el calendario...")
                        created_events = calendar.create_events_from_assignments(assignments)
                        
                        if created_events:
                            print(f"\n✅ ¡Éxito! Se crearon {len(created_events)} eventos en tu calendario de Google")
                            print(f"📅 Puedes verlos en: https://calendar.google.com/")
                        else:
                            print("\n⚠️ No se pudieron crear los eventos. Verifica las fechas y vuelve a intentar.")
                    else:
                        print("\n❌ No se pudo conectar con Google Calendar")
                        print("💡 Asegúrate de tener el archivo 'credentials.json' en la carpeta del proyecto")
                except Exception as e:
                    print(f"\n❌ Error al agregar eventos al calendario: {e}")
            else:
                print("\n📋 Operación cancelada. Las entregas no se agregaron al calendario.")
        else:
            print("\n❌ No se encontraron entregas pendientes.")
            
    except Exception as e:
        print(f"💥 Error durante la ejecución: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    main()