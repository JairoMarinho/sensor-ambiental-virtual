import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.sensor_virtual.sensor import LeituraAmbiental
from src.sensor_virtual.storage import carregar_leituras, salvar_leitura


class TesteArmazenamento(unittest.TestCase):
    def setUp(self) -> None:
        self.leitura = LeituraAmbiental(
            identificador="teste-01",
            local="Sala de teste",
            data_hora="2026-10-27T12:30:00+00:00",
            temperatura_c=25.2,
            umidade_percentual=58.0,
            situacao="confortavel",
        )

    def test_leitura_e_gravacao_do_arquivo(self) -> None:
        with TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "dados" / "leituras.jsonl"
            salvar_leitura(arquivo, self.leitura)
            salvar_leitura(arquivo, self.leitura)

            registros = carregar_leituras(arquivo)

            self.assertEqual(len(registros), 2)
            self.assertEqual(registros[0], self.leitura.como_dicionario())

    def test_erro_indica_a_linha_com_json_invalido(self) -> None:
        with TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "leituras.jsonl"
            conteudo = json.dumps(self.leitura.como_dicionario()) + "\ntexto inválido\n"
            arquivo.write_text(conteudo, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "linha 2"):
                carregar_leituras(arquivo)


if __name__ == "__main__":
    unittest.main()
