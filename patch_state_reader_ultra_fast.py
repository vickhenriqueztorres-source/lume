from pathlib import Path

# 1. Update state_reader.py
sr_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\state_reader.py")
sr_content = sr_path.read_text(encoding="utf-8")

old_read_dom_fast = """    async def read_dom_state_fast(self, job_id: int | None = None) -> ScreenObservation:
        \"\"\"Fallback for locator stalls: inspect the DOM directly for terminal states.\"\"\"
        started = time.perf_counter()"""

# Find start of read_dom_state_fast
idx = sr_content.find("async def read_dom_state_fast")
if idx != -1:
    header = sr_content[:idx]
    new_method = """    async def read_dom_state_fast(self, job_id: int | None = None) -> ScreenObservation:
        \"\"\"Inspeciona o DOM com seletores específicos em < 2ms, sem layout thrashing.\"\"\"
        started = time.perf_counter()
        selectors_found: list[str] = []
        selectors_absent: list[str] = []

        try:
            # Avaliação direta ultra-rápida (zero querySelectorAll('*') e zero body.innerText)
            payload = await self.page.evaluate('''() => {
                function isVisible(el) {
                    return !!el && (el.offsetWidth > 0 || el.offsetHeight > 0 || (el.getClientRects && el.getClientRects().length > 0));
                }

                // 1. Botão de Download ativo (conclusão)
                let dl = document.querySelector('[data-testid="generate-video-download-button"]');
                if (!dl) {
                    const h = document.querySelector('firefly-video-generation-download-button');
                    if (h && h.shadowRoot) dl = h.shadowRoot.querySelector('sp-button, button');
                }
                const downloadReady = !!dl && !dl.disabled && dl.getAttribute('aria-disabled') !== 'true' && isVisible(dl);

                // 2. Animação de carregamento / progresso (gerando)
                const hasLoading = !!document.querySelector('firefly-video-generation-loading-animation, [data-testid="loading-subtext"], sp-progress-circle');
                const hasCancel = !!document.querySelector('[data-testid="generate-video-history-thumbnail-cancel-button"]');

                // 3. Toasts e erros
                const toast = document.querySelector('sp-toast, [role="alert"]');
                const toastText = toast ? (toast.textContent || '').trim().toLowerCase() : '';

                // 4. Botão Gerar
                let gen = document.querySelector('[data-testid="video-generation-generate-button"]');
                if (!gen) {
                    const gh = document.querySelector('firefly-video-generation-generate-button');
                    if (gh && gh.shadowRoot) gen = gh.shadowRoot.querySelector('sp-button, button');
                }
                const genActive = !!gen && !gen.disabled && gen.getAttribute('aria-disabled') !== 'true';

                return {
                    url: location.href,
                    downloadReady,
                    hasLoading,
                    hasCancel,
                    toastText,
                    genActive
                };
            }''')

            download_ready = bool(payload.get("downloadReady"))
            has_loading = bool(payload.get("hasLoading"))
            has_cancel = bool(payload.get("hasCancel"))
            toast_text = str(payload.get("toastText") or "").lower()
            gen_active = bool(payload.get("genActive"))

            if "não foi possível processar esse prompt" in toast_text:
                state = ScreenState.CONTENT_REJECTED
                selectors_found.append("dom_fast:content_rejected")
            elif any(q in toast_text for q in ["quota", "crédito", "credito", "saldo", "insufficient credits"]):
                state = ScreenState.QUOTA_EXHAUSTED
                selectors_found.append("dom_fast:quota_exhausted")
            elif any(e in toast_text for e in ["erro", "error", "falhou"]):
                state = ScreenState.ERROR_TOAST
                selectors_found.append("dom_fast:error_toast")
            elif download_ready:
                state = ScreenState.RESULT_READY
                selectors_found.append("dom_fast:result_ready")
            elif has_loading or has_cancel:
                state = ScreenState.STILL_GENERATING
                selectors_found.append("dom_fast:still_generating")
            elif gen_active:
                state = ScreenState.UNKNOWN
                selectors_found.append("dom_fast:idle_ready")
            else:
                state = ScreenState.UNKNOWN
                selectors_found.append("dom_fast:unknown")

            duration_ms = (time.perf_counter() - started) * 1000
            observation = ScreenObservation(
                state,
                url=str(payload.get("url") or self.page.url),
                selectors_found=tuple(selectors_found),
                selectors_absent=tuple(selectors_absent),
                read_duration_ms=duration_ms,
            )
            event(
                self.logger,
                logging.INFO,
                "screen_state_dom_fallback",
                job_id=job_id,
                state=state.value,
                url=observation.url,
                selectors_found=",".join(selectors_found),
                read_duration_ms=round(duration_ms, 1),
            )
            return observation
        except Exception as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            return ScreenObservation(
                ScreenState.UNKNOWN,
                url=self.page.url,
                selectors_found=(),
                selectors_absent=(),
                selector_errors=({"error": str(exc)},),
                read_duration_ms=duration_ms,
            )
"""
    sr_path.write_text(header + new_method, encoding="utf-8")
    print("SUCCESS: state_reader.py patched with ultra-fast non-blocking reader!")
else:
    print("ERROR: could not locate read_dom_state_fast in state_reader.py")

# 2. Update _click_generate_and_confirm in worker.py to click directly without ghost-cursor hanging
worker_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py")
worker_content = worker_path.read_text(encoding="utf-8")

c_idx = worker_content.find("async def _click_generate_and_confirm")
c_end = worker_content.find("async def _complete_generation")

if c_idx != -1 and c_end != -1:
    before = worker_content[:c_idx]
    after = worker_content[c_end:]
    clean_click = """async def _click_generate_and_confirm(
        self, job: Job, page: object, human_input: HumanInput
    ) -> None:
        generate_button = locator_for(page, "generate_button")
        state_reader = StateReader(page, self.config.screenshots_dir, self.logger, self.config)

        await dismiss_overlays(page, human_input, self.logger, job.id)

        # Checa se uma geracao ja esta ativa antes de tentar clicar
        initial_obs = await state_reader.read_dom_state_fast(job.id)
        if initial_obs.state in {ScreenState.STILL_GENERATING, ScreenState.RESULT_READY}:
            event(
                self.logger,
                logging.INFO,
                "generate_precheck_already_active",
                job_id=job.id,
                state=initial_obs.state.value,
            )
            return

        for attempt in range(1, 4):
            event(self.logger, logging.INFO, "generate_click_attempt", job_id=job.id, attempt=attempt)
            try:
                # 1. Clique nativo Playwright com force=True para perfurar shadow roots
                await generate_button.click(timeout=3000, force=True)
            except Exception:
                try:
                    # 2. Fallback via JS no botão interno do Shadow DOM
                    await page.evaluate('''() => {
                        const host = document.querySelector('firefly-video-generation-generate-button');
                        if (host) {
                            const btn = (host.shadowRoot && host.shadowRoot.querySelector('sp-button, button')) || host;
                            btn.click();
                        }
                    }''')
                except Exception:
                    await human_input.click(generate_button)

            deadline = asyncio.get_running_loop().time() + 10
            while asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(1)
                observation = await state_reader.read_dom_state_fast(job.id)
                if observation.state in {
                    ScreenState.STILL_GENERATING,
                    ScreenState.RESULT_READY,
                    ScreenState.ERROR_TOAST,
                    ScreenState.CONTENT_REJECTED,
                    ScreenState.QUOTA_EXHAUSTED,
                }:
                    event(
                        self.logger,
                        logging.INFO,
                        "generate_click_confirmed",
                        job_id=job.id,
                        attempt=attempt,
                        state=observation.state.value,
                    )
                    return

        raise RuntimeError("generate button click did not start provider generation")

    """
    worker_path.write_text(before + clean_click + after, encoding="utf-8")
    print("SUCCESS: _click_generate_and_confirm in worker.py patched cleanly!")
else:
    print(f"ERROR: could not locate markers: c_idx={c_idx}, c_end={c_end}")
