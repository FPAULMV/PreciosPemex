# Importación de módulos de Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 

# Otros modulos
from webdriver_manager.chrome import ChromeDriverManager
from decouple import config
import time
import pyautogui

#----------------------------------------------------------------
# (Disabled)
# This module execute a webscraping to download a pdf 
# hosted in to Pemex web.

def web_scraping_pemex():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    try: 
        driver = webdriver.Chrome(service =ChromeService(ChromeDriverManager().install()),options=options) 
    except Exception as msg_error:
        print(f"""Error al validar: {msg_error}""")
        raise SystemExit(1)

    pagina_de_inicio = 'https://www.comercialrefinacion.pemex.com/portal/'
    pagina_de_precios = 'https://www.comercialrefinacion.pemex.com/portal/scafi038/controlador?Destino=scafi038_01.jsp'

    driver.maximize_window()
    while True:
        driver.get(pagina_de_inicio)
        driver.find_element(By.NAME,'usuario').send_keys(config('usuario_Pmx'))
        driver.find_element(By.NAME,'contrasena').send_keys(config('contrasena_pmx'))
        driver.find_element(By.NAME,'botonEntrar').click()
        try: 
            nombre_user_activo_pmx = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'textoEjecutivo')))
            break
        except:
            print('Usuario ocupado, reintentando.')
            
    driver.get(pagina_de_precios)
    ventana_original = driver.current_window_handle
    elemento = driver.find_element(By.XPATH, '//*[@id="maincontent"]/form/table/tbody/tr[2]/td/a').click()
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).click(elemento).key_up(Keys.CONTROL).perform()

    # Cambio a la paguina del PDF
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(10)
    pyautogui.hotkey('ctrl', 's')
    time.sleep(2)
    ruta_archivo = config('ruta_temp')
    pyautogui.write(ruta_archivo)
    pyautogui.press("enter")
    time.sleep(1)
    nombre_archivo = config('nombre_temp')
    pyautogui.write(nombre_archivo)
    pyautogui.press("enter")
    pyautogui.press("enter")
    driver.switch_to.window(ventana_original)

    while True:
        try:
            driver.find_element(By.XPATH,"//ul[@id='nav']/li[4]/a[1]").click()
            validacion = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,"//p[text()=' Contraseña : ']")))
            if validacion.text == 'Contraseña :':
                driver.quit()
                break
            else:
                break
        except:
            pass