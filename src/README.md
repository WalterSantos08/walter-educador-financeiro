# Passo a Passo de Execução

Este guia mostra como executar o projeto **walter-educador-financeiro** localmente.

---

## Setup do Ollama

```bash
# 1. Instalar o Ollama
# https://ollama.com/

# 2. Baixar o modelo utilizado no projeto
ollama pull qwen2.5:1.5b

# 3. Testar se o modelo está funcionando
ollama run qwen2.5:1.5b "Olá!"