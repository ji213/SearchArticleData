from db_config import get_db_connection_string
import pyodbc

def get_article_to_summarize():
    # this function will return the key variables around an article to summarize

    connection_string = get_db_connection_string()
    article_data = None

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
    else:
        print("\n No data available to display")

if __name__ == "__main__":
    main()


