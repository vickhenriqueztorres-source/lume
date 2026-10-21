from pathlib import Path

worker_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py")
content = worker_path.read_text(encoding="utf-8")

old_func_start = "    async def _read_generation_state("
old_func_end = "    async def _click_generate_and_confirm("

s_idx = content.find(old_func_start)
e_idx = content.find(old_func_end)

if s_idx != -1 and e_idx != -1:
    before = content[:s_idx]
    after = content[e_idx:]
    new_func = """    async def _read_generation_state(
        self, job: Job, state_reader: StateReader
    ) -> ScreenObservation:
        # 1. Leitura direta ultrarrápida via DOM fast (executa em < 15ms)
        try:
            dom_obs = await state_reader.read_dom_state_fast(job.id)
            if dom_obs.state is not ScreenState.UNKNOWN:
                return dom_obs
        except Exception:
            pass

        # 2. Fallback com timeout estrito de 2.0 segundos para evitar bloqueio do loop
        try:
            return await asyncio.wait_for(
                state_reader.read_screen_state(job.id),
                timeout=2.0,
            )
        except Exception:
            return ScreenObservation(ScreenState.UNKNOWN, url=self._page.url if self._page else "")

"""
    worker_path.write_text(before + new_func + after, encoding="utf-8")
    print("SUCCESS: _read_generation_state patched to prioritize DOM fast reader!")
else:
    print(f"ERROR: could not locate markers: s_idx={s_idx}, e_idx={e_idx}")
