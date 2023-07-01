# GeoWifi
GeoWifi es una herramienta de creación propia que permite hacer [[Análisis de cobertura Wifi]] y te muestra un mapa de calor con los puntos que quieras escanear.

Por ahora sólo es compatible con Windows, ya que comencé a hacerla para esta plataforma por la facilidad que tuve para el tema de las coordenadas GPS, aunque con la última adición de ADB en un futuro lo compatibilizaré con Linux.

## Instalación

Es un proyecto de python, por lo que las librerías extras que se deben añadir son:

```python
pip install pandas
pip install numpy
pip install folium
```

Clonas el proyecto:

```bash
git clone https://github.com/barricadadigital/GeoWifi
```

### ADB

Si quieres hacer uso de ADB deberás seguir los siguientes pasos (¡Importante! Es bastante probable que Huawei no sea compatible):

1. Habilitar opciones de desarrollador en tu móvil, busca algún tutorial por internet ya que hay ligeras diferencias entre distintos dispositivos.
2. Descarga ADB https://dl.google.com/android/repository/platform-tools-latest-windows.zip
3. Por defecto yo lo tengo descomprimido en ``C:\platform-tools`` aunque no es muy importante ya que la propia herramienta te permite seleccionar el path por defecto de tu `adb`
4. A continuación debes manualmente desde tu consola y tu móvil permitir la conexión
```bash
adb devices

#En tu móvil aceptas la notificación de emparejamiento
```
5. Además recomiendo por comodidad si estáis en una red segura que habilitéis adb inalámbrico, podéis buscar tutoriales de cómo hacerlo porque hay pequeñas diferencias entre dispositivos.

### Windows GPS

Si vais a usar el GPS de vuestro propio ordenador debéis habilitarlo en windows:

Nos vamos a `Configuración -> Ubicación`

![image](https://github.com/barricadadigital/GeoWifi/assets/92856868/faf10e59-9f38-4976-9f73-b5a97901834a)

### Listado de Coordenadas

Si queréis preparar previamente las coordenadas donde vais a hacer los escáneres existe una opción simplemente tendréis que crear un archivo que tenga las coordenadas separadas de la siguiente forma:

```bash
latitud1, longitud1
latitud2, longitud2
latitud3, longitud3
latitud4, longitud4
latitud5, longitud5
```

Más adelante explico su uso.

## Uso

>¡Importante! Os recomiendo que lo ejecutéis con privilegios de administrador ya que por defecto Windows tiene un tiempo de espera hasta que borra el caché del último análisis de redes cercanas hasta el siguiente y tenemos que forzarlo.

Ejecutamos la herramienta:

```bash
python .\geowifi.py
```

En primer lugar detectará las interfaces de red compatibles y nos las mostrará para seleccionar:

```bash
Por favor, seleccione la interfaz que desea utilizar

1. TP-Link Wireless USB Adapter
2. Intel(R) Wi-Fi AX201 160MHz


Seleccione el número de interfaz que desea usar:   
```

Una vez seleccionado tenemos el panel importante (Nos avisará en caso de no haberlo ejecutado cómo administrador):

```bash
¿Qué quieres hacer?:
        1. Introducir listado de coordenadas
        2. Obtener coordenadas In Situ
        3. Coordenadas por ADB
        4. Generar un mapa de calor
        5. Cambiar interfaz
        6. Comprobar, Almacenar o eliminar datos actuales
        0. Salir

Introduce el número (TP-Link Wireless USB Adapter):
```

Cómo podemos ver en todo momento nos mostrará la interfaz elegida, además podemos cambiarla en cualquier momento simplemente con la opción 5.

Comencemos a explicar las distintas opciones:

### Comprobar, Almacenar o eliminar datos actuales

Aunque sea la última opción me parece importante, todos los datos que tomemos se irán almacenando en un archivo dentro del proyecto llamado `informacion.json` por lo que si queremos podemos tomar distintas mediciones en distintos momentos incluso tras cerrar el programa.

Si vamos a esta opción:

```bash
Hay un total de 2 puntos almacenados. ¿Qué deseas hacer?
1. Borrarlos
2. Guardarlos en un archivo aparte
3. No hacer nada

Ingrese el número de la opción deseada:
```

Nos recuerda el número de puntos almacenados actualmente y nos da la opción de borrarlos o guardarlos en un archivo aparte.

### Introducir listado de coordenadas

Cómo mencionaba anteriormente si introducimos una lista con ese formato de `latitud, longitud` podremos ir tomando mediciones.

Pongamos que sabemos exactamente en qué puntos vamos a tomar esos datos, simplemente tenemos que tener nuestro listado, activar esta opción y el propio programa nos guiará, tenemos que pulsar a enter cada vez que lleguemos a ese punto.

En ese momento se escanearán los SSID disponibles y su fuerza de señal (Además si comprobamos el json tenemos más datos sobre cada uno) Cuando se acabe la lista nos devolverá a la pantalla principal del programa.

### Obtener coordenadas In Situ

Esta opción es la que usaremos si queremos utilizar el GPS de nuestro ordenador *No olvidéis activarlo*, el funcionamiento es muy simple también, cada vez que queramos escanear podemos dar a Enter o poner un nombre al punto y dar a Enter.

Hasta que no escribamos exit seguiremos con la posibilidad de tomar distintos puntos.

### Coordenadas por ADB

En este caso hacemos uso del siguiente comando de adb:

```bash
adb shell dumpsys location
```

Puede haber dispositivos como Huawei que den algunos problemas.

El funcionamiento también es muy simple, activamos la sección y comenzamos a tomar todos los puntos que queramos simplemente pulsando enter y moviéndonos con nuestro teléfono móvil.

En caso de existir algún error para encontrar las coordenadas el propio programa explica los pasos a seguir.

### Generar un mapa de calor

Para esta opción no es necesario haber ejecutado con permisos de administrador, básicamente nos permite crear un mapa de calor en `html` con los distintos puntos que hemos tomado y la potencia de señal obtenida.

Además te permite seleccionar por SSID o BSSID la red de la que quieres generar el mapa de calor de todas las obtenidas.

A continuación muestro un ejemplo de mapa de calor con la fuerza de señal hipotética de un wifi colocado en la mitad de Independence Park.

![image](https://github.com/barricadadigital/GeoWifi/assets/92856868/696ab61c-cfe1-4d56-857c-bf3aed259665)

El archivo se genera en formato HTML, por lo que la foto deberéis tomarla vosotros si queréis añadirla a un informe.


