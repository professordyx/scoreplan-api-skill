#!/usr/bin/env python3
"""
Scoreplan Bulk Upload — Upload em massa de indicadores, ações, projetos, OKRs e valores via planilha.

Uso:
    python3 bulk_upload.py --url URL --login USER --password PASS --type TYPE --file FILE [--api-version v1|v2] [--api-key KEY] [--dry-run] [--delay SECONDS]

Tipos suportados:
    indicators       — Criar indicadores em massa
    actions          — Criar ações/planos de ação em massa
    projects         — Criar projetos em massa
    okrs             — Criar OKRs em massa
    indicator-values — Inserir valores de indicadores em massa
    integration-fields — Inserir valores de campos integrados

Formatos de arquivo: .xlsx, .csv

Exemplos:
    # Upload de indicadores via API v2 (Bearer Token)
    python3 bulk_upload.py --url https://api-prod.scoreplan.com.br --login admin --password s3nh4 --type indicators --file indicadores.xlsx

    # Upload de valores via API v1 (Chave da API)
    python3 bulk_upload.py --url https://api-prod.scoreplan.com.br --api-version v1 --api-key MINHA_CHAVE --type indicator-values --file valores.csv

    # Dry run (simular sem enviar)
    python3 bulk_upload.py --url https://api-prod.scoreplan.com.br --login admin --password s3nh4 --type actions --file acoes.xlsx --dry-run
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERRO: Módulo 'requests' não encontrado. Instale com: pip install requests")
    sys.exit(1)

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# ─── Configuração ────────────────────────────────────────────────────────────


def _to_br_date(d):
    """Converte yyyy-mm-dd -> dd/mm/yyyy; mantem se ja estiver em dd/mm/yyyy."""
    if not d:
        return d
    d = str(d).strip()
    if "-" in d and len(d.split("-")[0]) == 4:
        y, m, day = d.split("-")[:3]
        return f"{day.zfill(2)}/{m.zfill(2)}/{y}"
    return d

DEFAULT_DELAY = 0.2  # segundos entre requisições


# ─── Leitura de Planilha ─────────────────────────────────────────────────────

def read_xlsx(filepath: str) -> list[dict]:
    """Lê arquivo .xlsx e retorna lista de dicts (header como chaves)."""
    if not HAS_OPENPYXL:
        print("ERRO: Módulo 'openpyxl' necessário para .xlsx. Instale com: pip install openpyxl")
        sys.exit(1)
    wb = openpyxl.load_workbook(filepath, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h).strip() for h in rows[0]]
    data = []
    for row in rows[1:]:
        if all(v is None for v in row):
            continue
        record = {}
        for i, header in enumerate(headers):
            val = row[i] if i < len(row) else None
            if isinstance(val, datetime):
                val = val.strftime("%Y-%m-%d")
            record[header] = val
        data.append(record)
    wb.close()
    return data


def read_csv(filepath: str) -> list[dict]:
    """Lê arquivo .csv e retorna lista de dicts."""
    data = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        # Tentar com vírgula se não houver colunas com ;
        if len(reader.fieldnames or []) <= 1:
            f.seek(0)
            reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            data.append({k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()})
    return data


def read_file(filepath: str) -> list[dict]:
    """Lê planilha (.xlsx ou .csv) e retorna lista de dicts."""
    ext = Path(filepath).suffix.lower()
    if ext == ".xlsx":
        return read_xlsx(filepath)
    elif ext == ".csv":
        return read_csv(filepath)
    else:
        print(f"ERRO: Formato '{ext}' não suportado. Use .xlsx ou .csv")
        sys.exit(1)


# ─── Autenticação ────────────────────────────────────────────────────────────

class ScoreplanClient:
    """Cliente para API do Scoreplan (v1 e v2)."""

    def __init__(self, base_url: str, api_version: str = "v2",
                 login: str = None, password: str = None, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.api_key = api_key
        self.login = login
        self.password = password
        self.token = None
        self.token_expiration = None
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def authenticate(self):
        """Autenticar e obter Bearer Token (API v2)."""
        if self.api_version == "v1":
            if not self.api_key:
                print("ERRO: API v1 requer --api-key")
                sys.exit(1)
            # v1 usa chave na URL, validar
            resp = self.session.get(f"{self.base_url}/api/1.0/{self.api_key}/Console/Ping")
            if resp.status_code != 200:
                print(f"ERRO: Chave da API inválida. Status: {resp.status_code}")
                sys.exit(1)
            data = resp.json()
            if data.get("status") == "ERROR":
                print(f"ERRO: {data.get('content', {}).get('mensagem', 'Chave inválida')}")
                sys.exit(1)
            print("OK: Chave da API validada com sucesso")
            return

        # API v2 — Bearer Token
        if not self.login or not self.password:
            print("ERRO: API v2 requer --login e --password")
            sys.exit(1)

        print(f"Autenticando como '{self.login}'...")
        resp = self.session.post(
            f"{self.base_url}/auth/login",
            json={"Username": self.login, "Password": self.password}
        )
        if resp.status_code != 200:
            print(f"ERRO: Falha na autenticação. Status: {resp.status_code}")
            print(f"Resposta: {resp.text[:500]}")
            sys.exit(1)

        data = resp.json()
        self.token = data.get("token")
        self.token_expiration = data.get("expiration")
        if not self.token:
            print(f"ERRO: Token não retornado. Resposta: {json.dumps(data, indent=2)[:500]}")
            sys.exit(1)

        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        print(f"OK: Autenticado. Token expira em: {self.token_expiration or '2h'}")

    def _ensure_token(self):
        """Verifica se o token ainda é válido, reautentica se necessário."""
        if self.api_version == "v1":
            return
        if self.token_expiration:
            try:
                exp = datetime.fromisoformat(self.token_expiration.replace("Z", "+00:00"))
                if datetime.now(exp.tzinfo) >= exp:
                    print("Token expirado. Reautenticando...")
                    self.authenticate()
            except (ValueError, TypeError):
                pass

    def _url(self, endpoint: str) -> str:
        """Monta URL completa baseada na versão da API."""
        if self.api_version == "v1":
            return f"{self.base_url}/api/1.0/{self.api_key}/{endpoint}"
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint: str, params: dict = None) -> dict:
        """Requisição GET."""
        self._ensure_token()
        resp = self.session.get(self._url(endpoint), params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, endpoint: str, data: dict = None) -> dict:
        """Requisição POST."""
        self._ensure_token()
        resp = self.session.post(self._url(endpoint), json=data)
        resp.raise_for_status()
        return resp.json()

    def put(self, endpoint: str, data: dict = None) -> dict:
        """Requisição PUT."""
        self._ensure_token()
        resp = self.session.put(self._url(endpoint), json=data)
        resp.raise_for_status()
        return resp.json()


# ─── Upload Handlers ─────────────────────────────────────────────────────────

def upload_indicators(client: ScoreplanClient, records: list[dict], dry_run: bool, delay: float):
    """Upload de indicadores em massa."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Enviando {len(records)} indicadores...")
    success, errors = 0, 0
    for i, rec in enumerate(records, 1):
        payload = {
            "codigo": rec.get("codigo"),
            "nome": rec.get("nome"),
            "descricao": rec.get("descricao", ""),
            "unidade": rec.get("unidade", ""),
            "polaridade": rec.get("polaridade", ""),
            "meta": float(rec["meta"]) if rec.get("meta") else None,
            "periodoTipo": rec.get("periodoTipo", "SC_MES"),
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        if dry_run:
            print(f"  [{i}/{len(records)}] {payload.get('codigo', '?')} — {payload.get('nome', '?')}")
            success += 1
            continue

        try:
            if client.api_version == "v1":
                # v1 não tem endpoint direto para criar indicador — usar campos integrados
                print(f"  [{i}/{len(records)}] AVISO: API v1 não suporta criação direta de indicadores")
                errors += 1
                continue
            result = client.post("Indicators/Insert", payload)
            print(f"  [{i}/{len(records)}] OK: {payload.get('codigo')} — {payload.get('nome')}")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(records)}] ERRO: {payload.get('codigo')} — {e}")
            errors += 1

        if delay > 0:
            time.sleep(delay)

    print(f"\nResultado: {success} sucesso, {errors} erros")
    return success, errors


def upload_actions(client: ScoreplanClient, records: list[dict], dry_run: bool, delay: float):
    """Upload de ações em massa."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Enviando {len(records)} ações...")
    success, errors = 0, 0
    for i, rec in enumerate(records, 1):
        # ActionDTO da API v2 External
        resp_uid = rec.get("responsibleUserId") or rec.get("userId")
        responsibles = [{"userId": int(resp_uid), "trackProgress": False}] if resp_uid else []
        tags = rec.get("tags")
        tags = [t.strip() for t in tags.split(",")] if isinstance(tags, str) and tags else []
        payload = {
            "title": rec.get("title") or rec.get("titulo"),
            "startDateEstimated": _to_br_date(rec.get("startDateEstimated") or rec.get("dataInicio")),
            "endDateEstimated": _to_br_date(rec.get("endDateEstimated") or rec.get("dataFim")),
            "situation": int(rec.get("situation") or 0),
            "raci": {
                "responsibles": responsibles, "groupResponsible": [],
                "authorities": responsibles, "groupAuthority": [],
                "consulted": [], "groupConsulted": [],
                "informed": [], "groupInformed": [],
            },
            "tags": tags,
            "sector": rec.get("sector") or rec.get("setor") or "",
        }

        if dry_run:
            print(f"  [{i}/{len(records)}] {payload.get('title', '?')}")
            success += 1
            continue

        try:
            if client.api_version == "v1":
                raise RuntimeError("API v1 nao cria acoes - use v2 External (Actions/External/Insert)")
            result = client.post("Actions/External/Insert", payload)
            print(f"  [{i}/{len(records)}] OK: {payload.get('title')}")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(records)}] ERRO: {payload.get('title')} — {e}")
            errors += 1

        if delay > 0:
            time.sleep(delay)

    print(f"\nResultado: {success} sucesso, {errors} erros")
    return success, errors


def _raci(rec):
    """Monta RACI da API External a partir de responsibleUserId/userId (grupos vazios p/ evitar erro)."""
    uid = rec.get("responsibleUserId") or rec.get("userId")
    responsibles = [{"userId": int(uid), "trackProgress": False}] if uid else []
    return {
        "responsibles": responsibles, "groupResponsible": [],
        "authorities": responsibles, "groupAuthority": [],
        "consulted": [], "groupConsulted": [],
        "informed": [], "groupInformed": [],
    }


def _tags(rec):
    t = rec.get("tags")
    return [x.strip() for x in t.split(",")] if isinstance(t, str) and t else []


def upload_programs(client: ScoreplanClient, records: list[dict], dry_run: bool, delay: float):
    """Upload de programas em massa (v2 External -> Program/External/Insert)."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Enviando {len(records)} programas...")
    success, errors = 0, 0
    for i, rec in enumerate(records, 1):
        payload = {"title": rec.get("title") or rec.get("titulo") or rec.get("nome"), "raci": _raci(rec)}
        if dry_run:
            print(f"  [{i}/{len(records)}] {payload.get('title', '?')}")
            success += 1
            continue
        try:
            client.post("Program/External/Insert", payload)
            print(f"  [{i}/{len(records)}] OK: {payload.get('title')}")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(records)}] ERRO: {payload.get('title')} — {e}")
            errors += 1
        if delay > 0:
            time.sleep(delay)
    print(f"\nResultado: {success} sucesso, {errors} erros")
    return success, errors


def upload_projects(client: ScoreplanClient, records: list[dict], dry_run: bool, delay: float):
    """Upload de projetos em massa (v2 External -> Project/External/Insert).

    Colunas: title, programId, situation, level (E/T/O), startDateEstimated|dataInicio,
    endDateEstimated|dataFim, estimatedExpenseDeduction, estimatedRevenueDeduction,
    responsibleUserId, tags, sector.
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Enviando {len(records)} projetos...")
    success, errors = 0, 0
    for i, rec in enumerate(records, 1):
        payload = {
            "title": rec.get("title") or rec.get("titulo") or rec.get("nome"),
            "programId": int(rec["programId"]) if rec.get("programId") else None,
            "situation": int(rec.get("situation") or 1),
            "level": rec.get("level") or "O",
            "startDateEstimated": _to_br_date(rec.get("startDateEstimated") or rec.get("dataInicio")),
            "endDateEstimated": _to_br_date(rec.get("endDateEstimated") or rec.get("dataFim")),
            "validateDate": False,
            "raci": _raci(rec),
            "tags": _tags(rec),
            "sector": rec.get("sector") or rec.get("setor") or "",
        }
        if rec.get("estimatedExpenseDeduction"):
            payload["estimatedExpenseDeduction"] = float(rec["estimatedExpenseDeduction"])
        if rec.get("estimatedRevenueDeduction"):
            payload["estimatedRevenueDeduction"] = float(rec["estimatedRevenueDeduction"])
        payload = {k: v for k, v in payload.items() if v is not None}

        if dry_run:
            print(f"  [{i}/{len(records)}] {payload.get('title', '?')}")
            success += 1
            continue
        try:
            client.post("Project/External/Insert", payload)
            print(f"  [{i}/{len(records)}] OK: {payload.get('title')}")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(records)}] ERRO: {payload.get('title')} — {e}")
            errors += 1
        if delay > 0:
            time.sleep(delay)
    print(f"\nResultado: {success} sucesso, {errors} erros")
    return success, errors


def upload_phases(client: ScoreplanClient, records: list[dict], dry_run: bool, delay: float):
    """Upload de fases de projeto em massa (v2 External -> ProjectPhase/External/Insert).

    Colunas: title, projectId, startDateEstimated|dataInicio, endDateEstimated|dataFim,
    estimatedExpenseDeduction, estimatedRevenueDeduction, weight.
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Enviando {len(records)} fases...")
    success, errors = 0, 0
    for i, rec in enumerate(records, 1):
        payload = {
            "title": rec.get("title") or rec.get("titulo") or rec.get("nome"),
            "projectId": int(rec["projectId"]) if rec.get("projectId") else None,
            "startDateEstimated": _to_br_date(rec.get("startDateEstimated") or rec.get("dataInicio")),
            "endDateEstimated": _to_br_date(rec.get("endDateEstimated") or rec.get("dataFim")),
            "weight": float(rec["weight"]) if rec.get("weight") else None,
        }
        if rec.get("estimatedExpenseDeduction"):
            payload["estimatedExpenseDeduction"] = float(rec["estimatedExpenseDeduction"])
        if rec.get("estimatedRevenueDeduction"):
            payload["estimatedRevenueDeduction"] = float(rec["estimatedRevenueDeduction"])
        payload = {k: v for k, v in payload.items() if v is not None}

        if dry_run:
            print(f"  [{i}/{len(records)}] {payload.get('title', '?')} (projectId={payload.get('projectId')})")
            success += 1
            continue
        try:
            client.post("ProjectPhase/External/Insert", payload)
            print(f"  [{i}/{len(records)}] OK: {payload.get('title')}")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(records)}] ERRO: {payload.get('title')} — {e}")
            errors += 1
        if delay > 0:
            time.sleep(delay)
    print(f"\nResultado: {success} sucesso, {errors} erros")
    return success, errors


def upload_okrs(client: ScoreplanClient, records: list[dict], dry_run: bool, delay: float):
    """Upload de OKRs em massa."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Enviando {len(records)} OKRs...")
    success, errors = 0, 0
    for i, rec in enumerate(records, 1):
        key_results = []
        for j in range(1, 6):
            kr_name = rec.get(f"keyResult{j}")
            kr_meta = rec.get(f"meta{j}")
            if kr_name:
                kr = {"nome": kr_name}
                if kr_meta:
                    kr["meta"] = float(kr_meta)
                key_results.append(kr)

        payload = {
            "objetivo": rec.get("objetivo"),
            "descricao": rec.get("descricao", ""),
            "responsavel": rec.get("responsavel", ""),
            "periodo": rec.get("periodo"),
            "keyResults": key_results,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        if dry_run:
            print(f"  [{i}/{len(records)}] {payload.get('objetivo', '?')} ({len(key_results)} KRs)")
            success += 1
            continue

        try:
            raise RuntimeError("OKR nao suporta insert via API External (apenas OKR/External/List)")
            print(f"  [{i}/{len(records)}] OK: {payload.get('objetivo')} ({len(key_results)} KRs)")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(records)}] ERRO: {payload.get('objetivo')} — {e}")
            errors += 1

        if delay > 0:
            time.sleep(delay)

    print(f"\nResultado: {success} sucesso, {errors} erros")
    return success, errors


def upload_indicator_values(client: ScoreplanClient, records: list[dict], dry_run: bool, delay: float):
    """Upload de valores de indicadores em massa."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processando {len(records)} valores de indicadores...")

    # Agrupar por indicador
    grouped = {}
    for rec in records:
        key = rec.get("indicadorCodigo") or rec.get("indicadorId") or rec.get("codigo")
        if key not in grouped:
            grouped[key] = []
        grouped[key].append({
            "periodo": rec.get("periodo"),
            "periodoId": rec.get("periodoId"),
            "valor": float(rec["valor"]) if rec.get("valor") else 0,
        })

    success, errors = 0, 0
    for i, (indicator_key, values) in enumerate(grouped.items(), 1):
        if dry_run:
            print(f"  [{i}/{len(grouped)}] {indicator_key}: {len(values)} valores")
            success += 1
            continue

        try:
            if client.api_version == "v1":
                payload = {
                    "campoId": indicator_key,
                    "valores": [{"periodoId": v.get("periodoId", v.get("periodo")), "valor": v["valor"]} for v in values]
                }
                result = client.post("CamposIndicadores/InserirValor", payload)
            else:
                payload = {"valores": values}
                result = client.post(f"indicators/{indicator_key}/values", payload)
            print(f"  [{i}/{len(grouped)}] OK: {indicator_key} — {len(values)} valores")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(grouped)}] ERRO: {indicator_key} — {e}")
            errors += 1

        if delay > 0:
            time.sleep(delay)

    print(f"\nResultado: {success} indicadores atualizados, {errors} erros")
    return success, errors


def upload_integration_fields(client: ScoreplanClient, records: list[dict], dry_run: bool, delay: float):
    """Upload de valores de campos integrados em massa (API v1)."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processando {len(records)} valores de campos integrados...")

    grouped = {}
    for rec in records:
        key = rec.get("campoId")
        if key not in grouped:
            grouped[key] = []
        grouped[key].append({
            "periodoId": rec.get("periodoId"),
            "valor": float(rec["valor"]) if rec.get("valor") else 0,
        })

    success, errors = 0, 0
    for i, (campo_id, values) in enumerate(grouped.items(), 1):
        payload = {"campoId": campo_id, "valores": values}

        if dry_run:
            print(f"  [{i}/{len(grouped)}] Campo {campo_id}: {len(values)} valores")
            success += 1
            continue

        try:
            if client.api_version == "v1":
                result = client.post("CamposIndicadores/InserirValor", payload)
            else:
                result = client.post("integration-fields/values", payload)
            print(f"  [{i}/{len(grouped)}] OK: Campo {campo_id} — {len(values)} valores")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(grouped)}] ERRO: Campo {campo_id} — {e}")
            errors += 1

        if delay > 0:
            time.sleep(delay)

    print(f"\nResultado: {success} campos atualizados, {errors} erros")
    return success, errors


# ─── CLI ─────────────────────────────────────────────────────────────────────

UPLOAD_HANDLERS = {
    "indicators": upload_indicators,
    "actions": upload_actions,
    "programs": upload_programs,
    "projects": upload_projects,
    "phases": upload_phases,
    "okrs": upload_okrs,
    "indicator-values": upload_indicator_values,
    "integration-fields": upload_integration_fields,
}


def main():
    parser = argparse.ArgumentParser(
        description="Scoreplan Bulk Upload — Upload em massa via planilha",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--url", required=True, help="Base URL da API (ex: https://api-prod.scoreplan.com.br)")
    parser.add_argument("--login", help="Usuário para autenticação (API v2)")
    parser.add_argument("--password", help="Senha para autenticação (API v2)")
    parser.add_argument("--api-version", choices=["v1", "v2"], default="v2", help="Versão da API (default: v2)")
    parser.add_argument("--api-key", help="Chave da API (API v1)")
    parser.add_argument("--type", required=True, choices=list(UPLOAD_HANDLERS.keys()), help="Tipo de upload")
    parser.add_argument("--file", required=True, help="Arquivo .xlsx ou .csv com os dados")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem enviar (mostra o que seria enviado)")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help=f"Delay entre requisições em segundos (default: {DEFAULT_DELAY})")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"ERRO: Arquivo não encontrado: {args.file}")
        sys.exit(1)

    # Ler planilha
    print(f"Lendo arquivo: {args.file}")
    records = read_file(args.file)
    if not records:
        print("ERRO: Arquivo vazio ou sem dados válidos")
        sys.exit(1)
    print(f"OK: {len(records)} registros encontrados")
    print(f"Colunas: {', '.join(records[0].keys())}")

    # Autenticar
    client = ScoreplanClient(
        base_url=args.url,
        api_version=args.api_version,
        login=args.login,
        password=args.password,
        api_key=args.api_key,
    )
    if not args.dry_run:
        client.authenticate()

    # Upload
    handler = UPLOAD_HANDLERS[args.type]
    success, errors = handler(client, records, args.dry_run, args.delay)

    # Resumo
    print(f"\n{'=' * 50}")
    print(f"RESUMO {'(DRY RUN)' if args.dry_run else ''}")
    print(f"  Tipo: {args.type}")
    print(f"  Arquivo: {args.file}")
    print(f"  Total: {len(records)}")
    print(f"  Sucesso: {success}")
    print(f"  Erros: {errors}")
    print(f"{'=' * 50}")

    sys.exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()
