import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validacoes import validar_avaliacao, validar_filme

VALIDO = {"titulo": "  Matrix ", "genero": "Ficção científica", "ano": "1999",
          "duracao": "136", "classificacao": "14", "sinopse": ""}


def filme(**alteracoes):
    return validar_filme(dict(VALIDO, **alteracoes))


class TestValidacoes(unittest.TestCase):
    def test_filme_valido_e_convertido(self):
        resultado = filme()
        self.assertEqual(resultado["titulo"], "Matrix")  # espaços removidos
        self.assertEqual(resultado["ano"], 1999)         # texto virou inteiro

    def test_campos_obrigatorios(self):
        for campo in ("titulo", "genero", "ano", "duracao", "classificacao"):
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                filme(**{campo: "  "})

    def test_ano_com_letras(self):
        with self.assertRaisesRegex(ValueError, "número inteiro"):
            filme(ano="20x5")

    def test_limites(self):
        ano_atual = str(date.today().year)
        for campo, aceitos, recusados in [("titulo", ["A" * 100], ["A" * 101]),
                                          ("ano", ["1888", ano_atual], ["1887", str(int(ano_atual) + 1)]),
                                          ("duracao", ["1", "600"], ["0", "601", "1.5"]),
                                          ("sinopse", ["x" * 500], ["x" * 501])]:
            for valor in aceitos:
                filme(**{campo: valor})
            for valor in recusados:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    filme(**{campo: valor})

    def test_avaliacao(self):
        self.assertEqual(validar_avaliacao(5, " Ótimo "), (5, "Ótimo"))
        self.assertEqual(validar_avaliacao(1, "x" * 200)[0], 1)
        for nota, comentario in [(0, ""), (6, ""), (3, "x" * 201)]:
            with self.assertRaises(ValueError):
                validar_avaliacao(nota, comentario)


if __name__ == "__main__":
    unittest.main()
