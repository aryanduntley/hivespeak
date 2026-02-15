"""HiveSpeak token compression benchmarking tool.

Measures BPE token counts for English vs HiveSpeak (verbose and compressed)
using tiktoken. Reports per-pair and aggregate compression ratios.

Usage (via CLI):
    python3 -m compiler.htc bench                    # Run all benchmark pairs
    python3 -m compiler.htc bench --category commands # Filter by category
    python3 -m compiler.htc bench --verbose           # Show per-pair details
"""

import json
import os

try:
    import tiktoken
except ImportError:
    tiktoken = None


# Default encoding — cl100k_base is used by GPT-4, GPT-3.5-turbo
_ENCODING_NAME = "cl100k_base"

_BENCHMARKS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "benchmarks", "pairs.json",
)


def _get_encoder():
    """Get tiktoken encoder, raising a clear error if not installed."""
    if tiktoken is None:
        raise RuntimeError(
            "tiktoken is required for benchmarking. Install: pip install tiktoken"
        )
    return tiktoken.get_encoding(_ENCODING_NAME)


def count_tokens(text, encoder=None):
    """Count BPE tokens in a string."""
    if encoder is None:
        encoder = _get_encoder()
    return len(encoder.encode(text))


def load_pairs(path=None):
    """Load benchmark pairs from JSON file."""
    path = path or _BENCHMARKS_PATH
    with open(path, "r") as f:
        return json.load(f)


def bench_pair(pair, encoder):
    """Benchmark a single English/HiveSpeak pair. Returns a result dict."""
    eng_tokens = count_tokens(pair["english"], encoder)
    verbose_tokens = count_tokens(pair["hivespeak_verbose"], encoder)
    shorthand_tokens = count_tokens(pair["hivespeak_shorthand"], encoder)
    compressed_tokens = count_tokens(pair["hivespeak_compressed"], encoder)

    return {
        "id": pair["id"],
        "category": pair["category"],
        "english_tokens": eng_tokens,
        "verbose_tokens": verbose_tokens,
        "shorthand_tokens": shorthand_tokens,
        "compressed_tokens": compressed_tokens,
        "verbose_ratio": eng_tokens / verbose_tokens if verbose_tokens else 0,
        "shorthand_ratio": eng_tokens / shorthand_tokens if shorthand_tokens else 0,
        "compressed_ratio": eng_tokens / compressed_tokens if compressed_tokens else 0,
        "verbose_savings": 1 - (verbose_tokens / eng_tokens) if eng_tokens else 0,
        "shorthand_savings": 1 - (shorthand_tokens / eng_tokens) if eng_tokens else 0,
        "compressed_savings": 1 - (compressed_tokens / eng_tokens) if eng_tokens else 0,
    }


def run_benchmark(category=None, pairs_path=None):
    """Run benchmarks on all pairs (or filtered by category). Returns results list + summary."""
    encoder = _get_encoder()
    pairs = load_pairs(pairs_path)

    if category:
        pairs = [p for p in pairs if p["category"] == category]

    results = [bench_pair(p, encoder) for p in pairs]

    # Aggregate stats
    total_eng = sum(r["english_tokens"] for r in results)
    total_verbose = sum(r["verbose_tokens"] for r in results)
    total_shorthand = sum(r["shorthand_tokens"] for r in results)
    total_compressed = sum(r["compressed_tokens"] for r in results)

    summary = {
        "pair_count": len(results),
        "total_english_tokens": total_eng,
        "total_verbose_tokens": total_verbose,
        "total_shorthand_tokens": total_shorthand,
        "total_compressed_tokens": total_compressed,
        "overall_verbose_ratio": total_eng / total_verbose if total_verbose else 0,
        "overall_shorthand_ratio": total_eng / total_shorthand if total_shorthand else 0,
        "overall_compressed_ratio": total_eng / total_compressed if total_compressed else 0,
        "overall_verbose_savings": 1 - (total_verbose / total_eng) if total_eng else 0,
        "overall_shorthand_savings": 1 - (total_shorthand / total_eng) if total_eng else 0,
        "overall_compressed_savings": 1 - (total_compressed / total_eng) if total_eng else 0,
        "avg_verbose_savings": (
            sum(r["verbose_savings"] for r in results) / len(results) if results else 0
        ),
        "avg_shorthand_savings": (
            sum(r["shorthand_savings"] for r in results) / len(results) if results else 0
        ),
        "avg_compressed_savings": (
            sum(r["compressed_savings"] for r in results) / len(results) if results else 0
        ),
    }

    return results, summary


def format_report(results, summary, verbose=False):
    """Format benchmark results as a readable report string."""
    lines = []
    lines.append("=" * 72)
    lines.append("HiveSpeak Token Compression Benchmark")
    lines.append(f"Encoding: {_ENCODING_NAME}  |  Pairs: {summary['pair_count']}")
    lines.append("=" * 72)

    if verbose:
        lines.append("")
        lines.append(f"{'ID':<25} {'Cat':<12} {'Eng':>5} {'Verb':>5} {'Short':>5} {'Comp':>5} {'V.Sav':>7} {'S.Sav':>7} {'C.Sav':>7}")
        lines.append("-" * 86)
        for r in results:
            lines.append(
                f"{r['id']:<25} {r['category']:<12} "
                f"{r['english_tokens']:>5} {r['verbose_tokens']:>5} {r['shorthand_tokens']:>5} {r['compressed_tokens']:>5} "
                f"{r['verbose_savings']:>6.0%} {r['shorthand_savings']:>6.0%} {r['compressed_savings']:>6.0%}"
            )
        lines.append("-" * 86)

    # Per-category summary
    categories = sorted(set(r["category"] for r in results))
    if len(categories) > 1:
        lines.append("")
        lines.append("By Category:")
        lines.append(f"  {'Category':<15} {'Pairs':>5} {'Eng':>6} {'Verb':>6} {'Short':>6} {'Comp':>6} {'V.Sav':>7} {'S.Sav':>7} {'C.Sav':>7}")
        lines.append("  " + "-" * 72)
        for cat in categories:
            cat_results = [r for r in results if r["category"] == cat]
            eng = sum(r["english_tokens"] for r in cat_results)
            verb = sum(r["verbose_tokens"] for r in cat_results)
            short = sum(r["shorthand_tokens"] for r in cat_results)
            comp = sum(r["compressed_tokens"] for r in cat_results)
            v_sav = 1 - (verb / eng) if eng else 0
            s_sav = 1 - (short / eng) if eng else 0
            c_sav = 1 - (comp / eng) if eng else 0
            lines.append(
                f"  {cat:<15} {len(cat_results):>5} {eng:>6} {verb:>6} {short:>6} {comp:>6} "
                f"{v_sav:>6.0%} {s_sav:>6.0%} {c_sav:>6.0%}"
            )

    # Overall summary
    lines.append("")
    lines.append("Overall:")
    lines.append(f"  English total:                {summary['total_english_tokens']:>6} tokens")
    lines.append(f"  HiveSpeak verbose total:      {summary['total_verbose_tokens']:>6} tokens")
    lines.append(f"  HiveSpeak shorthand total:    {summary['total_shorthand_tokens']:>6} tokens")
    lines.append(f"  HiveSpeak compressed total:   {summary['total_compressed_tokens']:>6} tokens")
    lines.append("")
    lines.append(f"  Verbose savings:     {summary['overall_verbose_savings']:>6.1%}  ({summary['overall_verbose_ratio']:.2f}x compression)")
    lines.append(f"  Shorthand savings:   {summary['overall_shorthand_savings']:>6.1%}  ({summary['overall_shorthand_ratio']:.2f}x compression)")
    lines.append(f"  Compressed savings:  {summary['overall_compressed_savings']:>6.1%}  ({summary['overall_compressed_ratio']:.2f}x compression)")
    lines.append("")
    lines.append(f"  Avg verbose savings per pair:     {summary['avg_verbose_savings']:.1%}")
    lines.append(f"  Avg shorthand savings per pair:   {summary['avg_shorthand_savings']:.1%}")
    lines.append(f"  Avg compressed savings per pair:  {summary['avg_compressed_savings']:.1%}")
    lines.append("=" * 86)

    return "\n".join(lines)
