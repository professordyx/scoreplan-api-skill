# Scoreplan API — Catálogo Completo de Endpoints

## Referências Oficiais
- Documentação Connector (v2): https://docs.scoreplan.com.br/Manuais/Visualizar/698
- Documentação API Clássica (v1): https://docs.scoreplan.com.br/Manuais/Visualizar/149
- Swagger UI (completo): https://app.scoreplan.com.br/api/docs

---

## API v2 — Connector (Bearer Token)

**Base URL:** `https://api-prod.scoreplan.com.br/`
**Auth:** `Authorization: Bearer {token}`
**Token TTL:** 2 horas

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/login` | Autenticar e obter Bearer Token |

**Request Body:**
```json
{"login": "usuario", "password": "senha"}
```

**Response:**
```json
{"token": "eyJhbGci...", "expiration": "2026-03-19T23:00:00Z"}
```

### Indicadores

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/indicators` | Listar todos os indicadores |
| GET | `/indicators/{id}` | Obter indicador por ID |
| POST | `/indicators` | Criar novo indicador |
| PUT | `/indicators/{id}` | Atualizar indicador |
| DELETE | `/indicators/{id}` | Remover indicador |
| GET | `/indicators/{id}/values` | Listar valores do indicador |
| POST | `/indicators/{id}/values` | Inserir valores do indicador |

### Ações / Planos de Ação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/actions` | Listar ações |
| GET | `/actions/{id}` | Obter ação por ID |
| POST | `/actions` | Criar nova ação |
| PUT | `/actions/{id}` | Atualizar ação |
| DELETE | `/actions/{id}` | Remover ação |

### Projetos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/projects` | Listar projetos |
| GET | `/projects/{id}` | Obter projeto por ID |
| POST | `/projects` | Criar novo projeto |
| PUT | `/projects/{id}` | Atualizar projeto |
| DELETE | `/projects/{id}` | Remover projeto |

### OKRs

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/okrs` | Listar OKRs |
| GET | `/okrs/{id}` | Obter OKR por ID |
| POST | `/okrs` | Criar novo OKR |
| PUT | `/okrs/{id}` | Atualizar OKR |
| DELETE | `/okrs/{id}` | Remover OKR |

### Períodos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/periods` | Listar períodos |
| POST | `/periods` | Criar período |

### Orçamento

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/budget` | Listar orçamentos |
| GET | `/budget/{id}` | Obter orçamento por ID |

### Campos Integrados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/integration-fields` | Listar campos para integração |
| POST | `/integration-fields/values` | Inserir valores de campos integrados |

### GED (Gestão Eletrônica de Documentos)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/documents` | Listar documentos |
| GET | `/documents/{id}` | Obter documento |
| POST | `/documents` | Criar documento |

### GDP (Gestão de Processos)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/processes` | Listar processos |
| GET | `/processes/{id}` | Obter processo |

---

## API v1 — Clássica (Chave da API)

**Base URL:** `https://api-prod.scoreplan.com.br/api/1.0/{chave_da_API}/`
**Auth:** Chave da API na URL (configurar em Scoreplan > Configurações > Integrações)

| Método | Endpoint | HTTP | Descrição |
|--------|----------|------|-----------|
| ValidarChave | `/ValidarChave` | GET | Validar chave da API |
| ListarPeriodos | `/ListarPeriodos` | GET | Listar períodos por tipo |
| InserirPeriodo | `/InserirPeriodo` | POST | Inserir período personalizado |
| ListarIndicadores | `/ListarIndicadores` | GET | Listar indicadores |
| ListarCamposIntegracao | `/ListarCamposIntegracao` | GET | Listar campos para integração |
| InserirValorCampoIntegrado | `/InserirValorCampoIntegrado` | POST | Inserir valor de campo integrado |
| ListarAcoes | `/ListarAcoes` | GET | Listar ações com filtros |
| AlterarValoresAcao | `/AlterarValoresAcao` | POST | Alterar valores de ação |

---

## Objetos de Resposta

### ApiResposta
```json
{
  "status": "SUCCESS",
  "content": {}
}
```

### Eftpa008 (Erro)
```json
{
  "mensagem": "Descrição do erro ocorrido"
}
```

### Indicador
```json
{
  "id": "guid",
  "codigo": "IND001",
  "nome": "Receita Mensal",
  "descricao": "Receita total mensal da empresa",
  "unidade": "R$",
  "polaridade": "Maior melhor",
  "responsavel": "João Silva",
  "periodoTipo": "SC_MES",
  "meta": 100000.00,
  "valores": [
    {"periodoId": "guid", "periodo": "2026-01", "valor": 95000.00}
  ]
}
```

### Periodo
```json
{
  "id": "guid",
  "codigo": "2026-01",
  "descricao": "Janeiro 2026",
  "dataInicio": "2026-01-01",
  "dataFim": "2026-01-31",
  "tipoPeriodo": "SC_MES"
}
```

### Acao
```json
{
  "id": "guid",
  "codigo": "ACT001",
  "titulo": "Revisar processo de vendas",
  "descricao": "Revisão completa do pipeline",
  "responsavel": "Maria Santos",
  "status": "Em andamento",
  "dataInicio": "2026-01-01",
  "dataFim": "2026-03-31",
  "percentualConclusao": 45,
  "origem": "Mapa Estratégico",
  "prioridade": "Alta"
}
```

### OrigemIntegracao
```json
{
  "id": "guid",
  "nome": "ERP Principal",
  "campos": [
    {
      "id": "guid",
      "nome": "Receita Bruta",
      "tipo": "decimal",
      "indicadorId": "guid"
    }
  ]
}
```

---

## Notas Importantes

1. **Token expira em 2h** — Implementar refresh automático
2. **Transacional** — Inserção de valores é atômica: se falhar em um período, tudo reverte
3. **Grupo de negócios** — Dados são isolados por grupo de negócios do token
4. **Tipos de período padrão** — SC_MES e SC_ANO não podem ser criados via API (são padrão)
5. **Permissões** — Usuário da API deve ter acesso ao módulo específico
6. **Endpoints v2** — Os paths exatos devem ser verificados no Swagger UI (https://app.scoreplan.com.br/api/docs)
