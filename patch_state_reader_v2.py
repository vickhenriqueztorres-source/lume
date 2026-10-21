import re

path = r'D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\state_reader.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'(\s+payload = await self\.page\.evaluate\(\s+"""\(\) => \{)(.*?)(\}\"\"\"\s+\))'

replacement = r'''        payload = await self.page.evaluate(
            """() => {
                function isFastVisible(el) {
                    return !!el && (el.offsetWidth > 0 || el.offsetHeight > 0 || (el.getClientRects && el.getClientRects().length > 0));
                }

                let download = document.querySelector('[data-testid="generate-video-download-button"]');
                let generate = document.querySelector('[data-testid="video-generation-generate-button"]');
                let allText = (document.body ? document.body.innerText : '') + ' ';

                const queue = [document.body];
                let visited = 0;
                while (queue.length > 0 && visited < 300) {
                    const current = queue.shift();
                    visited++;
                    if (!current) continue;
                    if (current.shadowRoot) {
                        if (!download) download = current.shadowRoot.querySelector('[data-testid="generate-video-download-button"]');
                        if (!generate) generate = current.shadowRoot.querySelector('[data-testid="video-generation-generate-button"]');
                        allText += (current.shadowRoot.textContent || '') + ' ';
                        for (let i = 0; i < current.shadowRoot.children.length; i++) {
                            queue.push(current.shadowRoot.children[i]);
                        }
                    }
                    for (let i = 0; i < current.children.length; i++) {
                        const c = current.children[i];
                        if (c.shadowRoot || c.tagName.includes('-')) {
                            queue.push(c);
                        }
                    }
                }

                const videos = Array.from(document.querySelectorAll('video')).map(v => ({
                    src: v.currentSrc || v.src || v.getAttribute('src') || '',
                    poster: v.getAttribute('poster') || '',
                    visible: isFastVisible(v)
                }));

                const downloadVisible = isFastVisible(download);
                const downloadDisabled = !download || download.hasAttribute('disabled') || download.getAttribute('aria-disabled') === 'true';
                const generateVisible = isFastVisible(generate);
                const generateDisabled = !generate || generate.hasAttribute('disabled') || generate.getAttribute('aria-disabled') === 'true';
                const generateText = generate ? (generate.textContent || generate.getAttribute('aria-label') || '') : '';

                return {
                    url: location.href,
                    bodyText: allText,
                    downloadVisible,
                    downloadDisabled,
                    generateVisible,
                    generateDisabled,
                    generateText,
                    videoCount: videos.length,
                    videos,
                    generatedCandidates: []
                };
            }"""
        )'''

new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
if count == 1:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print(f"FAILED TO MATCH: count={count}")
