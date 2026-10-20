# Agentes: fichas individuais

> **O que é esta pasta:** uma ficha por agente do runtime LangGraph descrito no [doc 05](../05-arquitetura-agentes-langgraph.md): os 47 agentes dos 10 departamentos + o Showrunner.
> **Hierarquia:** o doc 05 continua sendo a fonte da verdade do **grafo** (estado, contrato do plano, gates). As fichas detalham **cada nó**: missão, entradas, saídas, regras, critérios de aceite e falhas. Se uma ficha contradisser o doc 05, vale o doc 05, e a ficha precisa ser corrigida.
> **O que não tem aqui:** código. Os prompts de verdade ficam em `prompts/` (doc 06 §7) e são escritos *a partir* destas fichas.
> **Não confundir** com os agentes do Antigravity (doc 06 §3), que constroem e operam o sistema. Os agentes desta pasta **usam** o sistema para produzir o episódio.

---

## 1. Modelo de ficha

Toda ficha segue a mesma ordem, para que o Engenheiro de prompts (doc 06 §3) consiga transformá-la em prompt e casos de teste sem interpretar:

| Seção | O que responde |
|---|---|
| **Cabeçalho** | Departamento, tipo de modelo, id do nó, se bloqueia ou não |
| **Missão** | O que este agente entrega, em uma frase |
| **Posição no fluxo** | Quem roda antes, quem roda depois e se roda em paralelo ou por `Send` |
| **Entradas** | Campos do estado que ele **lê** |
| **Saída** | Campos do estado que ele **escreve** (só os do seu departamento) |
| **Ferramentas** | O que ele pode chamar |
| **Regras de trabalho** | O que o prompt (ou a configuração da ferramenta) precisa exigir |
| **Critérios de aceite** | Checklist objetivo: se tudo passa, o nó encerra |
| **Falhas e escalada** | O que fazer em cada falha, quantas tentativas e quando chamar humano |
| **Métricas** | O que medir para saber se o agente está melhorando |
| **Não faz** | Limites explícitos, para evitar que o agente invada outro departamento |

**Tipos de modelo** (mesma legenda do doc 05): **LLM-R** raciocínio/escrita · **LLM-V** multimodal com visão · **IMG** geração de imagem · **TTS** voz · **Ferr.** ferramenta determinística.

---

## 2. Regras que valem para todos os agentes

Estas regras não se repetem em cada ficha, mas todas as fichas as assumem:

1. **Escreve só no seu campo.** Cada departamento é dono de um campo do estado (doc 05 §2). Dentro do departamento, cada agente escreve no seu **subcampo** (ex.: `pesquisa.fontes`).
2. **Append em listas.** `custos`, `erros` e `qa` só recebem acréscimos; nada é sobrescrito.
3. **Assinatura em toda escrita:** `versao` + `autor_no`.
4. **Arquivo pesado nunca entra no estado:** só **caminho + hash** do storage de objetos.
5. **Idempotência:** todo nó com efeito colateral (upload, cobrança, envio de job) grava uma **chave de operação** antes de agir e confere essa chave ao ser retomado.
6. **Custo:** todo nó registra em `custos` os tokens, os segundos de GPU e as chamadas de API que gastou.
7. **Erro:** toda falha vai para `erros` com: o que falhou, tentativa nº, e a **decisão** tomada (refazer, alternativa, escalar).
8. **Modelos por categoria**, nunca por nome fixo (doc 06 §10).
9. **Lições da memória:** o Showrunner injeta no contexto de cada agente as lições da Store que se aplicam a ele. O agente as trata como regras adicionais, **abaixo** dos docs 03–05 em prioridade.
10. **Identidade e cinematografia** (docs 03 e 04) são regras, não sugestões. Em dúvida entre "mais bonito" e "dentro da regra", vence a regra; a exceção é pedida num gate.

**Convenção do id do nó:** `<departamento>.<agente>` em minúsculas e sem acento, ex.: `roteiro.revisor_fidelidade`.

---

## 3. Índice

### Supervisor
| Agente | Tipo | Ficha |
|---|---|---|
| Showrunner | LLM-R + regras | [00-showrunner](./00-showrunner.md) |

### 1 · Pesquisa
| Agente | Tipo | Ficha |
|---|---|---|
| Pesquisador de fontes | LLM-R | [01-pesquisa/01-pesquisador-de-fontes](./01-pesquisa/01-pesquisador-de-fontes.md) |
| Verificador de fatos | LLM-R | [01-pesquisa/02-verificador-de-fatos](./01-pesquisa/02-verificador-de-fatos.md) |
| Analista de referência | Ferr. + LLM-V | [01-pesquisa/03-analista-de-referencia](./01-pesquisa/03-analista-de-referencia.md) |
| Analista de demanda | LLM-R | [01-pesquisa/04-analista-de-demanda](./01-pesquisa/04-analista-de-demanda.md) |

### 2 · Roteiro
| Agente | Tipo | Ficha |
|---|---|---|
| Arquiteto de estrutura | LLM-R | [02-roteiro/01-arquiteto-de-estrutura](./02-roteiro/01-arquiteto-de-estrutura.md) |
| Roteirista (voz do Contador) | LLM-R | [02-roteiro/02-roteirista](./02-roteiro/02-roteirista.md) |
| Editor de retenção | LLM-R | [02-roteiro/03-editor-de-retencao](./02-roteiro/03-editor-de-retencao.md) |
| Revisor de fidelidade | LLM-R | [02-roteiro/04-revisor-de-fidelidade](./02-roteiro/04-revisor-de-fidelidade.md) |
| Revisor de tom | LLM-R | [02-roteiro/05-revisor-de-tom](./02-roteiro/05-revisor-de-tom.md) |

### 3 · Direção
| Agente | Tipo | Ficha |
|---|---|---|
| Diretor (decupagem) | LLM-R | [03-direcao/01-diretor-decupagem](./03-direcao/01-diretor-decupagem.md) |
| Diretor de fotografia | LLM-R | [03-direcao/02-diretor-de-fotografia](./03-direcao/02-diretor-de-fotografia.md) |
| Supervisor de direção de tela | LLM-R (regras) | [03-direcao/03-supervisor-direcao-de-tela](./03-direcao/03-supervisor-direcao-de-tela.md) |
| Diretor de arte | LLM-R + Store | [03-direcao/04-diretor-de-arte](./03-direcao/04-diretor-de-arte.md) |
| Storyboarder | IMG + Ferr. | [03-direcao/05-storyboarder](./03-direcao/05-storyboarder.md) |

### 4 · Arte & marionetes
| Agente | Tipo | Ficha |
|---|---|---|
| Designer de silhuetas | IMG + LLM-V | [04-arte/01-designer-de-silhuetas](./04-arte/01-designer-de-silhuetas.md) |
| Vetorizador | Ferr. | [04-arte/02-vetorizador](./04-arte/02-vetorizador.md) |
| Rigger | LLM-V + Ferr. | [04-arte/03-rigger](./04-arte/03-rigger.md) |
| Cenógrafo | IMG + Ferr. | [04-arte/04-cenografo](./04-arte/04-cenografo.md) |
| Bibliotecário | Ferr. + Store | [04-arte/05-bibliotecario](./04-arte/05-bibliotecario.md) |

### 5 · Animação & render
| Agente | Tipo | Ficha |
|---|---|---|
| Animador de plano | LLM-R + Ferr. | [05-animacao/01-animador-de-plano](./05-animacao/01-animador-de-plano.md) |
| Montador de cena 3D | Ferr. | [05-animacao/02-montador-de-cena-3d](./05-animacao/02-montador-de-cena-3d.md) |
| Gerente de render | Ferr. | [05-animacao/03-gerente-de-render](./05-animacao/03-gerente-de-render.md) |
| Revisor de plano | LLM-V | [05-animacao/04-revisor-de-plano](./05-animacao/04-revisor-de-plano.md) |
| VFX | Ferr. | [05-animacao/05-vfx](./05-animacao/05-vfx.md) |

### 6 · Áudio
| Agente | Tipo | Ficha |
|---|---|---|
| Diretor de voz | LLM-R | [06-audio/01-diretor-de-voz](./06-audio/01-diretor-de-voz.md) |
| Narrador | TTS / Ferr. | [06-audio/02-narrador](./06-audio/02-narrador.md) |
| Sound designer | LLM-R + Ferr. | [06-audio/03-sound-designer](./06-audio/03-sound-designer.md) |
| Supervisor musical | LLM-R + Ferr. | [06-audio/04-supervisor-musical](./06-audio/04-supervisor-musical.md) |
| Mixador | Ferr. | [06-audio/05-mixador](./06-audio/05-mixador.md) |

### 7 · Montagem & finalização
| Agente | Tipo | Ficha |
|---|---|---|
| Editor | LLM-R + Ferr. | [07-montagem/01-editor](./07-montagem/01-editor.md) |
| Grafismo | Ferr. | [07-montagem/02-grafismo](./07-montagem/02-grafismo.md) |
| Finalizador | Ferr. | [07-montagem/03-finalizador](./07-montagem/03-finalizador.md) |
| Legendador | ASR + LLM-R | [07-montagem/04-legendador](./07-montagem/04-legendador.md) |

### 8 · Embalagem
| Agente | Tipo | Ficha |
|---|---|---|
| Titulista | LLM-R | [08-embalagem/01-titulista](./08-embalagem/01-titulista.md) |
| Designer de thumbnail | IMG + Ferr. | [08-embalagem/02-designer-de-thumbnail](./08-embalagem/02-designer-de-thumbnail.md) |
| Avaliador de feed | LLM-V | [08-embalagem/03-avaliador-de-feed](./08-embalagem/03-avaliador-de-feed.md) |
| Redator de metadados | LLM-R | [08-embalagem/04-redator-de-metadados](./08-embalagem/04-redator-de-metadados.md) |
| Cortador de Shorts | LLM-R + Ferr. | [08-embalagem/05-cortador-de-shorts](./08-embalagem/05-cortador-de-shorts.md) |

### 9 · QA
| Agente | Bloqueia? | Ficha |
|---|---|---|
| QA técnico | Sim | [09-qa/01-qa-tecnico](./09-qa/01-qa-tecnico.md) |
| QA de continuidade | Sim | [09-qa/02-qa-de-continuidade](./09-qa/02-qa-de-continuidade.md) |
| QA de fidelidade | Sim | [09-qa/03-qa-de-fidelidade](./09-qa/03-qa-de-fidelidade.md) |
| QA de marca | Não (aviso) | [09-qa/04-qa-de-marca](./09-qa/04-qa-de-marca.md) |
| QA de direitos | Sim | [09-qa/05-qa-de-direitos](./09-qa/05-qa-de-direitos.md) |
| QA de originalidade | Sim | [09-qa/06-qa-de-originalidade](./09-qa/06-qa-de-originalidade.md) |

### 10 · Publicação & aprendizado
| Agente | Tipo | Ficha |
|---|---|---|
| Publicador | Ferr. | [10-publicacao/01-publicador](./10-publicacao/01-publicador.md) |
| Analista de desempenho | Ferr. + LLM-R | [10-publicacao/02-analista-de-desempenho](./10-publicacao/02-analista-de-desempenho.md) |
| Curador de memória | LLM-R + Store | [10-publicacao/03-curador-de-memoria](./10-publicacao/03-curador-de-memoria.md) |

---

## 4. Subcampos do estado por agente (resumo)

Os campos do doc 05 §2 são divididos assim dentro de cada departamento. Este quadro **não cria campos novos**: só detalha quem escreve em qual parte.

| Campo | Subcampo | Agente dono |
|---|---|---|
| `episodio` | `status`, `rota`, `orcamento`, `fila_humana`, `licoes_aplicadas` | Showrunner |
| `pesquisa` | `fontes`, `nomes_canonicos` | Pesquisador de fontes |
| | `fatos`, `controversias` | Verificador de fatos |
| | `referencia` (métricas de ritmo, lacunas) | Analista de referência |
| | `angulos` | Analista de demanda |
| `roteiro` | `esqueleto` | Arquiteto de estrutura |
| | `blocos`, `versoes` | Roteirista |
| | `notas` (uma lista por revisor) | Editor de retenção, Revisor de fidelidade, Revisor de tom |
| `decupagem` | `planos` (campos de cena, câmera, duração) | Diretor (decupagem) |
| | `planos[].fogo`, `luz_deus`, `proporcao` | Diretor de fotografia |
| | `correcoes_direcao` | Supervisor de direção de tela |
| | `planos[].storyboard`, `animatic` | Storyboarder |
| `color_script` | todo | Diretor de fotografia |
| `elenco` | todo | Diretor de arte |
| `assets` | `marionetes`, `cenarios`, `indice` | Arte (Designer, Vetorizador, Rigger, Cenógrafo, Bibliotecário) |
| | `planos[].cena`, `planos[].render`, `planos[].vfx`, `planos[].revisao` | Animação |
| `audio` | `roteiro_anotado` | Diretor de voz |
| | `narracao` | Narrador |
| | `sfx` | Sound designer |
| | `trilha` | Supervisor musical |
| | `mix`, `lufs` | Mixador |
| `timeline` | todo | Editor (Grafismo acrescenta camadas) |
| `master` | `arquivo`, `capitulos` | Finalizador |
| | `legendas` | Legendador |
| `embalagem` | `titulos` / `thumbs` / `ranking` / `metadados` / `shorts` | Titulista / Designer de thumbnail / Avaliador de feed / Redator de metadados / Cortador de Shorts |
| `qa` | um relatório por checagem (append) | Os 6 agentes de QA |
