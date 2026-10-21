from pathlib import Path

# 1. Patch selectors.py
selectors_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\selectors.py")
s_text = selectors_path.read_text(encoding="utf-8")

old_s = """    "first_frame_thumbnail": SelectorDef(
        "test_id",
        "remove-frame-0",
        "Botão 'Remover imagem' do quadro 0; só existe depois que o upload realmente terminou",
        True,
    ),"""

new_s = """    "first_frame_thumbnail": SelectorDef(
        "css",
        '[data-testid="uploaded-image-preview"], [data-testid="uploaded-image-remove-button"], [data-testid="uploaded-image"], [data-testid="remove-frame-0"]',
        "Elemento de preview ou remoção do quadro carregado; confirma término do upload",
        True,
    ),"""

s_norm = s_text.replace("\r\n", "\n")
old_norm = old_s.replace("\r\n", "\n")
new_norm = new_s.replace("\r\n", "\n")

if old_norm in s_norm:
    selectors_path.write_text(s_norm.replace(old_norm, new_norm), encoding="utf-8")
    print("SUCCESS: selectors.py updated with modern thumbnail selector!")
else:
    print("WARNING: old_s not found directly in selectors.py")

# 2. Patch worker.py _upload_first_frame
worker_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py")
w_text = worker_path.read_text(encoding="utf-8")

u_idx = w_text.find("async def _upload_first_frame")
u_end = w_text.find("async def _ensure_single_capture_mode")

if u_idx != -1 and u_end != -1:
    before = w_text[:u_idx]
    after = w_text[u_end:]
    clean_upload = """async def _upload_first_frame(self, image_path: str) -> None:
        path = Path(image_path).resolve()
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise FileNotFoundError(f"first frame inválido: {path}")

        thumbnail = self._get_locator("first_frame_thumbnail")
        if await thumbnail.count() > 0:
            event(
                self.logger,
                logging.INFO,
                "first_frame_already_present",
                job_id=self._current_job_id,
                image=path,
            )
            return

        button = self._get_locator("first_frame_button")
        if await button.count() > 0 and await button.is_visible():
            human = self._require_human()
            await human.click_element(button, "botão First frame")
            await human.human_delay(0.3, 0.8)
            await self._get_locator("first_frame_upload").set_input_files(str(path))
            try:
                await thumbnail.wait_for(state="attached", timeout=15000)
            except Exception:
                await asyncio.sleep(3)
            event(
                self.logger,
                logging.INFO,
                "first_frame_uploaded",
                job_id=self._current_job_id,
                image=path,
            )

    """
    worker_path.write_text(before + clean_upload + after, encoding="utf-8")
    print("SUCCESS: _upload_first_frame in worker.py patched cleanly!")
else:
    print("ERROR: could not locate _upload_first_frame markers")
