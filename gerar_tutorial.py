from __future__ import annotations

from pathlib import Path

from fpdf import FPDF


class TutorialPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120)
            self.cell(0, 6, "docrag - Tutorial de Uso dos Agentes", align="C")
            self.ln(8)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120)
            self.cell(0, 10, f"Pagina {self.page_no() - 1}", align="C")

    def titulo_secao(self, num: str, titulo: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 60, 120)
        self.cell(0, 10, f"{num}. {titulo}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(20, 60, 120)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def subsecao(self, titulo: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, titulo, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def corpo(self, texto: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, texto)
        self.ln(2)

    def codigo(self, texto: str):
        self.set_font("Courier", "", 9)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(40, 40, 40)
        self.set_draw_color(200, 200, 200)
        self.ln(1)
        for linha in texto.strip().split("\n"):
            self.cell(0, 5, f"  {linha}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)

    def comando(self, texto: str):
        self.set_font("Courier", "", 10)
        self.set_fill_color(20, 40, 80)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, f"  $ {texto}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)

    def nota(self, texto: str):
        self.set_font("Helvetica", "I", 9)
        self.set_fill_color(255, 255, 220)
        self.set_text_color(100, 80, 0)
        self.set_draw_color(200, 180, 0)
        self.ln(1)
        self.multi_cell(0, 5, f"  {texto}", fill=True)
        self.ln(3)

    def bullet(self, texto: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.cell(5, 5.5, "-")
        self.multi_cell(0, 5.5, texto)


pdf = TutorialPDF(orientation="P", unit="mm", format="A4")
pdf.set_auto_page_break(auto=True, margin=20)

# --- CAPA ---
pdf.add_page()
pdf.ln(50)
pdf.set_font("Helvetica", "B", 26)
pdf.set_text_color(20, 60, 120)
pdf.cell(0, 12, "docrag", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", "", 16)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 10, "Tutorial de Uso dos Agentes", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 8, "Consulta e Revisao de Codigo com IA", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(30)
pdf.set_draw_color(20, 60, 120)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(10)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Versao 1.0 - Junho 2026", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Repositorio: github.com/tsvsampaio/docrag", align="C", new_x="LMARGIN", new_y="NEXT")

# --- SUMARIO ---
pdf.add_page()
pdf.titulo_secao("", "Sumario")
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(30, 30, 30)
itens_sumario = [
    ("1", "Introducao"),
    ("2", "Pre-requisitos"),
    ("3", "Configuracao do Ambiente"),
    ("4", "Agente Expert - Consulta a Documentacao"),
    ("  4.1", "Sintaxe basica"),
    ("  4.2", "Exemplos de perguntas"),
    ("  4.3", "Entendendo a resposta"),
    ("5", "Agente Revisor - Correcao de Codigo"),
    ("  5.1", "Sintaxe basica"),
    ("  5.2", "Exemplo de revisao"),
    ("  5.3", "Ferramentas do revisor"),
    ("6", "Cenarios de Uso"),
    ("7", "Solucao de Problemas"),
    ("8", "Referencias"),
]
for num, tit in itens_sumario:
    pdf.cell(0, 6.5, f"  {num}   {tit}", new_x="LMARGIN", new_y="NEXT")

# --- 1. INTRODUCAO ---
pdf.add_page()
pdf.titulo_secao("1", "Introducao")
pdf.corpo(
    "O docrag e um sistema de RAG (Retrieval-Augmented Generation) que combina "
    "a documentacao do framework agno com agentes de IA para oferecer dois "
    "servicos principais:\n\n"
    "- Agente Expert: consulta a documentacao indexada em uma base vetorial "
    "(ChromaDB) e responde perguntas sobre o framework agno em portugues ou ingles.\n\n"
    "- Agente Revisor: analisa arquivos de codigo Python, executa linter e "
    "formatador, e retorna o codigo corrigido completo.\n\n"
    "Os agentes utilizam modelos da OpenAI:\n\n"
    "- Expert: GPT-4o-mini (rapido e economico para consulta a documentacao)\n"
    "- Revisor: GPT-4o (mais preciso para geracao e correcao de codigo)\n\n"
    "O embedder text-embedding-3-small e usado para indexacao vetorial."
)

# --- 2. PRE-REQUISITOS ---
pdf.titulo_secao("2", "Pre-requisitos")
pdf.corpo("Antes de utilizar os agentes, certifique-se de ter:")
itens = [
    "Python 3.12 ou superior",
    "uv (gerenciador de pacotes) ou pip",
    "Chave de API da OpenAI (OPENAI_API_KEY)",
    "Conexao com a internet (para chamadas as APIs)",
    "O codigo-fonte do projeto clonado do GitHub",
]
for item in itens:
    pdf.bullet(item)
    pdf.ln(1)
pdf.ln(3)

# --- 3. CONFIGURACAO ---
pdf.titulo_secao("3", "Configuracao do Ambiente")
pdf.subsecao("3.1. Clonar o repositorio")
pdf.comando("git clone https://github.com/tsvsampaio/docrag.git")
pdf.comando("cd docrag")

pdf.subsecao("3.2. Criar ambiente virtual com uv")
pdf.comando("uv venv --python 3.12")
pdf.comando(".venv\\Scripts\\activate")
pdf.comando("uv pip install -r requirements.txt")

pdf.subsecao("3.3. Configurar variaveis de ambiente")
pdf.corpo(
    "Crie um arquivo .env na raiz do projeto com sua chave da OpenAI:"
)
pdf.codigo(
    "OPENAI_API_KEY=sk-sua-chave-aqui"
)
pdf.nota(
    "A chave OPENAI_API_KEY e obrigatoria para o funcionamento de ambos os "
    "agentes. Ela e usada tanto para o embedder (indexacao) quanto para o "
    "modelo de linguagem (GPT-4o-mini)."
)

pdf.subsecao("3.4. Verificar a instalacao")
pdf.comando("python cli.py --help")
pdf.corpo("O comando acima deve exibir a lista de subcomandos disponiveis: "
          "crawl, translate, index, ask e review.")

# --- 4. AGENTE EXPERT ---
pdf.add_page()
pdf.titulo_secao("4", "Agente Expert - Consulta a Documentacao")
pdf.corpo(
    "O Agente Expert e um assistente especializado no framework agno. "
    "Ele utiliza duas bases de conhecimento indexadas no ChromaDB:\n\n"
    "- agno_docs_en: documentacao original em ingles (1041 documentos)\n"
    "- agno_docs_pt: documentacao traduzida para portugues (1041 documentos)\n\n"
    "O agente detecta automaticamente o idioma da pergunta e responde no "
    "mesmo idioma, priorizando a base de conhecimento em portugues quando "
    "a pergunta for em PT-BR."
)

pdf.subsecao("4.1. Sintaxe basica")
pdf.comando('python cli.py ask "sua pergunta aqui"')
pdf.corpo("O comando retornara uma resposta formatada em Markdown com "
          "explicacoes e exemplos de codigo quando relevante.")

pdf.subsecao("4.2. Exemplos de perguntas")
pdf.corpo("Perguntas em portugues:")
pdf.comando('python cli.py ask "O que e agno e como criar um agente?"')
pdf.comando('python cli.py ask "Como usar tools em agentes agno?"')
pdf.comando('python cli.py ask "Qual a diferenca entre Agent e Workflow?"')
pdf.ln(2)
pdf.corpo("Perguntas em ingles:")
pdf.comando('python cli.py ask "How to create a custom tool in agno?"')
pdf.comando('python cli.py ask "How does Knowledge work in agno 2.x?"')

pdf.subsecao("4.3. Entendendo a resposta")
pdf.corpo(
    "A resposta do Expert contem:\n\n"
    "- Uma explicacao direta da pergunta\n"
    "- Exemplos de codigo com syntax highlighting (bound por ```)\n"
    "- Referencia a documentacao oficial quando aplicavel\n"
    "- Links uteis para aprofundamento\n\n"
    "O agente consulta a base vetorial em tempo real para cada pergunta, "
    "garantindo que a resposta seja baseada na documentacao mais recente "
    "do agno que foi indexada."
)

# --- 5. AGENTE REVISOR ---
pdf.add_page()
pdf.titulo_secao("5", "Agente Revisor - Correcao de Codigo")
pdf.corpo(
    "O Agente Revisor e um assistente especializado em revisao de codigo "
    "Python. Ele le o arquivo, analisa o codigo, executa ferramentas de "
    "qualidade (linter e formatador) e retorna o codigo corrigido completo "
    "com explicacoes das alteracoes realizadas."
)

pdf.subsecao("5.1. Sintaxe basica")
pdf.comando("python cli.py review caminho/para/arquivo.py")
pdf.corpo("O caminho pode ser absoluto ou relativo ao diretorio do projeto.\n\n"
"O Revisor utiliza o modelo GPT-4o (modelo completo, nao o mini) para "
"maior precisao na geracao de codigo corrigido. O Expert continua "
"usando GPT-4o-mini.")

pdf.subsecao("5.2. Exemplo de revisao")
pdf.corpo("Vamos revisar o proprio cli.py do projeto:")
pdf.comando("python cli.py review cli.py")
pdf.corpo(
    "O agente ira:\n"
    "1. Ler o conteudo do arquivo\n"
    "2. Executar o linter (ruff check) para identificar problemas\n"
    "3. Executar o formatador (ruff format --check) para verificar formatacao\n"
    "4. Analisar o codigo e sugerir melhorias\n"
    "5. Retornar o CODIGO CORRIGIDO COMPLETO\n\n"
    "Diferenca de ferramentas convencionais: o Revisor nao apenas aponta "
    "erros, mas reescreve o codigo corrigido e explica cada alteracao."
)

pdf.subsecao("5.3. Ferramentas do revisor")
pdf.corpo("O agente Revisor possui quatro ferramentas integradas:")

pdf.corpo("1. read_file(caminho)")
pdf.corpo("   Le o conteudo do arquivo especificado. Suporta qualquer "
          "arquivo de texto (Python, Markdown, JSON, etc).")
pdf.ln(1)
pdf.corpo("2. run_linter(caminho)")
pdf.corpo("   Executa ruff check no arquivo e retorna a saida do linter. "
          "Identifica erros de sintaxe, codigo morto, importacoes nao "
          "utilizadas, convencoes PEP 8, entre outros.")
pdf.ln(1)
pdf.corpo("3. run_format_check(caminho)")
pdf.corpo("   Executa ruff format --check para verificar se o arquivo esta "
          "formatado corretamente segundo o estilo padrao do ruff, que "
          "segue a PEP 8 com ajustes modernos.")
pdf.ln(1)
pdf.corpo("4. run_syntax_check(caminho)")
pdf.corpo("   Executa compile() no codigo Python para detectar erros de "
          "sintaxe sem executar o arquivo. Esta e a primeira linha de "
          "defesa contra alucinacoes: se o codigo sugerido pelo modelo "
          "tiver erro de sintaxe, esta ferramenta aponta antes mesmo "
          "de voce tentar rodar.")
pdf.ln(2)
pdf.nota(
    "O ruff precisa estar instalado no ambiente. Se nao estiver, "
    "instale com: uv pip install ruff"
)

# --- 6. CENARIOS ---
pdf.add_page()
pdf.titulo_secao("6", "Cenarios de Uso")

pdf.subsecao("6.1. Aprendendo um novo framework")
pdf.corpo(
    "Ao iniciar com o framework agno, use o Expert para tirar duvidas "
    "rapidas sem precisar ler toda a documentacao:\n\n"
    '  python cli.py ask "Como criar um Agent com ferramentas?"\n\n'
    "O agente busca os documentos relevantes e sintetiza uma resposta "
    "objetiva com exemplos."
)

pdf.subsecao("6.2. Code review automatizado")
pdf.corpo(
    "Antes de fazer um commit, revise o codigo com o agente Revisor:\n\n"
    "  python cli.py review src/crawler.py\n\n"
    "Isso economiza tempo ao identificar problemas que passariam "
    "despercebidos e ja entrega o codigo corrigido."
)

pdf.subsecao("6.3. Documentacao em PT-BR")
pdf.corpo(
    "A documentacao do agno e integralmente em ingles. O projeto docrag "
    "traduz os 1041 documentos para portugues, permitindo que "
    "desenvolvedores com menos fluencia em ingles consultem a documentacao "
    "no seu idioma nativo:\n\n"
    '  python cli.py ask "O que sao tools no agno?"\n\n'
    "A resposta vira em portugues com exemplos em ingles (preservados "
    "para nao quebrar a sintaxe)."
)

pdf.subsecao("6.4. Pipeline CI/CD local")
pdf.corpo(
    "Integre o Revisor em um script de pre-commit:\n\n"
    '  python cli.py review "$@"\n\n'
    "Isso garante que todo codigo commitado passe por uma revisao "
    "automatizada antes de ir para o repositorio."
)

# --- 7. SOLUCAO DE PROBLEMAS ---
pdf.add_page()
pdf.titulo_secao("7", "Solucao de Problemas")

pdf.subsecao("Problema: OPENAI_API_KEY nao configurada")
pdf.corpo(
    "Sintoma: Erro de autenticacao ao executar ask ou review.\n"
    "Solucao: Verifique se o arquivo .env existe na raiz do projeto "
    "e contem a linha OPENAI_API_KEY=sk-... ."
)

pdf.subsecao("Problema: ChromaDB vazio / nenhum documento encontrado")
pdf.corpo(
    "Sintoma: O Expert responde com conhecimento geral, sem citar "
    "a documentacao.\n"
    "Solucao: Execute o pipeline completo novamente:\n"
    "  python cli.py crawl --site agno\n"
    "  python cli.py translate\n"
    "  python cli.py index"
)

pdf.subsecao("Problema: ruff nao encontrado")
pdf.corpo(
    "Sintoma: O Revisor retorna erro ao executar linter.\n"
    "Solucao: Instale o ruff no ambiente:\n"
    "  uv pip install ruff"
)

pdf.subsecao("Problema: GPT-4o retorna erro de autenticacao")
pdf.corpo(
    "Sintoma: O Revisor falha ao chamar o modelo gpt-4o.\n"
    "Solucao: O modelo gpt-4o requer uma conta OpenAI com acesso "
    "ao nivel adequado. Verifique se sua chave OPENAI_API_KEY tem "
    "acesso ao gpt-4o (contas de desenvolvedor tem). "
    "Se necessario, troque de volta para gpt-4o-mini no reviewer.py."
)

pdf.subsecao("Problema: Resposta em ingles quando esperava PT-BR")
pdf.corpo(
    "Sintoma: O Expert respondeu em ingles para uma pergunta em "
    "portugues.\n"
    "Solucao: Reformule a pergunta de forma clara em portugues. O "
    "agente detecta o idioma pelo texto da pergunta. "
    "Perguntas curtas ou ambíguas podem ser interpretadas como ingles."
)

pdf.subsecao("Problema: Erro de memoria / rate limit")
pdf.corpo(
    "Sintoma: Resposta truncada ou erro HTTP 429.\n"
    "Solucao: O GPT-4o-mini tem limites de uso por minuto. "
    "Aguarde alguns segundos e tente novamente."
)

# --- 8. REFERENCIAS ---
pdf.titulo_secao("8", "Referencias")
pdf.corpo(
    "- Repositorio do projeto: https://github.com/tsvsampaio/docrag\n"
    "- Documentacao do agno: https://docs.agno.com\n"
    "- Documentacao do ChromaDB: https://docs.trychroma.com\n"
    "- OpenAI API: https://platform.openai.com\n"
    "- Ruff (linter): https://docs.astral.sh/ruff\n"
    "- Tutorial gerado em 22/06/2026"
)

pdf.ln(10)
pdf.set_font("Helvetica", "I", 9)
pdf.set_text_color(140, 140, 140)
pdf.multi_cell(0, 5, "docrag - Tutorial de Uso dos Agentes\n"
               "Criado por tsvsampaio | github.com/tsvsampaio/docrag\n"
               "Licenca: MIT")

# Salvar
caminho = Path(__file__).resolve().parent / "docrag_tutorial_agentes.pdf"
pdf.output(str(caminho))
print(f"PDF gerado: {caminho}")
print(f"Tamanho: {caminho.stat().st_size / 1024:.0f} KB")
print(f"Paginas: {pdf.page_no()}")
