# 💰 Walter - Educador Financeiro Inteligente

> Assistente virtual com IA que ensina conceitos de finanças pessoais de forma simples e personalizada, utilizando os dados do próprio usuário como exemplos práticos.

---

## 💡 O Que é o Walter?

O Walter é um educador financeiro virtual que **ensina**, não recomenda.  
Ele explica conceitos como reserva de emergência, tipos de investimento e análise de gastos com uma abordagem clara, prática e baseada nos dados do usuário.

---

## ✅ O que o Walter faz

- Explica conceitos financeiros de forma simples  
- Usa dados do usuário como exemplos reais  
- Responde dúvidas sobre produtos financeiros  
- Analisa padrões de gastos de forma educativa  
- Apresenta métricas e gráficos financeiros  

---

## ❌ O que o Walter NÃO faz

- Não recomenda investimentos específicos  
- Não acessa dados bancários sensíveis  
- Não substitui um profissional certificado  

---

## 🏗️ Arquitetura

```mermaid
flowchart TD
    A[Usuário] --> B[Interface Streamlit]
    B --> C[Ollama - LLM Local]
    C --> D[Base de Conhecimento (JSON/CSV)]
    D --> C
    C --> E[Resposta Educativa]

**Stack:**
Interface: Streamlit
IA: Ollama (modelo local qwen2.5:1.5b)
Dados: JSON/CSV mockados
Backend: Python

## 📁 Estrutura do Projeto

```
├── data/                          # Base de conhecimento
│   ├── perfil_investidor.json     # Perfil do usuário
│   ├── transacoes.csv             # Histórico financeiro
│   ├── historico_atendimento.csv  # Interações anteriores
│   └── produtos_financeiros.json  # Produtos para ensino
│
├── docs/                          # Documentação completa
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
│
└── src/
    └── app.py                     # Aplicação principal (Streamlit)
```

## 🚀 Como Executar

### 1. Instalar Ollama

```bash
# Baixar em: ollama.com
ollama pull qwen2.5:1.5b
ollama serve
```

### 2. Instalar Dependências

```bash
pip install streamlit pandas requests
```

### 3. Rodar o Edu

```bash
streamlit run src/app.py
```

## 🎯 Exemplo de Uso

**Pergunta:** "O que é CDI?"  
**Walter:** "CDI é uma taxa usada pelos bancos para empréstimos entre si. Quando um investimento rende 100% do CDI, significa que ele acompanha essa taxa. Geralmente, o CDI fica próximo da taxa Selic. Quer que eu te explique a diferença entre CDI e Selic?"

**Pergunta:** "Onde estou gastando mais?"  
**Walter:** "Analisando seus dados, sua maior categoria de gasto está concentrada em moradia, seguida por alimentação. Isso representa a maior parte das suas despesas mensais. Esse padrão é comum. Quer que eu te mostre formas simples de organizar melhor esses gastos?"

## 📊 Métricas de Avaliação

| Métrica | Objetivo |
|---------|----------|
| **Assertividade** | O assistente responde corretamente? |
| **Segurança** | Evita inventar informações? |
| **Coerência** | A resposta é adequada ao perfil do cliente? |

## 🎬 Diferenciais

- **Personalização:** Usa os dados do próprio cliente nos exemplos
- **100% Local:** Roda com Ollama, sem enviar dados para APIs externas
- **Educativo:** Foco em ensinar, não em vender produtos
- **Seguro:** Estratégias de anti-alucinação documentadas

## 📝 Documentação Completa

Toda a documentação técnica, estratégias de prompt e casos de teste estão disponíveis na pasta [`docs/`](./docs/).
