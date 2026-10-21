path = r'D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\state_reader.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '"cancel generation" in body_text'
replacement = '"mantenha esta aba" in body_text\n            or "carregado em breve" in body_text\n            or "cancel generation" in body_text'

if target in text:
    text = text.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("STATUS STRINGS UPDATED SUCCESSFULLY")
else:
    print("TARGET NOT FOUND")
