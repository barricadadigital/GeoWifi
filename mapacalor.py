import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import json
import subprocess

def mapa_de_calor():
    subprocess.call('cls', shell=True)
    # Parsear el JSON
    #data = json.loads(json_data)
    # Leer datos del archivo JSON
    with open('informacion.json') as file:
        data = json.load(file)

    
    # Obtener todos los SSIDs y sus correspondientes "bssid 1" presentes en el JSON
    ssids = []
    for entry in data:
        redes_wifi = entry["redes_wifi"]
        for red_wifi in redes_wifi:
            if "ssid" in red_wifi and "bssid 1" in red_wifi:
                ssid = red_wifi["ssid"]
                bssid = red_wifi["bssid 1"]
                ssids.append((ssid, bssid))

    # Eliminar duplicados y mostrar los SSIDs numerados con su "bssid 1" entre paréntesis
    print("\n\nSSID obtenidos\n---\n")
    ssids_unicos = list(set(ssids))
    for i, (ssid, bssid) in enumerate(ssids_unicos, start=1):
        print(f"{i}. {ssid} ({bssid})")

    # Solicitar al usuario el número del SSID seleccionado
    opcion = int(input("\nSeleccione el número del SSID que desea seguir: "))
    ssid_seleccionado = ssids_unicos[opcion - 1][0]
    print(f"\nEl SSID Seleccionado es: {ssid_seleccionado}\n")
    output = input("Nombre del output(Default map): ")
    if output == "":
        output = "map"

    # Obtener coordenadas y fuerza de señal
    coords = []
    signal_strengths = []
    coords_filtered = []
    signal_strengths_filtered = []


    for entry in data:
        ubicacion = entry["ubicacion"]
        redes_wifi = entry["redes_wifi"]
        found_ssid = False
        
        for red_wifi in redes_wifi:
            if "ssid" in red_wifi and red_wifi["ssid"] == ssid_seleccionado:
                found_ssid = True
                if "seal" in red_wifi:
                    seal = red_wifi["seal"]
                    signal_strength = int(seal.strip("%"))
                    
                    if signal_strength < 21:
                        signal_strengths_filtered.append(signal_strength)
                    else:
                        signal_strengths_filtered.append(min(signal_strength + 49, 100))
                        
                    coords_filtered.append(ubicacion)
                
        if not found_ssid:
            coords_filtered.append(None)
            signal_strengths_filtered.append(None)
    
    coords_filtered.append([90,90])
    signal_strengths_filtered.append(0)
    coords_filtered.append([-90,90])
    signal_strengths_filtered.append(100)

    # Crear el DataFrame
    df = pd.DataFrame({'latitud': [coord[0] if coord is not None else None for coord in coords_filtered],
                    'longitud': [coord[1] if coord is not None else None for coord in coords_filtered],
                    'fuerza de señal': signal_strengths_filtered})
    
    # Eliminar filas con valores NaN
    df.dropna(subset=['latitud', 'longitud', 'fuerza de señal'], inplace=True)


    # Filtrar filas duplicadas y con diferencias menores a 0.000050 en latitud o longitud (No funciona correctamente las elimina por completo)
    #df = df.groupby(['latitud', 'longitud']).filter(lambda x: (x.shape[0] == 1) or
    #                                                    ((x['latitud'].max() - x['latitud'].min()) > 0.000050) or
    #                                                    ((x['longitud'].max() - x['longitud'].min()) > 0.000050))
    

    # Eliminar filas duplicadas basadas en latitud y longitud
    df.drop_duplicates(subset=['latitud', 'longitud'], keep='first', inplace=True)


    # Crear el mapa de calor
    mapa = folium.Map(location=[np.mean(df['latitud'][:-2]), np.mean(df['longitud'][:-2])], zoom_start=100)

    capa_calor = folium.FeatureGroup(name='Mapa de calor')
    capa_calor.add_child(HeatMap(data=df[['latitud', 'longitud', 'fuerza de señal']].values.tolist(), radius=15))
    mapa.add_child(capa_calor)

    leyenda = folium.features.GeoJson(
        data={
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'properties': {
                    'name': 'Leyenda',
                    'description': 'Fuerza de señal'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [np.mean(df['latitud']), np.mean(df['longitud'])]
                }
            }]
        },
        style_function=lambda x: {
            'color': 'black',
            'weight': 2,
            'fillColor': '#ffae42',
            'fillOpacity': 0.7
        }
    ).add_to(mapa)

    output = output + ".html"
    mapa.save(output)