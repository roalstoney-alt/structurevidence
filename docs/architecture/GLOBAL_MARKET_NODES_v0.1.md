# Global Market Nodes v0.1

## Objective

StructureEvidence serves three market-facing language nodes from one canonical evidence system:

- English: `/en/`
- Simplified Chinese: `/zh-cn/`
- Spanish: `/es/`
- Global language gateway / x-default: `/`

The localized homepages are **not translations of one marketing page**. They are market-specific entry interfaces that use different framing while preserving the same evidence, machine states, case identifiers, timestamps, and Decision Memory records.

## Core rule

```
ONE EVIDENCE CORE
      ↓
ONE CANONICAL MACHINE STATE
      ↓
MULTIPLE MARKET INTERFACES
```

Localization may change:

- headline
- examples
- explanation order
- market vocabulary
- CTA wording
- buyer framing

Localization must not change:

- evidence state
- case ID
- knowledge cutoff
- source provenance
- state-transition history
- canonical enum values
- outcome history

## Market positioning

### English node

Primary concept: **Structural Openings**

Core promise:

> The world changes before consensus does. We record the gap.

Commercial language:

- decision intelligence
- technical due diligence
- evidence trail
- structural opening
- decision memory
- verification

Primary buyers:

- engineering
- procurement
- technical diligence
- corporate strategy
- industrial investors
- supply-chain risk teams

### Simplified Chinese node

Primary concept: **结构性窗口**

Core promise:

> 先找结构变化，再决定把资源投向哪里。

The page does not sell a social theory. It converts the familiar intuition that effort has different returns under different structural constraints into a verifiable industrial decision tool.

Commercial language:

- 结构性窗口
- 路径依赖
- 技术迁移
- 产业替代
- 证据边界
- 决策记忆

Primary buyers:

- 工业品企业
- 技术采购
- 创业团队
- 供应链团队
- 技术尽调
- 跨境分销与替代方案团队

### Spanish node

Primary concept: **Ventanas estructurales**

Core promise:

> El mundo cambia antes de que llegue el consenso. Registramos esa brecha.

Commercial language:

- cambio estructural
- diligencia técnica
- trazabilidad
- evidencia verificable
- memoria de decisión
- riesgo de cadena de suministro

Primary buyers:

- compras técnicas
- ingeniería
- energía
- manufactura
- distribuidores industriales
- estrategia corporativa
- diligencia tecnológica

## URL and SEO policy

Every node has:

- a self-canonical URL
- reciprocal `hreflang` references for `en`, `zh-CN`, `es`
- `x-default` pointing to `/`
- explicit HTML `lang`
- no forced browser-language redirect

The root page is a global language gateway. Browser preference may be used in future only as a non-blocking suggestion, never as a forced redirect.

## Language pack contract

Language packs live in `locales/`.

They contain:

- market positioning
- navigation labels
- CTA labels
- localized display labels for canonical evidence states
- localization invariants

Canonical machine states remain English enums. For example:

```
NOT_ESTABLISHED
```

may display as:

- English: `NOT ESTABLISHED`
- Simplified Chinese: `尚未建立`
- Spanish: `NO ESTABLECIDO`

The underlying stored value remains `NOT_ESTABLISHED`.

## Public evidence boundary

Localized pages may summarize the 800VDC and sodium-ion cases, but the canonical public case records remain authoritative.

Future localization of full case pages must reference the same case IDs and frozen state files instead of creating language-specific research forks.

## Next expansion

After homepage validation:

1. localized case index
2. localized case summaries
3. localized intake forms
4. localized email / WhatsApp handoff
5. locale-aware outbound content templates
6. shared analytics by market node
