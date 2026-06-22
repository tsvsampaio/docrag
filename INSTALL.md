# Instalacao e Dependencias

## Ambiente

- **Python:** >= 3.10 (testado com 3.14.3)
- **Pip:** 25.3+ (ou **uv** 0.6+)
- **SO:** Windows 11 (x64)

## Instalacao com uv (recomendado)

```bash
# 1. Instalar uv (se ainda nao tiver)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Criar e ativar ambiente virtual
uv venv --python 3.12
.venv\Scripts\activate

# 3. Instalar dependencias
uv pip install -r requirements.txt

# 4. Configurar .env
copy .env.example .env
# Edite .env com suas chaves (GROQ_API_KEY, OPENAI_API_KEY, TAVILY_API_KEY)
```

## Alternativa com pip

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Dependencias Diretas

| Pacote | Versao | Uso |
|--------|--------|-----|
| `agno[chromadb,openai]` | >= 2.6.18 | Framework de agentes com vector store e embedder |
| `chromadb` | >= 1.5.9 | Vector store local |
| `groq` | >= 1.4.0 | SDK Groq API |
| `openai` | >= 2.43.0 | Embedder OpenAI + SDK |
| `tavily-python` | >= 0.7.26 | Busca web (ferramenta do agente) |
| `fastapi` | >= 0.123.10 | API REST |
| `uvicorn` | >= 0.38.0 | Servidor ASGI |
| `sqlalchemy` | >= 2.0.51 | Banco relacional |
| `pypdf` | >= 6.13.3 | Leitura de PDFs |
| `python-dotenv` | >= 1.2.1 | Carregar .env |
| `httpx` | >= 0.28.1 | HTTP client |
| `yfinance` | >= 1.4.1 | Dados financeiros |
| `ipykernel` | >= 7.3.0 | Jupyter kernel |
| `onnxruntime` | < 1.24 | Execucao de modelos ONNX |

## Variaveis de Ambiente

```bash
# Obrigatorio para rodar os agentes
GROQ_API_KEY=gsk_xxx

# Necessario para o embedder padrao do ChromaDb no agno
OPENAI_API_KEY=sk-xxx

# Opcional — busca web via Tavily
TAVILY_API_KEY=tvly-xxx
```

## Estrutura de Pastas

```
docrag/
├── .venv/               # Ambiente virtual
├── data/
│   ├── agno/            # Docs crawleadas (.md en)
│   └── agno_pt/         # Docs traduzidas (.pt-BR.md)
├── chroma_db/           # Banco ChromaDB persistente
├── .env                 # Chaves de API (gitignorado)
└── ... demais arquivos ...
```
