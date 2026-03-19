# Scoreplan API Reference

Referência completa da API REST do Scoreplan para integração de dados.

## Sumário

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Indicadores](#indicadores)
- [Ações](#ações)
- [Projetos](#projetos)
- [OKRs](#okrs)
- [Períodos](#períodos)
- [Orçamento](#orçamento)
- [Campos Integrados](#campos-integrados)
- [Objetos de Resposta](#objetos-de-resposta)
- [Erros](#erros)
- [API v1 (Legacy)](#api-v1-legacy)

---

## Visão Geral

A API do Scoreplan funciona no modelo REST. A integração deve ser feita através de requisições HTTP.

| Propriedade | Valor |
|-------------|-------|
| Base URL (v2) | `https://api-prod.scoreplan.com.br/` |
| Base URL (v1) | `https://api-prod.scoreplan.com.br/api/1.0/{chave}/{metodo}` |
| Formato | JSON (preferido) ou XML |
| Autenticação (v2) | Bearer Token |
| Autenticação (v1) | API Key na URL |
| Token TTL | 2 horas |

---

## Autenticação

### API v2 — Bearer Token

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "login": "usuario@empresa.com",
  "password": "senha_segura"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiration": "2026-03-19T23:00:00Z"
}
```

**Uso do token em chamadas:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Observações:**
- O token expira em **2 horas**
- O usuário deve ter permissão ao módulo acessado
- Recomendado usar perfil de **administrador**
- Todos os dados são limitados ao **grupo de negócios** vinculado

### API v1 — API Key

A chave deve ser configurada em: **Scoreplan > Configurações > Integrações**

```
GET https://api-prod.scoreplan.com.br/api/1.0/{CHAVE_API}/{METODO}
Content-Type: application/json
```

**Validação:**
```
GET /api/1.0/{chave}/ValidarChave
```

---

## Indicadores

### Listar Indicadores

```
GET /indicators
```

**Query Parameters:**

| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `page` | int | Não | Página (paginação) |
| `limit` | int | Não | Itens por página |
| `search` | string | Não | Busca por nome/código |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "content": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "codigo": "IND001",
      "nome": "Receita Mensal",
      "descricao": "Receita total mensal da empresa",
      "unidade": "R$",
      "polaridade": "Maior melhor",
      "responsavel": "João Silva",
      "periodoTipo": "SC_MES",
      "meta": 100000.00
    }
  ]
}
```

### Obter Indicador

```
GET /indicators/{id}
```

### Criar Indicador

```
POST /indicators
```

**Request Body:**
```json
{
  "codigo": "IND006",
  "nome": "Taxa de Conversão",
  "descricao": "Percentual de leads convertidos em clientes",
  "unidade": "%",
  "polaridade": "Maior melhor",
  "meta": 25.0,
  "periodoTipo": "SC_MES"
}
```

### Atualizar Indicador

```
PUT /indicators/{id}
```

**Request Body:** Campos a serem atualizados (parcial aceito)

### Remover Indicador

```
DELETE /indicators/{id}
```

### Listar Valores do Indicador

```
GET /indicators/{id}/values
```

**Response:**
```json
{
  "status": "SUCCESS",
  "content": [
    {
      "periodoId": "guid",
      "periodo": "2026-01",
      "valor": 95000.00,
      "meta": 100000.00
    }
  ]
}
```

### Inserir Valores do Indicador

```
POST /indicators/{id}/values
```

**Request Body:**
```json
{
  "valores": [
    {"periodo": "2026-01", "valor": 95000.00},
    {"periodo": "2026-02", "valor": 102000.00},
    {"periodo": "2026-03", "valor": 110000.00}
  ]
}
```

**Nota:** A inserção é **transacional** — se falhar em um período, todas as alterações são revertidas.

---

## Ações

### Listar Ações

```
GET /actions
```

**Query Parameters:**

| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `status` | string | Não | Filtrar por status |
| `responsavel` | string | Não | Filtrar por responsável |
| `origem` | string | Não | Filtrar por origem (Mapa Estratégico, FCA, Projetos, Reuniões, Ocorrências) |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "content": [
    {
      "id": "guid",
      "codigo": "ACT001",
      "titulo": "Revisar processo de vendas",
      "descricao": "Mapear e otimizar pipeline comercial",
      "responsavel": "João Silva",
      "status": "Em andamento",
      "dataInicio": "2026-01-01",
      "dataFim": "2026-03-31",
      "percentualConclusao": 45,
      "origem": "Mapa Estratégico",
      "prioridade": "Alta"
    }
  ]
}
```

### Criar Ação

```
POST /actions
```

**Request Body:**
```json
{
  "titulo": "Implementar CRM",
  "descricao": "Configurar e treinar equipe no novo CRM",
  "responsavel": "Maria Santos",
  "dataInicio": "2026-02-01",
  "dataFim": "2026-06-30",
  "prioridade": "Alta",
  "status": "Pendente"
}
```

### Atualizar Ação

```
PUT /actions/{id}
```

### Remover Ação

```
DELETE /actions/{id}
```

---

## Projetos

### Listar Projetos

```
GET /projects
```

### Criar Projeto

```
POST /projects
```

**Request Body:**
```json
{
  "codigo": "PRJ001",
  "nome": "Expansão Regional Sul",
  "descricao": "Expandir operações para região Sul do Brasil",
  "responsavel": "Maria Santos",
  "dataInicio": "2026-01-01",
  "dataFim": "2026-12-31",
  "status": "Planejado",
  "orcamento": 500000.00
}
```

### Atualizar Projeto

```
PUT /projects/{id}
```

### Remover Projeto

```
DELETE /projects/{id}
```

---

## OKRs

### Listar OKRs

```
GET /okrs
```

### Criar OKR

```
POST /okrs
```

**Request Body:**
```json
{
  "objetivo": "Aumentar receita em 30%",
  "descricao": "Crescimento sustentável no Q1 2026",
  "responsavel": "Diretoria Comercial",
  "periodo": "2026-Q1",
  "keyResults": [
    {"nome": "Receita total", "meta": 1300000},
    {"nome": "Novos clientes", "meta": 50},
    {"nome": "Ticket médio", "meta": 2500}
  ]
}
```

### Atualizar OKR

```
PUT /okrs/{id}
```

### Remover OKR

```
DELETE /okrs/{id}
```

---

## Períodos

### Listar Períodos

```
GET /periods
```

### Criar Período

```
POST /periods
```

**Request Body:**
```json
{
  "tipoPeriodo": "PERSONALIZADO",
  "periodos": [
    {
      "codigo": "2026-S1",
      "descricao": "Primeiro Semestre 2026",
      "dataInicio": "2026-01-01",
      "dataFim": "2026-06-30"
    }
  ]
}
```

**Nota:** Não é possível criar períodos dos tipos padrão `SC_MES` (meses) e `SC_ANO` (anos) — estes são gerados automaticamente.

---

## Orçamento

### Listar Orçamentos

```
GET /budget
```

### Obter Orçamento

```
GET /budget/{id}
```

---

## Campos Integrados

### Listar Campos para Integração

```
GET /integration-fields
```

**Response:**
```json
{
  "status": "SUCCESS",
  "content": [
    {
      "id": "guid",
      "nome": "ERP Principal",
      "campos": [
        {
          "id": "campo-guid",
          "nome": "Receita Bruta",
          "tipo": "decimal",
          "indicadorId": "indicador-guid"
        }
      ]
    }
  ]
}
```

### Inserir Valores de Campos Integrados

```
POST /integration-fields/values
```

**Request Body:**
```json
{
  "campoId": "campo-guid",
  "valores": [
    {"periodoId": "periodo-guid", "valor": 150000.00},
    {"periodoId": "periodo-guid-2", "valor": 162000.00}
  ]
}
```

**Nota:** Operação **transacional** — se falhar em qualquer período, todas as alterações são revertidas.

---

## Objetos de Resposta

### ApiResposta (Sucesso)

```json
{
  "status": "SUCCESS",
  "content": { }
}
```

### Eftpa008 (Erro)

```json
{
  "status": "ERROR",
  "content": {
    "mensagem": "Descrição do erro ocorrido"
  }
}
```

---

## Erros

| Código HTTP | Descrição | Ação |
|-------------|-----------|------|
| 200 | Sucesso | - |
| 400 | Requisição inválida | Verificar body/params |
| 401 | Token expirado/inválido | Reautenticar |
| 403 | Sem permissão ao módulo | Verificar permissões do usuário |
| 404 | Recurso não encontrado | Verificar ID |
| 500 | Erro interno | Tentar novamente / Contatar suporte |

---

## API v1 (Legacy)

### Endpoints

| Endpoint | HTTP | Descrição |
|----------|------|-----------|
| `/api/1.0/{chave}/ValidarChave` | GET | Validar chave da API |
| `/api/1.0/{chave}/ListarPeriodos` | GET | Listar períodos |
| `/api/1.0/{chave}/InserirPeriodo` | POST | Inserir período |
| `/api/1.0/{chave}/ListarIndicadores` | GET | Listar indicadores |
| `/api/1.0/{chave}/ListarCamposIntegracao` | GET | Listar campos para integração |
| `/api/1.0/{chave}/InserirValorCampoIntegrado` | POST | Inserir valor de campo integrado |
| `/api/1.0/{chave}/ListarAcoes` | GET | Listar ações |
| `/api/1.0/{chave}/AlterarValoresAcao` | POST | Alterar valores da ação |

### Exemplo Completo (v1)

```bash
# 1. Validar chave
curl -s "https://api-prod.scoreplan.com.br/api/1.0/MINHA_CHAVE/ValidarChave" \
  -H "Content-Type: application/json"

# 2. Listar indicadores
curl -s "https://api-prod.scoreplan.com.br/api/1.0/MINHA_CHAVE/ListarIndicadores" \
  -H "Content-Type: application/json"

# 3. Inserir valor de campo integrado
curl -X POST "https://api-prod.scoreplan.com.br/api/1.0/MINHA_CHAVE/InserirValorCampoIntegrado" \
  -H "Content-Type: application/json" \
  -d '{
    "campoId": "guid-do-campo",
    "valores": [
      {"periodoId": "guid-do-periodo", "valor": 95000.00}
    ]
  }'
```

---

## Referências

- [Documentação Connector (v2)](https://docs.scoreplan.com.br/Manuais/Visualizar/698)
- [Documentação API Clássica (v1)](https://docs.scoreplan.com.br/Manuais/Visualizar/149)
- [Swagger UI](https://app.scoreplan.com.br/api/docs)
