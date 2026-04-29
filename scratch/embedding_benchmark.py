"""
Sprint 2 Phase 2 micro-benchmark: embedding model selection.

Compares:
  - intfloat/multilingual-e5-base (512 tokens, 768-dim, MIT)
  - BAAI/bge-m3 (8192 tokens, 1024-dim, MIT)

Metric: cosine similarity gap between relevant query-passage pairs
vs. irrelevant pairs (higher gap = better retrieval discrimination).
Also measures encode time per batch.

Models are downloaded on first run (~1 GB and ~2.2 GB respectively).
Run on CPU (WSL2). bge-m3 will be 2-3x slower than e5-base.

Run:
  uv run python scratch/embedding_benchmark.py
"""

import time
import sys
import numpy as np
from sentence_transformers import SentenceTransformer

# ── Benchmark pairs ────────────────────────────────────────────────────────────
# 6 relevant (query semantically matches passage) + 4 irrelevant (no match)
# Drawn from actual dsm-residential-heating-ds-guide content.

RELEVANT_PAIRS = [
    # EN query, EN passage
    (
        "What is the heating curve and how does it affect flow temperature?",
        "The Heizkennlinie defines the relationship between outdoor temperature and "
        "heating system flow temperature. It is the single most impactful control "
        "parameter for heating efficiency. A simpler linear approximation: "
        "T_Vorlauf = T_base - m * T_outdoor.",
    ),
    # DE query, DE passage
    (
        "Was ist die Heizkennlinie und wie beeinflusst sie die Vorlauftemperatur?",
        "Die Heizkennlinie beschreibt den Zusammenhang zwischen Außentemperatur und "
        "der Vorlauftemperatur des Heizungssystems. Sie ist der entscheidende "
        "Regelparameter für die Heizungseffizienz.",
    ),
    # EN query, passage contains both EN and DE
    (
        "How does hydraulic balancing improve heating efficiency?",
        "Hydraulischer Abgleich (hydraulic balancing) ensures equal flow through all "
        "radiator circuits. Without balancing, distant radiators underperform and "
        "return temperatures rise, reducing system efficiency. Spreizung (temperature "
        "spread) between Vorlauf and Rücklauf indicates heat extraction efficiency.",
    ),
    # DE query, EN-dominant passage
    (
        "Wie beeinflusst die Vorlauftemperatur den COP einer Wärmepumpe?",
        "Modern heat pumps achieve COP values of 3-5. The key optimization insight: "
        "COP improves dramatically with lower flow temperatures. Reducing Vorlauftemperatur "
        "from 55°C to 35°C can improve COP by 30-50%.",
    ),
    # EN query, technical passage
    (
        "What is Spreizung and why does it matter for heating systems?",
        "Spreizung (temperature spread) between Vorlauf and Rücklauf indicates heat "
        "extraction efficiency. Higher spreizung means more energy extracted per unit "
        "water flow, reducing pumping energy and improving system efficiency. "
        "Typical target: ΔT ≥ 20-30K.",
    ),
    # Mixed: EN query about a DE concept
    (
        "Explain Anschlussleistung and peak demand in district heating",
        "District heating contracts often specify maximum Rücklauftemperatur (50-60°C). "
        "Violations trigger penalties. Coordinated control prevents simultaneous heating "
        "and DHW peaks that drive up measured Anschlussleistung costs.",
    ),
]

IRRELEVANT_PAIRS = [
    (
        "What is the heating curve and how does it affect flow temperature?",
        "Battery arbitrage strategies store midday PV surplus in batteries for evening "
        "operation. Economics depend on battery costs, degradation, and alternative "
        "revenue from grid feed-in tariffs.",
    ),
    (
        "Was ist die Heizkennlinie und wie beeinflusst sie die Vorlauftemperatur?",
        "Without storage, PV self-consumption in residential buildings typically reaches "
        "20-30%. Adding heat pump flexibility increases this to 40-60%. Batteries push "
        "further to 60-80%.",
    ),
    (
        "How does hydraulic balancing improve heating efficiency?",
        "Buffer tanks in heat pump systems store thermal energy for bridging defrost "
        "cycles in air-source heat pumps. PV self-consumption optimization and "
        "predictive control leverage weather forecasts.",
    ),
    (
        "Explain Anschlussleistung and peak demand in district heating",
        "A building with high thermal mass can be pre-heated during periods of cheap "
        "electricity, storing thermal energy for later use. This enables peak shaving "
        "strategies that work independently of the heating contract penalties.",
    ),
]


# ── Model configurations ───────────────────────────────────────────────────────
MODELS = [
    {
        "id": "intfloat/multilingual-e5-base",
        "short_name": "e5-base",
        "query_prefix": "query: ",
        "passage_prefix": "passage: ",
        "dim": 768,
        "max_tokens": 512,
    },
    {
        "id": "BAAI/bge-m3",
        "short_name": "bge-m3",
        "query_prefix": "",   # no prefix required for bge-m3
        "passage_prefix": "",
        "dim": 1024,
        "max_tokens": 8192,
    },
]


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def run_benchmark(cfg: dict) -> dict:
    print(f"\n{'─' * 60}")
    print(f"Model: {cfg['id']}")
    print(f"{'─' * 60}")

    t_load = time.time()
    model = SentenceTransformer(cfg["id"])
    load_time = time.time() - t_load
    print(f"Load time: {load_time:.1f}s")

    queries_rel = [cfg["query_prefix"] + q for q, _ in RELEVANT_PAIRS]
    passages_rel = [cfg["passage_prefix"] + p for _, p in RELEVANT_PAIRS]
    queries_irr = [cfg["query_prefix"] + q for q, _ in IRRELEVANT_PAIRS]
    passages_irr = [cfg["passage_prefix"] + p for _, p in IRRELEVANT_PAIRS]

    all_texts = queries_rel + passages_rel + queries_irr + passages_irr
    t_enc = time.time()
    all_embs = model.encode(all_texts, normalize_embeddings=True, show_progress_bar=False)
    enc_time = time.time() - t_enc
    n = len(RELEVANT_PAIRS)
    m = len(IRRELEVANT_PAIRS)

    q_rel_embs = all_embs[:n]
    p_rel_embs = all_embs[n : 2 * n]
    q_irr_embs = all_embs[2 * n : 2 * n + m]
    p_irr_embs = all_embs[2 * n + m :]

    rel_sims = [cosine_sim(q_rel_embs[i], p_rel_embs[i]) for i in range(n)]
    irr_sims = [cosine_sim(q_irr_embs[i], p_irr_embs[i]) for i in range(m)]

    avg_rel = float(np.mean(rel_sims))
    avg_irr = float(np.mean(irr_sims))
    gap = avg_rel - avg_irr

    print(f"Avg relevant sim:   {avg_rel:.4f}")
    print(f"Avg irrelevant sim: {avg_irr:.4f}")
    print(f"Gap (rel - irr):    {gap:.4f}  ← higher is better")
    print(f"Encode time ({len(all_texts)} texts): {enc_time:.2f}s  "
          f"({len(all_texts)/enc_time:.1f} texts/sec)")

    print("\nPer-pair relevant similarities:")
    for i, (q, _) in enumerate(RELEVANT_PAIRS):
        print(f"  [{i+1}] {q[:55]:<55} → {rel_sims[i]:.4f}")

    return {
        "model": cfg["short_name"],
        "avg_relevant": avg_rel,
        "avg_irrelevant": avg_irr,
        "gap": gap,
        "encode_time_s": enc_time,
        "texts_per_sec": len(all_texts) / enc_time,
        "load_time_s": load_time,
        "per_pair_relevant": rel_sims,
        "per_pair_irrelevant": irr_sims,
    }


# ── Main ──────────────────────────────────────────────────────────────────────
print("=" * 60)
print("Sprint 2 Phase 2: Embedding Model Micro-Benchmark")
print("=" * 60)
print(f"Relevant pairs:   {len(RELEVANT_PAIRS)}")
print(f"Irrelevant pairs: {len(IRRELEVANT_PAIRS)}")
print("Device: CPU (WSL2)")

results = []
for cfg in MODELS:
    try:
        r = run_benchmark(cfg)
        results.append(r)
    except Exception as e:
        print(f"\nERROR running {cfg['id']}: {e}")
        import traceback
        traceback.print_exc()

# ── Summary table ─────────────────────────────────────────────────────────────
if results:
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Model':<12} {'Avg-Rel':>9} {'Avg-Irr':>9} {'Gap':>9} {'Texts/s':>9} {'Load(s)':>9}")
    print("─" * 60)
    for r in results:
        print(f"{r['model']:<12} {r['avg_relevant']:>9.4f} {r['avg_irrelevant']:>9.4f} "
              f"{r['gap']:>9.4f} {r['texts_per_sec']:>9.1f} {r['load_time_s']:>9.1f}")

    winner_by_gap = max(results, key=lambda r: r["gap"])
    winner_by_speed = max(results, key=lambda r: r["texts_per_sec"])
    print()
    print(f"Best retrieval discrimination (gap): {winner_by_gap['model']}")
    print(f"Fastest encode:                      {winner_by_speed['model']}")
    print()
    print("Decision input for Phase 2 model selection (Opus turn post-Thu 21:00).")