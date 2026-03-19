---
name: scoreplan
description: |
  Gerenciar e integrar dados com a API do Scoreplan — indicadores, ações, projetos,
  OKRs, períodos, orçamento e campos integrados. Suporta upload em massa via planilha
  (.xlsx/.csv). Use quando o usuário mencionar 'Scoreplan', 'indicadores Scoreplan',
  'ações Scoreplan', 'projetos Scoreplan', 'OKR Scoreplan', 'integrar Scoreplan',
  'upload Scoreplan', 'importar indicadores', 'importar ações', 'importar projetos',
  'importar OKRs', 'API Scoreplan', 'scoreplan API', 'listar indicadores',
  'listar ações', 'campos integrados', 'períodos Scoreplan', 'orçamento Scoreplan',
  'scoreplan connector', ou qualquer variação de integração/consulta/importação
  de dados no Scoreplan.
---

# Scoreplan — Integração via API REST

Skill para gerenciar indicadores, ações, projetos, OKRs e períodos no Scoreplan via API REST. Suporta operações individuais e upload em massa via planilha (.xlsx/.csv).

**Documentação oficial:**
- Connector (v2): https://docs.scoreplan.com.br/Manuais/Visualizar/698
- API clássica (v1): https://docs.scoreplan.com.br/Manuais/Visualizar/149
- Swagger UI: https://app.scoreplan.com.br/api/docs

## Versões da API

O Scoreplan possui duas versões de API:

### API v2 — Connector (Recomendada)

- **Base URL:** `https://api-prod.scoreplan.com.br/`
- **Autenticação:** Bearer Token (válido por 2h)
- **Módulos:** Ações, Projetos, Orçamento, GED, GDP, Indicadores, OKRs
- **Formato:** JSON (preferido) ou XML

### API v1 — Clássica (Legacy)

- **Base URL:** `https://api-prod.scoreplan.com.br/api/1.0/{chave_da_API}/{metodo}`
- **Autenticação:** Chave da API na URL (configurada na página Integrações)
- **Módulos:** Indicadores, Períodos, Ações, Campos Integrados
- **Formato:** JSON (preferido) ou XML

## Autenticação

### API v2 — Bearer Token

```bash
# 1. Obter token (válido por 2h)
curl -X POST "https://api-prod.scoreplan.com.br/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "USUARIO", "password": "SENHA"}'

# Resposta: {"token": "eyJhbGci...", "expiration": "..."}

# 2. Usar token em todas as chamadas
curl -X GET "https://api-prod.scoreplan.com.br/ENDPOINT" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json"
```

**Importante:**
- O token expira em **2 horas** — reautenticar quando expirar
- O usuário deve ter permissão de **administrador** ou permissão ao módulo
- Todos os dados são limitados ao **grupo de negócios** vinculado à autenticação

### API v1 — Chave da API

```bash
curl -X GET "https://api-prod.scoreplan.com.br/api/1.0/{CHAVE_API}/{METODO}" \
  -H "Content-Type: application/json"
```

A chave deve ser configurada em: **Scoreplan > Configurações > Integrações**

## Endpoints — API v1 (Clássica)

### Validar Chave da API
| Campo | Valor |
|-------|-------|
| **URL** | `/api/1.0/{chave}/ValidarChave` |
| **Método** | GET |
| **Descrição** | Valida se a chave da API é válida |
| **Argumentos** | Nenhum |
| **Retorno** | `ApiResposta` com status de validação |

### Listar Períodos
| Campo | Valor |
|-------|-------|
| **URL** | `/api/1.0/{chave}/ListarPeriodos` |
| **Método** | GET |
| **Descrição** | Lista períodos de um tipo de período específico |
| **Argumentos** | `tipoPeriodo` (string, obrigatório) — código do tipo de período |
| **Retorno** | Lista de objetos `Periodo` |

### Inserir Período
| Campo | Valor |
|-------|-------|
| **URL** | `/api/1.0/{chave}/InserirPeriodo` |
| **Método** | POST |
| **Descrição** | Insere períodos para tipos de período personalizados (não funciona para SC_MES e SC_ANO) |
| **Body** | `{"tipoPeriodo": "CODIGO", "periodos": [{"codigo": "...", "descricao": "...", "dataInicio": "...", "dataFim": "..."}]}` |
| **Retorno** | `ApiResposta` com mensagem de sucesso |

### Listar Indicadores
| Campo | Valor |
|-------|-------|
| **URL** | `/api/1.0/{chave}/ListarIndicadores` |
| **Método** | GET |
| **Descrição** | Retorna lista de indicadores do grupo de negócios |
| **Argumentos** | Filtros opcionais via query parameters |
| **Retorno** | Lista de objetos `Indicador` |

### Listar Campos para Integração
| Campo | Valor |
|-------|-------|
| **URL** | `/api/1.0/{chave}/ListarCamposIntegracao` |
| **Método** | GET |
| **Descrição** | Lista campos marcados para integração que ainda não iniciaram o processo, agrupados por origem de integração |
| **Argumentos** | Nenhum |
| **Retorno** | Lista de objetos `OrigemIntegracao` |

### Inserir Valor de Campo Integrado
| Campo | Valor |
|-------|-------|
| **URL** | `/api/1.0/{chave}/InserirValorCampoIntegrado` |
| **Método** | POST |
| **Descrição** | Insere valores de um campo integrado para os períodos informados. Se falhar em algum período, todas as alterações são revertidas (transacional) |
| **Body** | `{"campoId": "...", "valores": [{"periodoId": "...", "valor": 123.45}]}` |
| **Retorno** | `ApiResposta` com mensagem de sucesso |

### Listar Ações
| Campo | Valor |
|-------|-------|
| **URL** | `/api/1.0/{chave}/ListarAcoes` |
| **Método** | GET |
| **Descrição** | Lista ações registradas com base nos filtros fornecidos |
| **Argumentos** | Filtros opcionais (origem, status, responsável, etc.) |
| **Retorno** | Lista de objetos `Acao` |

### Alterar Valores da Ação
| Campo | Valor |
|-------|-------|
| **URL** | `/api/1.0/{chave}/AlterarValoresAcao` |
| **Método** | POST |
| **Descrição** | Altera os valores de uma ação existente |
| **Body** | Objeto com campos da ação a serem alterados |
| **Retorno** | `ApiResposta` com mensagem de sucesso |

## Endpoints — API v2 (Connector)

A API v2 usa Bearer Token e oferece acesso ampliado aos módulos. Os endpoints seguem o padrão RESTful.

**Base URL:** `https://api-prod.scoreplan.com.br/`

### Autenticação
| Campo | Valor |
|-------|-------|
| **URL** | `POST /auth/login` |
| **Body** | `{"login": "...", "password": "..."}` |
| **Retorno** | `{"token": "Bearer ...", "expiration": "..."}` |

### Indicadores
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/indicators` | Listar indicadores |
| GET | `/indicators/{id}` | Obter indicador por ID |
| POST | `/indicators` | Criar indicador |
| PUT | `/indicators/{id}` | Atualizar indicador |
| DELETE | `/indicators/{id}` | Remover indicador |
| GET | `/indicators/{id}/values` | Listar valores do indicador |
| POST | `/indicators/{id}/values` | Inserir valores do indicador |

### Ações / Planos de Ação
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/actions` | Listar ações |
| GET | `/actions/{id}` | Obter ação por ID |
| POST | `/actions` | Criar ação |
| PUT | `/actions/{id}` | Atualizar ação |
| DELETE | `/actions/{id}` | Remover ação |

### Projetos
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/projects` | Listar projetos |
| GET | `/projects/{id}` | Obter projeto por ID |
| POST | `/projects` | Criar projeto |
| PUT | `/projects/{id}` | Atualizar projeto |
| DELETE | `/projects/{id}` | Remover projeto |

### OKRs
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/okrs` | Listar OKRs |
| GET | `/okrs/{id}` | Obter OKR por ID |
| POST | `/okrs` | Criar OKR |
| PUT | `/okrs/{id}` | Atualizar OKR |
| DELETE | `/okrs/{id}` | Remover OKR |

### Períodos
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/periods` | Listar períodos |
| POST | `/periods` | Criar período |

### Orçamento
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/budget` | Listar orçamentos |
| GET | `/budget/{id}` | Obter orçamento por ID |

### Campos Integrados
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/integration-fields` | Listar campos para integração |
| POST | `/integration-fields/values` | Inserir valores de campos integrados |

**Nota:** Os endpoints exatos da API v2 devem ser verificados no Swagger UI em https://app.scoreplan.com.br/api/docs — os paths acima são baseados no padrão REST documentado. Os endpoints podem variar ligeiramente.

## Estrutura de Objetos

### ApiResposta
```json
{
  "status": "SUCCESS" | "ERROR",
  "content": { /* conteúdo específico do método */ }
}
```

### Eftpa008 (Erro)
```json
{
  "mensagem": "Descrição do erro"
}
```

### Indicador
```json
{
  "id": "guid",
  "codigo": "string",
  "nome": "string",
  "descricao": "string",
  "unidade": "string",
  "polaridade": "string",
  "responsavel": "string",
  "periodoTipo": "string",
  "meta": 0.0,
  "valores": []
}
```

### Periodo
```json
{
  "id": "guid",
  "codigo": "string",
  "descricao": "string",
  "dataInicio": "yyyy-MM-dd",
  "dataFim": "yyyy-MM-dd",
  "tipoPeriodo": "string"
}
```

### Acao
```json
{
  "id": "guid",
  "codigo": "string",
  "titulo": "string",
  "descricao": "string",
  "responsavel": "string",
  "status": "string",
  "dataInicio": "yyyy-MM-dd",
  "dataFim": "yyyy-MM-dd",
  "percentualConclusao": 0,
  "origem": "string",
  "prioridade": "string"
}
```

### OrigemIntegracao
```json
{
  "id": "guid",
  "nome": "string",
  "campos": [
    {
      "id": "guid",
      "nome": "string",
      "tipo": "string",
      "indicadorId": "guid"
    }
  ]
}
```

## Workflows Principais

### 1. Upload em Massa de Indicadores via Planilha

**Formato da planilha (.xlsx ou .csv):**

| codigo | nome | descricao | unidade | polaridade | meta | periodoTipo |
|--------|------|-----------|---------|------------|------|-------------|
| IND001 | Receita Mensal | Receita total mensal | R$ | Maior melhor | 100000 | SC_MES |
| IND002 | Satisfação Cliente | NPS | % | Maior melhor | 80 | SC_MES |

**Fluxo:**
1. Ler a planilha com openpyxl/pandas
2. Autenticar na API (obter Bearer Token)
3. Para cada linha: `POST /indicators` com os dados
4. Registrar sucessos/falhas em log

### 2. Upload em Massa de Ações via Planilha

**Formato da planilha:**

| titulo | descricao | responsavel | dataInicio | dataFim | prioridade | status |
|--------|-----------|-------------|------------|---------|------------|--------|
| Revisar processo | Revisar processo de vendas | João Silva | 2026-01-01 | 2026-03-31 | Alta | Em andamento |

**Fluxo:**
1. Ler a planilha
2. Autenticar na API
3. Para cada linha: `POST /actions` com os dados
4. Registrar resultados

### 3. Upload em Massa de Projetos via Planilha

**Formato da planilha:**

| codigo | nome | descricao | responsavel | dataInicio | dataFim | status | orcamento |
|--------|------|-----------|-------------|------------|---------|--------|-----------|
| PRJ001 | Expansão Regional | Expandir para Sul | Maria Santos | 2026-01-01 | 2026-12-31 | Planejado | 500000 |

### 4. Upload em Massa de OKRs via Planilha

**Formato da planilha:**

| objetivo | descricao | responsavel | keyResult1 | meta1 | keyResult2 | meta2 | periodo |
|----------|-----------|-------------|------------|-------|------------|-------|---------|
| Aumentar receita | Crescimento Q1 | Diretoria | Receita total | 1000000 | Novos clientes | 50 | 2026-Q1 |

### 5. Upload de Valores de Indicadores via Planilha

**Formato da planilha:**

| indicadorCodigo | periodo | valor |
|-----------------|---------|-------|
| IND001 | 2026-01 | 95000 |
| IND001 | 2026-02 | 102000 |
| IND002 | 2026-01 | 78.5 |

**Fluxo:**
1. Ler a planilha
2. Autenticar na API
3. Buscar IDs dos indicadores via `GET /indicators`
4. Para cada grupo de valores: `POST /indicators/{id}/values`
5. Registrar resultados

## Script de Upload em Massa

Para upload via planilha, use o script Python em [references/bulk_upload.py](references/bulk_upload.py).

**Uso:**
```bash
python3 references/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --login "usuario" \
  --password "senha" \
  --type indicators \
  --file planilha.xlsx
```

**Tipos suportados:** `indicators`, `actions`, `projects`, `okrs`, `indicator-values`

## Tratamento de Erros

- **Status SUCCESS:** Operação realizada com sucesso
- **Status ERROR:** Retorna objeto `Eftpa008` com mensagem de erro
- **Token expirado (401):** Reautenticar e repetir a chamada
- **Inserção transacional:** Em inserções de valores, se falhar em um período, TODAS as alterações são revertidas

## Boas Práticas

1. **Cache do token:** Reutilize o token por até 2h, não reautentique a cada chamada
2. **Rate limiting:** Respeite limites de requisições — use delays em uploads em massa
3. **Validação prévia:** Valide dados da planilha antes de enviar à API
4. **Logs:** Sempre registre sucessos e falhas para auditoria
5. **Rollback:** Em caso de falha parcial, a API reverte automaticamente (transacional)
6. **Permissões:** Use usuário com perfil administrador para integração
7. **JSON preferido:** Sempre use `Content-Type: application/json`
