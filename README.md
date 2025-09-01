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
