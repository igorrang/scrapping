# CRIA Digital - Lead Scraper 🚀

Scraper de PMEs no Sul do Brasil para prospecção do **Cockpit - Inteligência Unificada**.

---

## 📋 O que ele coleta

| Campo | Fonte |
|---|---|
| Nome da empresa | Google Maps |
| Setor | Classificado automaticamente |
| Cidade | Extraído da query |
| Endereço | Google Maps |
| Telefone/WhatsApp | Google Maps |
| E-mail | Google Maps (quando disponível) |
| Website | Google Maps |
| Rating Google | Google Maps |

---

## 🚀 Como subir na Apify

### Opção 1 — Via Apify CLI (recomendado)

```bash
# 1. Instale a CLI
npm install -g apify-cli

# 2. Login
apify login

# 3. Na pasta do projeto
apify push
```

### Opção 2 — Via GitHub

1. Suba este projeto em um repositório GitHub
2. Na Apify, crie um novo Actor → **"Link to GitHub"**
3. Conecte o repositório
4. Clique em **Build & Run**

---

## ⚙️ Configurações de Input

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `maxResultsPerQuery` | 20 | Quantos leads por busca |
| `customQueries` | [] | Deixe vazio para usar as 36 queries padrão do ICP |

---

## 📊 Queries padrão incluídas

O script já vem com **36 queries** cobrindo:
- 8 cidades: Porto Alegre, Florianópolis, Curitiba, Joinville, Caxias do Sul, Blumenau, Londrina, Maringá
- 7 setores: Metalúrgica, Alimentos, Têxtil, Distribuição/Atacado, Construção, Saúde, Contabilidade/Jurídico

**Estimativa: 400–700 leads por execução**

---

## 💾 Exportar os dados

Após a execução, na Apify vá em:
**Storage → Dataset → Export → CSV ou Excel**

---

## 💡 Dica de enriquecimento

Após exportar, use o **Apollo.io** ou **Hunter.io** para:
- Encontrar e-mail do decisor (dono/sócio)
- Confirmar número de funcionários
- Buscar perfil LinkedIn do CEO
