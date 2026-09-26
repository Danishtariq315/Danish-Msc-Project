from src.evaluation.evaluator import run_full_evaluation

summary, results = run_full_evaluation(n_cases=5)

print("\n\nFINAL COMPARISON TABLE")
print(f"{'Config':<35} {'TCR':>6} {'Steps':>7} {'Latency':>9}")
print("-"*60)
for config, metrics in summary.items():
    print(f"{config:<35} {metrics['tcr_percent']:>5}% "
          f"{metrics['avg_steps']:>7} "
          f"{metrics['avg_latency_s']:>8}s")