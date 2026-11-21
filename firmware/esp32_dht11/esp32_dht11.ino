#include <ArduinoMqttClient.h>
#include <DHT.h>
#include <WiFi.h>
#include <time.h>

#include "config.h"

constexpr uint8_t DHT_PIN = 4;
constexpr uint8_t DHT_TYPE = DHT11;
constexpr unsigned long INTERVALO_LEITURA_MS = 5000;

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient clienteRede;
MqttClient clienteMqtt(clienteRede);
unsigned long ultimaLeitura = 0;

void conectarWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  Serial.printf("\nWi-Fi conectado. IP: %s\n", WiFi.localIP().toString().c_str());
}

void conectarMqtt() {
  while (!clienteMqtt.connected()) {
    Serial.print("Conectando ao broker MQTT...");
    clienteMqtt.setId(DEVICE_ID);
    if (clienteMqtt.connect(MQTT_HOST, MQTT_PORT)) {
      Serial.println("conectado");
    } else {
      Serial.printf(
          "falha, código %d. Nova tentativa em 2 s\n",
          clienteMqtt.connectError());
      delay(2000);
    }
  }
}

void dataHoraUtc(char* destino, size_t tamanho) {
  time_t agora;
  time(&agora);
  struct tm instante;
  gmtime_r(&agora, &instante);
  strftime(destino, tamanho, "%Y-%m-%dT%H:%M:%SZ", &instante);
}

const char* classificar(float temperatura, float umidade) {
  if (temperatura >= 30.0) return "calor";
  if (temperatura <= 18.0) return "frio";
  if (umidade >= 80.0) return "umidade_alta";
  if (umidade <= 30.0) return "umidade_baixa";
  return "confortavel";
}

void publicarLeitura() {
  const float umidade = dht.readHumidity();
  const float temperatura = dht.readTemperature();
  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("Leitura inválida do DHT11");
    return;
  }

  char dataHora[25];
  dataHoraUtc(dataHora, sizeof(dataHora));

  char payload[320];
  snprintf(
      payload,
      sizeof(payload),
      "{\"identificador\":\"%s\",\"local\":\"%s\",\"data_hora\":\"%s\","
      "\"temperatura_c\":%.1f,\"umidade_percentual\":%.1f,\"situacao\":\"%s\"}",
      DEVICE_ID,
      DEVICE_LOCATION,
      dataHora,
      temperatura,
      umidade,
      classificar(temperatura, umidade));

  clienteMqtt.beginMessage(MQTT_TOPIC, strlen(payload), false, 1, false);
  clienteMqtt.print(payload);
  if (clienteMqtt.endMessage()) {
    Serial.println(payload);
  } else {
    Serial.println("Falha ao publicar a leitura");
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  conectarWifi();
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) conectarWifi();
  if (!clienteMqtt.connected()) conectarMqtt();
  clienteMqtt.poll();

  const unsigned long agora = millis();
  if (agora - ultimaLeitura >= INTERVALO_LEITURA_MS) {
    ultimaLeitura = agora;
    publicarLeitura();
  }
}
