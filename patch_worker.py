path = r'D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                finally:
                    try:
                        await context.close()
                    except PatchrightError as exc:
                        event(
                            self.logger,
                            logging.WARNING,
                            "browser_context_already_closed",
                            error=type(exc).__name__,
                        )'''

replacement = '''                finally:
                    try:
                        await context.close()
                    except Exception as exc:
                        event(
                            self.logger,
                            logging.WARNING,
                            "browser_context_already_closed",
                            error=type(exc).__name__,
                        )'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("PATCH WORKER APPLIED")
else:
    print("TARGET IN WORKER NOT FOUND")
