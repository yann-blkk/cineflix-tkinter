import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dados import Catalogo

FILME = {"titulo": "Matrix", "genero": "Ficção científica", "ano": 1999,
         "duracao": 136, "classificacao": "14", "sinopse": ""}


class TestCatalogo(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.arquivo = Path(self.pasta.name) / "filmes.json"
        self.catalogo = Catalogo(self.arquivo)

    def tearDown(self):
        self.pasta.cleanup()

    def reabrir(self):
        novo = Catalogo(self.arquivo)
        novo.carregar()
        return novo

    def test_cadastro_edicao_e_exclusao_persistem(self):
        self.catalogo.salvar_filme(FILME)
        self.assertEqual(self.reabrir().filmes[0]["titulo"], "Matrix")
        self.catalogo.salvar_filme(dict(FILME, duracao=140), id_filme=1)
        self.assertEqual(self.reabrir().filmes[0]["duracao"], 140)
        self.catalogo.excluir(1)
        self.assertEqual(self.reabrir().filmes, [])

    def test_nao_permite_duplicado(self):
        self.catalogo.salvar_filme(FILME)
        with self.assertRaises(ValueError):
            self.catalogo.salvar_filme(dict(FILME, titulo="MATRIX"))

    def test_pesquisa(self):
        self.catalogo.salvar_filme(FILME)
        self.assertEqual(len(self.catalogo.pesquisar("matr")), 1)
        self.assertEqual(self.catalogo.pesquisar("zzz"), [])
        self.assertEqual(self.catalogo.pesquisar(genero="Drama"), [])
        self.assertEqual(self.catalogo.pesquisar(somente_lista=True), [])

    def test_minha_lista_avaliacoes_e_resumo(self):
        self.catalogo.salvar_filme(FILME)
        self.catalogo.alternar_lista(1)
        self.catalogo.avaliar(1, 5, "Ótimo")
        self.catalogo.avaliar(1, 4, "")
        resumo = self.reabrir().resumo()
        self.assertEqual(resumo["na_lista"], 1)
        self.assertEqual(resumo["avaliacoes"], 2)
        self.assertEqual(resumo["media"], "★ 4.5")
        self.assertEqual(resumo["melhor"]["titulo"], "Matrix")

    def test_arquivo_corrompido_vira_backup(self):
        self.arquivo.write_text("{ isso não é json", encoding="utf-8")
        self.assertIn("corrompido", self.catalogo.carregar())
        self.assertEqual(self.catalogo.filmes, [])
        self.assertTrue(self.arquivo.with_suffix(".bak").exists())


if __name__ == "__main__":
    unittest.main()
