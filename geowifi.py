import json
import subprocess
import asyncio
import winsdk.windows.devices.geolocation as wdg
import mapacalor
import time
import sys
import ctypes
import re
import shutil
import os

#¿Estás cómo administrador?
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Variables Globales
interfaz_seleccionada = "sin_interfaz"
nombre_interfaz = ""

async def getCoords():
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    return [pos.coordinate.latitude, pos.coordinate.longitude]

def obtener_redes_wifi():
    if is_admin():
        print("\n\nLo estamos ejecutando cómo administrador las mediciones serán más precisas\n\n")
        # Tumbamos red
        comando = 'netsh interface set interface name="%s" admin=disabled' % nombre_interfaz

        try:
            # Ejecutar el comando sin capturar la salida
            subprocess.run(comando, check=True)
            print("\n...Estamos reiniciando el adaptador de red...\n")
        except subprocess.CalledProcessError:
            print("Error al tumbar el adaptador ¿Estás ejecutando cómo administrador?")
            sys.exit()

        time.sleep(2)

        #Levantamos red
        comando = 'netsh interface set interface name="%s" admin=enabled' % nombre_interfaz

        try:
            # Ejecutar el comando sin capturar la salida
            subprocess.run(comando, check=True)
            print("\n...Terminando de reiniciar el adaptador de red...\n")
        except subprocess.CalledProcessError:
            print("Error al levantar el adaptador ¿Estás ejecutando cómo administrador?")
            sys.exit()

        #Esperamos 7 segundos
        print("\n...Escaneando la red...\n")
        time.sleep(7)
    else:
        print("""\n\nNo lo estás ejecutando como administrador, ten en cuenta que habrá un tiempo de espera 
hasta que Windows vuelva a escanear las redes y las mediciones pueden ser erróneas
se recomienda ejecutar cómo administrador o usar tiempos de espera largos entre mediciones\n\n""")

    # Ejecuta el comando para obtener información de las redes WiFi cercanas en Windows
    cmd = ['netsh', 'wlan', 'show', 'network', 'mode=Bssid', 'interface=%s' % nombre_interfaz]
    output = subprocess.check_output(cmd, shell=True)
    output = output.decode('utf8', errors='ignore')
    redes_wifi = output.strip().split('\r\n\r\n')

    redes = []

    for red_info in redes_wifi:
        red_actual = {}
        lineas = red_info.split('\r\n')

        for linea in lineas:
            if linea.startswith('SSID'):
                red_actual['ssid'] = linea.split(':', 1)[1].strip()
            elif ':' in linea:
                clave, valor = linea.split(':', 1)
                red_actual[clave.strip().lower()] = valor.strip()

        if red_actual:
            redes.append(red_actual)

    return redes

def obtener_localizacion_gps():
    try:
        return asyncio.run(getCoords())
    except PermissionError:
        print("ERROR: You need to allow applications to access you location in Windows settings")

def almacenar_informacion(nombre, ubicacion, redes_wifi):
    # Carga los datos existentes del archivo JSON
    datos_existentes = []
    try:
        with open('informacion.json', 'r', encoding='utf-8') as archivo:
            datos_existentes = json.load(archivo)
    except FileNotFoundError:
        pass
    
    # Crea un diccionario con la información a almacenar
    informacion = {
        'nombre': nombre,
        'ubicacion': ubicacion,
        'redes_wifi': redes_wifi
    }
    
    # Agrega los nuevos datos a la lista existente
    datos_existentes.append(informacion)
    
    # Escribe los datos completos en el archivo JSON con encoding utf-8
    with open('informacion.json', 'w', encoding='utf-8') as archivo:
        json.dump(datos_existentes, archivo, ensure_ascii=False)

def puntos_de_control():
    subprocess.call('cls', shell=True)
    while True:
        nombre = input('¿Cómo llamar al siguiente punto? (Escribe "exit" para salir): ')
        
        if nombre.lower() == 'exit':
            break
        
        ubicacion = obtener_localizacion_gps()
        redes_wifi = obtener_redes_wifi()
        
        almacenar_informacion(nombre, ubicacion, redes_wifi)
        
        print('Información almacenada correctamente.\n')
    
    print('¡Hasta luego!')

def introducir_coordenadas():
    subprocess.call('cls', shell=True)
    nombre_archivo = input("Introduce el nombre de tu archivo de coordenadas (Default:coord.txt): ")
    
    if nombre_archivo == "":
        nombre_archivo = "coord.txt"

    with open(nombre_archivo, 'r') as archivo:
        lineas = archivo.readlines()

    for i, linea in enumerate(lineas, 1):
        respuesta = input("Presiona enter para continuar o escribe 'exit' para salir: ")
        if respuesta == 'exit':
            break
        latitud, longitud = linea.strip().split(',')
        ubicacion = [float(latitud), float(longitud)]
        nombre = f'punto_{i}'
        redes_wifi = obtener_redes_wifi()
        almacenar_informacion(nombre, ubicacion, redes_wifi)
        print("Información almacenada correctamente.\n")

def seleccionar_interfaz():
    # Ejecutar el comando y obtener la salida como texto
    output = subprocess.check_output(['powershell', 'Get-NetAdapter | Where-Object { $_.MediaType -eq "Native 802.11" } | Select-Object InterfaceDescription | Format-Table -HideTableHeaders'])

    # Decodificar la salida a una cadena de texto legible
    output = output.decode('utf-8')

    interfaces = []
    # Analizar la salida y almacenar los resultados en la lista
    for linea in output.splitlines():
        linea = linea.strip()
        if linea != "":
            interfaces.append(linea)

    # Imprimir interfaces
    subprocess.call('cls', shell=True)
    print("\n\nPor favor, seleccione la interfaz que desea utilizar\n")

    for i, ssid in enumerate(interfaces, start=1):
        print(f"{i}. {ssid}")
    
    print("\n")

    # Solicitar al usuario el número de interfaz seleccionado
    opcion = int(input("Seleccione el número de interfaz que desea usar: "))
    global interfaz_seleccionada
    interfaz_seleccionada = interfaces[opcion - 1]

    # Obtener y guardar el nombre
    comando = 'Get-NetAdapter | Where-Object { $_.InterfaceDescription -eq "%s" } | Select-Object Name | Format-Table -HideTableHeaders' % interfaz_seleccionada
    output = subprocess.check_output(['powershell', comando])
    output = output.decode('utf-8')

    nombre = []

    for linea in output.splitlines():
        linea = linea.strip()
        if linea != "":
            nombre.append(linea)

    # Asignar el primer valor no vacío a la variable nombre_interfaz (si existe)
    global nombre_interfaz
    nombre_interfaz = nombre[0] if nombre else None

def adb_gps(adb_path):
    comando = f'{adb_path} shell dumpsys location'
    output = subprocess.check_output(['powershell', comando])
    output = output.decode('utf-8')
    
    regex = r'-?\d{1,3}\.-?\d{6},[ -]?\d{1,3}\.-?\d{6}'

    # Buscar el siguiente regex en cada línea del resultado
    for line in output.splitlines():
        match = re.search(regex, line)
        if match:
            return match.group()
    print("Ha habido algún problema obteniendo las coordenadas mediante adb")
    consejo = input("Escribe consejo para saber qué hacer o cualquier otra cosa para salir")
    if consejo == "consejo":
        print("""1. Comprueba que has conectado correctamente tu dispositivo por adb con el comando adb devices
2. lanza el comando adb shell dumpsys location y comprueba con la herramienta de tu elección el siguiente regex '-?\d{1,3}\.-?\d{6},[ -]?\d{1,3}\.-?\d{6}'
3. En caso de no encontrar nada busca manualmente las coordenadas, crea un nuevo regex y cambia el mostrado que está en el código.""")

def obtener_por_adb():
    subprocess.call('cls', shell=True)
    print("\nEscribe la ruta para ejecutar tu adb, adb si está en el path (Por defecto:C:\platform-tools\\adb)")
    adb_path_input = input("\n")
    if adb_path_input == "":
        adb_path = "C:\platform-tools\\adb"
    else:
        adb_path = adb_path_input
    i = 1
    while True:
        respuesta = input("Presiona enter para continuar o escribe 'exit' para salir: ")
        if respuesta == 'exit':
            break
        coordenadas = adb_gps(adb_path)
        latitud, longitud = coordenadas.strip().split(',')
        ubicacion = [float(latitud), float(longitud)]
        nombre = f'punto_{i}'
        i = i + 1
        redes_wifi = obtener_redes_wifi()
        almacenar_informacion(nombre, ubicacion, redes_wifi)
        print("Información almacenada correctamente.\n")

def print_error_message(message):
    RED = '\033[91m'
    END = '\033[0m'
    print(RED + message + END)

def procesar_archivo():
    subprocess.call('cls', shell=True)
    if os.path.exists("informacion.json"):
        with open("informacion.json", "r") as file:
            data = json.load(file)
            count = sum(1 for item in data if "nombre" in item)

        if count > 0:
            print(f"\n\nHay un total de {count} puntos almacenados. ¿Qué deseas hacer?\n"
                  f"1. Borrarlos\n"
                  f"2. Guardarlos en un archivo aparte\n"
                  f"3. No hacer nada")

            opcion = int(input("\nIngrese el número de la opción deseada: "))

            if opcion == 1:
                os.remove("informacion.json")
                print("\nEl archivo informacion.json ha sido borrado.")
                input("Presiona cualquier tecla para continuar")

            elif opcion == 2:
                nombre_archivo = input("\n¿Con qué nombre quieres almacenarlo? (La terminación será .json): ")
                nombre_archivo += ".json"
                shutil.copy("informacion.json", nombre_archivo)
                print(f"\nEl archivo informacion.json ha sido copiado a {nombre_archivo}.")

                borrar_original = input("\n¿Deseas además borrar el original? (s/n): ")
                if borrar_original.lower() == "s":
                    os.remove("informacion.json")
                    print("\nEl archivo informacion.json ha sido borrado.")
                    input("Presiona cualquier tecla para continuar")

            elif opcion == 3:
                return

        else:
            print("\n\nNo se encontraron puntos almacenados en el archivo informacion.json.\n")
            input("Presiona cualquier tecla para continuar")

    else:
        print("\n\nNo hay datos almacenados.\n")
        input("Presiona cualquier tecla para continuar")

def main():
    seleccionar_interfaz()
    while True:
        subprocess.call('cls', shell=True)
        if not is_admin():
            print_error_message("\nNo estás ejecutando como administrador. Las mediciones no serán precisas o requerirán un largo tiempo de espera\n")
        print("""\n¿Qué quieres hacer?:
        1. Introducir listado de coordenadas
        2. Obtener coordenadas In Situ
        3. Coordenadas por ADB
        4. Generar un mapa de calor
        5. Cambiar interfaz
        6. Comprobar, Almacenar o eliminar datos actuales
        0. Salir\n""")

        opcion = input(f"Introduce el número ({interfaz_seleccionada}): ")
        if opcion == "1":
            introducir_coordenadas()
        elif opcion == "2":
            puntos_de_control()
        elif opcion == "3":
            obtener_por_adb()
        elif opcion == "4":
            mapacalor.mapa_de_calor()
        elif opcion == "5":
            seleccionar_interfaz()
        elif opcion == "6":
            procesar_archivo()
        elif opcion == "0":
            break
        else:
            print("\nUn, Dos, Tres, Responde otra vez\n")


if __name__ == '__main__':
    main()
    
