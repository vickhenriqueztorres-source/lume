# Diretor de arte

> **Departamento:** 3 · Direção · **Tipo:** LLM-R + Store · **Nó:** `direcao.diretor_arte` · **Doc-mãe:** [05 §3.3](../../05-arquitetura-agentes-langgraph.md) · **Silhuetas:** [03 §6](../../03-identidade-visual-lume.md)

## Missão
Fazer o **elenco** do episódio: quais marionetes e cenários cada plano precisa, o que já existe na biblioteca e o que precisa ser criado, com a ficha pronta para a Arte.

## Posição no fluxo
- **Antes:** Supervisor de direção de tela.
- **Depois:** Storyboarder → Gate 2. Depois do Gate 2, o `elenco` é a lista de trabalho da **Arte**.

## Entradas
| Campo | Para quê |
|---|---|
| `decupagem.planos` | Que personagens, objetos e paredes aparecem |
| `color_script` | Tipos de parede escolhidos pelo DoP |
| Store: biblioteca de marionetes e texturas | O que já existe (índice do Bibliotecário) |
| Fichas de silhueta (doc 03 §6.2 e, no futuro, doc 08) | Regras de cada personagem |

## Saída
| Campo | Conteúdo |
|---|---|
| `elenco` | Lista de itens. Cada um: id na biblioteca (ou `novo`), tipo (marionete / objeto / parede / mapa), planos onde aparece, **ficha** (para os novos), poses necessárias |
| | Os ids provisórios em `decupagem.planos[].marionetes` são trocados pelos ids reais da biblioteca |

**Ficha de item novo (o que a Arte recebe):**
| Campo | Exemplo |
|---|---|
| Nome e papel | Polifemo · ciclope, filho de Poseidon |
| Elemento de silhueta obrigatório | Um olho (único furo de luz, brilha em Brasa), ombros 3× maiores |
| Direção padrão | Esquerda |
| Furos decorativos | Sim (monstro) |
| Articulações | Ombro, cotovelo, quadril, joelho + mandíbula |
| Poses | dormindo, de pé, erguendo pedra, cego |
| Referência de vaso | Descrição do estilo figura negra a seguir |

## Regras de trabalho
1. **Reaproveitar antes de criar:** buscar na Store por personagem + versão. Personagem que já existe **não é redesenhado** (doc 06 §10); se precisar de pose nova, pede só a pose.
2. **Regra de ouro do doc 03 §6.1:** reconhecível só pela silhueta, em 1 segundo, num celular. A ficha precisa dizer **qual elemento** garante isso.
3. **Deuses que não aparecem:** Zeus e Hélio são só luz (doc 03 §6.2), então não entram no elenco como marionete; vão para o DoP como `luz_deus`.
4. **Poseidon nunca inteiro:** só tridente e ondas com rosto.
5. **Sereias são aves com cabeça humana** (como nos vasos), nunca sereia-peixe.
6. **Furos decorativos** só em deuses e monstros (doc 03 §6.3).

## Critérios de aceite
- [ ] Todo personagem/objeto dos planos está no elenco
- [ ] Todo item novo tem ficha completa
- [ ] Nenhum item existente foi marcado como novo por engano

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Personagem sem ficha no doc 03/08 | Escreve a ficha proposta e a destaca no Gate 2 (o humano aprova o design antes da criação) |
| Versão antiga incompatível com o estilo atual | Propõe nova versão (`_v2`) em vez de editar a antiga |

## Métricas
% de itens reaproveitados por episódio (deve subir com o tempo) · nº de marionetes refeitas por não serem reconhecíveis.

## Não faz
Não desenha marionetes (é o Designer de silhuetas) e não decide luz (é o DoP).
