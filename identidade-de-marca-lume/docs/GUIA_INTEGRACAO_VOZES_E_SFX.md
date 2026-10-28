# Guia de Integração de Vozes, SFX e Fallback Multi-Chave de API

Este guia documenta a integração de síntese vocal neural (TTS), geração de efeitos sonoros diegéticos (SFX), trilha musical (BGM) e o sistema de **Fallback Automático de Chaves de API** quando os tokens/cotas da chave primária se esgotam (`HTTP 429` / `403` / `RESOURCE_EXHAUSTED`).

---

## 1. Pool de Chaves de API e Rotação Automática (Fallback)

O motor de áudio ([grafo/ferramentas/audio.py](file:///d:/LUME/grafo/ferramentas/audio.py) e [config/modelos.yaml](file:///d:/LUME/config/modelos.yaml)) mantém um pool ordenado de chaves da API Google Generative Language (`gemini-2.5-flash-preview-tts`):

1. **Chave 1 (Primária):** `ENV_GEMINI_API_KEY_1`
2. **Chave 2 (Fallback / Backup):** `ENV_GEMINI_API_KEY_2`

### Como Funciona a Rotação quando os Tokens Acabam:
- Toda requisição passa por `requisitar_gemini_com_fallback()` em [grafo/ferramentas/audio.py](file:///d:/LUME/grafo/ferramentas/audio.py).
- O cliente tenta inicialmente a **Chave 1**.
- Se a API retornar erro de esgotamento de cota/tokens (`HTTP 429 Too Many Requests`, `HTTP 402/403`, `RESOURCE_EXHAUSTED`, `quota_exceeded` ou `rateLimitExceeded`), o sistema registra o aviso `[API_AUDIO_FALLBACK]` e reexecuta imediatamente a chamada utilizando a **Chave 2**, sem interromper a renderização do episódio.
- Você também pode sobrescrever ou adicionar chaves via variáveis de ambiente:
  ```powershell
  $env:GEMINI_API_KEYS="ENV_GEMINI_API_KEY_1,ENV_GEMINI_API_KEY_2"
  ```

---

## 2. Uso Programático do Motor de Voz com Fallback

```python
from grafo.ferramentas.audio import sintetizar_voz_gemini_com_fallback

caminho_audio = sintetizar_voz_gemini_com_fallback(
    texto="Nas trevas da Grécia antiga, quem não tem saída inventa a luz.",
    output_path="storage_local/audio/narracao_bloco_1.wav",
    voice_name="Charon",  # Opções: Charon, Orus, Fenrir, Enceladus, Algenib, Kore
)
```

---

## 3. Especificações Broadcast de Vozes, SFX e Mixagem

- **Taxa de Amostragem e Profundidade:** `48.000 Hz`, `24-bit PCM` (`pcm_s24le`), `2 Canais Estéreo`.
- **Loudness Integrado (EBU R128):** `-14.0 LUFS` (`±0.2 LU`) com True Peak `<= -1.0 dBTP`.
- **Sidechain Ducking:** Atenuação dinâmica de `-8.5 dB` na trilha musical (BGM) e `-6.0 dB` nos efeitos sonoros (SFX) durante a fala ativa (`attack=22ms`, `release=340ms`), mantendo a voz `>= +6.0 dB` acima da cama musical.
- **Janela de Silêncio Dramático:** Zeramento absoluto (`0.000`) de todos os barramentos antes do clímax (`47.20s–48.10s`).
