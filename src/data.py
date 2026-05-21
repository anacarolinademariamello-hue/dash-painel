"""
data.py — Carrega todos os dados do painel em batch (uma query por tabela).
Agrupa por client_key em Python para eficiência máxima.
"""
from __future__ import annotations

import json
import datetime
import requests
import streamlit as st


# ── Credenciais ───────────────────────────────────────────────────────────────

def _creds() -> tuple[str, str]:
    try:
        url = st.secrets.get("supabase_url", "") or ""
        key = st.secrets.get("supabase_service_key", "") or ""
        return url, key
    except Exception:
        return "", ""


def _configured() -> bool:
    u, k = _creds()
    return bool(u and k)


def _auth_headers() -> dict:
    _, key = _creds()
    return {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
    }


# ── Clientes ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=120)
def load_all_clients() -> list[dict]:
    """Carrega todos os clientes ativos."""
    if not _configured():
        return []
    url, _ = _creds()
    try:
        r = requests.get(
            f"{url}/rest/v1/clients",
            headers=_auth_headers(),
            params={"active": "eq.true", "order": "name.asc", "select": "*"},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


# ── Relatórios ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=120)
def load_all_reports() -> dict[str, dict]:
    """
    Carrega o relatório mais recente de TODOS os clientes em uma só query.
    Retorna {client_key: report_row}.
    """
    if not _configured():
        return {}
    url, key = _creds()
    try:
        r = requests.get(
            f"{url}/rest/v1/report_history",
            headers=_auth_headers(),
            params={
                "order":  "generated_at.desc",
                "limit":  "200",
                "select": "client_key,date_from,date_to,generated_at,metrics",
            },
            timeout=15,
        )
        r.raise_for_status()
        rows = r.json()
    except Exception:
        return {}

    # Pega só o mais recente por client_key
    result: dict[str, dict] = {}
    for row in rows:
        ck = row.get("client_key", "")
        if ck and ck not in result:
            result[ck] = row
    return result


# ── Calendário editorial ──────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_calendar_summary_all(mes_ano: str) -> dict[str, dict]:
    """
    Carrega todos os posts do calendário do mês para TODOS os clientes.
    Retorna {client_key: {total, publicados, aprovados_cliente, pediu_alteracao,
                          urgentes, sem_legenda, pendentes_cliente}}.
    """
    if not _configured():
        return {}
    url, _ = _creds()
    try:
        r = requests.get(
            f"{url}/rest/v1/editorial_calendar",
            headers=_auth_headers(),
            params={
                "mes_ano": f"eq.{mes_ano}",
                "select":  "client_key,data_publicacao,status,client_status",
                "order":   "data_publicacao.asc",
                "limit":   "2000",
            },
            timeout=15,
        )
        r.raise_for_status()
        rows = r.json()
    except Exception:
        return {}

    today = datetime.date.today()
    in_3_days = today + datetime.timedelta(days=3)

    summary: dict[str, dict] = {}
    for row in rows:
        ck = row.get("client_key", "")
        if not ck:
            continue
        if ck not in summary:
            summary[ck] = {
                "total": 0,
                "publicados": 0,
                "aprovados_cliente": 0,
                "pediu_alteracao": 0,
                "urgentes": 0,           # publicação em 3 dias, ainda em 'ideia'
                "pendentes_cliente": 0,  # sem resposta do cliente
            }
        s = summary[ck]
        s["total"] += 1

        status        = row.get("status", "")
        client_status = row.get("client_status", "") or ""

        if status == "publicado":
            s["publicados"] += 1
        if client_status == "aprovado":
            s["aprovados_cliente"] += 1
        if client_status == "alteracao":
            s["pediu_alteracao"] += 1
        if not client_status:
            s["pendentes_cliente"] += 1

        # Urgente: publicação nos próximos 3 dias e ainda em 'ideia'
        data_pub_str = row.get("data_publicacao", "")
        if data_pub_str and status == "ideia":
            try:
                data_pub = datetime.date.fromisoformat(str(data_pub_str)[:10])
                if today <= data_pub <= in_3_days:
                    s["urgentes"] += 1
            except Exception:
                pass

    return summary


# ── Roteiros ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def load_scripts_summary_all(days: int = 30) -> dict[str, dict]:
    """
    Carrega sumário de roteiros de TODOS os clientes nos últimos N dias.
    Retorna {client_key: {aprovados, rejeitados, pendentes}}.
    """
    if not _configured():
        return {}
    url, _ = _creds()
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    try:
        r = requests.get(
            f"{url}/rest/v1/script_copies",
            headers=_auth_headers(),
            params={
                "created_at": f"gte.{since}",
                "select":     "client_key,status",
                "limit":      "2000",
            },
            timeout=15,
        )
        r.raise_for_status()
        rows = r.json()
    except Exception:
        return {}

    summary: dict[str, dict] = {}
    for row in rows:
        ck = row.get("client_key", "")
        if not ck:
            continue
        if ck not in summary:
            summary[ck] = {"aprovados": 0, "rejeitados": 0, "pendentes": 0}
        st_val = row.get("status", "")
        if st_val == "aprovado":
            summary[ck]["aprovados"] += 1
        elif st_val == "rejeitado":
            summary[ck]["rejeitados"] += 1
        else:
            summary[ck]["pendentes"] += 1

    return summary


# ── Legendas ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def load_captions_summary_all(days: int = 30) -> dict[str, dict]:
    """
    Carrega sumário de legendas de TODOS os clientes nos últimos N dias.
    Retorna {client_key: {aprovadas, rejeitadas, pendentes}}.
    """
    if not _configured():
        return {}
    url, _ = _creds()
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    try:
        r = requests.get(
            f"{url}/rest/v1/caption_history",
            headers=_auth_headers(),
            params={
                "created_at": f"gte.{since}",
                "select":     "client_key,status",
                "limit":      "2000",
            },
            timeout=15,
        )
        r.raise_for_status()
        rows = r.json()
    except Exception:
        return {}

    summary: dict[str, dict] = {}
    for row in rows:
        ck = row.get("client_key", "")
        if not ck:
            continue
        if ck not in summary:
            summary[ck] = {"aprovadas": 0, "rejeitadas": 0, "pendentes": 0}
        st_val = row.get("status", "")
        if st_val == "aprovado":
            summary[ck]["aprovadas"] += 1
        elif st_val == "rejeitado":
            summary[ck]["rejeitadas"] += 1
        else:
            summary[ck]["pendentes"] += 1

    return summary


# ── Score e semáforo ──────────────────────────────────────────────────────────

def compute_health_score(
    report: dict | None,
    cal: dict | None,
    scripts: dict | None,
    captions: dict | None,
) -> tuple[int, str, list[str]]:
    """
    Calcula score 0–100 e retorna (score, cor_semaforo, lista_alertas).
    cor_semaforo: 'green' | 'yellow' | 'red'
    """
    score = 100
    alerts: list[str] = []

    # ── Relatório ────────────────────────────────────────────────
    if not report:
        score -= 25
        alerts.append("⚠️ Nenhum relatório gerado ainda")
    else:
        ga = report.get("generated_at", "")[:10]
        try:
            age = (datetime.date.today() - datetime.date.fromisoformat(ga)).days
            if age > 45:
                score -= 20
                alerts.append(f"⚠️ Último relatório há {age} dias (mais de 45 dias)")
            elif age > 30:
                score -= 10
                alerts.append(f"💡 Último relatório há {age} dias — considere atualizar")
        except Exception:
            pass

    # ── Calendário ───────────────────────────────────────────────
    if not cal or cal.get("total", 0) == 0:
        score -= 20
        alerts.append("⚠️ Sem calendário gerado este mês")
    else:
        if cal.get("urgentes", 0) > 0:
            score -= 15
            u = cal["urgentes"]
            alerts.append(f"🔴 {u} post{'s' if u>1 else ''} urgente{'s' if u>1 else ''} (publicação em 3 dias, ainda em 'ideia')")
        if cal.get("pediu_alteracao", 0) > 0:
            pa = cal["pediu_alteracao"]
            score -= 10
            alerts.append(f"💬 {pa} post{'s' if pa>1 else ''} com pedido de alteração do cliente")
        aprovados = cal.get("aprovados_cliente", 0)
        total     = cal.get("total", 1)
        pct_aprov = aprovados / total if total else 0
        if pct_aprov < 0.3 and total >= 4:
            score -= 5
            alerts.append(f"💡 Apenas {aprovados}/{total} posts aprovados pelo cliente")

    # ── Conteúdo ─────────────────────────────────────────────────
    if scripts:
        rejeit = scripts.get("rejeitados", 0)
        aprov  = scripts.get("aprovados", 0)
        total_sc = rejeit + aprov
        if total_sc >= 3 and (rejeit / total_sc) > 0.5:
            score -= 10
            alerts.append(f"💡 Alta taxa de rejeição em roteiros ({rejeit}/{total_sc})")

    score = max(0, score)

    if score >= 75:
        color = "green"
    elif score >= 45:
        color = "yellow"
    else:
        color = "red"

    return score, color, alerts


# ── Extrair métricas do relatório ─────────────────────────────────────────────

def parse_report_metrics(report: dict) -> dict:
    """Extrai métricas principais do row do relatório."""
    m = report.get("metrics", {})
    if isinstance(m, str):
        try:
            m = json.loads(m)
        except Exception:
            m = {}
    return {
        "date_from":       report.get("date_from", "")[:10],
        "date_to":         report.get("date_to", "")[:10],
        "generated_at":    report.get("generated_at", "")[:10],
        "org_reach":       int(m.get("org_reach") or 0),
        "org_eng_rate":    float(m.get("org_eng_rate") or 0),
        "followers_gained":int(m.get("followers_gained") or 0),
        "total_posts":     int(m.get("total_posts") or 0),
        "best_format":     m.get("best_format", ""),
    }
