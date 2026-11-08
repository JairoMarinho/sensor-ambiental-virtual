# Sistema IoT de Monitoramento Ambiental - IN1061

Projeto acadêmico de um sistema IoT para acompanhamento de temperatura e umidade em ambientes internos, desenvolvido para a disciplina **IN1061 - Tópicos Avançados em Sistemas Distribuídos 2: IoT, Tecnologias, Arquiteturas e Aplicações**.

## Descrição do projeto

O sistema representa, em software, um sensor ambiental instalado em uma sala de aula. A cada coleta são gerados valores de temperatura e umidade. As leituras podem ser consultadas no terminal ou acompanhadas em um dashboard web que atualiza os indicadores automaticamente.

### Problema abordado

Ambientes de estudo desconfortáveis podem prejudicar a concentração e o bem-estar. Sem instrumentação, não há um histórico objetivo das condições ambientais que permita identificar períodos de calor ou umidade inadequada.

### Ideia central

Construir as partes do sistema de forma progressiva. O sensor virtual representa a camada de percepção, o MQTT foi definido como protocolo de comunicação entre sensor e servidor, e o dashboard oferece a primeira interface de monitoramento. Nesta versão, o servidor local utiliza diretamente o sensor para viabilizar a demonstração; a conexão com um broker MQTT será incorporada na evolução do projeto.

### Escopo das entregas

**Entrega 01:**

- geração de temperatura e umidade com variações graduais e limites realistas;
- data e hora em UTC, identificador e localização do dispositivo;
- classificação simples da condição ambiental;
- persistência das leituras em JSON Lines;
- consulta do histórico pelo terminal;
- interface de linha de comando e testes automatizados.

**Entrega 02:**

- documento de arquitetura com o fluxo de dados;
- conectividade Wi-Fi sobre a pilha TCP/IP;
- paradigma Publish/Subscribe com protocolo MQTT;
- servidor HTTP local para a interface;
- dashboard responsivo com leitura atual, estado e histórico recente;
- teste automatizado da resposta JSON usada pelo dashboard.

Fora do escopo atual:

- sensor físico;
- implantação do broker MQTT;
- banco de dados remoto;
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
├── dashboard/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── docs/
│   └── arquitetura-entrega-02.pdf
├── src/
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── server.py
│   └── sensor_virtual/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── storage.py
│       └── sensor.py
├── tests/
│   ├── __init__.py
│   ├── test_dashboard.py
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

As medições aparecem no terminal e são acrescentadas a `data/leituras.jsonl`. Para uma demonstração imediata, use intervalo zero:

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
{"identificador":"sensor-sala-01","local":"Sala de Aula","data_hora":"2026-10-27T17:30:00+00:00","temperatura_c":25.4,"umidade_percentual":61.2,"situacao":"confortavel"}
```

### 4. Abrir o dashboard

Inicie o servidor local:

```bash
python3 -m src.dashboard.server
```

Depois, acesse no navegador:

```text
http://127.0.0.1:8000
```

A página consulta uma nova leitura a cada três segundos. Para encerrar, volte ao terminal e pressione `Ctrl+C`.

### 5. Executar os testes

```bash
python3 -m unittest discover -s tests -v
```

### 6. Ver todas as opções

```bash
python3 -m src.sensor_virtual --help
python3 -m src.sensor_virtual generate --help
python3 -m src.sensor_virtual read --help
```

## Fluxo da solução

```text
Ambiente -> Sensor virtual -> MQTT Broker -> Servidor -> Dashboard
              |                              |
              +-> JSON Lines                 +-> API HTTP/JSON
```

## Decisões técnicas

- **Python:** facilita a execução e a apresentação do protótipo.
- **Variação limitada:** evita mudanças bruscas entre medições consecutivas.
- **JSON Lines:** cada leitura é independente, permitindo acréscimo contínuo e processamento incremental.
- **Biblioteca padrão:** reduz a preparação necessária para executar o projeto.
- **Wi-Fi:** conectividade prevista para o dispositivo no ambiente monitorado.
- **MQTT:** comunicação Publish/Subscribe, adequada ao envio contínuo de eventos de sensoriamento.
- **HTTP:** entrega da interface e consulta das leituras pelo navegador.

## Evolução futura

A próxima evolução deve conectar o sensor a um broker MQTT, implementar o consumidor no servidor e conservar o histórico em um banco de dados. A separação atual permite realizar essas mudanças sem alterar a interface do dashboard.

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).
