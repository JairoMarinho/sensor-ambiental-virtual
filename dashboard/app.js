const estado = {
  leituras: [],
  maximo: 8,
};

const elementos = {
  conexao: document.querySelector(".conexao"),
  textoConexao: document.querySelector("#texto-conexao"),
  identificador: document.querySelector("#identificador"),
  local: document.querySelector("#local"),
  atualizacao: document.querySelector("#atualizacao"),
  temperatura: document.querySelector("#temperatura"),
  umidade: document.querySelector("#umidade"),
  situacao: document.querySelector("#situacao"),
  linha: document.querySelector("#linha-grafico"),
  pontos: document.querySelector("#pontos-grafico"),
  historico: document.querySelector("#historico"),
};

function formatarSituacao(situacao) {
  return situacao.replaceAll("_", " ");
}

function desenharGrafico() {
  if (estado.leituras.length === 0) return;

  const largura = 610;
  const inicioX = 45;
  const baseY = 185;
  const altura = 165;
  const passo = estado.leituras.length === 1 ? 0 : largura / (estado.leituras.length - 1);

  const pontos = estado.leituras.map((leitura, indice) => {
    const x = inicioX + indice * passo;
    const temperaturaNormalizada = Math.max(20, Math.min(30, leitura.temperatura_c));
    const y = baseY - ((temperaturaNormalizada - 20) / 10) * altura;
    return { x, y };
  });

  elementos.linha.setAttribute("points", pontos.map(({ x, y }) => `${x},${y}`).join(" "));
  elementos.pontos.innerHTML = pontos
    .map(({ x, y }) => `<circle class="ponto-grafico" cx="${x}" cy="${y}" r="5" />`)
    .join("");
}

function atualizarHistorico() {
  elementos.historico.innerHTML = [...estado.leituras]
    .reverse()
    .slice(0, 5)
    .map((leitura) => {
      const horario = new Date(leitura.data_hora).toLocaleTimeString("pt-BR");
      return `<li><div><strong>${leitura.temperatura_c} °C · ${leitura.umidade_percentual}%</strong><span>${formatarSituacao(leitura.situacao)}</span></div><span>${horario}</span></li>`;
    })
    .join("");
}

function exibirLeitura(leitura) {
  estado.leituras.push(leitura);
  estado.leituras = estado.leituras.slice(-estado.maximo);

  elementos.identificador.textContent = leitura.identificador;
  elementos.local.textContent = leitura.local;
  elementos.atualizacao.textContent = new Date(leitura.data_hora).toLocaleTimeString("pt-BR");
  elementos.temperatura.textContent = leitura.temperatura_c.toFixed(1);
  elementos.umidade.textContent = leitura.umidade_percentual.toFixed(1);
  elementos.situacao.textContent = formatarSituacao(leitura.situacao);
  elementos.conexao.className = "conexao ativa";
  elementos.textoConexao.textContent = "Sensor conectado";

  desenharGrafico();
  atualizarHistorico();
}

async function obterLeitura() {
  try {
    const resposta = await fetch("/api/leitura", { cache: "no-store" });
    if (!resposta.ok) throw new Error("Falha ao consultar o sensor");
    exibirLeitura(await resposta.json());
  } catch (erro) {
    elementos.conexao.className = "conexao erro";
    elementos.textoConexao.textContent = "Sem conexão";
    console.error(erro);
  }
}

obterLeitura();
window.setInterval(obterLeitura, 3000);
