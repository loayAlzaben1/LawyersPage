from django import template
import json
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def faq_jsonld(faqs):
    """Render FAQPage JSON-LD from a list of faqs. Each item should have `q` and `a` attributes/keys.
    """
    try:
        items = []
        for item in faqs:
            q = getattr(item, 'q', '') if not isinstance(item, dict) else item.get('q', '')
            a = getattr(item, 'a', '') if not isinstance(item, dict) else item.get('a', '')
            # strip HTML from answers for JSON-LD, keep text only
            a_text = strip_tags(a)
            items.append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a_text
                }
            })
        data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": items
        }
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return ""
