import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import GEMINI_API_KEY, GEMINI_MODEL_NAME, REPORTS_DIR

def generate_campaign_for_segment(segment_name="At-Risk / Inactive", favorite_category="Electronics", avg_spend=450.00, churn_risk="High Risk"):
    """
    Generates segment-tailored marketing email copy and promotional strategy using GenAI (with template fallback).
    """
    print(f"\n--- GenAI Marketing Campaign Generator for Segment: '{segment_name}' ---")
    api_key = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)

            prompt = f"""
You are an expert E-Commerce Direct Marketing Copywriter.
Generate an engaging, high-converting personalized email campaign tailored for the following customer segment:

Target Segment: {segment_name}
Average Historical Spend: ${avg_spend:.2f}
Favorite Product Category: {favorite_category}
Churn Risk Level: {churn_risk}

Output in valid Markdown with the following exact sections:
### Campaign Strategy: {segment_name}
* **Target Audience:** Description of target customer behavior.
* **Email Subject Line:** Catchy, urgent, non-spammy subject line.
* **Email Body:** Personalized 2-3 paragraph message offering value.
* **Incentive / Promo Code:** Discount or offer structure (e.g., 15% off, free express shipping).
* **Call to Action (CTA):** Clear action button text.
"""
            response = model.generate_content(prompt)
            campaign_text = response.text
            print("Campaign generated successfully using Gemini API!")

        except Exception as e:
            print(f"Gemini API call failed: {e}. Generating rule-based campaign template.")
            campaign_text = generate_template_campaign(segment_name, favorite_category, avg_spend, churn_risk)
    else:
        campaign_text = generate_template_campaign(segment_name, favorite_category, avg_spend, churn_risk)

    # Save generated campaign to reports folder
    clean_seg_filename = segment_name.lower().replace(" ", "_").replace("/", "").replace("-", "_")
    output_file = REPORTS_DIR / f"campaign_{clean_seg_filename}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(campaign_text)

    print(f"Campaign file saved to: {output_file}")
    return campaign_text

def generate_template_campaign(segment_name, favorite_category, avg_spend, churn_risk):
    if "VIP" in segment_name:
        subject = f"Exclusive VIP Perk: Preview our latest {favorite_category} collection"
        offer = "20% Exclusive Rewards Voucher + Priority Customer Support"
        body = f"As one of our premier VIP customers (with average orders around ${avg_spend:.2f}), we want to personally thank you for your loyalty. We've reserved early access for our newest arrivals in {favorite_category}."
        cta = "Access VIP Perks Now"
    elif "At-Risk" in segment_name or "Inactive" in segment_name:
        subject = f"We miss you! Here is $25 off your next {favorite_category} purchase"
        offer = "$25 Instant Credit + Free Express Shipping on orders over $50"
        body = f"We noticed it's been a while since your last visit. We've added a special credit to your account to help you get back to shopping your favorites in {favorite_category}."
        cta = "Claim My $25 Credit"
    else:
        subject = f"Special Offer on {favorite_category} just for you!"
        offer = "15% Off Your Next Order (Code: SAVE15)"
        body = f"Thank you for being a valued customer. Explore our top-rated trending products in {favorite_category} and enjoy 15% off your next purchase."
        cta = "Shop Trending Products"

    template = f"""### Campaign Strategy: {segment_name}

* **Target Audience:** Customers categorized as '{segment_name}' with {churn_risk} churn risk.
* **Email Subject Line:** {subject}

* **Email Body:**  
  Dear Customer,

  {body}

  Don't miss out on exploring our curated selections designed to bring you the best value.

  Warm regards,  
  The E-Commerce Customer Care Team

* **Incentive / Promo Code:** {offer}
* **Call to Action (CTA):** [{cta}]
"""
    return template

if __name__ == "__main__":
    generate_campaign_for_segment("At-Risk / Inactive", "Electronics", 320.00, "High Risk")
    generate_campaign_for_segment("High-Value VIPs", "Electronics", 850.00, "Low Risk")
