# Conflitos e Lacunas Encontrados nos Documentos

Este arquivo registra contradições, ambiguidades ou lacunas entre os documentos de especificação, a resolução adotada no código (seguindo a hierarquia e regras inegociáveis) e a correção proposta para os documentos.

---

### CONFLITO 01: Contagem total de agentes (47 vs 48)
- **Arquivo / Seção:** `docs/05-arquitetura-agentes-langgraph.md` §3 vs `docs/agentes/README.md` §3
- **Trecho:** "Total: 47 agentes + o Showrunner (4 + 5 + 5 + 5 + 5 + 5 + 4 + 5 + 6 + 3)" vs menções a "47 agentes" ou "48 agentes".
- **Problema:** Em alguns títulos é dito "47 agentes", mas com o Showrunner são 48 nós no grafo.
- **Resolução no código:** O sistema implementa 48 nós ao todo: 1 Supervisor (Showrunner) e 47 nós distribuídos nos 10 departamentos.
- **Correção proposta para o doc:** Padronizar para "48 nós (Showrunner + 47 agentes)".

---

### CONFLITO 02: Localização e granularidade de campos de plano (`decupagem` vs `assets`)
- **Arquivo / Seção:** `docs/05-arquitetura-agentes-langgraph.md` §2 e §5 vs `docs/agentes/README.md` §4
- **Trecho:** Em `05` §5, o contrato de plano inclui `id, bloco_roteiro, mundo, tipo_plano, duracao_s, marionetes[], camera, fogo, luz_deus, proporcao, parede, transicao_saida, sfx[], storyboard, render, qa`. Em `README` §4, `decupagem` tem `planos` e `assets` tem `planos[].cena, planos[].render...`.
- **Problema:** Se o plano é a unidade que trafega via `Send` e o estado armazena planos, há divisão entre a decupagem de direção e os renders de animação.
- **Resolução no código:** O modelo `Plano` em `contratos/plano.py` define o contrato canônico completo do plano. No estado do episódio (`EstadoEpisodio`), `decupagem["planos"]` armazena a lista de planos decupados com seus metadados de direção e storyboarding, e `assets["planos"]` (ou o próprio plano enriquecido em seu ciclo) mantém as referências de render, hash e status de animação sem duplicar dados contraditórios.
- **Correção proposta para o doc:** Deixar explícito que `Plano` é uma entidade tipada unificada compartilhada, referenciada tanto na decupagem quanto na esteira de assets/animação.

---

### CONFLITO 03: Lista de aprovacoes e Reducers
- **Arquivo / Seção:** `docs/05-arquitetura-agentes-langgraph.md` §2 vs `docs/agentes/README.md` §2 regra 2
- **Trecho:** Regra 2 do README cita `custos, erros e qa só recebem acréscimos`, enquanto o doc 05 §2 lista `aprovacoes` como dono "Gates humanos". A regra inegociável 4 do prompt mestre determina: `custos, erros, qa e aprovacoes só recebem append (reducer de lista)`.
- **Problema:** README §2 regra 2 omitiu `aprovacoes` na frase explicativa, embora doc 05 e prompt mestre exijam reducer de append para `aprovacoes`.
- **Resolução no código:** `aprovacoes` é tipado como lista com reducer `operator.add` (append-only), assim como `custos`, `erros` e `qa`.
- **Correção proposta para o doc:** Incluir `aprovacoes` na Regra 2 do `docs/agentes/README.md`.
