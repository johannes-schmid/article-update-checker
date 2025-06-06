# Article Update Checker with OpenAI and Web Search
# Requirements:
# - openai (with GPT-4o)
# - use of a web search tool (via OpenAI web tool or SerpAPI/Bing if external)
# - requests (for link validation)

from openai import OpenAI
import urllib3
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
import os
import requests
import re
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import sqlite3

def get_articles_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM articles")
    articles = cursor.fetchall()
    conn.close()
    return articles


def search_web_for_claim(claim):
    try:
        response = client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search_preview"}],
            input=f"""Find the most recent information about the following content and return only if there's anything outdated or that clearly needs updating. Be specific and avoid generic advice.

Return in this format:
• Outdated Information: [original]
• Updated Information: [your version] [Source](https://...)
• Suggestion: [short actionable advice]

Here is the content:
{claim}"""
        )
        return response.output_text
    except Exception as e:
        return f"[Web Search Error] {e}"


def check_links_in_text(text):
    urls = re.findall(r'https?://\S+', text)
    dead_links = []
    for url in urls:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code >= 400:
                dead_links.append((url, response.status_code))
        except requests.RequestException:
            dead_links.append((url, 'timeout or error'))
    return dead_links


def suggest_updates(claim, current_info):
    prompt = f"The following claim might be outdated: '{claim}'. Here is newer info: '{current_info}'. Suggest an updated version of the claim."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def save_suggestion(db_path, article_id, title, suggestion):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            title TEXT,
            suggestion TEXT
        )
    """)
    cursor.execute("INSERT INTO article_reviews (article_id, title, suggestion) VALUES (?, ?, ?)",
                   (article_id, title, suggestion))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    db_path = "articles.db"  # Update path if needed
    review_db_path = "article_reviews.db"
    articles = get_articles_from_db(db_path)
    print(f"✅ Found {len(articles)} articles in the database.")

    for article_id, title, content in articles:
        print(f"\nReviewing article '{title}' (ID: {article_id})...\n")
        updated_info = search_web_for_claim(content)

        print("⸻\n\nArticle Update Summary:\n")
        if "No updated info found" in updated_info:
            print("Article up to date.")
        else:
            print(updated_info)

        if "Outdated Information" in updated_info:
            suggestions = updated_info.split("• Outdated Information:")
            for s in suggestions[1:]:
                save_suggestion(
                    review_db_path,
                    article_id,
                    title,
                    "• Outdated Information:" + s.strip()
                )

        print("\nChecking links...")
        broken_links = check_links_in_text(content)
        if broken_links:
            print("Dead Links Found:")
            for link, status in broken_links:
                print(f"{link} — Status: {status}")
        else:
            print("No dead links detected.")