"""
Q1: AI Lead Classification System for KeaBuilder
Classifies incoming leads as HOT, WARM, or COLD based on CRM form inputs
"""

import json
from datetime import datetime

TIER1_COUNTRIES = ["United States", "United Kingdom", "Canada", "Australia", "Germany", "France"]
TIER2_COUNTRIES = ["India", "Brazil", "Mexico", "Philippines", "Indonesia", "South Africa"]

HIGH_INTENT_SOURCES = ["pricing_page_funnel", "demo_request_funnel", "checkout_funnel", "free_trial_funnel"]
MEDIUM_INTENT_SOURCES = ["feature_page_funnel", "comparison_funnel", "webinar_funnel", "case_study_funnel"]
LOW_INTENT_SOURCES = ["blog_newsletter_signup", "homepage_funnel", "social_media_funnel", "general_contact_form"]


def validate_email(email):
    if not email or "@" not in email or "." not in email:
        return False
    return True


def infer_name_from_email(email):
    if not email:
        return ""
    prefix = email.split("@")[0]
    name = ''.join(c for c in prefix if c.isalpha() or c == '.')
    return name.replace('.', ' ').strip().title()


def infer_country_from_dial_code(dial_code):
    dial_map = {
        "+1": "United States", "+44": "United Kingdom",
        "+91": "India", "+61": "Australia", "+49": "Germany",
        "+33": "France", "+55": "Brazil"
    }
    return dial_map.get(dial_code, "")


def handle_incomplete_inputs(form_data):
    cleaned = form_data.copy()

    if not cleaned.get("first_name"):
        inferred = infer_name_from_email(cleaned.get("email", ""))
        cleaned["first_name"] = inferred if inferred else "there"
        cleaned["name_inferred"] = True

    if not cleaned.get("country") and cleaned.get("dial_code"):
        cleaned["country"] = infer_country_from_dial_code(cleaned["dial_code"])
        cleaned["country_inferred"] = True

    if not validate_email(cleaned.get("email", "")):
        cleaned["email_valid"] = False
        cleaned["action_required"] = "re_engagement_funnel"
    else:
        cleaned["email_valid"] = True

    return cleaned


def calculate_lead_score(form_data):
    score = {
        "contact_completeness": 0,
        "phone_provided": 0,
        "country_tier": 0,
        "funnel_intent": 0,
        "engagement": 5
    }

    filled = sum(1 for f in ["first_name", "last_name", "email", "phone", "country"] if form_data.get(f))
    if filled >= 5:
        score["contact_completeness"] = 25
    elif filled >= 3:
        score["contact_completeness"] = 15
    elif filled >= 1:
        score["contact_completeness"] = 10

    if form_data.get("phone") and form_data.get("dial_code"):
        score["phone_provided"] = 20
    elif form_data.get("phone"):
        score["phone_provided"] = 10

    country = form_data.get("country", "")
    if country in TIER1_COUNTRIES:
        score["country_tier"] = 15
    elif country in TIER2_COUNTRIES:
        score["country_tier"] = 10
    else:
        score["country_tier"] = 5

    source = form_data.get("form_source", "")
    if source in HIGH_INTENT_SOURCES:
        score["funnel_intent"] = 25
    elif source in MEDIUM_INTENT_SOURCES:
        score["funnel_intent"] = 15
    elif source in LOW_INTENT_SOURCES:
        score["funnel_intent"] = 10

    if form_data.get("returning_visitor"):
        score["engagement"] = 15

    return score


def classify_lead(form_data):
    cleaned = handle_incomplete_inputs(form_data)

    if not cleaned.get("email_valid", True):
        return {
            "lead_id": f"KB-LD-{datetime.now().strftime('%Y%m%d')}-INVALID",
            "classification": "DISCARD",
            "confidence_score": 0,
            "reasoning": "Invalid or missing email",
            "action": "trigger_re_engagement_funnel"
        }

    scores = calculate_lead_score(cleaned)
    total = sum(scores.values())

    if total >= 70:
        classification = "HOT"
        action = "Send immediate email + schedule demo"
        delay = "immediate"
        crm_list = "hot_leads"
        stage = "qualified"
    elif total >= 40:
        classification = "WARM"
        action = "Send case study email"
        delay = "1_hour"
        crm_list = "warm_leads"
        stage = "nurture"
    else:
        classification = "COLD"
        action = "Add to drip campaign"
        delay = "24_hours"
        crm_list = "newsletter_subscribers"
        stage = "awareness"

    return {
        "lead_id": f"KB-LD-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "classification": classification,
        "confidence_score": min(total, 100),
        "score_breakdown": scores,
        "total_score": total,
        "reasoning": f"Score {total}/100 based on completeness, phone, country, funnel intent",
        "priority_action": action,
        "response_config": {"send_delay": delay},
        "crm_actions": {
            "add_to_list": crm_list,
            "add_tag": cleaned.get("form_source", "general"),
            "create_opportunity": classification == "HOT",
            "pipeline_stage": stage
        }
    }


if __name__ == "__main__":
    test_leads = [
        ("HOT", {"first_name": "Sarah", "last_name": "Johnson", "email": "sarah@techcorp.com", "phone": "+1-555-0142", "dial_code": "+1", "country": "United States", "form_source": "pricing_page_funnel"}),
        ("WARM", {"first_name": "Rahul", "last_name": "", "email": "rahul.dev@gmail.com", "phone": "", "dial_code": "+91", "country": "India", "form_source": "feature_page_funnel"}),
        ("COLD", {"first_name": "", "last_name": "", "email": "random123@yahoo.com", "phone": "", "dial_code": "", "country": "", "form_source": "blog_newsletter_signup"})
    ]

    for label, lead in test_leads:
        print(f"\n{'='*40}\n{label} LEAD:")
        print(json.dumps(classify_lead(lead), indent=2))
