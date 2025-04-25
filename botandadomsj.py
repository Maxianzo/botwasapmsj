import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 📌 Leer archivo CSV y normalizar nombres de columnas
df = pd.read_csv("pruevabot.csv", dtype={"phone": str})
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("á", "a").str.replace("é", "e")
df["last_interaction"] = pd.to_datetime(df["last_interaction"], errors="coerce")

# 📌 Verificar las primeras filas de los datos para ver cómo está la columna de cliente
print("Primeros registros:")
print(df.head())

# 📌 Total registros antes del filtro
print(f"Total registros antes del filtro: {len(df)}")

# 📌 Filtrar solo los contactos que no sean clientes
df_filtrado = df[
    (df["tag_es_cliente"].str.lower() == "no") &  # Solo contactos que NO son clientes
    (df["phone"].notna())  # Asegurarse de que el número de teléfono no sea nulo
]

# 📌 Verificar cuántos registros quedan después del filtro
print(f"Total registros después del filtro: {len(df_filtrado)}")

# Verificar si hay números para enviar
if len(df_filtrado) > 0:
    print(f"Se encontraron {len(df_filtrado)} contactos para enviar mensajes.")
else:
    print("No se encontraron contactos para enviar mensajes.")

# ✅ Mensaje a enviar
mensaje = """Hola buenos días, mi nombre es Maximiliano, vendedor de Distrolac.

Me han pasado su número desde el Chatbot de la empresa para consultarle si pudieron ver el PDF o si necesitan que se los reenvíe.

Cualquier cosa avíseme y se los reenvío. Si le sirve, los agrego al grupo de WhatsApp donde tengo a mis clientes y paso la información reciente de ofertas y cambios de precio.

Quedo a su disposición. ¡Muchas gracias!"""

# 📌 Configuración del navegador
profile_path = r"C:\Users\casa\AppData\Local\Google\Chrome\User Data"
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={profile_path}")
options.add_argument('--profile-directory=Default')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=options)
time.sleep(20)  # Aumentar el tiempo de espera para que el navegador se inicie correctamente

# 🔁 Enviar mensajes si se encontraron contactos
for index, row in df_filtrado.iterrows():
    numero = row["phone"].strip()
    if not numero.startswith("+"):
        numero = "+54" + numero  # Agregar prefijo internacional

    print(f"📲 Enviando mensaje a {numero}...")

    url = f"https://web.whatsapp.com/send?phone={numero}&source&data&app_absent"
    driver.get(url)
    time.sleep(20)  # Esperar más tiempo para que cargue la página

    try:
        msg_box = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@title='Escribe un mensaje aquí'] | //div[@contenteditable='true'][@data-tab='10']"))
        )
        msg_box.click()
        msg_box.send_keys(mensaje)
        msg_box.send_keys(Keys.ENTER)
        print("✅ Mensaje enviado.")
    except Exception as e:
        print(f"❌ Error al enviar mensaje a {numero}: {e}")

    time.sleep(5)

print("🎉 Todos los mensajes fueron enviados.")
