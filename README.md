# はじめに
ESP32に接続された温度センサー（LM61CIZ）から取得した温度データを返す、RESTful なAPI Serverを構築しました。

# 動作環境
- ボード : ESP32-WROOM-32
- 温度センサー : lm61ciz
- micropython v1.14
- MicroWebSrv2 v2.0.6

# 環境構築
1. esptoolのインストール
    ```bash
    pip install のインストール
    ```
    <br>
2. ampyのインストール
    ```bash
    pip install adafruit-ampy
    ```
    <br>
3. フラッシュメモリの削除
    ```bash
    esptool --chip esp32 --port `ポート番号` erase_flash
    ```
    <br>
4. micropythonファームウェアの書き込み
    ```bash
    esptool --chip esp32 --port `ポート番号` write_flash -z 0x1000 ESP32_GENERIC-IDF3-20210202-v1.14.bin
    ```
    <br>
5. ライブラリ(MicroWebSrv2)のアップロード
    ```bash
    ampy -p `ポート番号` put .\MicroWebSrv2\
    ```
    <br>
6. プログラム(main.py)のアップロード
    ```bash
    ampy -p `ポート番号` put .\main.py
    ```

 # プログラム
 - main.py
    ```python
    import machine
    import network
    from time import sleep
    from MicroWebSrv2 import *
    
    
    def connect_wifi(ssid, password, max_attempts=10):
        sta_if = network.WLAN(network.STA_IF)
        sta_if.ifconfig(("***.***.***.***", "255.255.255.0", "***.***.***.***", "8.8.8.8"))
    
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
    
    
    ssid = "********"
    password = "********"
    
    connect_wifi(ssid, password)
    
    mws2 = MicroWebSrv2()
    mws2.SetEmbeddedConfig()
    mws2.BindAddress = ("***.***.***.***", 80)
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
    
    ```
# コードの説明
- IPアドレスの固定
    ```python
    sta_if.ifconfig(("***.***.***.***", "255.255.255.0", "***.***.***.***", "8.8.8.8"))
    ```
    - 左から、IPアドレス、サブネットマスク、デフォルトゲートウェイ、DNSサーバのIPを記述することでIPアドレスを固定しています
    <br>
- 温度センサー
    ```python
    def read_temp():
        adc = machine.ADC(machine.Pin(35))
        adc.atten(machine.ADC.ATTN_11DB)
        temp = (adc.read() / 4095.0 * 3.3 + 0.1132 - 0.6) / 0.01
        return temp
    ```
    - ESP32の35番ピンに接続されたADCを初期化
    - ADCから読み取った値（0から4095の範囲）を電圧（0から3.3V）に変換し、それを温度に変換しています。

- ssid password
    ```python
    ssid = "Buffalo-G-9BD0"
    password = "ppd7j7yi7jr4j"
    ```
    - 使用するwifiのssidをpasswardを記述してください
    <br>
- エンドポイント
    ```python
    @WebRoute(GET, "/temperature")
    def GetTemperature(microWebSrv2, request):
        temp = read_temp()
        request.Response.ReturnOkJSON(
            {
                "temperature": temp,
            }
        )
    ```
    - このコードは、Webサーバーが"/temperature"というパスでGETリクエストを受け取ったときの処理を定義しています。
    - "/temperature"というパスでGETリクエストが来たときに、read_temp()関数を呼び出して温度を読み取ります。
    - 読み取った温度を含むJSON形式のレスポンスを生成し、HTTPステータスコード200（OK）とともにクライアントに送信します。

 # 動作

 <img src="/img/ESP32_API_Server_postman.png">



 # まとめ
 ESP32に接続された温度センサー（LM61CIZ）から取得した温度データを返す、RESTful なAPI Serverを構築しました。
本当は、センサーを増やしたり、APIエンドポイントももっと増やしたいですが、ESP32の処理性能やメモリに制限があるため、断念しました。
 
