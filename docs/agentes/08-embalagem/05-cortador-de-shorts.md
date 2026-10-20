# Cortador de Shorts

> **Departamento:** 8 · Embalagem · **Tipo:** LLM-R + Ferr. · **Nó:** `embalagem.cortador_shorts` · **Doc-mãe:** [05 §3.8](../../05-arquitetura-agentes-langgraph.md) · **Formato:** [03 §9](../../03-identidade-visual-lume.md)

## Missão
Escolher **3 a 5 trechos de 30–50 s** do episódio e reenquadrá-los em 9:16, para que cada Short funcione sozinho e leve o espectador ao episódio inteiro.

## Posição no fluxo
- **Antes:** Gate 3.
- **Em paralelo:** Titulista, Designer de thumbnail e Redator de metadados.
- **Depois:** Gate 4 → Publicador (os Shorts são publicados depois do episódio).

## Entradas
| Campo | Para quê |
|---|---|
| `timeline` e `master.arquivo` | Material |
| `roteiro.esqueleto` | Viradas e clímax |
| `assets.planos[].render` | Renders sem letterbox, para reenquadrar com margem |
| `master.legendas` | Texto para a legenda grande |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `embalagem.shorts` | Por Short: trecho (timecode de origem), duração, MP4 9:16 (caminho + hash), título curto, gancho do 1º segundo |

## Regras de trabalho
1. **Trechos fechados:** cada Short tem começo, tensão e fim (ou um corte que deixa a pergunta aberta para o episódio). Bons candidatos: viradas e o olho de Polifemo.
2. **Gancho no primeiro segundo:** começa na ação, nunca na introdução.
3. **Sem Contador:** vai direto ao clímax (doc 03 §9).
4. **Layout:** parede de pedra com colunas e tocha, figura em sombra gigante na parede, fogueira na base e legenda grande em Cinzel Bold com textura de pergaminho no terço inferior, logo acima da fogueira (doc 03 §9).
5. **Reenquadrar com intenção:** manter a silhueta principal e a direção de tela; refazer o enquadramento a partir do render, não esticar o 16:9.
6. **Sem spoiler do final do episódio** (a resolução fica para o vídeo longo).

## Critérios de aceite
- [ ] 3 a 5 Shorts de 30–50 s
- [ ] Nenhum Short usa plano do Contador
- [ ] Silhueta principal inteira no quadro 9:16
- [ ] Legenda no terço superior

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Trecho bom, mas a silhueta não cabe em 9:16 | Pede um render vertical do plano ao Gerente de render (usa cache das marionetes) |

## Métricas
Visualizações por Short · % de espectadores que vão do Short para o episódio.

## Não faz
Não cria cenas novas e não altera o episódio longo.
