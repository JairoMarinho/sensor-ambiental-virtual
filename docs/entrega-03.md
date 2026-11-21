# Entrega 3 — Integração e testes experimentais

## Integração implementada

O fluxo de dados da Entrega 3 utiliza o tópico MQTT `cidade/sala-01/ambiente`. O firmware do ESP32 lê o DHT11, acrescenta identificação e horário UTC e publica o objeto JSON. O servidor Python assina o tópico com QoS 1, valida o payload, elimina duplicatas, grava o histórico em JSON Lines e atualiza o estado consultado pela rota `/api/leitura`. O dashboard busca essa rota a cada três segundos.

O publicador virtual disponível em `src/mqtt/publisher.py` emite o mesmo contrato do ESP32. Ele permite testar broker, consumidor, persistência, API e dashboard antes de conectar o hardware, sem criar um caminho alternativo na aplicação.

## Evidências automatizadas

A suíte de testes cobre:

- validação de campos, tipos, faixas e data ISO 8601;
- recepção de um payload MQTT e exposição da mesma leitura na API;
- resposta HTTP 503 enquanto nenhuma amostra tiver sido recebida;
- persistência de eventos únicos e descarte de duplicatas;
- cálculo de completude, duplicatas e latência;
- geração, classificação e armazenamento do sensor virtual.

Na verificação local de 21 de novembro de 2026, os 13 testes automatizados foram concluídos sem falhas. Também foi executado um ensaio de ponta a ponta com Mosquitto e `paho-mqtt`, no qual as publicações virtuais chegaram ao servidor, ao histórico e à API usada pelo dashboard. Essa verificação comprova a integração de software; as medições físicas continuam dependendo da montagem e da execução com o ESP32 e o DHT11.

Comando:

```bash
python3 -m unittest discover -s tests -v
```

## Procedimento experimental com o hardware

1. Iniciar o Mosquitto com `docker compose up -d broker`.
2. Iniciar o servidor com `python3 -m src.dashboard.server --source mqtt`.
3. Energizar o ESP32 e confirmar no Monitor Serial a associação ao Wi-Fi e ao broker.
4. Abrir `http://127.0.0.1:8000` e confirmar que os valores e horários mudam.
5. Executar o coletor de métricas por cinco minutos:

```bash
python3 -m scripts.teste_experimental --duration 300 --sensor-interval 5
```

6. Guardar `data/resultado-experimento.json` e registrar uma captura do dashboard e do Monitor Serial.

O ensaio calcula mensagens esperadas, recebidas e únicas, duplicatas, completude e latência. Resultados numéricos só devem ser apresentados depois da execução com o dispositivo físico; valores simulados não comprovam a leitura real do ambiente.

## Critérios de aceitação

- o ESP32 publica uma leitura válida a cada cinco segundos;
- o servidor recebe a leitura sem reinicialização manual;
- a leitura exposta pela API possui o mesmo identificador, instante e valores do evento MQTT;
- o dashboard atualiza sem recarregar a página;
- uma mensagem duplicada não cria uma segunda linha no histórico;
- o sistema volta a receber eventos após a reconexão do broker.
