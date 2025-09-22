from django import template
import json
from django.utils.html import strip_tags
from django.conf import settings

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


@register.simple_tag(takes_context=True)
def services_jsonld(context, services):
    """Render Service schema JSON-LD for a list/queryset of services.
    Produces Service objects and includes provider information from settings/context.
    """
    try:
        request = context.get('request')
        site_name = context.get('SITE_NAME') or ''
        provider = {
            "@type": "Organization",
            "name": site_name,
        }
        # URL
        if request:
            provider["url"] = request.build_absolute_uri('/')

        # Optional fields from settings (or context) to enrich provider metadata
        phone = getattr(settings, 'SITE_PHONE', None) or context.get('SITE_PHONE')
        logo = getattr(settings, 'SITE_LOGO', None) or context.get('SITE_LOGO')
        sameas = getattr(settings, 'SITE_SAMEAS', None) or context.get('SITE_SAMEAS')
        address = getattr(settings, 'SITE_ADDRESS', None) or context.get('SITE_ADDRESS')

        if phone:
            provider['telephone'] = phone

        if logo:
            # Make logo absolute if possible
            if request and not (logo.startswith('http://') or logo.startswith('https://')):
                try:
                    provider['logo'] = request.build_absolute_uri(logo)
                except Exception:
                    provider['logo'] = logo
            else:
                provider['logo'] = logo

        if sameas:
            # normalize to list
            if isinstance(sameas, str):
                provider['sameAs'] = [sameas]
            elif isinstance(sameas, (list, tuple)):
                provider['sameAs'] = list(sameas)

        if address:
            # address can be a simple string or a dict with structured fields
            if isinstance(address, str):
                provider['address'] = {
                    "@type": "PostalAddress",
                    "streetAddress": address,
                }
            elif isinstance(address, dict):
                # copy known keys if present
                pa = {"@type": "PostalAddress"}
                for k in ('streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry'):
                    if k in address and address[k]:
                        pa[k] = address[k]
                provider['address'] = pa

        items = []
        for s in services:
            title = getattr(s, 'title', '') if not isinstance(s, dict) else s.get('title', '')
            desc = getattr(s, 'description', '') if not isinstance(s, dict) else s.get('description', '')
            items.append({
                "@type": "Service",
                "name": title,
                "description": strip_tags(desc),
            })

        data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Service",
                    "serviceType": [it.get('name') for it in items]
                },
                {
                    "@type": "Service",
                    "provider": provider,
                    "hasOfferCatalog": {
                        "@type": "OfferCatalog",
                        "name": site_name + " Services",
                        "itemListElement": items
                    }
                }
            ]
        }
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return ""
