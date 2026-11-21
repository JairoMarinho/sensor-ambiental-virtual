#pragma once

// Copie este arquivo para config.h e preencha com os dados da sua rede local.
#define WIFI_SSID "NOME_DA_REDE"
#define WIFI_PASSWORD "SENHA_DA_REDE"

// Use o endereço IP do computador que executa o broker Mosquitto.
#define MQTT_HOST "192.168.0.100"
#define MQTT_PORT 1883
#define MQTT_TOPIC "cidade/sala-01/ambiente"

#define DEVICE_ID "esp32-sala-01"
#define DEVICE_LOCATION "Sala de Aula"
