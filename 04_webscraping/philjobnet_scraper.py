"""
PhilJobNet Test Script - Debug Version
Tests basic functionality step by step
"""

import asyncio
from playwright.async_api import async_playwright

async def test_philjobnet():
    print("🧪 Testing PhilJobNet Scraper\n")
    
    async with async_playwright() as p:
        # Launch browser
        print("1️⃣ Launching browser...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to job vacancies
        print("2️⃣ Loading job vacancies page...")
        await page.goto("https://philjobnet.gov.ph/job-vacancies/", wait_until="networkidle")
        await asyncio.sleep(2)
        print("   ✅ Page loaded")
        
        # Check if job table exists
        print("\n3️⃣ Checking for job listings table...")
        table_exists = await page.locator('#ctl00_BodyContentPlaceHolder_GridView1').count() > 0
        if table_exists:
            print("   ✅ Job table found")
        else:
            print("   ❌ Job table NOT found")
            await browser.close()
            return
        
        # Count job cards
        print("\n4️⃣ Counting job cards...")
        job_cards = page.locator('.jobcard')
        job_count = await job_cards.count()
        print(f"   ✅ Found {job_count} job cards")
        
        # Extract first job
        if job_count > 0:
            print("\n5️⃣ Extracting first job details...")
            first_card = job_cards.first
            
            # Get job title
            job_title = await first_card.locator('.jobtitle').inner_text()
            print(f"   Job Title: {job_title}")
            
            # Get company name
            company_name = await first_card.locator('.companytitle').inner_text()
            print(f"   Company: {company_name}")
            
            # Get salary
            salary = await first_card.locator('.salary').inner_text()
            print(f"   Salary: {salary}")
            
            # Get job URL
            job_link = first_card.locator('xpath=ancestor::a')
            job_url = await job_link.get_attribute('href')
            full_url = f"https://philjobnet.gov.ph{job_url}" if job_url.startswith('/') else job_url
            print(f"   URL: {full_url}")
            
            # Try to open job detail page
            print("\n6️⃣ Opening job detail page...")
            detail_page = await context.new_page()
            try:
                await detail_page.goto(full_url, wait_until="domcontentloaded", timeout=15000)
                print("   ✅ Detail page opened")
                
                # Get page content
                content = await detail_page.inner_text('body')
                
                # Look for vacancy info
                print("\n7️⃣ Searching for vacancy information...")
                if 'vacanc' in content.lower():
                    print("   ✅ Found word 'vacancy' in page")
                    # Print surrounding text
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'vacanc' in line.lower():
                            print(f"   Line {i}: {line.strip()}")
                else:
                    print("   ⚠️  Word 'vacancy' not found")
                
                # Look for email
                print("\n8️⃣ Searching for email...")
                if '@' in content:
                    print("   ✅ Found '@' symbol - email might be present")
                    lines = content.split('\n')
                    for line in lines:
                        if '@' in line and '.' in line:
                            print(f"   Possible email line: {line.strip()[:100]}")
                else:
                    print("   ⚠️  No '@' symbol found")
                
                # Look for phone
                print("\n9️⃣ Searching for phone number...")
                import re
                phone_match = re.search(r'(\+63|0)\s*\d{3}\s*\d{3}\s*\d{4}', content)
                if phone_match:
                    print(f"   ✅ Found phone: {phone_match.group(0)}")
                else:
                    print("   ⚠️  No phone number pattern found")
                
                await detail_page.close()
                
            except Exception as e:
                print(f"   ❌ Error opening detail page: {e}")
        
        # Test pagination
        print("\n🔟 Testing pagination...")
        page_2_link = page.locator('a:has-text("2")')
        page_2_exists = await page_2_link.count() > 0
        
        if page_2_exists:
            print("   ✅ Page 2 link found")
            print("   🔄 Clicking page 2...")
            
            await page_2_link.first.click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            # Check if page changed
            new_job_count = await page.locator('.jobcard').count()
            print(f"   ✅ Page 2 loaded with {new_job_count} jobs")
        else:
            print("   ⚠️  Page 2 link not found")
        
        print("\n✅ Test complete! Press Enter to close browser...")
        input()
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_philjobnet())