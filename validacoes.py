"""Regras de validação do CineFlix. Erros viram ValueError com mensagem para o usuário."""

from datetime import date

GENEROS = ["Ação", "Animação", "Aventura", "Comédia", "Documentário", "Drama",
           "Fantasia", "Ficção científica", "Romance", "Suspense", "Terror"]
CLASSIFICACOES = ["L", "10", "12", "14", "16", "18"]


def para_inteiro(texto, campo, minimo, maximo):
    try:
        valor = int(texto.strip())
    except ValueError:
        raise ValueError(f"{campo} deve ser um número inteiro.") from None
    if not minimo <= valor <= maximo:
        raise ValueError(f"{campo} deve estar entre {minimo} e {maximo}.")
    return valor


def validar_filme(campos):
    """Recebe os textos do formulário e devolve o filme pronto para salvar."""
    titulo = campos["titulo"].strip()
    sinopse = campos["sinopse"].strip()
    if not titulo:
        raise ValueError("O título é obrigatório.")
    if len(titulo) > 100:
        raise ValueError("O título deve ter no máximo 100 caracteres.")
    if campos["genero"] not in GENEROS:
        raise ValueError("Escolha um gênero da lista.")
    if campos["classificacao"] not in CLASSIFICACOES:
        raise ValueError("Selecione a classificação indicativa.")
    if len(sinopse) > 500:
        raise ValueError("A sinopse deve ter no máximo 500 caracteres.")
    return {
        "titulo": titulo,
        "genero": campos["genero"],
        "ano": para_inteiro(campos["ano"], "Ano", 1888, date.today().year),
        "duracao": para_inteiro(campos["duracao"], "Duração", 1, 600),
        "classificacao": campos["classificacao"],
        "sinopse": sinopse,
    }


def validar_avaliacao(nota, comentario):
    if nota not in range(1, 6):
        raise ValueError("Escolha uma nota de 1 a 5 estrelas.")
    comentario = comentario.strip()
    if len(comentario) > 200:
        raise ValueError("O comentário deve ter no máximo 200 caracteres.")
    return nota, comentario
