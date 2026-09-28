# CineFlix — streaming de filmes com Tkinter

Criadores: 
Yan Lucas,
Henrique Falcão 

Aplicativo desktop em Python, no estilo Netflix, para organizar um catálogo de filmes. Permite "assistir" num player simulado, avaliar com estrelas e montar a **Minha Lista** (lista de desejos). Foi desenvolvido para a atividade *Aplicativo Desktop com Python e Tkinter* (SENAI).

## Objetivo

Substituir os controles manuais de um cineclube ou locadora comunitária: acervo, notas dos espectadores e filmes que cada pessoa quer assistir. Os dados ficam íntegros e as mensagens ajudam a corrigir erros.

## Requisitos para executar

- **Python 3.10 ou superior** (testado no Python 3.14 com Windows 11)
- **Tkinter**: já vem com o Python no Windows e no macOS. No Linux: `sudo apt install python3-tk`
- Nenhuma biblioteca externa

## Instalação e execução

```bash
# 1. Baixe o projeto e entre na pasta
git clone https://github.com/yann-blkk/cineflix-tkinter.git
cd cineflix-tkinter

# 2. (opcional) crie um ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS

# 3. Execute
python main.py
```

Para rodar os testes automatizados:

```bash
python -m unittest discover -s testes -v
```

## Como usar

| Aba / janela | O que fazer |
|---|---|
| **Catálogo** | Digite parte do título na busca, filtre por gênero ou marque "Somente Minha Lista". Clique num filme para ver os detalhes, a média e as avaliações. Use os botões **Assistir**, **Adicionar à Minha Lista**, **Editar** e **Excluir** |
| **Avaliar** | No painel do Catálogo, escolha de ★ a ★★★★★, escreva um comentário opcional (até 200 caracteres) e clique em **Avaliar** |
| **Player** | Abre ao clicar em Assistir (ou com duplo clique/Enter na tabela). A barra de progresso simula o filme (cerca de 8 s); Esc fecha. Ao terminar, o filme fica como assistido |
| **Cadastro** | Preencha os campos com * e clique em **Salvar** (Ctrl+S). **Limpar / Novo** (Ctrl+N) começa um cadastro novo. Para editar, use o botão Editar no Catálogo |
| **Resumo** | Totais, média geral e filme em destaque |

**Atalhos:** Ctrl+F busca · Ctrl+N novo · Ctrl+S salvar · Enter assistir · Delete excluir · Esc fechar o player.

## Requisitos atendidos

RF01 a RF08 e RNF01 a RNF06 do enunciado. A tabela que liga cada requisito à funcionalidade está em [docs/2_proposta_e_planejamento.docx](docs/2_proposta_e_planejamento.docx).

## Estrutura

```
main.py            ponto de entrada
interface.py       telas, eventos e player (classe AppCineFlix)
dados.py           classe Catalogo: CRUD, Minha Lista, avaliações, resumo e JSON
validacoes.py      regras de validação
dados/filmes.json  dados iniciais (12 filmes de exemplo)
testes/            10 testes automatizados (unittest)
evidencias/        capturas de tela dos testes
docs/              pesquisa, planejamento, plano de testes, apresentação
```

## Persistência

Os dados ficam em `dados/filmes.json`, gravado a cada operação. A gravação usa um arquivo temporário e depois substitui o original, para não corromper os dados se o programa fechar no meio. Se o arquivo estiver ilegível ao abrir, ele é preservado como `filmes.bak` e o app começa vazio, com um aviso. Para voltar aos dados de exemplo, restaure o `filmes.json` original do ZIP.

## Limitações

- O player é uma **simulação**: não reproduz vídeo, porque o Tkinter não tem player de vídeo nativo.
- Não há login nem perfis: a Minha Lista e as avaliações são do computador, não de cada usuário.
- Não há capas (imagens) dos filmes, e o player não pode ser pausado.
- O JSON é regravado inteiro a cada operação, o que é adequado para centenas de filmes, mas não para milhares. Para isso, SQLite seria melhor.
- Se a gravação falhar (disco cheio, arquivo bloqueado), o erro é informado, mas a alteração continua na memória até o app ser fechado.
- Mensagens de validação aparecem uma por vez (a primeira encontrada).
- O Tkinter tem suporte limitado a leitores de tela.

## Documentação da atividade

1. [Pesquisa sobre Tkinter + fontes](docs/1_pesquisa_tkinter.docx)
2. [Proposta, esboço e dicionário de dados](docs/2_proposta_e_planejamento.docx)
3. [Plano de testes, falhas e correções](docs/3_plano_de_testes.docx)
4. [Roteiro da apresentação, checklist e autoavaliação](docs/4_apresentacao_e_autoavaliacao.docx)
