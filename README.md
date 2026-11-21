# SAVF-ESP32 — Sistema IoT de Monitoramento Ambiental

Projeto acadêmico desenvolvido para a disciplina **IN1061 — Tópicos Avançados em Sistemas Distribuídos 2: IoT, Tecnologias, Arquiteturas e Aplicações**, do Centro de Informática da Universidade Federal de Pernambuco.

## Descrição do projeto

O SAVF-ESP32 acompanha temperatura e umidade em um ambiente interno. Um ESP32 conectado a um módulo DHT11 coleta as medições e publica eventos em um broker MQTT. O servidor Python valida e armazena os eventos, enquanto o dashboard consulta a leitura mais recente por HTTP e a apresenta em cartões, gráfico e histórico.

O projeto preserva um sensor virtual para testes sem o hardware. Tanto o publicador virtual quanto o ESP32 utilizam o mesmo tópico e o mesmo objeto JSON, permitindo verificar separadamente o broker, o servidor e o dashboard.

## Problema resolvido

Sem instrumentação, as condições térmicas de uma sala são avaliadas apenas pela percepção dos ocupantes e não formam um histórico verificável. O sistema transforma as medições do ambiente em eventos datados, mantém os registros e disponibiliza uma visualização atualizada.

## Fluxo de dados

```text
DHT11 → ESP32 → Wi-Fi → Broker MQTT → Servidor Python → API HTTP → Dashboard
                                      └──────────────→ JSON Lines
```

Durante testes, o publicador virtual pode ocupar o lugar do ESP32:

```text
Sensor virtual → Broker MQTT → Servidor Python → Dashboard
```

## Tecnologias escolhidas

- **ESP32:** unidade de processamento e conectividade Wi-Fi do nó físico.
- **DHT11:** aquisição de temperatura e umidade relativa.
- **C++ com framework Arduino:** firmware do nó físico.
- **MQTT com QoS 1:** comunicação Publish/Subscribe entre o coletor e o servidor.
- **Eclipse Mosquitto:** broker MQTT local usado na demonstração.
- **Python 3.10 ou superior:** servidor, validação, persistência e avaliação.
- **HTML, CSS e JavaScript:** interface de acompanhamento no navegador.

## Estrutura de pastas

```text
.
├── dashboard/                    # Interface web
├── data/                         # Leituras e resultados locais
├── docs/                         # Documentos das entregas
├── firmware/esp32_dht11/         # Código da placa e configuração de exemplo
├── infra/mosquitto/              # Configuração do broker local
├── scripts/teste_experimental.py # Coleta das métricas da avaliação
├── src/
│   ├── dashboard/                # Servidor HTTP e API
│   ├── experimentos/             # Cálculo das métricas
│   ├── integracao/               # Validação e estado das leituras
│   ├── mqtt/                     # Consumidor e publicador MQTT
│   └── sensor_virtual/           # Fonte simulada e armazenamento
├── tests/                        # Testes unitários e de integração
├── compose.yaml                  # Broker Mosquitto
├── pyproject.toml
└── README.md
```

## Contrato de dados

O tópico padrão é `cidade/sala-01/ambiente`. Cada mensagem contém um objeto JSON:

```json
{
  "identificador": "esp32-sala-01",
  "local": "Sala de Aula",
  "data_hora": "2026-11-21T12:00:00Z",
  "temperatura_c": 25.4,
  "umidade_percentual": 61.2,
  "situacao": "confortavel"
}
```

O servidor rejeita campos ausentes, tipos incorretos, datas sem fuso e valores fora da faixa declarada pelo fabricante do DHT11: temperatura entre -20 e 60 °C e umidade relativa entre 5 e 95%. Mensagens com dispositivo, horário e valores idênticos não são gravadas duas vezes.

## Como executar a aplicação

### 1. Obter o projeto

```bash
git clone https://github.com/JairoMarinho/sensor-ambiental-virtual.git
cd sensor-ambiental-virtual
```

### 2. Preparar o Python

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

No Windows, ative o ambiente com `.venv\Scripts\activate`.

### 3. Iniciar o broker MQTT

Com Docker Desktop aberto:

```bash
docker compose up -d broker
docker compose ps
```

A configuração permite acesso anônimo somente para facilitar a demonstração em uma rede local confiável. Ela não deve ser exposta à Internet. Uma implantação externa exige autenticação, autorização por tópico e TLS.

### 4. Iniciar o servidor e o dashboard

```bash
python3 -m src.dashboard.server --source mqtt
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000). O painel exibirá **Aguardando sensor** até a primeira mensagem MQTT válida.

### 5. Testar sem a placa

Em outro terminal, ative o mesmo ambiente virtual e publique dez leituras:

```bash
python3 -m src.mqtt.publisher --count 10 --interval 2
```

As amostras devem aparecer no terminal do servidor, no dashboard e em `data/leituras-mqtt.jsonl`. Esse teste percorre o mesmo broker, consumidor, API e dashboard usados pelo hardware.

### 6. Conectar o ESP32 e o DHT11

Ligação de referência:

| DHT11 | ESP32 |
|---|---|
| VCC | 3,3 V |
| DATA | GPIO 4 |
| GND | GND |

Use um resistor de pull-up de 4,7 kΩ entre VCC e DATA quando ele não estiver presente no módulo.

1. Instale no Arduino IDE as bibliotecas **DHT sensor library**, da Adafruit, e **ArduinoMqttClient**, da Arduino.
2. Abra `firmware/esp32_dht11/esp32_dht11.ino`.
3. Copie `config.example.h` para `config.h` na mesma pasta.
4. Preencha Wi-Fi e `MQTT_HOST` em `config.h`. Use o IP do computador na rede local, não `127.0.0.1`.
5. Selecione a placa e a porta, compile e envie o firmware.
6. Abra o Monitor Serial em `115200` baud e confirme as publicações JSON.

O arquivo `config.h` é ignorado pelo Git para evitar o envio da senha da rede.

### 7. Executar os testes automatizados

```bash
python3 -m unittest discover -s tests -v
```

A suíte verifica geração, classificação, persistência, validação do payload MQTT, rejeição de valores inválidos, ausência inicial de leitura, deduplicação e o caminho completo `payload MQTT → repositório → API do dashboard`.

## Teste experimental da solução

Com broker, servidor e ESP32 em execução, abra outro terminal e rode:

```bash
python3 -m scripts.teste_experimental \
  --duration 300 \
  --sensor-interval 5 \
  --poll-interval 1 \
  --output data/resultado-experimento.json
```

O ensaio de cinco minutos espera 60 mensagens e calcula:

- quantidade recebida e quantidade única;
- mensagens duplicadas;
- completude percentual;
- latência média e máxima entre coleta e consulta.

Para o ensaio de uma hora descrito no artigo, altere `--duration` para `3600`. O resultado só deve ser incluído no relatório após a coleta com o ESP32 ligado; o repositório não apresenta números físicos fabricados.

## Teste rápido sem MQTT

Para verificar apenas o dashboard com a fonte virtual direta:

```bash
python3 -m src.dashboard.server --source virtual
```

Esse modo é útil para diagnóstico, mas não comprova o fluxo MQTT exigido na Entrega 3.

## Encerrar os serviços

Encerre o servidor com `Ctrl+C` e pare o broker:

```bash
docker compose down
```

## Limitações atuais

- O DHT11 é adequado à prova de conceito, mas sua exatidão e resolução não substituem um instrumento calibrado.
- O broker fornecido é destinado à rede local de demonstração.
- Os resultados físicos dependem da montagem e da execução do experimento com o hardware.
- O histórico utiliza arquivo local; uma implantação maior deve usar banco de séries temporais.

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).
