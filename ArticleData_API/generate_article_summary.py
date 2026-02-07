from db_config import get_db_connection_string
import trafilatura
from playwright.sync_api import sync_playwright
import pyodbc
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re

SUMMARYLENGTH_SENTENCES = 4

# One-time download of necessary data
nltk.download('punkt')
nltk.download('stopwords')

def get_article_to_summarize():
    # this function will return the key variables around an article to summarize

    connection_string = get_db_connection_string()
    article_data = None

    # this variable is for debugging purposes only, we grab unsummarized article by id when debugging errors
    # comma tells compiler that the value inside of the parenthesis is a tuple, best for multiple parameters
    # cursor.execute("{CALL dbo.usp_GetUnsummarizedArticle_byID (?)}", (target_id,))
    # target_id = 563

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            print("Querying Database...")
            cursor.execute("{CALL dbo.usp_GetUnsummarizedArticle}")
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
            ## page.screenshot(path="debug.png")
            ## print("📸 Debug screenshot saved as debug_view.png")

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

def get_article_summary(text, title, summarylength):
    # summarize article text
    # passes in summary length in sentences
    print('\nSummarizing article...')

    # Split text into sentences
    sentences = sent_tokenize(text)

    print(f'Found {len(sentences)} sentences...')

    if len(sentences) <= summarylength:
        # if the text is already less than the length of summary we are looking for, return
        return text

    # Build Word Frequency Map.... CLEAN
    # hash table of stop words
    stop_words = set(stopwords.words('english'))

    print(f'Retreived {len(stop_words)} stop words')

    # strip words from text... in lowercase
    words = word_tokenize(text.lower())

    # track frequency of words
    # only count alphanumeric words that arent in our stop words list
    freq_table = Counter(word for word in words if word.isalnum() and word not in stop_words)

    # Score Sentences
    sentence_scores = {}

    for i, sentence in enumerate(sentences):
        sentence_word_count = 0

        for word in word_tokenize(sentence.lower()):
            if word in freq_table:

                sentence_word_count += 1

                if sentence not in sentence_scores:
                    sentence_scores[sentence] = freq_table[word]
                else:
                    sentence_scores[sentence] += freq_table[word]

        # Normalizing score by sentence length
        # Doing this to make sure we dont allow long sentences in summary by default

        if sentence in sentence_scores:
            if sentence_word_count > 0:
                sentence_scores[sentence] = sentence_scores[sentence] / sentence_word_count

        # Edmunson Cues

        # Position Bonus: Boost the first 3 sentences
        if i < 3:
            sentence_scores[sentence] *= 2.0

        # Title Bonus: Boost sentences that share words with the title
        title_words = [w.lower() for w in word_tokenize(title) if w.isalnum()]

        # Loop through each word in title
        for tw in title_words:
            # is the title word in the sentence?
            if tw in sentence.lower():
                sentence_scores[sentence] += 5

    # Pick top Sentences
    import heapq
    summary_sentences = heapq.nlargest(summarylength, sentence_scores, key=sentence_scores.get)

    # Sort back into original order so the summary flows naturally

    summary_sentences.sort(key=lambda s: sentences.index(s))

    return " ".join(summary_sentences)

def update_article_summary(article_id, article_summary):
    # Update summary in database table

    # init variables
    connection_string = get_db_connection_string()
    sql_call = "{CALL dbo.usp_UpdateArticleSummary_byID (?, ?)}"
    parameters = (article_id, article_summary)

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            print("Querying Database...")

            # call process to update generatedsummary in db table
            cursor.execute(sql_call, parameters)
            # commit date
            conn.commit()
            print(f"✅ Summary saved for ID: {article_id}")

    except Exception as e:
        print(f"❌ Posting Error: {e}")







def main():
    # main logic

    print("="*40)
    print("       Generating article summary...")
    print("="*40)

    count = 0
    while True:
        # Fecth article data that doesnt have a generated summary
        article = get_article_to_summarize()

        if not article:
            print(f"\n✅ All caught up! Total articles summarized: {count}")
            break

        print("-" * 40)
        print("\n Ready for next steps...")
        # initialize all missing variables required for the summary generation
        article_title = article['title']
        # Scrape article text
        print("\n📝 SCRAPING CONTENT...")
        article_text = get_article_text(article['url'])
        
        if article_text:
            # Get article summary
            article_summary = get_article_summary(article_text, article_title, SUMMARYLENGTH_SENTENCES)
            # Update summary in db table
            update_article_summary(article['id'], article_summary)   
            count += 1
        else:
            # Important: If scraping fails, we need to mark it so it doesn't loop forever
            # For now, we'll just print a warning.
            print(f"⚠️ Skipping ID {article['id']} - No text could be scraped.")       

    

if __name__ == "__main__":
    main()


