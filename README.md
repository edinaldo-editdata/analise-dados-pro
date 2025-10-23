<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

Este repositório contém tudo o que você precisa para rodar o app localmente e fazer deploy no GitHub Pages.

URL do app no AI Studio: https://ai.studio/apps/drive/1eqY2E2Fupap-YzlGf8zaVab7W6QxveXf

## Rodar localmente

Pré-requisitos: `Node.js`

1. Instale dependências: `npm install`
2. Defina `GEMINI_API_KEY` em [.env.local](.env.local)
3. Rode: `npm run dev`

## Deploy no GitHub Pages

Este projeto já está configurado para GitHub Pages:
- `vite.config.ts` com `base: '/analise-dados-pro/'`
- Workflow em `.github/workflows/deploy.yml`

Passos:
1. Faça push para a branch `main`
2. Em `Settings > Pages`, selecione "Source: GitHub Actions"
3. Aguarde o workflow publicar `dist` automaticamente

URL esperada: `https://edinaldo-editdata.github.io/analise-dados-pro/`

# 📊 Análise de Dados Pro

Uma aplicação Streamlit para análise e manipulação de dados CSV de forma interativa.

## Funcionalidades

- 📥 **Import de Dados**: Carregue arquivos CSV, TXT, Excel ou cole dados diretamente
- 🔍 **Visualização**: Explore seus datasets com interface intuitiva
- ✏️ **Edição**: Modifique dados diretamente na interface
- 📊 **Análise**: Ferramentas de análise estatística e visualização
- 💾 **Projetos**: Salve e gerencie seus projetos de análise
- 🎨 **Temas**: Interface clara ou escura

## Instalação

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd csv_editor
```

1. Instale as dependências:

```bash
pip install streamlit pandas numpy plotly
```

## Uso

Execute a aplicação:

```bash
streamlit run app.py
```

A aplicação será aberta no seu navegador em `http://localhost:8501`

## Estrutura do Projeto

csv_editor/ ├── app.py # Aplicação principal ├── projects/ # Projetos salvos (.pkl) ├── README.md # Este arquivo └── .gitignore # Arquivos ignorados pelo Git

## Dependências

- streamlit
- pandas
- numpy
- plotly
- openpyxl (para arquivos Excel)

## Contribuição

Sinta-se à vontade para contribuir com melhorias e correções!
