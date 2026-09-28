import json
import os
from datetime import date
from pathlib import Path

ARQUIVO_PADRAO = Path(__file__).parent / "dados" / "filmes.json"


def media(filme):
    notas = [a["nota"] for a in filme["avaliacoes"]]
    return sum(notas) / len(notas) if notas else 0.0


class Catalogo:
    def __init__(self, arquivo=ARQUIVO_PADRAO):
        self.arquivo = Path(arquivo)
        self.filmes = []

    def carregar(self):
        if not self.arquivo.exists():
            return None
        try:
            with open(self.arquivo, encoding="utf-8") as f:
                self.filmes = json.load(f)
        except json.JSONDecodeError:
            os.replace(self.arquivo, self.arquivo.with_suffix(".bak"))
            self.filmes = []
            return
        return None

    def salvar(self):
        self.arquivo.parent.mkdir(exist_ok=True)
        temporario = self.arquivo.with_suffix(".tmp")
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(self.filmes, f, ensure_ascii=False, indent=2)
        os.replace(temporario, self.arquivo)

    def buscar(self, id_filme):
        return next((f for f in self.filmes if f["id"] == id_filme), None)

    def salvar_filme(self, dados, id_filme=None):
        for f in self.filmes:
            if (f["titulo"].lower(), f["ano"]) == (dados["titulo"].lower(), dados["ano"]) and f["id"] != id_filme:
                raise ValueError("Já existe um filme com esse título e ano.")
        if id_filme is None:
            novo_id = max((f["id"] for f in self.filmes), default=0) + 1
            self.filmes.append({"id": novo_id, **dados, "na_lista": False,
                                "assistido": False, "avaliacoes": []})
        else:
            self.buscar(id_filme).update(dados)
        self.salvar()

    def excluir(self, id_filme):
        self.filmes.remove(self.buscar(id_filme))
        self.salvar()

    def pesquisar(self, texto="", genero="Todos", somente_lista=False):
        texto = texto.strip().lower()
        encontrados = [f for f in self.filmes
                       if texto in f["titulo"].lower()
                       and genero in ("Todos", f["genero"])
                       and (f["na_lista"] or not somente_lista)]
        return sorted(encontrados, key=lambda f: f["titulo"].lower())

    def alternar_lista(self, id_filme):
        filme = self.buscar(id_filme)
        filme["na_lista"] = not filme["na_lista"]
        self.salvar()

    def marcar_assistido(self, id_filme):
        self.buscar(id_filme)["assistido"] = True
        self.salvar()

    def avaliar(self, id_filme, nota, comentario):
        self.buscar(id_filme)["avaliacoes"].append(
            {"nota": nota, "comentario": comentario, "data": date.today().strftime("%d/%m/%Y")})
        self.salvar()

    def resumo(self):
        notas = [a["nota"] for f in self.filmes for a in f["avaliacoes"]]
        avaliados = [f for f in self.filmes if f["avaliacoes"]]
        return {
            "total": len(self.filmes),
            "na_lista": sum(f["na_lista"] for f in self.filmes),
            "assistidos": sum(f["assistido"] for f in self.filmes),
            "avaliacoes": len(notas),
            "media": f"★ {sum(notas) / len(notas):.1f}" if notas else "—",
            "melhor": max(avaliados, key=media, default=None),
        }
