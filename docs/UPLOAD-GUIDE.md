# Guia de Upload em Massa — Scoreplan

Este guia explica como usar planilhas (.xlsx ou .csv) para importar dados em massa para o Scoreplan.

## Pré-requisitos

1. **Python 3.8+** instalado
2. **Dependências:** `pip install requests openpyxl`
3. **Credenciais:** Login e senha do Scoreplan com perfil administrador
4. **Planilha:** Arquivo .xlsx ou .csv no formato correto (ver templates)

## Passo a Passo

### 1. Preparar a planilha

Use um dos templates disponíveis em `templates/` como base:

| Template | Arquivo |
|----------|---------|
| Indicadores | `templates/indicadores.csv` |
| Ações | `templates/acoes.csv` |
| Projetos | `templates/projetos.csv` |
| OKRs | `templates/okrs.csv` |
| Valores de Indicadores | `templates/valores-indicadores.csv` |

### 2. Validar com dry-run

Antes de enviar os dados, faça uma simulação:

```bash
python3 scripts/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --login "admin" \
  --password "senha" \
  --type indicators \
  --file minha_planilha.xlsx \
  --dry-run
```

A saída mostra o que seria enviado sem fazer nenhuma alteração.

### 3. Executar o upload

```bash
python3 scripts/bulk_upload.py \
  --url "https://api-prod.scoreplan.com.br" \
  --login "admin" \
  --password "senha" \
  --type indicators \
  --file minha_planilha.xlsx
```

### 4. Verificar resultados

O script exibe um resumo ao final:

```
==================================================
RESUMO
  Tipo: indicators
  Arquivo: minha_planilha.xlsx
  Total: 50
  Sucesso: 48
  Erros: 2
==================================================
```

## Formato das Planilhas

### Indicadores

| Coluna | Tipo | Obrigatória | Descrição |
|--------|------|-------------|-----------|
| `codigo` | string | Sim | Código único (ex: IND001) |
| `nome` | string | Sim | Nome do indicador |
| `descricao` | string | Não | Descrição detalhada |
| `unidade` | string | Não | Unidade de medida (R$, %, dias) |
| `polaridade` | string | Não | "Maior melhor" ou "Menor melhor" |
| `meta` | number | Não | Meta do indicador |
| `periodoTipo` | string | Não | Tipo de período (SC_MES, SC_ANO) |

### Ações

| Coluna | Tipo | Obrigatória | Descrição |
|--------|------|-------------|-----------|
| `titulo` | string | Sim | Título da ação |
| `descricao` | string | Não | Descrição detalhada |
| `responsavel` | string | Não | Nome do responsável |
| `dataInicio` | date | Não | Data início (YYYY-MM-DD) |
| `dataFim` | date | Não | Data fim (YYYY-MM-DD) |
| `prioridade` | string | Não | Alta, Media, Baixa |
| `status` | string | Não | Pendente, Em andamento, Concluída |

### Projetos

| Coluna | Tipo | Obrigatória | Descrição |
|--------|------|-------------|-----------|
| `codigo` | string | Sim | Código único (ex: PRJ001) |
| `nome` | string | Sim | Nome do projeto |
| `descricao` | string | Não | Descrição detalhada |
| `responsavel` | string | Não | Nome do responsável |
| `dataInicio` | date | Não | Data início (YYYY-MM-DD) |
| `dataFim` | date | Não | Data fim (YYYY-MM-DD) |
| `status` | string | Não | Planejado, Em andamento, Concluído |
| `orcamento` | number | Não | Orçamento em R$ |

### OKRs

| Coluna | Tipo | Obrigatória | Descrição |
|--------|------|-------------|-----------|
| `objetivo` | string | Sim | Texto do objetivo |
| `descricao` | string | Não | Descrição detalhada |
| `responsavel` | string | Não | Responsável |
| `periodo` | string | Não | Período (ex: 2026-Q1) |
| `keyResult1` | string | Sim | Nome do KR 1 |
| `meta1` | number | Sim | Meta do KR 1 |
| `keyResult2` | string | Não | Nome do KR 2 |
| `meta2` | number | Não | Meta do KR 2 |
| `keyResult3` | string | Não | Nome do KR 3 |
| `meta3` | number | Não | Meta do KR 3 |
| `keyResult4` | string | Não | Nome do KR 4 |
| `meta4` | number | Não | Meta do KR 4 |
| `keyResult5` | string | Não | Nome do KR 5 |
| `meta5` | number | Não | Meta do KR 5 |

### Valores de Indicadores

| Coluna | Tipo | Obrigatória | Descrição |
|--------|------|-------------|-----------|
| `indicadorCodigo` | string | Sim | Código do indicador |
| `periodo` | string | Sim | Período (ex: 2026-01) |
| `valor` | number | Sim | Valor do indicador |

## Dicas

1. **CSV com ponto-e-vírgula:** O script detecta automaticamente o separador (; ou ,)
2. **Datas em Excel:** Use formato de data padrão — o script converte automaticamente para YYYY-MM-DD
3. **Encoding:** Use UTF-8 para acentos e caracteres especiais
4. **Delay:** Aumente o `--delay` se receber erros de rate limit
5. **Planilha grande:** Para +100 registros, considere dividir em lotes menores
6. **Transacional:** Na inserção de valores de indicadores, se um período falhar, todos os valores do mesmo indicador são revertidos

## Solução de Problemas

| Erro | Causa | Solução |
|------|-------|---------|
| "Falha na autenticação" | Credenciais inválidas | Verificar login/senha |
| "Token expirado" | Token de 2h expirou | Script reautentica automaticamente |
| "Sem permissão" | Usuário sem acesso ao módulo | Usar perfil administrador |
| "Campo obrigatório" | Coluna faltando na planilha | Verificar template |
| "Valor inválido" | Tipo de dado incorreto | Verificar formato dos valores |
