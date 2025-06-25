import os
import streamlit as st
import google.generativeai as genai
import requests

# === API Keys ===
GEMINI_API_KEY = "AIzaSyB-S2AERhYS7YPCs3ETnrK4A0ne-XeB8Lc"
RAPIDAPI_KEY = "30519c4941mshc4a0ea1fc7107d7p17bac2js"
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
            # === Call Crunchbase4 API ===
            url = "https://crunchbase4.p.rapidapi.com/company"
            payload = { "company_domain": startup_domain }
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

            # === Extract fields ===
            bio = data.get("bio", "No description available.")
            category = data.get("category", "N/A")
            valuation = data.get("valuation", "N/A")
            location = data.get("location", "N/A")
            name = data.get("company_name", startup_domain)

            # === Format summary text nicely ===
            summary_text = f"""
**Company Name:** {name}  
**Industry:** {category}  
**Location:** {location}  
**Valuation:** {valuation}  

**Description:**  
{bio}
"""

            # === Generate and display Gemini response ===
            if bio != "No description available.":
                gemini_prompt = (
                    f"Based on the following company data, provide a VC investment analysis:\n\n{summary_text}"
                )
                gemini_response = model.generate_content(gemini_prompt)

                st.success("Analysis Complete")
                st.markdown("### Company Summary")
                st.markdown(summary_text)

                st.markdown("### Gemini VC Analysis")
                st.write(gemini_response.text)
            else:
                st.warning("⚠️ Insufficient data for meaningful analysis. Try another company.")

        except Exception as e:
            st.error(f"Error: {e}")
