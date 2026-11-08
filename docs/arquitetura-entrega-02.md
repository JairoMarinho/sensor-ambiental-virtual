# Entrega 02 - Arquitetura do Sistema IoT de Monitoramento Ambiental

**Disciplina:** IN1061 - IoT: Tecnologias, Arquiteturas e Aplicações  
**Autor:** Jairo Marinho

## Funcionamento e fluxo de dados

O sistema acompanha temperatura e umidade em uma sala de aula. O sensor virtual em Python gera uma leitura, associa identificador, localização, data e hora e classifica a condição observada. Na arquitetura proposta, cada leitura é serializada em JSON e publicada no tópico MQTT `cidade/sala-01/ambiente`. O broker recebe o evento e o entrega ao servidor inscrito nesse tópico. O servidor valida e armazena a leitura, disponibilizando ao dashboard a informação atual e o histórico recente. O navegador consulta o servidor por HTTP e atualiza os cartões, o gráfico e a situação ambiental. Nesta implementação inicial, o servidor chama o sensor localmente para demonstrar a interface; a substituição dessa chamada pelo consumidor MQTT não altera o formato dos dados nem a tela.

## Componentes

- **Sensor virtual:** produz temperatura, umidade, horário, identificação e situação.
- **Broker MQTT:** desacopla a produção e o consumo dos eventos de sensoriamento.
- **Servidor:** consome, valida e disponibiliza as leituras por uma API HTTP/JSON.
- **Dashboard:** apresenta leitura atual, estado de conexão, gráfico e histórico recente.

## Definição tecnológica

- **Conectividade:** Wi-Fi, com IP e TCP para comunicação entre os componentes.
- **Paradigma:** Publish/Subscribe entre sensor e servidor, reduzindo o acoplamento.
- **Protocolo de aplicação IoT:** MQTT, tópico `cidade/sala-01/ambiente`, QoS 1 e mensagens JSON.
- **Interface:** HTTP em modelo requisição/resposta entre navegador e servidor.
- **Implementação inicial:** Python 3, HTML, CSS e JavaScript, sem bibliotecas externas.

## Fluxo resumido

`Ambiente -> Sensor virtual -> Wi-Fi/MQTT -> Broker -> Servidor -> HTTP/JSON -> Dashboard`
