def normalize_text(text: str):
    return text.strip().replace(';', ',')

def normalize_value(value: str):
    return round(float(str(value).replace('.', '').replace(',', '.').replace('R$', '').strip()), 2)