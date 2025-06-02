import re

SYMBOL_TO_CURRENCY = {
    '£': 'GBP',
    '$': 'USD',
    '€': 'EUR',
    '¥': 'JPY',
    '₹': 'INR',
    '₩': 'KRW',
    '₽': 'RUB',
    '₺': 'TRY',
    '₫': 'VND',
    '₪': 'ILS',
    '₦': 'NGN',
    '₴': 'UAH',
    '฿': 'THB',
}

def parse_formatted_currency(txt: str):
    text = txt.strip()
    currency_code = None

    for symbol, code in SYMBOL_TO_CURRENCY.items():
        if symbol in text:
            currency_code = code
            txt = text.replace(symbol, '')
            break
    else:
        currency_code = ' '.join(re.findall(r'[A-Za-z]+', text))
    value = re.sub(r'[^\d.\-]', '', txt)
    return currency_code, value