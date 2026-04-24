"""
Q1: AI Prompts for Lead Classification & Response Generation
"""

CLASSIFICATION_PROMPT = """
You are a lead scoring AI for KeaBuilder.
Given this form data:
- Name: {first_name} {last_name}
- Email: {email}
- Phone: {phone}
- Dial Code: {dial_code}
- Country: {country}
- Form Source: {form_source}
- Funnel: {funnel_name}

Classify as HOT, WARM, or COLD.
- HOT: Complete info + high-intent funnel + Tier-1 country
- WARM: Partial info OR medium-intent source
- COLD: Minimal info + low-intent source

Return JSON:
{{"classification": "HOT|WARM|COLD", "confidence_score": 0-100, "reasoning": "...", "priority_action": "..."}}
"""

RESPONSE_PROMPT = """
You are a friendly sales assistant for KeaBuilder.
Lead: {first_name}, Classification: {classification}, Source: {form_source}

Rules:
- HOT: Urgent demo offer, enthusiastic tone
- WARM: Case study + soft CTA, friendly tone
- COLD: Blog content, casual tone

Use first name, reference funnel source, under 150 words, sound human.

Return JSON:
{{"subject_line": "...", "email_body": "...", "cta_text": "...", "send_delay": "immediate|1_hour|24_hours"}}
"""

INCOMPLETE_INPUT_PROMPT = """
Form has incomplete data: {form_data}
Missing: {missing_fields}

Suggest what can be inferred and what follow-up action to take.
Return JSON:
{{"inferred_data": {{}}, "follow_up_action": "...", "should_process": true/false}}
"""


def format_classification_prompt(data):
    return CLASSIFICATION_PROMPT.format(
        first_name=data.get("first_name", "N/A"),
        last_name=data.get("last_name", "N/A"),
        email=data.get("email", "N/A"),
        phone=data.get("phone", "N/A"),
        dial_code=data.get("dial_code", "N/A"),
        country=data.get("country", "N/A"),
        form_source=data.get("form_source", "N/A"),
        funnel_name=data.get("funnel_name", "N/A")
    )


def format_response_prompt(data, classification):
    return RESPONSE_PROMPT.format(
        first_name=data.get("first_name", "there"),
        classification=classification,
        form_source=data.get("form_source", "general")
    )
