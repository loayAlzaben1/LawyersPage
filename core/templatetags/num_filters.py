from django import template

register = template.Library()

ARABIC_INDIC = {
    '0': '\u0660',
    '1': '\u0661',
    '2': '\u0662',
    '3': '\u0663',
    '4': '\u0664',
    '5': '\u0665',
    '6': '\u0666',
    '7': '\u0667',
    '8': '\u0668',
    '9': '\u0669',
}


@register.filter
def arabic_indic(value):
    """Convert Western digits in a string/number to Arabic-Indic digits."""
    s = str(value)
    return ''.join(ARABIC_INDIC.get(ch, ch) for ch in s)


@register.filter
def thousand_sep(value, sep=','):
    """Simple thousand separator for integers."""
    try:
        n = int(value)
    except Exception:
        return value
    s = f"{n:,}"
    if sep != ',':
        s = s.replace(',', sep)
    return s
