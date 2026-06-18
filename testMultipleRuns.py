from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sig = signature.Signature()

depth = 9
samples = 100
runs = 30

concept_name = "<http://yago-knowledge.org/resource/Actor>"

results = []

for run in range(runs):
    print(f"Run {run+1}/{runs}")

    extract_Examples(concept_name, sig, samples)

    accuracy, concept, _, _, _, _ = definition_extraction(
        "yago-fragment.owl",
        "P.txt",
        "N.txt",
        sig,
        concept_name,
        max_size=depth
    )

    definition = ALCConcept.to_dl_concept(concept)

    results.append({
        "run": run,
        "train_acc": accuracy[0],
        "overall_acc": accuracy[1],
        "definition": definition
    })

df = pd.DataFrame(results)

print("\n=== SUMMARY ===")
print(df[["train_acc", "overall_acc"]].describe())

print("\nSTD:")
print(df[["train_acc", "overall_acc"]].std())

plt.figure(figsize=(6,4))
sns.boxplot(data=df[["train_acc", "overall_acc"]])
plt.title(f"Variance over {runs} runs ({concept_name})")

plt.savefig("boxplot.png", dpi=300, bbox_inches="tight")
plt.close()

# === SUMMARY ===
#        train_acc  overall_acc
# count  30.000000    30.000000
# mean    0.883667     0.768218
# std     0.021930     0.046689
# min     0.830000     0.671617
# 25%     0.870000     0.745763
# 50%     0.885000     0.745763
# 75%     0.895000     0.772933
# max     0.930000     0.868563

# STD:
# train_acc      0.021930
# overall_acc    0.046689