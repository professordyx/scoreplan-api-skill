---
name: scoreplan
description: |
  Gerenciar e integrar dados com a API do Scoreplan — ações, projetos, programas,
  fases, OKRs, orçamento/financeiro, GED, RH/GDP, indicadores e períodos. Suporta
  upload em massa via planilha (.xlsx/.csv). Use quando o usuário mencionar 'Scoreplan',
  'indicadores Scoreplan', 'ações Scoreplan', 'projetos Scoreplan', 'OKR Scoreplan',
  'integrar Scoreplan', 'upload Scoreplan', 'importar ações', 'importar projetos',
  'API Scoreplan', 'scoreplan API', 'listar ações', 'campos integrados',
  'orçamento Scoreplan', 'scoreplan connector', 'API External Scoreplan', ou qualquer
  variação de integração/consulta/importação de dados no Scoreplan.
---

# Scoreplan — Integração via API REST

Skill para integrar dados com o Scoreplan via API REST. Cobre a **API v2 External** (a superfície de integração real, recomendada) e a **API v1 clássica**.

**Documentação oficial:**
- Connector (v2): https://docs.scoreplan.com.br/Manuais/Visualizar/698
- API clássica (v1): https://docs.scoreplan.com.br/Manuais/Visualizar/149
- **Catálogo de endpoints (Swagger/SPA):** https://app.scoreplan.com.br/api/docs

> ⚠️ **Contrato verificado por engenharia reversa + teste ao vivo (2026-06-30).** A documentação anterior desta skill estava incorreta. Os endpoints e schemas abaixo foram extraídos da doc oficial (`app.scoreplan.com.br/api/docs`, chunk `assets/docs/api-bd505ba2.js`) e confirmados criando ações reais. Catálogo completo dos 109 endpoints: ver `references/scoreplan_api_catalog.txt` quando disponível.

## Conceito central: 3 superfícies de API

| Superfície | Base | Auth | Serve para |
|---|---|---|---|
| **v2 External** (use esta) | `https://api-prod.scoreplan.com.br/{Modulo}/External/{Op}` | Bearer Token | **Criar/atualizar** ações, projetos, programas, fases, valores financeiros; importar RH/GDP; listar OKR/GED |
| v2 "interna" | `https://api-prod.scoreplan.com.br/{Modulo}/{Op}` (ex.: `/Actions/Insert`) | Bearer Token | Existe, mas exige **módulo de API liberado**; sem isso retorna `401 "You don't have access"` |
| v1 clássica | `https://api-prod.scoreplan.com.br/api/1.0/{chave}/{Modulo}/{Op}` | Chave na URL | Listar ações/indicadores; lançar valores; períodos |

> 🔑 **A v2 External NÃO exige o módulo de API liberado** — funciona com o Bearer Token normal do usuário, mesmo quando `/Actions/Insert` (interna) responde `401`. É o caminho recomendado para integração.

## Autenticação (v2)

```bash
# Campos são "Username"/"Password" (PascalCase). NÃO use "login"/"password".
curl -X POST "https://api-prod.scoreplan.com.br/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"Username": "usuario@empresa.com", "Password": "SENHA"}'
# Resposta: { "token": "<JWT>", "refreshToken": "...", "businessGroupLogged": "...",
#             "companyLogged": "...", "businessGroups": [ { "name", "companies":[{key,name}] } ] }
```
- Usar `Authorization: Bearer <token>` em todas as chamadas. Token expira em **2h** (claim `exp`).
- O `userId` do usuário logado está no claim `name` do JWT (ex.: `18914`).
- Dados limitados ao **grupo de negócios** da autenticação.

## API v2 External — endpoints por recurso

Base: `https://api-prod.scoreplan.com.br`. Header: `Authorization: Bearer <token>` + `Content-Type: application/json`.
`args:"Body"` = JSON no corpo; `args:"QueryParams"` = parâmetros na URL.

### Ações (`Actions/External`)
| Método | URL | Body/Params |
|---|---|---|
| GET | `Actions/External/List` | QueryParams (filtros) |
| GET | `Actions/External/Select` | `?id=` |
| POST | `Actions/External/Insert` ✅ | Body `ActionDTO` (ver schema) |
| POST | `Actions/External/InsertChangeProgress` | `{description, actionId, date:"dd/mm/yyyy", percentageConclusion, realizedExpenseDeduction, realizedRevenueDeduction}` |
| POST | `Actions/External/Reopen` | `{actionId, date, description}` |
| POST | `Actions/External/Cancel` | `{actionId, description}` |
| PUT | `Actions/External/Update` | Body `ActionDTO` + `id` |
| PUT | `Actions/External/UpdateValues` | `{actionId, date, valuePredictedExpense, valueRealizedExpense, valuePredictedRecipe, valueRealizedRecipe, valueReleased}` |
| DELETE | `Actions/Delete` | (sob a v2 interna; pode exigir módulo liberado) |

### Programas, Projetos e Fases
| Método | URL | Body |
|---|---|---|
| POST | `Program/External/Insert` | `{title, raci{...}}` |
| GET/PUT/DELETE | `Program/External/{List,Select,Update,Delete}` | — |
| POST | `Project/External/Insert` | `{title, programId, situation, level, startDateEstimated, endDateEstimated, validateDate, estimatedExpenseDeduction, estimatedRevenueDeduction, raci{...}, extraFields:[{path,value}], tags[], sector}` |
| GET/PUT/DELETE | `Project/External/{List,Select,Update,Delete}` | — |
| POST | `ProjectPhase/External/Insert` | `{title, projectId, startDateEstimated, endDateEstimated, estimatedExpenseDeduction, estimatedRevenueDeduction, weight}` |
| POST | `ProjectPhase/External/InsertAction` | igual ao `ActionDTO`, com `phaseId` |
| GET/PUT/DELETE | `ProjectPhase/External/{List,Select,Update,Delete,ListAction,UpdateAction}` | — |

`Project.level`: `E - Estratégico | T - Tático | O - Operacional`.
`Project.situation` (na listagem): `1 - Aberto | 2 - Fechado | 3 - Em aprovação | 4 - Cancelado`.

### OKR / GED (somente leitura via External)
| Método | URL | Params |
|---|---|---|
| GET | `OKR/External/List` | `{startDate, endDate, search, responsibleEmail, authorityEmail, page, rowsPerPage}` |
| GET | `GedDocument/External/{List,Select}` | — |

### Orçamento / Financeiro (`FinancialManagement*`)
| Método | URL | Observação |
|---|---|---|
| POST | `FinancialManagement/ExternalInsertValues` | Body grande: `{BudgetPlanCode, SalesRevenue[], VariableExpenses[], VariableCosts[], ...}` (por mês/ano/filial/canal/linha) |
| POST | `FinancialManagement/ExternalImportStructureInHierarchy` | importa estrutura |
| GET | `FinancialManagement/ExternalListBudgetPlans` / `SearchValues` / `SearchAnalyticalValues` | consultas |
| POST/DELETE | `FinancialManagementAccounting[Ledger]/External{ImportValuesOfAccounting,IntegrateValues,DeleteOfAccounting}` | contábil |
| GET/PUT | `FinancialItems/External{GetValues,UpdateValues}` | itens financeiros |
| GET | `Account/Lov`, `CostCenter/Lov`, `ProductLine/Lov`, `Subsidiary/Lov`, … | listas de valores (LOV) p/ códigos |

### RH / GDP (`Hrm*`)
| Método | URL |
|---|---|
| POST | `HrmOrganizationChart/External/ImportPositions` |
| POST | `HrmUserInfos/External/ImportEmployees` |
| POST | `HrmSkills/External/{ImportSkills, ImportPositionSkills, ImportEmployeeSkills}` |
| GET | `Hrm*/External/List` (e `ListPositionSkills`, `ListEmployeeSkills`) |

### Utilitários
| Método | URL | Uso |
|---|---|---|
| GET | `User/External/List` | **mapear e-mail → `userId`** para preencher a RACI |
| GET | `User/External/ListGroup` | mapear grupos → `userGroupId` |
| GET | `Attachments/External/GetFile` | baixar anexo |
| GET | `Queue/GetStatus` | status de processamento assíncrono |

## ⚠️ Indicadores na API External

**Não existe endpoint de criação de indicadores na API v2 External.** As seções da doc são Ações, Programas/Projetos/Fases, OKR (leitura), GED (leitura), Financeiro/Orçamento e RH/GDP — **indicadores não estão entre elas**. Para dados ligados a indicadores:
- **Valores de orçamento/financeiro:** `FinancialManagement/ExternalInsertValues`.
- **Valores de campos integrados de indicadores:** API **v1** `CamposIndicadores/InserirValor` (ver abaixo).
- **Criar a estrutura de um indicador:** não é exposto por API — usar a interface do Scoreplan, ou a v2 interna `/Indicators/Insert` (requer módulo de API liberado).

## Schema — `ActionDTO` (Actions/External/Insert) ✅ confirmado

```json
{
  "title": "Action Inserted by API",
  "startDateEstimated": "27/09/2022",
  "endDateEstimated": "27/09/2022",
  "situation": 0,
  "raci": {
    "responsibles":     [{ "userId": 18914, "trackProgress": false }],
    "groupResponsible": [],
    "authorities":      [{ "userId": 18914, "trackProgress": false }],
    "groupAuthority":   [],
    "consulted":        [],
    "groupConsulted":   [],
    "informed":         [],
    "groupInformed":    []
  },
  "tags": [],
  "sector": ""
}
```
**Retorno (200):** `{ "id", "code", "title", "phaseId", "startDateEstimated", "situation", "percentageConclusion", "raci", "sector", "tags" }`.

Regras descobertas em teste:
- Datas no formato **`dd/mm/yyyy`**.
- `userId` deve existir (use o seu = claim `name` do JWT; mapeie outros via `User/External/List`).
- `userGroupId` na RACI **precisa existir** no grupo, senão `400 "grupo(s) de usuário(s) na RACI inválido(s)"`. **Deixar os arrays de grupo vazios** evita o erro.
- `sector` e `tags` são **opcionais** (a maioria das ações não tem setor).
- `situation` (enum): `0 - Não iniciado | 1 - Em andamento | 2 - Finalizado | 3 - Cancelado | 4 - Rascunho | 5 - Finalizado com atraso | 6 - Arquivado`.

## API v1 (clássica) — leitura + valores

Sob `https://api-prod.scoreplan.com.br/api/1.0/{chave}/...`. Envelope: `{"ApiResposta":{"Status":"OK"|"ERRO","Conteudo":...}}`. Validar chave com `Console/Ping` (não existe `ValidarChave`).

| Método | Verbo | Descrição | Argumentos |
|---|---|---|---|
| `Console/Ping` | GET | valida a chave | — |
| `Acoes/Listar` | GET | lista ações (objeto completo) | filtros |
| `Acoes/AlterarValores` | POST | valores financeiros de ação existente | `acaoId, data(dd/mm/yyyy), usuario, cnpj, valorPrevistoReceita, valorRealizadoReceita, valorPrevistoDespesa, valorRealizadoDespesa, valorLiberado` |
| `Indicadores/Listar` | GET | lista indicadores | `usuario` (obrigatório) |
| `CamposIndicadores/InserirValor` | POST | insere valor de campo integrado de indicador | `campoId/cnpj, valores:[{periodoId, valor}]` |
| `CamposIndicadores/ListarProximosV2` | GET | campos pendentes de integração | — |
| `TiposPeriodo/ListarPeriodos` | GET | períodos de um tipo | `tipoPeriodo` |
| `TiposPeriodo/InserirPeriodos` | GET | cria períodos personalizados (≠ SC_MES/SC_ANO) | — |

> ❗ A v1 **não cria ações** (só `Listar` + `AlterarValores`). Para criar ações use `Actions/External/Insert`.

## Workflow — criar ações em massa (recomendado)

1. `POST /auth/login` `{"Username","Password"}` → token.
2. (opcional) `GET /User/External/List` → mapear e-mails dos responsáveis em `userId`.
3. Para cada linha da planilha: `POST /Actions/External/Insert` com o `ActionDTO` (datas `dd/mm/yyyy`, grupos da RACI vazios).
4. Conferir contagem/duplicatas via `GET /Actions/External/List` (ou v1 `Acoes/Listar`).

Use o script [references/bulk_upload.py](references/bulk_upload.py) (`--type actions` já usa `Actions/External/Insert`).

## Tratamento de Erros

- **`401 "You don't have access"`:** você chamou a v2 **interna** (`/Actions/Insert`) sem o módulo de API. Use a **External** (`/Actions/External/Insert`) ou peça liberação do módulo.
- **`400 "grupo(s) ... na RACI inválido(s)"`:** `userGroupId` inexistente — esvazie os arrays `group*` da RACI.
- **`400 "Need to inform title"` / "Value cannot be null (Parameter 's')":** falta campo obrigatório no body.
- **v1 `{"Status":"ERRO"}`:** ver `Conteudo.eftpa008.message` (ex.: "Invalid api key", "Invalid user").
- **429 Too Many Requests:** rate limit — adicione delays entre as chamadas.

## Boas Práticas

1. **Use a API External** para criar/atualizar (não a v2 interna, que é access-walled).
2. **Cache do token** (2h); não reautentique a cada chamada.
3. **Delays** em uploads em massa (evitar 429).
4. **Mapeie userId/userGroupId** antes de montar a RACI; grupos inexistentes quebram o insert.
5. **Datas** sempre `dd/mm/yyyy`.
6. **Confira o catálogo** completo em `app.scoreplan.com.br/api/docs` para recursos não detalhados aqui.
