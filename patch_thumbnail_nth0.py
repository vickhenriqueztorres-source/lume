from pathlib import Path

# 1. Update selectors.py
s_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\selectors.py")
s_text = s_path.read_text(encoding="utf-8")

old_s = """    "first_frame_thumbnail": SelectorDef(
        "css",
        '[data-testid="uploaded-image-preview"], [data-testid="uploaded-image-remove-button"], [data-testid="uploaded-image"], [data-testid="remove-frame-0"]',
        "Elemento de preview ou remoção do quadro carregado; confirma término do upload",
        True,
    ),"""

new_s = """    "first_frame_thumbnail": SelectorDef(
        "css",
        '[data-testid="uploaded-image-preview"], [data-testid="uploaded-image-remove-button"], [data-testid="uploaded-image"], [data-testid="remove-frame-0"]',
        "Elemento de preview ou remoção do quadro carregado; confirma término do upload",
        True,
        nth=0,
    ),"""

s_norm = s_text.replace("\r\n", "\n")
old_norm = old_s.replace("\r\n", "\n")
new_norm = new_s.replace("\r\n", "\n")

if old_norm in s_norm:
    s_path.write_text(s_norm.replace(old_norm, new_norm), encoding="utf-8")
    print("SUCCESS: selectors.py updated with nth=0!")
else:
    print("WARNING: old_s not found directly")

# 2. Update worker.py _upload_first_frame to use .first
w_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py")
w_text = w_path.read_text(encoding="utf-8")

old_w = "thumbnail = self._get_locator(\"first_frame_thumbnail\")"
new_w = "thumbnail = self._get_locator(\"first_frame_thumbnail\").first"

w_norm = w_text.replace("\r\n", "\n")
if old_w in w_norm:
    w_path.write_text(w_norm.replace(old_w, new_w), encoding="utf-8")
    print("SUCCESS: worker.py updated to use thumbnail.first!")
else:
    print("WARNING: old_w not found")
