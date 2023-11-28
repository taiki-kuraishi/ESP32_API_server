import machine
import network
from time import sleep
from MicroWebSrv2 import *


def connect_wifi(ssid, password, ip, subnet, gateway, dns):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.ifconfig((ip, subnet, gateway, dns))
    if not sta_if.isconnected():
        print("connecting to wifi...")
        sta_if.active(True)
        sta_if.connect(ssid, password)

        while not sta_if.isconnected():
            print("Failed to connect to wifi.")
            sleep(1)

    print("network config:", sta_if.ifconfig())


def read_temp():
    adc = machine.ADC(machine.Pin(35))
    adc.atten(machine.ADC.ATTN_11DB)
    temp = (adc.read() / 4095.0 * 3.3 + 0.1132 - 0.6) / 0.01
    return temp


ssid = "your_wifi_ssid"
password = "your_wifi_password"
ip = ""
subnet = ""
gateway = ""
dns = ""

connect_wifi(ssid, password)

mws2 = MicroWebSrv2()
mws2.SetEmbeddedConfig()
mws2.BindAddress = (ip, 80)
mws2.RequestsTimeoutSec = 10
mws2.StartManaged()


@WebRoute(GET, "/temperature")
def GetTemperature(microWebSrv2, request):
    temp = read_temp()
    request.Response.ReturnOkJSON(
        {
            "temperature": temp,
        }
    )


try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    mws2.Stop()
