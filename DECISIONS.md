# DECISIONS.md — Architecture & Engineering Decisions

## Decision 1: Dual-Storage Strategy for Vector Database
- **Decision**: Support both PostgreSQL + pgvector (for production/Docker) and an in-memory/SQLite cosine similarity engine (for instant local zero-dependency development).
- **Rationale**: Enables any developer or judge to immediately test and run the entire AI teacher with zero external database configuration requirements, while supporting enterprise pgvector deployment when available.

## Decision 2: Pure Pedagogical State Machine & Deterministic Adaptation Wrapper
- **Decision**: Wrap LLM generative responses in a deterministic pedagogical state machine and strict adaptation policy.
- **Rationale**: Never trust an LLM to reliably manage educational state or decide score calculations alone. The deterministic policy ensures that a student with a score < 40% is mathematically guaranteed a remedial explanation and visual analogy before advancing.

## Decision 3: Subject-Aware Client-Side Visual Engine
- **Decision**: Use deterministic client-side rendering (KaTeX for Math, Recharts for Curves/Analytics, Monaco for Code, Mermaid/SVG for Science/History) rather than hallucination-prone image generation models.
- **Rationale**: Mathematical proofs, code execution traces, physics free-body diagrams, and biological timelines must be mathematically and semantically accurate. Deterministic rendering is instantaneous, crisp, lightweight, and 100% accurate.

## Decision 4: Multilingual Canonical Concept Structure
- **Decision**: Store concepts in canonical technical form (e.g. formula $F = ma$, key terms) and translate pedagogical delivery dynamically without mutating lesson state.
- **Rationale**: Prevents corruption of mathematical formulas and scientific symbols when switching between English, Hindi, Hinglish, and Bengali during a live lesson.

## Decision 5: Multi-Factor Mastery Formula
- **Decision**: Formula: $\text{Mastery} = 100 \times (0.35 \times \text{Correctness} + 0.25 \times \text{Consistency} + 0.20 \times \text{Difficulty} + 0.10 \times \text{Reasoning} + 0.10 \times \text{Retention})$.
- **Rationale**: Transparent, deterministic mastery metric that rewards deep reasoning and consistency rather than superficial rote memorization.
