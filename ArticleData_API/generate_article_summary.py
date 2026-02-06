from db_config import get_db_connection_string
import trafilatura
from playwright.sync_api import sync_playwright
import pyodbc

def get_article_to_summarize():
    # this function will return the key variables around an article to summarize

    connection_string = get_db_connection_string()
    article_data = None

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            print("Querying Database...")
            cursor.execute("{CALL dbo.usp_GetUnsummarizedArticle_atRandom}")
            row = cursor.fetchone()

            if row:
                # Mapping to schema names: ArticleID, Title, URL, Domain, Language
                article_data = {
                    "id": row.ArticleID,
                    "url": row.URL,
                    "title": row.Title,
                    "domain": row.Domain,
                    "language": row.Language
                }
            else:
                print("ℹ️ No articles found that need a summary.")

    except Exception as e:
        print(f"❌ Error fetching: {e}")
    return article_data

def get_article_text (url):
    # inputs the article URL and gathers the text from it.

    try:
        print(f"🚀 Launching browser to bypass protections...")

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)

            # Mimic a real Windows Chrome user
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )

            page = context.new_page()

            #Navigate and wait for the page to stop loading data
            # wait_until="dotcomloaded" -  waits for the basic HTML has been completely downloaded and parsed into the DOM
            print(f"🌐 Navigating to: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            #SCREENSHOT DEBUG
            page.screenshot(path="debug.png")
            print("📸 Debug screenshot saved as debug_view.png")

            # wait for 3 seconds for any final JS/popups to clear
            page.wait_for_timeout(3000)

            #Grab the FULLY RENDERED HTML
            rendered_html = page.content()
            browser.close()

            # Use Trafilatura to extract clean text from the rendered HTML
            article_text = trafilatura.extract(rendered_html, favor_precision=True)

            

            # return article text, return none if article text doesnt exist
            return article_text.strip() if article_text else None
    except Exception as e:
        print(f"❌ Scraping Error: {e}")
        return None



def main():
    # main logic
    # used for testing each benchmark

    print("="*40)
    print("       ARTICLE FETCH TEST")
    print("="*40)

    # Fecth article data that doesnt have a generated summary
    article = get_article_to_summarize()

    # Display data, if it exists
    if article:
        print("\n ✅ DATA RETRIEVED SUCCESSFULLY:")
        print("-" * 40)

        # set padding variable for output formatting later
        # dynamically calculating this in case we add new columns for later
        padding = max(len(key) for key in article.keys()) + 2
        
        for key, value in article.items():
            print(f"{key:<{padding}}: {value}")

        print("-" * 40)
        print("\n Ready for next steps...")

        # Test scraping logic
        print("\n📝 TESTING... SCRAPING CONTENT...")
        test_content = get_article_text(article['url'])

        if test_content:
            print(f"✅ Successfully scraped {len(test_content)} characters.")
            print("-" * 40)
            # Show just the first 300 characters to verify it's real text
            print(test_content[:2000] + "...")
            print("-" * 40)
        else:
            print("⚠️ Trafilatura returned no text.")
    else:
        print("\n No data available to display")

if __name__ == "__main__":
    main()


