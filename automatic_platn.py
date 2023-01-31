import machine 
import network
import time
import urequests
import ujson
import sys
import dht
#import sleep

humiditySensor = machine.Pin(35)                        # Entrada del Sensor de Humedad del suelo, Se inicializa el PIN34
adcHumiditySensor = machine.ADC(humiditySensor)         

dth1 = dht.DHT11(machine.Pin(32))                       # Entrada del Sensor de Temperatura y Humedad Ambiente

ledPin = machine.Pin(22,machine.Pin.OUT)                # Tenia Pin 2 Para Encender La Luz
relayWaterPump = machine.Pin(23,machine.Pin.OUT)        # Pin De Salida Para Activar La Bomba De Agua 
 
ESP32ID = "001"											

WIFI_SSID     = 'Igoriok'                                  # Nombre Wifi
WIFI_PASSWORD = 'Camilo2306'                            # Contrasena Wifi

URLGET= 'http://192.168.1.4:8090/validate'              # URL Para Obtener Datos Del Servidor  
URLPOST= 'http://192.168.1.4:8090/sensorsData'          # URL Para Enviar Datos Al Servidor

# Conexión a Wifi  					 
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(False)
    time.sleep(0.5)
    wifi.active(True)
    wifi.connect(WIFI_SSID,WIFI_PASSWORD)
    
    if not wifi.isconnected():
        print('Conectando...') # connecting..
        timeout = 0
        while (not wifi.isconnected() and timeout < 5):
            print(5 - timeout)
            timeout = timeout + 1
            time.sleep(1)
            
    # Validación de Conexión
    
    if(wifi.isconnected()):
        print('Conectado')                # connected
    else:
        print('No Conectado')             # not connected
        sys.exit()
        
    

# Recibir Datos # 					

def receiveData():
    try:
        response = urequests.get(URLGET)
        response_json = response.json()
        print('datos:',response_json)
        return response_json
    except:
        print("Problemas en la validacion")
        return -1
        
# Enviar Datos

def sendData(params):
    try:
        post_data = ujson.dumps(params)
        res = urequests.post(URLPOST, headers = {'content-type': 'application/json'}, data = post_data).json()
        print('Enviar')                                            # Send
    except:
        print('Problema al enviar datos, inténtalo de nuevo')      # Problem sending data, please try again
        sys.exit()
        
# /////// Código principal / Main Code /////////			 

def main():
    waterPumpFlag = False
    ledFlag = False
    connect_wifi()                                      # Connecting to WiFi Router / Connecting to WiFi Router
    print('Listo')                                      # Ready / Listo
    dataReceived = receiveData()                       
    access = False
    index = 0
    if(dataReceived == -1):
        print("No se ha podido validar el esp, intenta de nuevo")
    else:
        while index < len(dataReceived):
             if (dataReceived[index]['esp32Id'] == ESP32ID):
                access = True
                break
             index = index+1
    if(access):
        while True:
            dth1.measure()
            humiditySensorValue = (1-(adcHumiditySensor.read()/4095))*100
            print(humiditySensorValue, dth1.temperature(), dth1.humidity())
            
           
            #print(sensorValue, humiditySensorValue,("T={:02d}C H={:02d}%".format(dth1.temperature(), dth1.humidity())))
            if (dth1.temperature() <= 20):
                ledPin.value(1)
            else:
                ledPin.value(0)
                
            if (humiditySensorValue <= 50):
                relayWaterPump.value(1)
            else:
                relayWaterPump.value(0)
                
            if (dth1.temperature() >= 35 or dth1.temperature() <= 20 or humiditySensorValue <= 50 or dth1.humidity() >=60):
                if(not waterPumpFlag):
                    sendData({
                        'floorHumidity':humiditySensorValue,
                        'humidity':dth1.humidity(),
                        #'humidity':("H={:02d}%".format(dth1.humidity())),
                        'temp': dth1.temperature()
                        #'temp':("T={:02d}C ".format(dth1.temperature()))
                        })
                    waterPumpFlag = True
            else: 
                
                if(waterPumpFlag):
                    sendData({
                        'floorHumidity':humiditySensorValue,
                        'humidity':dth1.humidity(),
                        #'humidity':("H={:02d}%".format(dth1.humidity())),
                        'temp': dth1.temperature()
                        #'temp':("T={:02d}C ".format(dth1.temperature()))
                        })
                    waterPumpFlag = False

            time.sleep(1)
    else:
        if(access == -1):
            print('Sin conexión de servidor')                      # No Server Connection
        else:
            print('No tienes acceso')                              # Yoy do not have access

main()          