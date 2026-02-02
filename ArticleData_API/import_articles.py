import os
import requests
import json
import pyodbc
from urllib.parse import urlencode
from datetime import datetime, timedelta
from dotenv import load_dotenv

# KEY CONFIGURATION

DOTENV_FILE_PATH = ".env"
API_KEY_NAME = "PERIGON_API_KEY"

def load_and_verify_key():
    """
    Loads environment variables from the .env file and prints key
    """

    print(f"--- Loading Environment Variables from {DOTENV_FILE_PATH}")

    # Call load_dotenv()
    # reads the .env file and adds its variables to os.environ

    load_dotenv(DOTENV_FILE_PATH)

    # Retreive key using os.getenv()

    api_key = os.getenv(API_KEY_NAME)

    if api_key:
        # Successfully found api key.... print truncated key for verification
        print(f"✅ Success: Key '{API_KEY_NAME}' loaded.")
        print(f"   Key Value (truncated): {api_key[:5]}...")
        return api_key
    else:
        #Failure block
        print(f"❌ Error: Key '{API_KEY_NAME}' not found.")
        print("   Please ensure the .env file exists and the key name is correct.")
        return None

def generate_perigon_url():
    # Get the API key using your existing function
    api_key = load_and_verify_key()

    if api_key:
        print("\nKey is loaded and available for API calls")

    # Calculate dates to use at runtime
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)

    # Format as YYYY-MM-DD strings
    datefrom = seven_days_ago.isoformat()
    dateto = today.isoformat()
    
    base_url = "https://api.perigon.io/v1/articles/all"
    
    # Define all parameters in a dictionary
    params = {
        "language": "en",
        "from": datefrom,
        "to": dateto,
        "sortBy": "date",
        "showNumResults": "true",
        "page": 0,
        "size": 100,
        "showReprints": "false",
        "apiKey": api_key
    }
    
    # urlencode handles the formatting (e.g., adding ? and & correctly)
    query_string = urlencode(params)
    full_url = f"{base_url}?{query_string}"
    
    return full_url

def get_db_connection_string():
    """
    Loads database credentials from .env and returns a 
    formatted pyodbc connection string.
    """
    # Load the .env file
    load_dotenv(DOTENV_FILE_PATH)

    # Retrieve variables
    driver = os.getenv("DRIVER")
    server = os.getenv("SERVER_NAME")
    database = os.getenv("DATABASE_NAME")

    # Validation: Ensure all required fields exist
    if not all([driver, server, database]):
        missing = [k for k, v in {"DRIVER": driver, "SERVER": server, "DATABASE": database}.items() if not v]
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    # Construct the string
    connection_string = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )
    
    return connection_string

def process_data_into_article_table(data_input):
    # take data input and process ingested articles into ssms table

    # validate input data is valid and present
    if not data_input:
        print("ERROR: No data received to process")
        return

    articles = data_input.get('articles', [])
    if not articles:
        print("Data received, but no article data found in the payload")
        return

    connection_string = get_db_connection_string()
    if not connection_string:
        print("ERROR: Issue generating connection string... aborting")
        return
    
    # Establish connection to SSMS using the .env parameters
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print(f"Connected to database successfully...")

        # SQL Merge statement (Upsert logic)
        sql_query = """
        MERGE INTO dbo.tbl_articles AS target
        USING (SELECT ? AS URL) AS source
        ON (target.URL = source.URL)
        WHEN MATCHED THEN
            UPDATE SET 
                Title = ?, Description = ?, imageURL = ?, Domain = ?, 
                Country = ?, Language = ?, Medium = ?, PublishDate = ?, 
                Score = ?, SentimentPositive = ?, DateImported = GETDATE()
        WHEN NOT MATCHED THEN
            INSERT (Title, Description, URL, imageURL, Domain, Country, Language, Medium, PublishDate, Score, SentimentPositive)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        for art in articles:
            # Slicing logic to prevent the 1800-byte index error
            raw_url = art.get('url', '')
            safe_url = raw_url[:900] if raw_url else None
            
            # Extract data
            title = art.get('title')
            description = art.get('description')
            image_url = art.get('imageUrl')
            domain = art.get('source', {}).get('domain')
            country = art.get('country')
            language = art.get('language')
            medium = art.get('medium')
            pub_date = art.get('pubDate')
            score = art.get('score')
            sentiment_pos = art.get('sentiment', {}).get('positive')

            params = (
                safe_url, 
                title, description, image_url, domain, country, language, medium, pub_date, score, sentiment_pos,
                title, description, safe_url, image_url, domain, country, language, medium, pub_date, score, sentiment_pos
            )

            cursor.execute(sql_query, params)

        conn.commit()
        print(f"Import complete. Processed {len(articles)} articles.")

    except Exception as e:
        print(f"A database error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def get_articles_by_date():
    # Gather article data for specified date range
    api_url = generate_perigon_url()

    headers = {
        "Content-Type": "application/json"
    }

    try:
        #Make the API request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        #
        data_output= response.json()

        # Print information about the response for debugging purposes
        print(f"Success! Found {len(data_output.get('articles', []))} articles.")

        # for the real api, we are going to write data directly to table
        # call function to act on data_output variable and process it into database
        process_data_into_article_table(data_output)
    except Exception as e:
        print(f"API Request failed... {e}")


def test_api_call ():

    # Request URL with user-selected parameters
    # We will add logic to append api key from .env file
    url = OS.getenv("TEST_URL")

    headers = {
      "Content-Type": "application/json"
    }

    # Make the API request
    response = requests.get(url, headers=headers)

    # 
    data = response.json()

    # write response to output file for storage
    write_response_to_file(response, 'perigon_articles.json')

    formatted_response = json.dumps(response.json(), indent=4)

    # Print information about the response for debugging purposes
    print(f"Success! Found {len(data.get('articles', []))} articles.")

def clear_file_if_populated (filename):
    ## clear data out of file if data already exists
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'w') as f:
            pass
        print(f"Cleared {filename}")


def write_response_to_file (output, filename):
    ## if output is empty do nothing
    clear_file_if_populated(filename)

    ## add logic to check if the file is currently populated with data
    ## if there was data, truncate file.

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output.json(), f, indent=4)

   

if __name__ == "__main__":
    ## perigon_key = load_and_verify_key()
 
    ## if perigon_key:
    ##     print("\nKey is loaded and available for API calls")
 
    ## we will eventually set this to poll every 30 minutes, and run a live container

    get_articles_by_date()