# Scoreplan API — Skill & Toolkit

Integração com a **API do Scoreplan** (ações, projetos, programas, fases, OKR, GED, orçamento/financeiro, RH/GDP e indicadores), empacotada como uma **[Claude Skill](https://docs.claude.com/en/docs/claude-code/skills)** + um script de **upload em massa** via planilha (`.xlsx`/`.csv`).

> Contrato de API verificado por engenharia reversa da documentação oficial (`app.scoreplan.com.br/api/docs`) e confirmado com chamadas reais à API de produção. Documentação anterior continha endpoints/credenciais incorretos — aqui está o contrato real.

## Por que este repositório existe

A documentação pública do Scoreplan é incompleta e parte do contrato (nomes de campos de autenticação, paths de endpoints, schemas de body) só está disponível em imagens ou dentro do app autenticado. Este projeto consolida **o contrato real, testado**, em formato reutilizável.

## Conteúdo

| Arquivo | Descrição |
|---|---|
| [`SKILL.md`](SKILL.md) | A skill em si (instruções + contrato completo da API) |
| [`references/bulk_upload.py`](references/bulk_upload.py) | Script de upload em massa (ações, programas, projetos, fases, valores) |
| [`references/scoreplan_api_catalog.txt`](references/scoreplan_api_catalog.txt) | Catálogo dos 109 endpoints (url, método, body, params, enums) |
| [`examples/`](examples/) | Planilhas de exemplo (.csv) |
| [`.claude/skills/scoreplan/`](.claude/skills/scoreplan/) | A skill já no layout pronto para instalar |

## As 3 superfícies de API

| Superfície | Base | Auth | Uso |
|---|---|---|---|
| **v2 External** ⭐ | `https://api-prod.scoreplan.com.br/{Modulo}/External/{Op}` | Bearer Token | **Criar/atualizar** ações, projetos, programas, fases, valores; importar RH/GDP; ler OKR/GED |
| v2 "interna" | `https://api-prod.scoreplan.com.br/{Modulo}/{Op}` | Bearer Token | Exige **módulo de API liberado**; senão `401 "You don't have access"` |
| v1 clássica | `https://api-prod.scoreplan.com.br/api/1.0/{chave}/{Modulo}/{Op}` | Chave na URL | Listar ações/indicadores; lançar valores; períodos |

> ⭐ **A API External funciona com o Bearer token normal, mesmo quando a v2 interna retorna `401`.** É o caminho recomendado.

## Autenticação

```bash
curl -X POST "https://api-prod.scoreplan.com.br/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"Username": "usuario@empresa.com", "Password": "SUA_SENHA"}'
```
Campos são **`Username`/`Password`** (PascalCase). A resposta traz `token` (JWT, validade 2h), `refreshToken`, `businessGroupLogged`, `companyLogged`, `businessGroups[]`. Use `Authorization: Bearer <token>`. O `userId` do usuário fica no claim `name` do JWT.

## Criar uma ação (exemplo mínimo)

```bash
curl -X POST "https://api-prod.scoreplan.com.br/Actions/External/Insert" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "title": "Ação criada via API",
    "startDateEstimated": "01/07/2026",
    "endDateEstimated": "31/07/2026",
    "situation": 0,
    "raci": {
      "responsibles": [{"userId": 18914, "trackProgress": false}],
      "authorities":  [{"userId": 18914, "trackProgress": false}],
      "groupResponsible": [], "groupAuthority": [],
      "consulted": [], "groupConsulted": [],
      "informed": [], "groupInformed": []
    },
    "tags": [], "sector": ""
  }'
```

**Regras importantes:**
- Datas em `dd/mm/yyyy`.
- `userId` deve existir (mapeie e-mails via `GET /User/External/List`).
- `userGroupId` na RACI **precisa existir** no grupo, senão `400`. Deixe os arrays `group*` vazios para evitar.
- `sector` e `tags` são opcionais.
- `situation`: `0` Não iniciado · `1` Em andamento · `2` Finalizado · `3` Cancelado · `4` Rascunho · `5` Finalizado com atraso · `6` Arquivado.

## Recursos da API External

- **Ações** — `Actions/External/{List, Select, Insert, InsertChangeProgress, Reopen, Update, UpdateValues, Cancel}`
- **Programas/Projetos/Fases** — `Program|Project|ProjectPhase /External/{List, Select, Insert, Update, Delete}` (+ `ProjectPhase/External/InsertAction`)
- **OKR** — `OKR/External/List` (somente leitura)
- **GED** — `GedDocument/External/{List, Select}`
- **Financeiro/Orçamento** — `FinancialManagement/External{InsertValues, ListBudgetPlans, ...}`, `FinancialManagementAccounting[Ledger]/External*`, `FinancialItems/External*`, vários `*/Lov`
- **RH/GDP** — `Hrm*/External/{ImportPositions, ImportEmployees, ImportSkills, ...}`
- **Utilitários** — `User/External/List` (e-mail → userId), `User/External/ListGroup`, `Attachments/External/GetFile`, `Queue/GetStatus`

> ⚠️ **Indicadores não têm criação via API External.** Para valores: `FinancialManagement/ExternalInsertValues` (orçamento) ou v1 `CamposIndicadores/InserirValor`. Criar o indicador em si só pela interface ou pela v2 interna (`/Indicators/Insert`, requer módulo liberado).

Catálogo completo: [`references/scoreplan_api_catalog.txt`](references/scoreplan_api_catalog.txt).

## Upload em massa via planilha

```bash
# Ações (v2 External)
python3 references/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --login "usuario@empresa.com" --password "SENHA" \
  --type actions --file examples/acoes_exemplo.csv

# Simular sem enviar
python3 references/bulk_upload.py --url ... --login ... --password ... \
  --type projects --file examples/projetos_exemplo.csv --dry-run
```

**Tipos suportados:** `actions`, `programs`, `projects`, `phases`, `indicators`, `okrs`, `indicator-values`, `integration-fields`.
Colunas aceitas (ações): `title`, `dataInicio`/`startDateEstimated`, `dataFim`/`endDateEstimated`, `situation`, `responsibleUserId`, `sector`, `tags`. O script converte datas `yyyy-mm-dd → dd/mm/yyyy` automaticamente. Requer Python 3 e `requests` (`pip install requests`); `openpyxl` para `.xlsx`.

## API v1 (clássica)

Útil para **listar** e **lançar valores** (não cria ações). Envelope: `{"ApiResposta":{"Status","Conteudo"}}`. Valide a chave com `Console/Ping`.

| Método | Verbo | Descrição |
|---|---|---|
| `Console/Ping` | GET | valida a chave |
| `Acoes/Listar` | GET | lista ações |
| `Acoes/AlterarValores` | POST | valores financeiros de ação existente (`acaoId`) |
| `Indicadores/Listar` | GET | lista indicadores (param `usuario`) |
| `CamposIndicadores/InserirValor` | POST | valor de campo integrado de indicador |
| `CamposIndicadores/ListarProximosV2` | GET | campos pendentes de integração |
| `TiposPeriodo/{ListarPeriodos, InserirPeriodos}` | GET | períodos |

## Instalar como Claude Skill

Copie a pasta da skill para o seu diretório de skills do Claude Code:

```bash
cp -r .claude/skills/scoreplan ~/.claude/skills/
```

Depois, no Claude Code, mencione "Scoreplan" / "API Scoreplan" e a skill será acionada.

## Aviso

Projeto não oficial, sem vínculo com o Scoreplan. Use credenciais próprias e respeite os termos de uso da plataforma. Nenhuma credencial é incluída neste repositório. Licença MIT.
