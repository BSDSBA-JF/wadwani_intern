import asyncio
from playwright.async_api import async_playwright
import pandas as pd

BASE_URL = "https://www.kalibrr.com"

async def scrape_kalibrr(keyword="finance", scrolls=10):
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # REAL browser context (important)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800}
        )

        page = await context.new_page()

        search_url = f"{BASE_URL}/job-board/search/{keyword}"

        # DO NOT use networkidle
        await page.goto(
            search_url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # wait for jobs to load
        await page.wait_for_selector("article", timeout=20000)

        prev_count = 0

        for _ in range(scrolls):
            cards = await page.query_selector_all("article")
            if len(cards) == prev_count:
                break
            prev_count = len(cards)

            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(2000)

        print(f"Total job cards loaded: {len(cards)}")

        for card in cards:
            title_el = await card.query_selector("h2")
            company_el = await card.query_selector("span")
            link_el = await card.query_selector("a")

            job_title = await title_el.inner_text() if title_el else ""
            company_name = await company_el.inner_text() if company_el else ""

            job_url = await link_el.get_attribute("href") if link_el else ""
            if job_url.startswith("/"):
                job_url = BASE_URL + job_url

            if job_title and company_name:
                jobs.append({
                    "company_name": company_name.strip(),
                    "job_title": job_title.strip(),
                    "job_url": job_url
                })

        await browser.close()

    return pd.DataFrame(jobs)

async def main():
    df = await scrape_kalibrr(keyword="finance", scrolls=12)

    if df.empty:
        print("No jobs scraped.")
        return

    company_counts = (
        df.groupby("company_name")
          .size()
          .reset_index(name="number_of_hirings")
    )

    mass_hiring = company_counts[company_counts["number_of_hirings"] > 1]

    df.to_csv("kalibrr_all_jobs.csv", index=False)
    mass_hiring.to_csv("kalibrr_mass_hiring_companies.csv", index=False)

    print("\nTop mass-hiring companies:")
    print(mass_hiring.sort_values("number_of_hirings", ascending=False).head(10))

if __name__ == "__main__":
    asyncio.run(main())
