# Sensor Ambiental Virtual - IN1061

Versão inicial de um dispositivo virtual da camada de percepção (*Perception Layer*) para a disciplina **IN1061 - Tópicos Avançados em Sistemas Distribuídos 2: IoT, Tecnologias, Arquiteturas e Aplicações**.

## Descrição do projeto

O projeto simula um sensor IoT ambiental instalado em uma sala de aula. O dispositivo produz leituras periódicas de temperatura e umidade, exibe cada medição no terminal e a armazena localmente em formato JSON Lines (`.jsonl`). Também é possível consultar as leituras já registradas.

### Problema abordado

Ambientes de estudo desconfortáveis podem prejudicar a concentração e o bem-estar. Sem instrumentação, não há um histórico objetivo das condições ambientais que permita identificar períodos de calor ou umidade inadequada.

### Ideia central

Criar um sensor virtual que represente a primeira camada de uma solução IoT. Nesta Entrega 01, ele simula a coleta e a leitura dos dados. Em etapas futuras, as medições poderão ser enviadas a uma plataforma IoT, por exemplo via MQTT, e apresentadas em um dashboard.

### Escopo da Entrega 01

Incluído:

- geração de temperatura e umidade com variações graduais e limites realistas;
- data e hora em UTC, identificador e localização do dispositivo;
- classificação simples da condição ambiental;
- persistência das leituras em JSON Lines;
- consulta do histórico pelo terminal;
- interface de linha de comando e testes automatizados.

Fora do escopo desta entrega:

- sensor físico;
- broker MQTT ou plataforma IoT;
- banco de dados remoto, API web ou dashboard;
- autenticação e implantação em nuvem.

## Requisitos funcionais

- **RF01:** gerar leituras de temperatura e umidade.
- **RF02:** associar metadados do dispositivo e instante da coleta a cada leitura.
- **RF03:** armazenar as leituras localmente.
- **RF04:** permitir a leitura do histórico armazenado.
- **RF05:** permitir configurar quantidade, intervalo e arquivo de saída.

## Requisitos não funcionais

- **RNF01:** executar com Python 3.10 ou superior.
- **RNF02:** utilizar somente a biblioteca padrão do Python.
- **RNF03:** armazenar dados em formato textual, legível e fácil de integrar.
- **RNF04:** manter código modular, documentado e testável.

## Estrutura

```text
.
├── data/
│   └── .gitkeep
├── src/
│   └── sensor_virtual/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── storage.py
│       └── sensor.py
├── tests/
│   ├── __init__.py
│   ├── test_sensor.py
│   └── test_storage.py
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## Como executar

### 1. Preparar o ambiente

Clone o repositório, entre na pasta do projeto e confira o Python:

```bash
git clone https://github.com/JairoMarinho/sensor-ambiental-virtual.git
cd sensor-ambiental-virtual
python3 --version
```

O projeto não possui dependências externas. A criação de um ambiente virtual é opcional:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows, ative com:

```powershell
.venv\Scripts\activate
```

### 2. Gerar dados de sensoriamento

Gere cinco leituras, uma por segundo:

```bash
python3 -m src.sensor_virtual generate --count 5 --interval 1
```

As medições aparecem no terminal e são acrescentadas a `data/readings.jsonl`. Para uma demonstração imediata, use intervalo zero:

```bash
python3 -m src.sensor_virtual generate --count 3 --interval 0
```

Também é possível personalizar o dispositivo, a localização e o arquivo:

```bash
python3 -m src.sensor_virtual generate --count 3 --interval 0 --device-id sala-b205 --location "Sala B205" --output data/sala-b205.jsonl
```

Use `Ctrl+C` para encerrar com segurança uma geração em andamento.

### 3. Ler os dados armazenados

```bash
python3 -m src.sensor_virtual read
```

Para ler outro arquivo ou limitar o resultado às últimas medições:

```bash
python3 -m src.sensor_virtual read --input data/sala-b205.jsonl --limit 2
```

Cada linha possui um objeto JSON independente, por exemplo:

```json
{"device_id":"sensor-sala-01","location":"Sala de Aula","timestamp":"2026-09-29T17:30:00+00:00","temperature_c":25.4,"humidity_percent":61.2,"status":"confortavel"}
```

### 4. Executar os testes

```bash
python3 -m unittest discover -s tests -v
```

### 5. Ver todas as opções

```bash
python3 -m src.sensor_virtual --help
python3 -m src.sensor_virtual generate --help
python3 -m src.sensor_virtual read --help
```

## Fluxo da solução

```text
Condições simuladas -> Sensor virtual -> Validação -> Terminal + arquivo JSONL
                                                           |
                                                           +-> futura plataforma IoT
```

## Decisões técnicas

- **Python:** facilita a execução e a apresentação do protótipo.
- **Passeio aleatório limitado:** evita saltos irreais entre medições consecutivas.
- **JSON Lines:** cada leitura é independente, permitindo acréscimo contínuo e processamento incremental.
- **Biblioteca padrão:** reduz a preparação necessária para executar o projeto.

## Evolução futura

Uma próxima entrega pode substituir ou complementar o armazenamento local por publicação MQTT, conectar uma plataforma IoT e criar um dashboard. A estrutura atual separa geração e persistência para facilitar essa evolução sem alterar a responsabilidade do sensor.

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).
