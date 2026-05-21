"""
styles.py — CSS global para o Painel de Clientes.
"""

SIDEBAR_CSS = """
<style>
/* ── Sidebar escura ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0d2137 !important;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stMarkdown p {
    color: #cbd5e1 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #1e3a5f !important;
}
[data-testid="stSidebar"] button[kind="primary"] {
    background: #f8b940 !important;
    color: #0d2137 !important;
    border: none !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] button[kind="secondary"] {
    background: transparent !important;
    color: #e2e8f0 !important;
    border: 1px solid #2d4a6b !important;
}

/* ── Layout geral ────────────────────────────────────────────────── */
.main .block-container {
    max-width: 1400px;
    padding-top: 1.5rem;
}

/* ── Cabeçalho do painel ─────────────────────────────────────────── */
.painel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.5rem;
}
.painel-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0d2137;
    margin: 0;
}

/* ── KPI global bar ──────────────────────────────────────────────── */
.kpi-bar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.kpi-chip {
    background: #f0f4f8;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.82rem;
    color: #334155;
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 110px;
}
.kpi-chip .kpi-val {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0d2137;
    line-height: 1.2;
}
.kpi-chip.kpi-green  { border-left: 4px solid #10b981; }
.kpi-chip.kpi-yellow { border-left: 4px solid #f59e0b; }
.kpi-chip.kpi-red    { border-left: 4px solid #ef4444; }
.kpi-chip.kpi-blue   { border-left: 4px solid #3b82f6; }

/* ── Card de cliente ─────────────────────────────────────────────── */
.client-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    position: relative;
}
.client-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}
.semaforo {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    flex-shrink: 0;
}
.semaforo-green  { background: #10b981; box-shadow: 0 0 6px #10b98166; }
.semaforo-yellow { background: #f59e0b; box-shadow: 0 0 6px #f59e0b66; }
.semaforo-red    { background: #ef4444; box-shadow: 0 0 6px #ef444466; }

.client-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0d2137;
}
.client-handle {
    font-size: 0.82rem;
    color: #64748b;
    margin-left: 4px;
}
.client-score {
    margin-left: auto;
    font-size: 0.78rem;
    color: #94a3b8;
    font-weight: 600;
}

/* ── Seções internas do card ─────────────────────────────────────── */
.card-sections {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}
.card-section {
    background: #f8fafc;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.83rem;
}
.section-title {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748b;
    margin-bottom: 6px;
}
.section-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2px 0;
    color: #334155;
}
.section-val {
    font-weight: 700;
    color: #0d2137;
}
.section-val-green  { font-weight: 700; color: #10b981; }
.section-val-yellow { font-weight: 700; color: #f59e0b; }
.section-val-red    { font-weight: 700; color: #ef4444; }
.section-val-gray   { font-weight: 400; color: #94a3b8; }

/* ── Alertas ─────────────────────────────────────────────────────── */
.alert-list {
    margin-top: 10px;
}
.alert-item {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    font-size: 0.8rem;
    color: #92400e;
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 6px;
    padding: 5px 10px;
    margin-bottom: 4px;
}
.alert-item.alert-red {
    color: #991b1b;
    background: #fff1f2;
    border-color: #fca5a5;
}

/* ── Badge de status ─────────────────────────────────────────────── */
.badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 99px;
    line-height: 1.4;
}
.badge-green  { background: rgba(16,185,129,0.12); color: #065f46; }
.badge-yellow { background: rgba(245,158,11,0.12); color: #92400e; }
.badge-red    { background: rgba(239,68,68,0.12);  color: #991b1b; }
.badge-gray   { background: #f1f5f9; color: #64748b; }

/* ── Linha divisória ─────────────────────────────────────────────── */
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 12px 0; }

/* ── Filtro de busca ─────────────────────────────────────────────── */
.search-hint {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: -10px;
    margin-bottom: 12px;
}

/* ── Rodapé ──────────────────────────────────────────────────────── */
.footer {
    text-align: center;
    font-size: 0.72rem;
    color: #94a3b8;
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid #e2e8f0;
}
</style>
"""
