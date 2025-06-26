import os
import streamlit as st
import google.generativeai as genai
import requests

# === API Keys ===
GEMINI_API_KEY = "AIzaSyAcdQnjmv1X2FqnPlZNWHfwSJBT5eFja8Q"
RAPIDAPI_KEY = "30519c4941mshc4a0ea1fc7107d7p17bac2jsn20a0f8415a0d"
RAPIDAPI_HOST = "crunchbase4.p.rapidapi.com"

# === Configure Gemini ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# === Streamlit UI ===
st.set_page_config(page_title="VC-Grade Startup Analyzer", layout="centered")
st.title("🚀 VC-Grade Startup Analyzer")

startup_domain = st.text_input("Enter the company's domain (e.g., openai.com):")

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

            # === Show Raw JSON ===
            st.subheader("🔎 Raw API JSON Response")
            st.json(data)

            # === Extract and format JSON from "company" object ===
            company = data.get("company", {})

            name = startup_domain
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

            # === Prompt Gemini ===
            if long_description:
                gemini_prompt = f"""
You are a venture capital analyst. Based on the following company profile, write a concise investment analysis, covering strengths, risks, and outlook:

{summary_text}
"""
                gemini_response = model.generate_content(gemini_prompt)
                safe_output = gemini_response.text.encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')

                st.markdown("### 🧠 Gemini VC Analysis")
                st.markdown(safe_output)
            else:
                st.warning("⚠️ Insufficient description data for meaningful analysis. Try another company.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
