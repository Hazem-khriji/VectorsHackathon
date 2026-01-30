import matplotlib.pyplot as plt
import numpy as np

# Representative data points for Qdrant HNSW performance
# These show the trade-off: small latency increase = huge recall gain, then plateaus
latency_ms = [5, 10, 15, 20, 30, 40, 50]
recall_score = [0.82, 0.94, 0.97, 0.985, 0.992, 0.995, 0.998]

plt.figure(figsize=(10, 6))
plt.plot(latency_ms, recall_score, marker='o', linestyle='-', color='#2A6FDB', linewidth=3, markersize=8, label='Qdrant HNSW Index')

# Styling to look "Professional/High-Tech" for presentation
plt.title('Recall@10 vs. Latency (ms)', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Latency (milliseconds)', fontsize=12)
plt.ylabel('Recall (Accuracy)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.ylim(0.8, 1.01)

# Annotate the "Sweet Spot"
plt.annotate('Target Operating Point\n(>99% Recall @ <30ms)', 
             xy=(30, 0.992), 
             xytext=(35, 0.90),
             arrowprops=dict(facecolor='black', shrink=0.05),
             fontsize=11,
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8))

plt.legend(loc='lower right')
plt.tight_layout()

# Save the plot
output_path = 'recall_latency_graph.png'
plt.savefig(output_path, dpi=300)
print(f"Graph generated at: {output_path}")
