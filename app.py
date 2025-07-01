import os
import streamlit as st
import google.generativeai as genai
import requests
from dotenv import load_dotenv
load_dotenv()

# Prefer st.secrets if available (Streamlit Cloud), otherwise fallback to .env
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", os.getenv("RAPIDAPI_KEY"))
RAPIDAPI_HOST = st.secrets.get("RAPIDAPI_HOST", os.getenv("RAPIDAPI_HOST"))
GNEWS_API_KEY = st.secrets.get("GNEWS_API_KEY", os.getenv("GNEWS_API_KEY"))

# === Configure Gemini ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# === Streamlit UI ===
st.set_page_config(page_title="Venture Capitalist Grade Startup Analyzer", layout="centered")
st.title("Venture Capitalist - Grade Startup Analyzer")

startup_domain = st.text_input("Enter the company's domain (e.g., openai.com):")

# === Fetch News Articles Unconditionally ===
def fetch_news_articles(company_name):
    try:
        url = f"https://gnews.io/api/v4/search?q={company_name}&lang=en&max=5&token={GNEWS_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("articles", [])
        else:
            return []
    except:
        return []

if st.button("Generate VC Analysis") and startup_domain:
    with st.spinner("Fetching data from Crunchbase..."):
        try:
            # === Crunchbase API Call ===
            url = "https://crunchbase4.p.rapidapi.com/company"
            payload = {"company_domain": startup_domain}
            headers = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": RAPIDAPI_HOST,
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            # === Extract and format JSON from "company" object ===
            company = data.get("company", {})

            name = startup_domain.split('.')[0].capitalize()
            about = company.get("about", "No description available.")
            founded = company.get("founded_year", "Unknown")
            funding = company.get("funding", {})
            funding_usd = funding.get("value_usd", "N/A")
            industries = ", ".join(company.get("industries", [])) or "N/A"
            location = company.get("location", "Unknown")
            size = company.get("size", "N/A")
            website = company.get("website", "N/A")
            long_description = company.get("long_description", "")

            # === Condensed Bullet Summary ===
            summary_text = f"""
### 🔍 Company Summary

- **About:** {about}
- **Founded:** {founded}
- **Funding Raised:** ${funding_usd:,} USD
- **Industries:** {industries}
- **Location:** {location}
- **Company Size:** {size}
- **Website:** [{website}]({website})

**📝 Long Description:**  
{long_description}
"""

            st.markdown(summary_text)

            # === News Section (Unfiltered) ===
            st.markdown("### 🗞️ Recent News")
            news_articles = fetch_news_articles(name)
            if news_articles:
                for article in news_articles:
                    title = article.get("title", "No title")
                    link = article.get("url", "")
                    published = article.get("publishedAt", "")
                    st.markdown(f"- [{title}]({link}) _(Published: {published[:10]})_")
            else:
                st.info("No recent news articles found.")

            # === Gemini Analysis ===
            if long_description:
                gemini_prompt = f"""
You are a venture capital analyst. Based on the following company profile, write a brief, but concise investment analysis, covering strengths, risks, and short but specific future outlook:

{summary_text}
"""
                gemini_response = model.generate_content(gemini_prompt)
                clean_output = gemini_response.text.replace('\ufffd', '').strip()

                st.markdown("### 🧠 Gemini VC Analysis")
                st.markdown(clean_output)
            else:
                st.warning("⚠️ Insufficient description data for meaningful analysis. Try another company.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
