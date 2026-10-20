"""Script para abrir o Google Chrome com o perfil e sessão salvos do Adobe Firefly."""

import os
import shutil
import sys
import time
from pathlib import Path
from patchright.sync_api import sync_playwright

PROFILE_DIR = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\data\chrome_profile")
CHROME_EXE = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

if not PROFILE_DIR.exists():
    # Fallback se necessário para HSL-FIREFLY-PROFILE
    alt_dir = Path(r"D:\HSL-FIREFLY-PROFILE")
    if alt_dir.exists():
        PROFILE_DIR = alt_dir

print(f"[FIREFLY TEST] Utilizando perfil do Chrome: {PROFILE_DIR}")

# Limpa locks residuais para permitir abertura simultânea sem conflito
for item in ["SingletonLock", "SingletonSocket", "SingletonCookie", "lockfile"]:
    lock_file = PROFILE_DIR / item
    if lock_file.exists():
        try:
            lock_file.unlink()
        except Exception:
            pass

with sync_playwright() as p:
    launch_kwargs = {
        "user_data_dir": str(PROFILE_DIR),
        "headless": False,
        "args": [
            "--start-maximized",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
        ],
        "viewport": None,
    }

    if CHROME_EXE.exists():
        launch_kwargs["executable_path"] = str(CHROME_EXE)

    print("[FIREFLY TEST] Disparando navegador Chrome...")
    context = p.chromium.launch_persistent_context(**launch_kwargs)
    page = context.pages[0] if context.pages else context.new_page()

    print("[FIREFLY TEST] Navegando para https://firefly.adobe.com/generate/video ...")
    page.goto("https://firefly.adobe.com/generate/video", wait_until="domcontentloaded", timeout=60000)

    print(f"[FIREFLY TEST] Pagina carregada com sucesso! Titulo: {page.title()}")
    print("[FIREFLY TEST] O navegador esta aberto e ativo na sua tela.")
    
    # Aguarda 60 segundos ou enquanto a página estiver aberta para o usuário visualizar
    print("[FIREFLY TEST] Mantendo a janela aberta...")
    for _ in range(120):
        time.sleep(1)
        if page.is_closed():
            break

    print("[FIREFLY TEST] Teste de abertura finalizado.")
