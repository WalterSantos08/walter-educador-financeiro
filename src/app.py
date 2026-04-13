import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# =========================
# CONFIGURAÇÕES
# =========================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "qwen2.5:1.5b"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

PERFIL_PATH = DATA_DIR / "perfil_investidor.json"
TRANSACOES_PATH = DATA_DIR / "transacoes.csv"
HISTORICO_PATH = DATA_DIR / "historico_atendimento.csv"
PRODUTOS_PATH = DATA_DIR / "produtos_financeiros.json"

# =========================
# CONFIG DA PÁGINA
# =========================
st.set_page_config(
    page_title="Walter, seu Educador Financeiro",
    page_icon="💰",
    layout="wide",
)

# =========================
# FUNÇÕES DE LEITURA
# =========================
def carregar_perfil():
    with open(PERFIL_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def carregar_transacoes():
    return pd.read_csv(TRANSACOES_PATH)


def carregar_historico():
    return pd.read_csv(HISTORICO_PATH)


def carregar_produtos():
    with open(PRODUTOS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================
# FUNÇÕES AUXILIARES
# =========================
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def obter_apenas_saidas(df):
    return df[df["tipo"].str.lower() == "saida"].copy()


def calcular_metricas(df_transacoes):
    df_saidas = obter_apenas_saidas(df_transacoes)

    total_entradas = df_transacoes.loc[
        df_transacoes["tipo"].str.lower() == "entrada", "valor"
    ].sum()

    total_saidas = df_saidas["valor"].sum()
    saldo = total_entradas - total_saidas
    quantidade_transacoes = len(df_transacoes)

    if not df_saidas.empty:
        gastos_categoria = (
            df_saidas.groupby("categoria", as_index=False)["valor"]
            .sum()
            .sort_values(by="valor", ascending=False)
        )
        maior_categoria = gastos_categoria.iloc[0]["categoria"]
        maior_valor_categoria = gastos_categoria.iloc[0]["valor"]
    else:
        gastos_categoria = pd.DataFrame(columns=["categoria", "valor"])
        maior_categoria = "N/A"
        maior_valor_categoria = 0.0

    return {
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "saldo": saldo,
        "quantidade_transacoes": quantidade_transacoes,
        "maior_categoria": maior_categoria,
        "maior_valor_categoria": maior_valor_categoria,
        "gastos_categoria": gastos_categoria,
    }


def montar_contexto(perfil, transacoes, historico, produtos):
    return f"""
DADOS DO CLIENTE
Nome: {perfil.get('nome', 'Não informado')}
Idade: {perfil.get('idade', 'Não informado')}
Profissão: {perfil.get('profissao', 'Não informado')}
Renda mensal: {perfil.get('renda_mensal', 0)}
Perfil de investidor: {perfil.get('perfil_investidor', 'Não informado')}
Objetivo principal: {perfil.get('objetivo_principal', 'Não informado')}
Patrimônio total: {perfil.get('patrimonio_total', 0)}
Reserva de emergência atual: {perfil.get('reserva_emergencia_atual', 0)}
Aceita risco: {perfil.get('aceita_risco', False)}
Metas: {json.dumps(perfil.get('metas', []), ensure_ascii=False, indent=2)}

TRANSAÇÕES RECENTES
{transacoes.to_string(index=False)}

HISTÓRICO DE ATENDIMENTO
{historico.to_string(index=False)}

PRODUTOS FINANCEIROS DISPONÍVEIS PARA EXPLICAÇÃO
{json.dumps(produtos, ensure_ascii=False, indent=2)}
"""


SYSTEM_PROMPT = """
Você é Walter, seu Educador Financeiro.

Seu papel é ajudar pessoas a entender melhor suas finanças pessoais de forma simples, educativa, segura e contextualizada.

OBJETIVO:
- Explicar conceitos financeiros de forma clara e acessível;
- Usar os dados do cliente como exemplo prático;
- Ajudar o usuário a interpretar gastos, hábitos financeiros e metas;
- Fazer simulações simples quando fizer sentido.

REGRAS IMPORTANTES:
- Responda sempre em português do Brasil;
- Use linguagem simples, amigável e direta;
- Explique como se estivesse ensinando um iniciante;
- Não recomende investimentos específicos;
- Não atue como consultor financeiro profissional;
- Não invente informações;
- Se faltar algum dado, diga isso com clareza;
- Se a pergunta estiver fora de finanças pessoais, lembre educadamente que seu foco é educação financeira;
- Sempre que possível, use os dados do cliente para personalizar a resposta;
- Prefira respostas objetivas, com no máximo 3 parágrafos curtos;
- Quando útil, termine perguntando se o usuário quer que você aprofunde a explicação.

EXEMPLOS DO QUE VOCÊ PODE FAZER:
- Explicar o que é CDI, Selic, CDB, Tesouro Selic, LCI, LCA, FII;
- Mostrar em qual categoria o usuário gasta mais;
- Explicar o que é reserva de emergência;
- Calcular uma simulação educativa simples;
- Ajudar a interpretar padrões de gastos.
"""


def chamar_ollama(pergunta_usuario, contexto, historico_chat):
    prompt = f"""
{SYSTEM_PROMPT}

CONTEXTO DO CLIENTE:
{contexto}

HISTÓRICO DA CONVERSA ATUAL:
{historico_chat}

PERGUNTA DO USUÁRIO:
{pergunta_usuario}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        if response.status_code != 200:
            return f"Erro do Ollama ({response.status_code}): {response.text}"

        data = response.json()
        return data.get("response", "Não consegui gerar uma resposta agora.")

    except requests.exceptions.ConnectionError:
        return (
            "Não consegui me conectar ao Ollama. Verifique se ele está rodando com `ollama serve` "
            "e se o modelo foi baixado corretamente."
        )
    except requests.exceptions.Timeout:
        return "A resposta demorou mais que o esperado. Tente novamente em instantes."
    except Exception as e:
        return f"Ocorreu um erro ao gerar a resposta: {str(e)}"


def montar_historico_chat(messages):
    linhas = []
    for msg in messages:
        role = "Usuário" if msg["role"] == "user" else "Assistente"
        linhas.append(f"{role}: {msg['content']}")
    return "\n".join(linhas)


# =========================
# CARREGAR DADOS
# =========================
perfil = carregar_perfil()
transacoes = carregar_transacoes()
historico = carregar_historico()
produtos = carregar_produtos()

metricas = calcular_metricas(transacoes)
contexto = montar_contexto(perfil, transacoes, historico, produtos)

# =========================
# ESTILO
# =========================
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            color: #6b7280;
            margin-bottom: 1.2rem;
        }
        .box-destaque {
            padding: 1rem;
            border-radius: 12px;
            background-color: #f5f7fb;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# CABEÇALHO
# =========================
st.markdown('<div class="main-title">💰 Walter, seu Educador Financeiro</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Seu assistente virtual para aprender a cuidar melhor do seu dinheiro.</div>',
    unsafe_allow_html=True,
)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("👤 Seu Perfil Financeiro")
st.sidebar.write(f"**Nome:** {perfil.get('nome', 'Não informado')}")
st.sidebar.write(f"**Idade:** {perfil.get('idade', 'Não informado')} anos")
st.sidebar.write(f"**Profissão:** {perfil.get('profissao', 'Não informado')}")
st.sidebar.write(f"**Renda mensal:** {formatar_moeda(perfil.get('renda_mensal', 0))}")
st.sidebar.write(f"**Perfil:** {perfil.get('perfil_investidor', 'Não informado').title()}")
st.sidebar.write(f"**Objetivo:** {perfil.get('objetivo_principal', 'Não informado')}")
st.sidebar.write(f"**Patrimônio:** {formatar_moeda(perfil.get('patrimonio_total', 0))}")
st.sidebar.write(
    f"**Reserva atual:** {formatar_moeda(perfil.get('reserva_emergencia_atual', 0))}"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Metas")
for meta in perfil.get("metas", []):
    st.sidebar.write(
        f"- **{meta.get('meta', 'Meta')}**: {formatar_moeda(meta.get('valor_necessario', 0))} até {meta.get('prazo', 'N/A')}"
    )

# =========================
# MÉTRICAS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Entradas", formatar_moeda(metricas["total_entradas"]))
col2.metric("Saídas", formatar_moeda(metricas["total_saidas"]))
col3.metric("Saldo", formatar_moeda(metricas["saldo"]))
col4.metric("Transações", metricas["quantidade_transacoes"])

st.markdown("### 📊 Visão rápida")
col5, col6 = st.columns([1.3, 1])

with col5:
    if not metricas["gastos_categoria"].empty:
        st.bar_chart(
            metricas["gastos_categoria"].set_index("categoria")["valor"]
        )
    else:
        st.info("Ainda não há gastos para exibir no gráfico.")

with col6:
    st.markdown('<div class="box-destaque">', unsafe_allow_html=True)
    st.write("**Maior categoria de gasto**")
    st.write(metricas["maior_categoria"].title() if metricas["maior_categoria"] != "N/A" else "N/A")
    st.write(formatar_moeda(metricas["maior_valor_categoria"]))
    st.markdown("</div>", unsafe_allow_html=True)

    if metricas["maior_categoria"] != "N/A":
        st.info(
            f"Você está gastando mais com **{metricas['maior_categoria']}**. Posso te ajudar a entender esse padrão melhor."
        )

# =========================
# PERGUNTAS RÁPIDAS
# =========================
st.markdown("### 💡 Perguntas que você pode fazer")
q1, q2, q3, q4 = st.columns(4)

if q1.button("Quanto eu gasto com alimentação?"):
    st.session_state["pergunta_rapida"] = "Quanto eu gasto com alimentação?"

if q2.button("Como montar reserva de emergência?"):
    st.session_state["pergunta_rapida"] = "Como montar uma reserva de emergência?"

if q3.button("Quanto sobra por mês?"):
    st.session_state["pergunta_rapida"] = "Com base nos meus dados, quanto sobra por mês?"

if q4.button("O que é renda fixa?"):
    st.session_state["pergunta_rapida"] = "O que é renda fixa?"

# =========================
# HISTÓRICO DO CHAT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Olá. Eu sou o Walter, seu educador financeiro. Posso te ajudar a entender seus gastos, produtos financeiros e metas de forma simples. Sobre o que você quer conversar hoje?"
        }
    ]

if "pergunta_rapida" in st.session_state and st.session_state["pergunta_rapida"]:
    pergunta_disparada = st.session_state["pergunta_rapida"]
    st.session_state.messages.append({"role": "user", "content": pergunta_disparada})

    historico_chat = montar_historico_chat(st.session_state.messages)
    resposta = chamar_ollama(pergunta_disparada, contexto, historico_chat)

    st.session_state.messages.append({"role": "assistant", "content": resposta})
    st.session_state["pergunta_rapida"] = None

st.markdown("### 💬 Conversa")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

pergunta = st.chat_input("Digite sua dúvida sobre finanças pessoais...")

if pergunta:
    st.session_state.messages.append({"role": "user", "content": pergunta})

    with st.chat_message("user"):
        st.write(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Walter está pensando..."):
            historico_chat = montar_historico_chat(st.session_state.messages)
            resposta = chamar_ollama(pergunta, contexto, historico_chat)
            st.write(resposta)

    st.session_state.messages.append({"role": "assistant", "content": resposta})