from pathlib import Path

p = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\state_reader.py")
text = p.read_text(encoding="utf-8")

old_snippet = """    async def read_dom_state_fast(self, job_id: int | None = None) -> ScreenObservation:
        \"\"\"Fallback for locator stalls: inspect the DOM directly for terminal states.\"\"\"
        started = time.perf_counter()
        payload = await self.page.evaluate(
            \"\"\"() => {
                function isFastVisible(el) {
                    return !!el && (el.offsetWidth > 0 || el.offsetHeight > 0 || (el.getClientRects && el.getClientRects().length > 0));
                }

                let download = null;
                let generate = null;
                let loadingAnimation = null;
                let hasCancelThumbnail = false;
                let hasThumbnailSpinner = false;
                let collectedTexts = [];

                const seen = new Set();
                function walk(root) {
                    if (!root || seen.has(root)) return;
                    seen.add(root);

                    if (!download && root.querySelector) download = root.querySelector('[data-testid="generate-video-download-button"]');
                    if (!generate && root.querySelector) generate = root.querySelector('[data-testid="video-generation-generate-button"]');
                    if (!loadingAnimation && root.querySelector) {
                        loadingAnimation = root.querySelector('firefly-video-generation-loading-animation, [data-testid="loading-subtext"]');
                    }
                    if (!hasCancelThumbnail && root.querySelector) {
                        hasCancelThumbnail = !!root.querySelector('[data-testid="generate-video-history-thumbnail-cancel-button"]');
                    }

                    const elements = root.querySelectorAll ? Array.from(root.querySelectorAll('*')) : [];
                    for (const el of elements) {
                        if (el.tagName === 'FIREFLY-VIDEO-GENERATION-LOADING-ANIMATION' || el.getAttribute('data-testid') === 'loading-subtext') {
                            if (isFastVisible(el)) loadingAnimation = el;
                        }
                        if (el.getAttribute('data-testid') === 'generate-video-history-thumbnail-cancel-button') {
                            hasCancelThumbnail = true;
                        }
                        if (el.tagName === 'SP-PROGRESS-CIRCLE' || (el.className && typeof el.className === 'string' && el.className.includes('spinner'))) {
                            if (isFastVisible(el)) hasThumbnailSpinner = true;
                        }

                        const txt = (el.innerText || el.textContent || '').trim();
                        if (txt && txt.length < 200 && isFastVisible(el)) {
                            collectedTexts.push(txt);
                        }

                        if (el.shadowRoot) {
                            walk(el.shadowRoot);
                        }
                    }
                }

                walk(document);

                const downloadVisible = isFastVisible(download);
                const downloadDisabled = !download || download.hasAttribute('disabled') || download.getAttribute('aria-disabled') === 'true';
                const generateVisible = isFastVisible(generate);
                const generateDisabled = !generate || generate.hasAttribute('disabled') || generate.getAttribute('aria-disabled') === 'true';
                const generateText = generate ? (generate.textContent || generate.getAttribute('aria-label') || '') : '';
                const loadingVisible = isFastVisible(loadingAnimation);

                return {
                    url: location.href,
                    allText: collectedTexts.join(' '),
                    downloadVisible,
                    downloadDisabled,
                    generateVisible,
                    generateDisabled,
                    generateText,
                    loadingVisible,
                    hasCancelThumbnail,
                    hasThumbnailSpinner
                };
            }\"\"\"
        )"""

new_snippet = """    async def read_dom_state_fast(self, job_id: int | None = None) -> ScreenObservation:
        \"\"\"Fallback for locator stalls: inspect the DOM directly for terminal states.\"\"\"
        started = time.perf_counter()
        payload = await self.page.evaluate(
            \"\"\"() => {
                function isFastVisible(el) {
                    return !!el && (el.offsetWidth > 0 || el.offsetHeight > 0 || (el.getClientRects && el.getClientRects().length > 0));
                }

                let download = document.querySelector('[data-testid="generate-video-download-button"]');
                let generate = document.querySelector('[data-testid="video-generation-generate-button"]');
                let loadingAnimation = document.querySelector('firefly-video-generation-loading-animation, [data-testid="loading-subtext"]');
                let hasCancelThumbnail = !!document.querySelector('[data-testid="generate-video-history-thumbnail-cancel-button"]');
                let hasThumbnailSpinner = !!document.querySelector('sp-progress-circle');

                // Busca direcionada em shadow roots sem iterar todo o DOM
                const seen = new Set();
                function searchShadow(root) {
                    if (!root || seen.has(root)) return;
                    seen.add(root);

                    if (!download && root.querySelector) download = root.querySelector('[data-testid="generate-video-download-button"]');
                    if (!generate && root.querySelector) generate = root.querySelector('[data-testid="video-generation-generate-button"]');
                    if (!loadingAnimation && root.querySelector) loadingAnimation = root.querySelector('firefly-video-generation-loading-animation, [data-testid="loading-subtext"]');
                    if (!hasCancelThumbnail && root.querySelector) hasCancelThumbnail = !!root.querySelector('[data-testid="generate-video-history-thumbnail-cancel-button"]');
                    if (!hasThumbnailSpinner && root.querySelector) hasThumbnailSpinner = !!root.querySelector('sp-progress-circle');

                    const hosts = root.querySelectorAll ? Array.from(root.querySelectorAll('*')).filter(el => el.shadowRoot) : [];
                    for (const host of hosts) {
                        searchShadow(host.shadowRoot);
                    }
                }
                searchShadow(document);

                const downloadVisible = isFastVisible(download);
                const downloadDisabled = !download || download.hasAttribute('disabled') || download.getAttribute('aria-disabled') === 'true';
                const generateVisible = isFastVisible(generate);
                const generateDisabled = !generate || generate.hasAttribute('disabled') || generate.getAttribute('aria-disabled') === 'true';
                const generateText = generate ? (generate.textContent || generate.getAttribute('aria-label') || '') : '';
                const loadingVisible = isFastVisible(loadingAnimation);
                const allText = (document.body ? (document.body.innerText || document.body.textContent || '') : '').toLowerCase();

                return {
                    url: location.href,
                    allText: allText,
                    downloadVisible,
                    downloadDisabled,
                    generateVisible,
                    generateDisabled,
                    generateText,
                    loadingVisible,
                    hasCancelThumbnail,
                    hasThumbnailSpinner
                };
            }\"\"\"
        )"""

text_n = text.replace("\r\n", "\n")
old_n = old_snippet.replace("\r\n", "\n")
new_n = new_snippet.replace("\r\n", "\n")

if old_n in text_n:
    text_n = text_n.replace(old_n, new_n)
    p.write_text(text_n, encoding="utf-8")
    print("state_reader.py otimizado com sucesso!")
else:
    print("Snippet alvo não encontrado em state_reader.py")
