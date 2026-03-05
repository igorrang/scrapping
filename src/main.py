"""
CRIA Digital - Lead Scraper Actor
Scraping de PMEs no Sul do Brasil para o produto Cockpit
"""

import asyncio
import json
import re
from apify import Actor
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext

# ─── Queries por setor e cidade ───────────────────────────────────────────────
SEARCH_QUERIES = [
    # Metalúrgica
    "metalúrgica Caxias do Sul RS",
    "metalúrgica Joinville SC",
    "metalúrgica Blumenau SC",
    "indústria metalúrgica Curitiba PR",
    "metalúrgica Porto Alegre RS",

    # Alimentos
    "indústria alimentícia Caxias do Sul RS",
    "indústria alimentos Blumenau SC",
    "indústria alimentos Curitiba PR",
    "indústria alimentos Porto Alegre RS",
    "indústria alimentos Maringá PR",

    # Têxtil
    "indústria têxtil Blumenau SC",
    "indústria têxtil Joinville SC",
    "confecção têxtil Maringá PR",
    "têxtil Caxias do Sul RS",

    # Distribuição e Atacado
    "distribuidora atacado Curitiba PR",
    "distribuidora atacado Porto Alegre RS",
    "distribuidora atacado Joinville SC",
    "distribuidora atacado Londrina PR",
    "distribuidora atacado Maringá PR",

    # Construção e Incorporação
    "construtora incorporadora Florianópolis SC",
    "construtora incorporadora Curitiba PR",
    "construtora incorporadora Porto Alegre RS",
    "construtora incorporadora Joinville SC",
    "construtora Maringá PR",

    # Saúde - Clínicas
    "clínica médica Londrina PR",
    "clínica médica Maringá PR",
    "clínica médica Florianópolis SC",
    "clínica médica Joinville SC",
    "rede clínicas Porto Alegre RS",

    # Contabilidade
    "escritório contabilidade Curitiba PR",
    "escritório contabilidade Porto Alegre RS",
    "contabilidade Joinville SC",
    "contabilidade Florianópolis SC",

    # Jurídico
    "escritório advocacia Curitiba PR",
    "escritório advocacia Porto Alegre RS",
    "escritório jurídico Florianópolis SC",
    "escritório advocacia Londrina PR",
]


def extract_email(text: str) -> str | None:
    """Extrai e-mail de um texto."""
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Extrai telefone brasileiro de um texto."""
    match = re.search(r"(\(?\d{2}\)?\s?[\d\s\-]{8,13})", text)
    return match.group(0).strip() if match else None


def classify_sector(query: str) -> str:
    """Classifica o setor com base na query usada."""
    q = query.lower()
    if "metalúrg" in q:
        return "Metalúrgica"
    elif "aliment" in q:
        return "Alimentos"
    elif "têxtil" in q or "confecção" in q:
        return "Têxtil"
    elif "distribu" in q or "atacado" in q:
        return "Distribuição/Atacado"
    elif "constru" in q or "incorpor" in q:
        return "Construção/Incorporação"
    elif "clínica" in q or "saúde" in q or "médic" in q or "rede clínic" in q:
        return "Saúde"
    elif "contabil" in q:
        return "Contabilidade"
    elif "advoc" in q or "jurídic" in q:
        return "Jurídico"
    return "Outro"


def extract_city(query: str) -> str:
    """Extrai cidade da query."""
    cities = [
        "Caxias do Sul", "Joinville", "Blumenau", "Curitiba",
        "Porto Alegre", "Florianópolis", "Londrina", "Maringá"
    ]
    for city in cities:
        if city.lower() in query.lower():
            return city
    return "Sul do Brasil"


async def scrape_google_maps(context: PlaywrightCrawlingContext, query: str, max_results: int) -> list[dict]:
    """Scraping do Google Maps para uma query específica."""
    page = context.page
    results = []

    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    await page.goto(search_url, wait_until="networkidle")
    await asyncio.sleep(3)

    sector = classify_sector(query)
    city = extract_city(query)

    # Scroll para carregar mais resultados
    for _ in range(5):
        await page.keyboard.press("End")
        await asyncio.sleep(1.5)

    # Coleta links dos resultados
    place_links = await page.eval_on_selector_all(
        'a[href*="/maps/place/"]',
        "els => els.map(el => el.href)"
    )
    place_links = list(dict.fromkeys(place_links))  # remove duplicatas

    Actor.log.info(f"[{query}] Encontrados {len(place_links)} lugares. Coletando detalhes...")

    for link in place_links[:max_results]:
        try:
            await page.goto(link, wait_until="networkidle")
            await asyncio.sleep(2)

            # Nome da empresa
            name = await page.title()
            name = name.replace(" - Google Maps", "").strip()

            # Texto completo da página para extração
            page_text = await page.inner_text("body")

            # Endereço
            address_el = await page.query_selector('[data-item-id="address"]')
            address = await address_el.inner_text() if address_el else ""

            # Telefone
            phone_el = await page.query_selector('[data-item-id*="phone"]')
            phone = await phone_el.inner_text() if phone_el else extract_phone(page_text) or ""

            # Site
            website_el = await page.query_selector('[data-item-id="authority"]')
            website = await website_el.inner_text() if website_el else ""

            # Rating
            rating_el = await page.query_selector('span[aria-hidden="true"]')
            rating = await rating_el.inner_text() if rating_el else ""

            # Email (tenta extrair do texto da página)
            email = extract_email(page_text) or ""

            lead = {
                "nome_empresa": name,
                "setor": sector,
                "cidade": city,
                "endereco": address,
                "telefone": phone.strip(),
                "email": email,
                "website": website.strip(),
                "rating_google": rating,
                "numero_funcionarios": "",  # será enriquecido via LinkedIn
                "nome_socio_decisor": "",   # será enriquecido via LinkedIn
                "fonte": "Google Maps",
                "query_usada": query,
                "url_google_maps": link,
            }

            results.append(lead)
            Actor.log.info(f"  ✓ {name} | {phone} | {address[:40]}")

        except Exception as e:
            Actor.log.warning(f"  ✗ Erro ao processar {link}: {e}")
            continue

    return results


async def main():
    async with Actor:
        # ─── Input do Actor ────────────────────────────────────────────────────
        actor_input = await Actor.get_input() or {}

        max_results_per_query = actor_input.get("maxResultsPerQuery", 20)
        custom_queries = actor_input.get("customQueries", [])
        queries = custom_queries if custom_queries else SEARCH_QUERIES

        Actor.log.info(f"Iniciando scraping com {len(queries)} queries | Max por query: {max_results_per_query}")

        all_leads = []

        # ─── Crawler ────────────────────────────────────────────────────────────
        crawler = PlaywrightCrawler(
            headless=True,
            browser_type="chromium",
        )

        @crawler.router.default_handler
        async def handler(context: PlaywrightCrawlingContext):
            query = context.request.user_data.get("query", "")
            leads = await scrape_google_maps(context, query, max_results_per_query)
            all_leads.extend(leads)

        # Cria uma request por query
        requests = [
            {
                "url": f"https://www.google.com/maps/search/{q.replace(' ', '+')}",
                "userData": {"query": q}
            }
            for q in queries
        ]

        await crawler.run(requests)

        # ─── Salva no dataset do Apify ─────────────────────────────────────────
        Actor.log.info(f"\n{'='*50}")
        Actor.log.info(f"Total de leads coletados: {len(all_leads)}")
        Actor.log.info(f"{'='*50}")

        if all_leads:
            await Actor.push_data(all_leads)
            Actor.log.info("✅ Leads salvos no dataset com sucesso!")
        else:
            Actor.log.warning("⚠️ Nenhum lead encontrado. Verifique as queries.")


if __name__ == "__main__":
    asyncio.run(main())
