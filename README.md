# Scoreplan API Skill — Claude Code Integration

Skill para [Claude Code](https://claude.com/claude-code) que permite gerenciar e integrar dados com a [API do Scoreplan](https://app.scoreplan.com.br/api/docs) — indicadores, ações, projetos, OKRs, períodos, orçamento e campos integrados. Inclui **upload em massa via planilha (.xlsx/.csv)**.

## Funcionalidades

- **Autenticação** automática via Bearer Token (API v2) ou Chave da API (API v1)
- **CRUD completo** de indicadores, ações, projetos, OKRs e períodos
- **Upload em massa** via planilha (.xlsx ou .csv) — indicadores, ações, projetos, OKRs e valores
- **Templates prontos** para cada tipo de upload
- **Script Python** standalone para integrações automatizadas
- **Tratamento de erros** com rollback automático (inserções transacionais)

## Instalação

### 1. Copiar a skill para o Claude Code

```bash
# Clonar o repositório
git clone https://github.com/SEU_USUARIO/scoreplan-api-skill.git

# Copiar para o diretório de skills do Claude Code
cp -r scoreplan-api-skill/skill ~/.claude/skills/scoreplan
```

### 2. Estrutura de diretórios

```
~/.claude/skills/scoreplan/
├── SKILL.md                          # Definição principal da skill
└── references/
    ├── api-catalog.md                # Catálogo completo de endpoints
    ├── bulk_upload.py                # Script de upload em massa
    └── templates/
        ├── indicadores.csv           # Template para indicadores
        ├── acoes.csv                 # Template para ações
        ├── projetos.csv              # Template para projetos
        ├── okrs.csv                  # Template para OKRs
        └── valores-indicadores.csv   # Template para valores
```

### 3. Dependências (para upload em massa)

```bash
pip install requests openpyxl
```

## Uso com Claude Code

Após instalar, basta mencionar "Scoreplan" em qualquer conversa com o Claude Code:

```
> Listar indicadores do Scoreplan
> Importar ações da planilha acoes.xlsx para o Scoreplan
> Criar um projeto no Scoreplan chamado "Expansão 2026"
> Upload em massa de OKRs via planilha
> Buscar valores do indicador IND001 no Scoreplan
```

## API do Scoreplan

### Versões

| Versão | Base URL | Autenticação | Status |
|--------|----------|--------------|--------|
| **v2 (Connector)** | `https://api-prod.scoreplan.com.br/` | Bearer Token (2h) | Recomendada |
| **v1 (Clássica)** | `https://api-prod.scoreplan.com.br/api/1.0/{chave}/{metodo}` | Chave na URL | Legacy |

### Autenticação (API v2)

```bash
# 1. Obter token
curl -X POST "https://api-prod.scoreplan.com.br/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "USUARIO", "password": "SENHA"}'

# 2. Usar token nas chamadas (válido por 2h)
curl -X GET "https://api-prod.scoreplan.com.br/indicators" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json"
```

### Endpoints Disponíveis

#### Indicadores
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/indicators` | Listar indicadores |
| GET | `/indicators/{id}` | Obter indicador |
| POST | `/indicators` | Criar indicador |
| PUT | `/indicators/{id}` | Atualizar indicador |
| DELETE | `/indicators/{id}` | Remover indicador |
| GET | `/indicators/{id}/values` | Valores do indicador |
| POST | `/indicators/{id}/values` | Inserir valores |

#### Ações
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/actions` | Listar ações |
| GET | `/actions/{id}` | Obter ação |
| POST | `/actions` | Criar ação |
| PUT | `/actions/{id}` | Atualizar ação |
| DELETE | `/actions/{id}` | Remover ação |

#### Projetos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/projects` | Listar projetos |
| GET | `/projects/{id}` | Obter projeto |
| POST | `/projects` | Criar projeto |
| PUT | `/projects/{id}` | Atualizar projeto |
| DELETE | `/projects/{id}` | Remover projeto |

#### OKRs
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/okrs` | Listar OKRs |
| GET | `/okrs/{id}` | Obter OKR |
| POST | `/okrs` | Criar OKR |
| PUT | `/okrs/{id}` | Atualizar OKR |
| DELETE | `/okrs/{id}` | Remover OKR |

#### Períodos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/periods` | Listar períodos |
| POST | `/periods` | Criar período |

#### Orçamento
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/budget` | Listar orçamentos |
| GET | `/budget/{id}` | Obter orçamento |

#### Campos Integrados
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/integration-fields` | Listar campos |
| POST | `/integration-fields/values` | Inserir valores |

#### API v1 (Legacy)
| Método | Endpoint | HTTP | Descrição |
|--------|----------|------|-----------|
| ValidarChave | `/ValidarChave` | GET | Validar chave |
| ListarPeriodos | `/ListarPeriodos` | GET | Listar períodos |
| InserirPeriodo | `/InserirPeriodo` | POST | Criar período |
| ListarIndicadores | `/ListarIndicadores` | GET | Listar indicadores |
| ListarCamposIntegracao | `/ListarCamposIntegracao` | GET | Campos integrados |
| InserirValorCampoIntegrado | `/InserirValorCampoIntegrado` | POST | Inserir valor |
| ListarAcoes | `/ListarAcoes` | GET | Listar ações |
| AlterarValoresAcao | `/AlterarValoresAcao` | POST | Alterar ação |

## Upload em Massa via Planilha

### Templates Disponíveis

| Template | Arquivo | Colunas |
|----------|---------|---------|
| Indicadores | `templates/indicadores.csv` | codigo, nome, descricao, unidade, polaridade, meta, periodoTipo |
| Ações | `templates/acoes.csv` | titulo, descricao, responsavel, dataInicio, dataFim, prioridade, status |
| Projetos | `templates/projetos.csv` | codigo, nome, descricao, responsavel, dataInicio, dataFim, status, orcamento |
| OKRs | `templates/okrs.csv` | objetivo, descricao, responsavel, periodo, keyResult1-5, meta1-5 |
| Valores | `templates/valores-indicadores.csv` | indicadorCodigo, periodo, valor |

### Usando o Script Python

```bash
# Upload de indicadores
python3 scripts/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --login "admin" \
  --password "senha123" \
  --type indicators \
  --file templates/indicadores.csv

# Upload de ações
python3 scripts/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --login "admin" \
  --password "senha123" \
  --type actions \
  --file planilha_acoes.xlsx

# Upload de OKRs
python3 scripts/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --login "admin" \
  --password "senha123" \
  --type okrs \
  --file okrs.xlsx

# Dry run (simulação sem enviar)
python3 scripts/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --login "admin" \
  --password "senha123" \
  --type indicators \
  --file indicadores.xlsx \
  --dry-run

# API v1 com chave
python3 scripts/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --api-version v1 \
  --api-key "MINHA_CHAVE_API" \
  --type indicator-values \
  --file valores.csv
```

### Tipos de Upload

| Tipo | Flag | Descrição |
|------|------|-----------|
| `indicators` | `--type indicators` | Criar indicadores |
| `actions` | `--type actions` | Criar ações |
| `projects` | `--type projects` | Criar projetos |
| `okrs` | `--type okrs` | Criar OKRs |
| `indicator-values` | `--type indicator-values` | Valores de indicadores |
| `integration-fields` | `--type integration-fields` | Valores de campos integrados |

### Opções do Script

| Flag | Descrição | Default |
|------|-----------|---------|
| `--url` | Base URL da API | (obrigatório) |
| `--login` | Usuário (API v2) | - |
| `--password` | Senha (API v2) | - |
| `--api-version` | `v1` ou `v2` | `v2` |
| `--api-key` | Chave da API (v1) | - |
| `--type` | Tipo de upload | (obrigatório) |
| `--file` | Arquivo .xlsx ou .csv | (obrigatório) |
| `--dry-run` | Simular sem enviar | `false` |
| `--delay` | Delay entre requests (s) | `0.2` |

## Documentação Oficial

- [Connector (v2)](https://docs.scoreplan.com.br/Manuais/Visualizar/698)
- [API Clássica (v1)](https://docs.scoreplan.com.br/Manuais/Visualizar/149)
- [Swagger UI](https://app.scoreplan.com.br/api/docs)
- [Blog: Integração via API](https://scoreplan.com.br/blog/integracao-via-api-como-funciona-e-que-vantagens-isso-traz-para-o-seu-negocio/)

## Licença

MIT
