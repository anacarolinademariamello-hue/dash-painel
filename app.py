"""
app.py — Painel de Clientes | Dash Digital
Dashboard completo com status em tempo real de todos os clientes.
"""
import datetime
import streamlit as st

from src.styles import SIDEBAR_CSS
from src.data import (
    load_all_clients,
    load_all_reports,
    load_calendar_summary_all,
    load_scripts_summary_all,
    load_captions_summary_all,
    compute_health_score,
    parse_report_metrics,
)

# ── Configuração da página ────────────────────────────────────────────────────

st.set_page_config(
    page_title="Painel de Clientes | Dash",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

# ── Links externos ────────────────────────────────────────────────────────────

APPS = {
    "relatorio":   "https://dash-relatorios-app.streamlit.app/",
    "calendario":  "https://dash-calendario-editorial.streamlit.app/",
    "roteiro":     "https://dash-copy-roteiro.streamlit.app/",
    "legenda":     "https://dash-legendas-app.streamlit.app/",
    "copy_ads":    "https://dash-copy-ads.streamlit.app/",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📊 Painel de Clientes")
    st.markdown("---")

    # Filtros
    st.markdown("### Filtros")
    filtro_busca = st.text_input("🔍 Buscar cliente", placeholder="Nome ou @handle...")
    filtro_saude = st.selectbox(
        "Filtrar por saúde",
        ["Todos", "🟢 Saudável", "🟡 Atenção", "🔴 Crítico"],
    )

    st.markdown("---")
    st.markdown("### Mês de referência")
    hoje = datetime.date.today()
    meses = []
    for delta in range(3):
        d = hoje.replace(day=1) - datetime.timedelta(days=delta * 28)
        meses.append(d.strftime("%Y-%m"))
    mes_selecionado = st.selectbox(
        "Mês",
        meses,
        format_func=lambda x: datetime.datetime.strptime(x, "%Y-%m").strftime("%B/%Y").title(),
    )

    st.markdown("---")
    if st.button("🔄 Atualizar dados", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### Acesso rápido")
    for label, url in [
        ("📈 Relatórios", APPS["relatorio"]),
        ("📅 Calendário", APPS["calendario"]),
        ("✍️ Roteiros", APPS["roteiro"]),
        ("💬 Legendas", APPS["legenda"]),
        ("💰 Copy Ads", APPS["copy_ads"]),
    ]:
        st.markdown(f'<a href="{url}" target="_blank" style="color:#93c5fd;font-size:0.85rem;">{label} ↗</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.72rem;color:#64748b;text-align:center;">Dash Digital · Painel interno</p>',
        unsafe_allow_html=True,
    )


# ── Carregamento de dados ─────────────────────────────────────────────────────

with st.spinner("Carregando dados..."):
    clients      = load_all_clients()
    all_reports  = load_all_reports()
    cal_summary  = load_calendar_summary_all(mes_selecionado)
    scr_summary  = load_scripts_summary_all(30)
    cap_summary  = load_captions_summary_all(30)

if not clients:
    st.warning("Nenhum cliente cadastrado ou Supabase não configurado.")
    st.stop()

# ── Enriquecer clientes com scores ───────────────────────────────────────────

enriched = []
for c in clients:
    ck     = c.get("key", "")
    report = all_reports.get(ck)
    cal    = cal_summary.get(ck)
    scr    = scr_summary.get(ck)
    cap    = cap_summary.get(ck)
    score, color, alerts = compute_health_score(report, cal, scr, cap)
    enriched.append({
        **c,
        "_report": report,
        "_cal":    cal,
        "_scr":    scr,
        "_cap":    cap,
        "_score":  score,
        "_color":  color,
        "_alerts": alerts,
    })

# ── Filtrar clientes ──────────────────────────────────────────────────────────

def _match_filter(c: dict) -> bool:
    if filtro_busca:
        q = filtro_busca.lower()
        if q not in c.get("name", "").lower() and q not in c.get("handle", "").lower():
            return False
    if filtro_saude != "Todos":
        color_map = {"🟢 Saudável": "green", "🟡 Atenção": "yellow", "🔴 Crítico": "red"}
        if c["_color"] != color_map[filtro_saude]:
            return False
    return True

visible = [c for c in enriched if _match_filter(c)]

# Ordenar: vermelhos primeiro, depois amarelos, depois verdes; dentro do grupo, menor score primeiro
order = {"red": 0, "yellow": 1, "green": 2}
visible.sort(key=lambda c: (order[c["_color"]], -c["_score"]))

# ── KPI global bar ────────────────────────────────────────────────────────────

total_green  = sum(1 for c in enriched if c["_color"] == "green")
total_yellow = sum(1 for c in enriched if c["_color"] == "yellow")
total_red    = sum(1 for c in enriched if c["_color"] == "red")
total_urgent = sum((c["_cal"] or {}).get("urgentes", 0) for c in enriched)
total_alteracao = sum((c["_cal"] or {}).get("pediu_alteracao", 0) for c in enriched)

mes_label = datetime.datetime.strptime(mes_selecionado, "%Y-%m").strftime("%B/%Y").title()

st.markdown(
    f"""
    <div class="painel-header">
        <span style="font-size:2rem;">📊</span>
        <div>
            <h1>Painel de Clientes</h1>
            <p style="font-size:0.85rem;color:#64748b;margin:0;">
                {len(enriched)} clientes · Calendário: {mes_label} · Atualizado agora
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="kpi-bar">
        <div class="kpi-chip kpi-green">
            <span class="kpi-val">{total_green}</span>
            <span>🟢 Saudáveis</span>
        </div>
        <div class="kpi-chip kpi-yellow">
            <span class="kpi-val">{total_yellow}</span>
            <span>🟡 Atenção</span>
        </div>
        <div class="kpi-chip kpi-red">
            <span class="kpi-val">{total_red}</span>
            <span>🔴 Críticos</span>
        </div>
        <div class="kpi-chip kpi-{"red" if total_urgent > 0 else "blue"}">
            <span class="kpi-val">{total_urgent}</span>
            <span>🚨 Posts urgentes</span>
        </div>
        <div class="kpi-chip kpi-{"yellow" if total_alteracao > 0 else "blue"}">
            <span class="kpi-val">{total_alteracao}</span>
            <span>💬 Pedidos alteração</span>
        </div>
        <div class="kpi-chip kpi-blue">
            <span class="kpi-val">{len(visible)}</span>
            <span>👁️ Exibindo</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Helpers de renderização ───────────────────────────────────────────────────

def _fmt_date(d: str) -> str:
    if not d:
        return "—"
    try:
        return datetime.date.fromisoformat(d[:10]).strftime("%d/%m/%Y")
    except Exception:
        return d[:10]


def _age_label(d: str) -> str:
    if not d:
        return ""
    try:
        age = (datetime.date.today() - datetime.date.fromisoformat(d[:10])).days
        if age == 0:
            return "hoje"
        if age == 1:
            return "ontem"
        return f"há {age} dias"
    except Exception:
        return ""


def _val_color(val, warn_if_zero=False) -> str:
    if warn_if_zero and val == 0:
        return "section-val-gray"
    return "section-val"


# ── Cards dos clientes ────────────────────────────────────────────────────────

if not visible:
    st.info("Nenhum cliente encontrado com os filtros aplicados.")
else:
    for c in visible:
        ck     = c.get("key", "")
        name   = c.get("name", "—")
        handle = c.get("handle", "")
        score  = c["_score"]
        color  = c["_color"]
        alerts = c["_alerts"]
        report = c["_report"]
        cal    = c["_cal"] or {}
        scr    = c["_scr"] or {}
        cap    = c["_cap"] or {}

        # Semáforo e cabeçalho
        semaforo_html = f'<span class="semaforo semaforo-{color}"></span>'
        handle_html   = f'<span class="client-handle">@{handle}</span>' if handle else ""
        score_html    = f'<span class="client-score">score {score}/100</span>'

        # ── Seção: Relatório ─────────────────────────────────────
        if report:
            m          = parse_report_metrics(report)
            rep_date   = _fmt_date(m["generated_at"])
            rep_age    = _age_label(m["generated_at"])
            rep_period = f"{_fmt_date(m['date_from'])} → {_fmt_date(m['date_to'])}"
            reach_fmt  = f"{m['org_reach']:,}".replace(",", ".")
            eng_fmt    = f"{m['org_eng_rate']:.2f}%"
            foll_fmt   = f"+{m['followers_gained']}"
            posts_fmt  = str(m["total_posts"])
            best_fmt   = m["best_format"] or "—"
            rep_age_class = (
                "section-val-red"    if rep_age.startswith("há") and int(rep_age.split()[1]) > 45
                else "section-val-yellow" if rep_age.startswith("há") and int(rep_age.split()[1]) > 30
                else "section-val-green"
            ) if rep_age.startswith("há") else "section-val-green"

            report_html = f"""
            <div class="card-section">
                <div class="section-title">📈 Último Relatório</div>
                <div class="section-row">
                    <span>Gerado</span>
                    <span class="{rep_age_class}">{rep_date} <span style="color:#94a3b8;font-size:0.75rem;">({rep_age})</span></span>
                </div>
                <div class="section-row">
                    <span>Período</span>
                    <span class="section-val" style="font-size:0.75rem;">{rep_period}</span>
                </div>
                <div class="section-row">
                    <span>Alcance orgânico</span>
                    <span class="section-val">{reach_fmt}</span>
                </div>
                <div class="section-row">
                    <span>Engajamento</span>
                    <span class="section-val">{eng_fmt}</span>
                </div>
                <div class="section-row">
                    <span>Seguidores ganhos</span>
                    <span class="section-val-green">{foll_fmt}</span>
                </div>
                <div class="section-row">
                    <span>Posts analisados</span>
                    <span class="section-val">{posts_fmt}</span>
                </div>
                <div class="section-row">
                    <span>Melhor formato</span>
                    <span class="section-val">{best_fmt}</span>
                </div>
            </div>
            """
        else:
            report_html = """
            <div class="card-section">
                <div class="section-title">📈 Último Relatório</div>
                <div style="color:#ef4444;font-size:0.82rem;padding:8px 0;">
                    ⚠️ Nenhum relatório gerado
                </div>
            </div>
            """

        # ── Seção: Calendário ────────────────────────────────────
        cal_total    = cal.get("total", 0)
        cal_pub      = cal.get("publicados", 0)
        cal_aprov    = cal.get("aprovados_cliente", 0)
        cal_alt      = cal.get("pediu_alteracao", 0)
        cal_pend     = cal.get("pendentes_cliente", 0)
        cal_urg      = cal.get("urgentes", 0)

        if cal_total == 0:
            cal_html = f"""
            <div class="card-section">
                <div class="section-title">📅 Calendário — {mes_label}</div>
                <div style="color:#f59e0b;font-size:0.82rem;padding:8px 0;">
                    ⚠️ Nenhum calendário gerado
                </div>
            </div>
            """
        else:
            urg_color  = "section-val-red"    if cal_urg  > 0 else "section-val-green"
            alt_color  = "section-val-yellow"  if cal_alt  > 0 else "section-val-green"
            pend_color = "section-val-yellow"  if cal_pend > 0 else "section-val-green"
            cal_html = f"""
            <div class="card-section">
                <div class="section-title">📅 Calendário — {mes_label}</div>
                <div class="section-row">
                    <span>Total de posts</span>
                    <span class="section-val">{cal_total}</span>
                </div>
                <div class="section-row">
                    <span>Publicados</span>
                    <span class="section-val">{cal_pub}</span>
                </div>
                <div class="section-row">
                    <span>Aprovados pelo cliente</span>
                    <span class="section-val-green">{cal_aprov}</span>
                </div>
                <div class="section-row">
                    <span>Pediu alteração</span>
                    <span class="{alt_color}">{cal_alt}</span>
                </div>
                <div class="section-row">
                    <span>Pendente (cliente)</span>
                    <span class="{pend_color}">{cal_pend}</span>
                </div>
                <div class="section-row">
                    <span>🚨 Urgentes</span>
                    <span class="{urg_color}">{cal_urg}</span>
                </div>
            </div>
            """

        # ── Seção: Conteúdo (últimos 30 dias) ────────────────────
        sc_aprov  = scr.get("aprovados",  0)
        sc_rejeit = scr.get("rejeitados", 0)
        sc_pend   = scr.get("pendentes",  0)
        cap_aprov  = cap.get("aprovadas",  0)
        cap_rejeit = cap.get("rejeitadas", 0)
        cap_pend   = cap.get("pendentes",  0)

        sc_rej_color  = "section-val-yellow" if sc_rejeit  > 0 else "section-val"
        cap_rej_color = "section-val-yellow" if cap_rejeit > 0 else "section-val"

        content_html = f"""
        <div class="card-section">
            <div class="section-title">✍️ Conteúdo — últimos 30 dias</div>
            <div style="color:#64748b;font-size:0.72rem;margin-bottom:4px;">Roteiros</div>
            <div class="section-row">
                <span>Aprovados</span>
                <span class="section-val-green">{sc_aprov}</span>
            </div>
            <div class="section-row">
                <span>Rejeitados</span>
                <span class="{sc_rej_color}">{sc_rejeit}</span>
            </div>
            <div class="section-row">
                <span>Pendentes</span>
                <span class="section-val">{sc_pend}</span>
            </div>
            <hr class="divider">
            <div style="color:#64748b;font-size:0.72rem;margin-bottom:4px;">Legendas</div>
            <div class="section-row">
                <span>Aprovadas</span>
                <span class="section-val-green">{cap_aprov}</span>
            </div>
            <div class="section-row">
                <span>Rejeitadas</span>
                <span class="{cap_rej_color}">{cap_rejeit}</span>
            </div>
            <div class="section-row">
                <span>Pendentes</span>
                <span class="section-val">{cap_pend}</span>
            </div>
        </div>
        """

        # ── Alertas ───────────────────────────────────────────────
        if alerts:
            alert_items = "".join(
                f'<div class="alert-item{"" if not a.startswith("🔴") else " alert-red"}">{a}</div>'
                for a in alerts
            )
            alerts_html = f'<div class="alert-list">{alert_items}</div>'
        else:
            alerts_html = (
                '<div class="alert-list">'
                '<div class="alert-item" style="color:#065f46;background:#f0fdf4;border-color:#bbf7d0;">'
                '✅ Tudo em ordem</div></div>'
            )

        # ── Links de ação ─────────────────────────────────────────
        action_links = " · ".join([
            f'<a href="{APPS["relatorio"]}" target="_blank" style="color:#3b82f6;font-size:0.78rem;text-decoration:none;">📈 Relatório</a>',
            f'<a href="{APPS["calendario"]}" target="_blank" style="color:#3b82f6;font-size:0.78rem;text-decoration:none;">📅 Calendário</a>',
            f'<a href="{APPS["roteiro"]}" target="_blank" style="color:#3b82f6;font-size:0.78rem;text-decoration:none;">✍️ Roteiro</a>',
            f'<a href="{APPS["legenda"]}" target="_blank" style="color:#3b82f6;font-size:0.78rem;text-decoration:none;">💬 Legenda</a>',
        ])

        # ── Montar card completo ──────────────────────────────────
        nicho_html = ""
        nicho = c.get("nicho", "")
        sub   = c.get("sub_nicho", "")
        if nicho:
            nicho_html = f'<span style="font-size:0.75rem;color:#64748b;margin-left:8px;">· {nicho}{" / "+sub if sub else ""}</span>'

        st.markdown(
            f"""
            <div class="client-card">
                <div class="client-card-header">
                    <span class="semaforo semaforo-{color}"></span>
                    <span class="client-name">{name}</span>
                    {handle_html}
                    {nicho_html}
                    {score_html}
                </div>
                <div class="card-sections">
                    {report_html}
                    {cal_html}
                    {content_html}
                </div>
                {alerts_html}
                <div style="margin-top:10px;border-top:1px solid #f1f5f9;padding-top:8px;">
                    {action_links}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Rodapé ────────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div class="footer">
        Painel de Clientes · Dash Digital · {datetime.date.today().strftime("%d/%m/%Y")}
    </div>
    """,
    unsafe_allow_html=True,
)
