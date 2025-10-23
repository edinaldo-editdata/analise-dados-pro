<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# SPC Statistical Process Control Analyzer (Vite + React)

Aplicação web feita com Vite + React para análise estatística e visualização (SPC).

## Rodar localmente

Pré-requisitos: `Node.js`

1. Instale dependências: `npm install`
2. Defina `GEMINI_API_KEY` em [.env.local](.env.local)
3. Inicie o servidor: `npm run dev`

## Build e Preview

- Gerar build de produção: `npm run build`
- Visualizar o build localmente: `npm run preview`

## Deploy no GitHub Pages

Este projeto está configurado para deploy via GitHub Actions:
- `vite.config.ts` com `base: '/analise-dados-pro/'`
- Workflow em `.github/workflows/deploy.yml`

Passos:
1. Faça push para a branch `main`
2. Em `Settings > Pages`, selecione "Source: GitHub Actions"
3. Aguarde o workflow publicar `dist` automaticamente

URL esperada: `https://edinaldo-editdata.github.io/analise-dados-pro/`

## Stack

- Vite 6, React 19
- TypeScript
- Recharts

## Contribuição

Sinta-se à vontade para abrir issues e pull requests.
