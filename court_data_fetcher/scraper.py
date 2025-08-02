from playwright.sync_api import sync_playwright

def scrape_case_details(case_type, case_number, year):
    url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index&state=D&dist=9"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("🌐 Navigating to eCourts site...")
        page.goto(url)

        # Step 1: Select State
        print("🗺️ Selecting state: Haryana")
        page.wait_for_selector("select#sess_state_code", timeout=15000)
        page.select_option("select#sess_state_code", label="Haryana")
        page.wait_for_timeout(3000)

        # Step 2: Select District and trigger JS change event
        print("🏢 Selecting district: Faridabad")
        page.select_option("select#sess_dist_code", label="Faridabad")
        page.evaluate("""
            const e = new Event('change', { bubbles: true });
            document.querySelector('#sess_dist_code').dispatchEvent(e);
        """)

        # Step 3: Retry loading Court Complex up to 3 times
        court_found = False
        for attempt in range(3):
            try:
                print(f"⏳ Attempt {attempt+1} to load court complex...")
                page.wait_for_selector("select#court_code", timeout=15000)
                court_options = page.locator("select#court_code option").all_text_contents()
                print("Court Complex Options:", court_options)

                if any("District Court, Faridabad" in opt for opt in court_options):
                    page.select_option("select#court_code", label="District Court, Faridabad")
                    court_found = True
                    print("✅ Selected court complex.")
                    break
                else:
                    print("⚠️ 'District Court, Faridabad' not found. Retrying...")
            except Exception as e:
                print(f"⚠️ Exception: {e}. Waiting and retrying...")
                page.wait_for_timeout(4000)

        if not court_found:
            print("❌ Could not load 'District Court, Faridabad' after 3 attempts.")
            with open("page_debug.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            browser.close()
            return {"error": "Court complex not found after retries"}, None

        # Step 4: Click on 'Case Number' tab
        print("📄 Opening 'Case Number' tab...")
        case_tab = page.get_by_role("tab", name="Case Number")
        case_tab.click(force=True)
        page.wait_for_timeout(1000)
        case_tab.click(force=True)
        page.wait_for_timeout(2000)

        # Step 5: Fill in form
        print("🧾 Filling form fields...")
        page.wait_for_selector("select#case_type", timeout=15000)
        page.wait_for_selector("input#case_number", timeout=15000)
        page.wait_for_selector("input#case_year", timeout=15000)

        page.evaluate(f'''
            var sel = document.querySelector('#case_type');
            sel.value = "{case_type}";
            sel.dispatchEvent(new Event('change'));
        ''')

        page.evaluate("document.querySelector('#case_number').style.display = 'block';")
        page.evaluate("document.querySelector('#case_year').style.display = 'block';")

        page.fill("input#case_number", case_number)
        page.fill("input#case_year", year)

        print("🔐 Solve CAPTCHA manually in browser, then press ENTER...")
        input()

        # Step 6: Submit
        print("🚀 Submitting form...")
        page.click("input[type='submit']")
        page.wait_for_timeout(5000)

        # Step 7: Extract results
        print("📥 Scraping case details...")
        html = page.content()

        try:
            result = {
                "Parties": page.locator("xpath=//td[contains(text(), 'Petitioner')]/following-sibling::td").inner_text(timeout=5000),
                "Filing Date": page.locator("xpath=//td[contains(text(), 'Filing')]/following-sibling::td").inner_text(timeout=5000),
                "Next Hearing": page.locator("xpath=//td[contains(text(), 'Next Hearing')]/following-sibling::td").inner_text(timeout=5000),
                "PDF Link": page.locator("a[href$='.pdf']").get_attribute('href') or "Not Available"
            }
        except:
            result = {
                "Parties": "",
                "Filing Date": "",
                "Next Hearing": "",
                "PDF Link": "Not Available"
            }

        browser.close()
        return result, html
