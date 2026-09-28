"""Interface gráfica do CineFlix (Tkinter + ttk)."""

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from dados import media
from validacoes import CLASSIFICACOES, GENEROS, validar_avaliacao, validar_filme

FUNDO, PAINEL, CAMPO, TEXTO, VERMELHO = "#141414", "#1f1f1f", "#2b2b2b", "#e5e5e5", "#e50914"
FONTE = "Segoe UI"


def estrelas(nota):
    return "★" * round(nota) + "☆" * (5 - round(nota))


class AppCineFlix(tk.Tk):
    def __init__(self, catalogo):
        super().__init__()
        self.catalogo = catalogo
        self.id_em_edicao = None  # None = cadastrando um filme novo
        self.title("CineFlix — Streaming de filmes")
        self.geometry("1100x700")
        self.minsize(900, 620)
        self.configure(bg=FUNDO)
        self._criar_estilo()

        # a janela principal usa só pack; cada aba usa grid por dentro
        ttk.Label(self, text="CINEFLIX", foreground=VERMELHO,
                  font=(FONTE, 24, "bold")).pack(anchor="w", padx=16, pady=(10, 0))
        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, padding=(16, 4)).pack(side="bottom", fill="x")
        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=16, pady=8)
        self.aba_catalogo = self._criar_catalogo()
        self.aba_cadastro = self._criar_cadastro()
        self._criar_resumo()

        self.bind("<Control-f>", lambda e: (self.abas.select(self.aba_catalogo),
                                            self.entrada_busca.focus_set()))
        self.bind("<Control-n>", lambda e: self.abrir_formulario())
        self.bind("<Control-s>", lambda e: self.salvar_filme())
        self.protocol("WM_DELETE_WINDOW", self.ao_sair)

        aviso = catalogo.carregar()
        if aviso:
            messagebox.showwarning("Problema nos dados", aviso)
        self.preencher_formulario()
        self.atualizar()
        self.status.set(f"{len(catalogo.filmes)} filme(s) carregado(s).")

    def _criar_estilo(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")  # o tema clam permite trocar as cores
        estilo.configure(".", background=FUNDO, foreground=TEXTO, fieldbackground=CAMPO,
                         bordercolor=CAMPO, lightcolor=CAMPO, darkcolor=CAMPO,
                         arrowcolor=TEXTO, insertcolor=TEXTO, font=(FONTE, 10))
        estilo.configure("Painel.TFrame", background=PAINEL)
        estilo.configure("Painel.TLabel", background=PAINEL)
        estilo.configure("TButton", background=CAMPO, padding=6)
        estilo.configure("Vermelho.TButton", background=VERMELHO, foreground="white")
        estilo.map("TButton", background=[("active", "#3a3a3a")])
        estilo.map("Vermelho.TButton", background=[("active", "#b20710")])
        estilo.configure("TNotebook.Tab", background=FUNDO, padding=(16, 6))
        estilo.map("TNotebook.Tab", background=[("selected", VERMELHO)])
        estilo.configure("Treeview", background=PAINEL, fieldbackground=PAINEL, rowheight=26)
        estilo.map("Treeview", background=[("selected", VERMELHO)])
        estilo.configure("Treeview.Heading", background=CAMPO)
        estilo.map("Treeview.Heading", background=[("active", "#3a3a3a")])
        estilo.map("TCombobox", fieldbackground=[("readonly", CAMPO)])
        for tipo in ("TCheckbutton", "TRadiobutton"):
            estilo.configure(tipo, indicatorbackground=CAMPO)
            estilo.map(tipo, background=[("active", FUNDO)],
                       indicatorbackground=[("selected", VERMELHO)])
        estilo.configure("Horizontal.TProgressbar", background=VERMELHO)
        self.option_add("*TCombobox*Listbox.background", CAMPO)
        self.option_add("*TCombobox*Listbox.foreground", TEXTO)

    # ---------------- aba Catálogo ----------------
    def _criar_catalogo(self):
        aba = ttk.Frame(self.abas, padding=10)
        self.abas.add(aba, text="Catálogo")
        aba.columnconfigure(0, weight=1)
        aba.rowconfigure(1, weight=1)

        filtros = ttk.Frame(aba)
        filtros.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        self.busca = tk.StringVar()
        self.genero = tk.StringVar(value="Todos")
        self.somente_lista = tk.BooleanVar()
        ttk.Label(filtros, text="Buscar título (Ctrl+F):").pack(side="left")
        self.entrada_busca = ttk.Entry(filtros, textvariable=self.busca, width=28)
        self.entrada_busca.pack(side="left", padx=6)
        ttk.Label(filtros, text="Gênero:").pack(side="left", padx=(12, 6))
        combo = ttk.Combobox(filtros, textvariable=self.genero, values=["Todos", *GENEROS],
                             state="readonly", width=18)
        combo.pack(side="left")
        ttk.Checkbutton(filtros, text="Somente Minha Lista", variable=self.somente_lista,
                        command=self.atualizar_tabela).pack(side="left", padx=12)
        self.busca.trace_add("write", lambda *args: self.atualizar_tabela())
        combo.bind("<<ComboboxSelected>>", lambda e: self.atualizar_tabela())

        colunas = [("titulo", "Título", 220), ("genero", "Gênero", 115), ("ano", "Ano", 50),
                   ("duracao", "Duração", 70), ("nota", "Avaliação", 110), ("lista", "Na lista", 65)]
        self.tabela = ttk.Treeview(aba, columns=[c[0] for c in colunas], show="headings",
                                   selectmode="browse")
        for chave, titulo, largura in colunas:
            self.tabela.heading(chave, text=titulo)
            self.tabela.column(chave, width=largura, stretch=chave == "titulo",
                               anchor="w" if chave == "titulo" else "center")
        rolagem = ttk.Scrollbar(aba, command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.grid(row=1, column=0, sticky="nsew")
        rolagem.grid(row=1, column=1, sticky="ns")
        self.aviso = ttk.Label(aba, foreground="#a3a3a3")
        self.aviso.grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.tabela.bind("<<TreeviewSelect>>", lambda e: self.mostrar_detalhes())
        self.tabela.bind("<Double-1>", lambda e: self.assistir())
        self.tabela.bind("<Return>", lambda e: self.assistir())
        self.tabela.bind("<Delete>", lambda e: self.excluir_filme())

        # painel de detalhes: widgets empilhados com pack
        painel = ttk.Frame(aba, style="Painel.TFrame", padding=14, width=320)
        painel.grid(row=1, column=2, rowspan=2, sticky="ns", padx=(10, 0))
        painel.pack_propagate(False)
        self.det_titulo = ttk.Label(painel, style="Painel.TLabel", wraplength=290,
                                    font=(FONTE, 15, "bold"))
        self.det_titulo.pack(anchor="w")
        self.det_texto = ttk.Label(painel, style="Painel.TLabel", wraplength=290, justify="left")
        self.det_texto.pack(anchor="w", pady=(4, 8))
        ttk.Button(painel, text="▶  Assistir", style="Vermelho.TButton",
                   command=self.assistir).pack(fill="x", pady=2)
        self.botao_lista = ttk.Button(painel, command=self.alternar_lista)
        self.botao_lista.pack(fill="x", pady=2)
        linha = ttk.Frame(painel, style="Painel.TFrame")
        linha.pack(fill="x", pady=2)
        ttk.Button(linha, text="✎  Editar", command=self.editar_filme).pack(
            side="left", fill="x", expand=True)
        ttk.Button(linha, text="✖  Excluir", command=self.excluir_filme).pack(
            side="left", fill="x", expand=True, padx=(4, 0))

        ttk.Label(painel, text="Sua nota e comentário (opcional):", style="Painel.TLabel",
                  font=(FONTE, 10, "bold")).pack(anchor="w", pady=(12, 4))
        self.nota = tk.StringVar()
        self.comentario = tk.StringVar()
        linha = ttk.Frame(painel, style="Painel.TFrame")
        linha.pack(fill="x")
        ttk.Combobox(linha, textvariable=self.nota, state="readonly", width=10,
                     values=["★" * n for n in range(1, 6)]).pack(side="left")
        ttk.Button(linha, text="★  Avaliar", command=self.avaliar).pack(side="right")
        ttk.Entry(painel, textvariable=self.comentario).pack(fill="x", pady=4)
        self.lista_avaliacoes = tk.Listbox(painel, bg=CAMPO, fg=TEXTO, borderwidth=0, height=4,
                                           highlightthickness=0, activestyle="none")
        self.lista_avaliacoes.pack(fill="both", expand=True, pady=(8, 0))
        return aba

    def filme_selecionado(self, avisar=True):
        selecao = self.tabela.selection()
        if selecao:
            return self.catalogo.buscar(int(selecao[0]))
        if avisar:
            self.status.set("Selecione um filme na tabela primeiro.")
        return None

    def atualizar_tabela(self):
        selecao = self.tabela.selection()
        self.tabela.delete(*self.tabela.get_children())
        filmes = self.catalogo.pesquisar(self.busca.get(), self.genero.get(),
                                         self.somente_lista.get())
        for f in filmes:
            nota = f"{estrelas(media(f))} {media(f):.1f}" if f["avaliacoes"] else "sem notas"
            self.tabela.insert("", "end", iid=f["id"], values=(
                f["titulo"], f["genero"], f["ano"], f"{f['duracao']} min", nota,
                "✔" if f["na_lista"] else ""))
        self.aviso.configure(text=f"{len(filmes)} filme(s). Duplo clique para assistir." if filmes
                             else "Nenhum filme encontrado. Altere a busca ou os filtros.")
        if selecao and self.tabela.exists(selecao[0]):
            self.tabela.selection_set(selecao[0])
        self.mostrar_detalhes()

    def mostrar_detalhes(self):
        filme = self.filme_selecionado(avisar=False)
        self.lista_avaliacoes.delete(0, "end")
        if filme is None:
            self.det_titulo.configure(text="Selecione um filme")
            self.det_texto.configure(text="")
            self.botao_lista.configure(text="+  Minha Lista")
            return
        nota = (f"{estrelas(media(filme))} {media(filme):.1f} ({len(filme['avaliacoes'])} avaliações)"
                if filme["avaliacoes"] else "Ainda sem avaliações")
        assistido = "  •  ✔ Assistido" if filme["assistido"] else ""
        self.det_titulo.configure(text=filme["titulo"])
        self.det_texto.configure(
            text=f"{filme['ano']} • {filme['genero']} • {filme['duracao']} min • "
                 f"Classificação {filme['classificacao']}{assistido}\n{nota}\n\n"
                 f"{filme['sinopse'] or 'Sinopse não informada.'}")
        self.botao_lista.configure(text="✔  Remover da Minha Lista" if filme["na_lista"]
                                   else "+  Adicionar à Minha Lista")
        for a in reversed(filme["avaliacoes"]):
            self.lista_avaliacoes.insert("end", f"{'★' * a['nota']}  {a['data']}  {a['comentario']}")

    # ---------------- ações sobre o filme selecionado ----------------
    def assistir(self):
        """Abre um player simulado: a barra enche em ~8 s e o filme vira 'assistido'."""
        filme = self.filme_selecionado()
        if filme is None:
            return
        player = tk.Toplevel(self, bg="black")
        player.title(f"Assistindo: {filme['titulo']}")
        player.geometry("600x340")
        player.bind("<Escape>", lambda e: player.destroy())
        tk.Label(player, text=f"▶\n\n{filme['titulo']}", font=(FONTE, 20, "bold"),
                 bg="black", fg=TEXTO).pack(expand=True)
        barra = ttk.Progressbar(player, maximum=100)
        barra.pack(fill="x", padx=16, pady=16)

        def avancar():
            if not player.winfo_exists():   # o usuário fechou o player
                return
            barra["value"] += 1
            if barra["value"] < 100:
                player.after(80, avancar)   # agenda o próximo passo sem travar a janela
            else:
                player.destroy()
                if self.executar(lambda: self.catalogo.marcar_assistido(filme["id"])):
                    self.avisar(f"Você terminou “{filme['titulo']}”. Que tal avaliar?")

        avancar()

    def alternar_lista(self):
        filme = self.filme_selecionado()
        if filme and self.executar(lambda: self.catalogo.alternar_lista(filme["id"])):
            acao = "adicionado à" if filme["na_lista"] else "removido da"
            self.status.set(f"“{filme['titulo']}” {acao} Minha Lista.")

    def avaliar(self):
        filme = self.filme_selecionado()
        if filme and self.executar(lambda: self.catalogo.avaliar(
                filme["id"], *validar_avaliacao(len(self.nota.get()), self.comentario.get()))):
            self.nota.set("")
            self.comentario.set("")
            self.avisar(f"Avaliação de “{filme['titulo']}” registrada. Obrigado!")

    def excluir_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            return
        if not messagebox.askyesno("Confirmar exclusão",
                                   f"Excluir “{filme['titulo']}” e as avaliações dele?",
                                   icon="warning", default="no"):
            self.status.set("Exclusão cancelada.")
            return
        if self.executar(lambda: self.catalogo.excluir(filme["id"])):
            if self.id_em_edicao == filme["id"]:
                self.preencher_formulario()
            self.status.set(f"“{filme['titulo']}” foi excluído.")

    # ---------------- aba Cadastro ----------------
    def _criar_cadastro(self):
        aba = ttk.Frame(self.abas, padding=16)
        self.abas.add(aba, text="Cadastro")
        self.titulo_form = ttk.Label(aba, font=(FONTE, 13, "bold"))
        self.titulo_form.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.campos = {c: tk.StringVar() for c in ("titulo", "genero", "ano", "duracao", "classificacao")}
        classificacao = ttk.Frame(aba)
        for valor in CLASSIFICACOES:
            ttk.Radiobutton(classificacao, text=valor, value=valor,
                            variable=self.campos["classificacao"]).pack(side="left", padx=(0, 12))
        self.sinopse = tk.Text(aba, width=60, height=5, wrap="word", bg=CAMPO, fg=TEXTO,
                               insertbackground=TEXTO, relief="flat", font=(FONTE, 10))
        # Tab dentro do Text inseriria uma tabulação; aqui ele passa ao próximo campo
        self.sinopse.bind("<Tab>", lambda e: (e.widget.tk_focusNext().focus_set(), "break")[1])
        self.entrada_titulo = ttk.Entry(aba, textvariable=self.campos["titulo"], width=50)

        linhas = [
            ("Título *", self.entrada_titulo),
            ("Gênero *", ttk.Combobox(aba, textvariable=self.campos["genero"], values=GENEROS,
                                      state="readonly")),
            ("Ano *", ttk.Spinbox(aba, textvariable=self.campos["ano"], from_=1888,
                                  to=date.today().year, width=8)),
            ("Duração (min) *", ttk.Entry(aba, textvariable=self.campos["duracao"], width=10)),
            ("Classificação *", classificacao),
            ("Sinopse (até 500)", self.sinopse),
        ]
        for linha, (rotulo, widget) in enumerate(linhas, start=1):
            ttk.Label(aba, text=rotulo).grid(row=linha, column=0, sticky="nw", padx=(0, 12), pady=5)
            widget.grid(row=linha, column=1, sticky="w", pady=5)

        botoes = ttk.Frame(aba)
        botoes.grid(row=7, column=1, sticky="w", pady=10)
        ttk.Button(botoes, text="Salvar (Ctrl+S)", style="Vermelho.TButton",
                   command=self.salvar_filme).pack(side="left")
        ttk.Button(botoes, text="Limpar / Novo (Ctrl+N)",
                   command=self.abrir_formulario).pack(side="left", padx=8)
        return aba

    def ler_formulario(self):
        dados = {c: v.get() for c, v in self.campos.items()}
        dados["sinopse"] = self.sinopse.get("1.0", "end-1c")
        return dados

    def preencher_formulario(self, filme=None):
        """Mostra um filme para edição, ou deixa o formulário vazio (filme=None)."""
        self.id_em_edicao = filme["id"] if filme else None
        for campo, var in self.campos.items():
            var.set(filme[campo] if filme else "")
        self.sinopse.delete("1.0", "end")
        self.sinopse.insert("1.0", filme["sinopse"] if filme else "")
        self.titulo_form.configure(text=f"Editando: {filme['titulo']}" if filme
                                   else "Cadastrar novo filme")
        self.formulario_original = self.ler_formulario()  # para detectar alterações

    def formulario_alterado(self):
        return self.ler_formulario() != self.formulario_original

    def abrir_formulario(self, filme=None):
        if self.formulario_alterado() and not messagebox.askyesno(
                "Alterações não salvas", "O cadastro tem alterações não salvas. Descartar?"):
            return
        self.preencher_formulario(filme)
        self.abas.select(self.aba_cadastro)
        self.entrada_titulo.focus_set()

    def editar_filme(self):
        filme = self.filme_selecionado()
        if filme:
            self.abrir_formulario(filme)

    def salvar_filme(self):
        dados = self.ler_formulario()
        editando = self.id_em_edicao
        if not self.executar(lambda: self.catalogo.salvar_filme(validar_filme(dados), editando)):
            return False
        self.preencher_formulario()
        acao = "atualizado" if editando else "cadastrado"
        self.avisar(f"Filme “{dados['titulo'].strip()}” {acao} com sucesso.")
        return True

    # ---------------- aba Resumo ----------------
    def _criar_resumo(self):
        aba = ttk.Frame(self.abas, padding=16)
        self.abas.add(aba, text="Resumo")
        self.indicadores = {}
        itens = [("total", "Filmes no catálogo"), ("na_lista", "Na Minha Lista"),
                 ("assistidos", "Assistidos"), ("avaliacoes", "Avaliações"), ("media", "Média geral")]
        for coluna, (chave, rotulo) in enumerate(itens):
            aba.columnconfigure(coluna, weight=1)
            cartao = ttk.Frame(aba, style="Painel.TFrame", padding=16)
            cartao.grid(row=0, column=coluna, sticky="ew", padx=4)
            self.indicadores[chave] = ttk.Label(cartao, style="Painel.TLabel",
                                                font=(FONTE, 24, "bold"))
            self.indicadores[chave].pack(anchor="w")
            ttk.Label(cartao, text=rotulo, style="Painel.TLabel").pack(anchor="w")
        self.destaque = ttk.Label(aba, font=(FONTE, 12))
        self.destaque.grid(row=1, column=0, columnspan=5, sticky="w", pady=16)

    def atualizar_resumo(self):
        resumo = self.catalogo.resumo()
        for chave, rotulo in self.indicadores.items():
            rotulo.configure(text=resumo[chave])
        melhor = resumo["melhor"]
        self.destaque.configure(text=f"Destaque: {melhor['titulo']} (média {media(melhor):.1f})"
                                if melhor else "Ainda não há avaliações.")

    # ---------------- utilidades ----------------
    def executar(self, operacao):
        """Roda uma operação que altera os dados. Erros de validação (ValueError) ou de
        gravação (OSError) viram uma mensagem, sem fechar o aplicativo."""
        try:
            operacao()
        except (ValueError, OSError) as erro:
            messagebox.showwarning("Não foi possível concluir", str(erro))
            return False
        self.atualizar()
        return True

    def atualizar(self):
        self.atualizar_tabela()
        self.atualizar_resumo()

    def avisar(self, mensagem):
        self.status.set(mensagem)
        messagebox.showinfo("CineFlix", mensagem)

    def ao_sair(self):
        if self.formulario_alterado():
            resposta = messagebox.askyesnocancel(
                "Sair", "O cadastro tem alterações não salvas. Salvar antes de sair?")
            if resposta is None or (resposta and not self.salvar_filme()):
                return  # cancelou, ou tentou salvar e os dados eram inválidos
        self.destroy()
