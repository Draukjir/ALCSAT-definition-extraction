import json

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from definition_extraction import definition_extraction
from extractExamples import extract_Examples
from spell.instance import ALCConcept
from yago_fragmentation import signature

with open("extracted_signature.json", "r", encoding="utf-8") as f:
    loaded_sig = json.load(f)

sig = signature.Signature(
    concept_names=loaded_sig["concept_names"], role_names=loaded_sig["role_names"]
)

# sig = signature.Signature()

# SETTINGS - CHANGE HERE
size = 4
samples = 100
runs = 30
timeout = 180
language = "alc"
fragment_file = "fragment-auto-07-08.owl"
inverse = True
concept_name = "<http://yago-knowledge.org/resource/Actor>"
# SETTINGS



results = []

for run in range(runs):
    print(f"Run {run + 1}/{runs}")

    extract_Examples(concept_name, sig, samples, fragment_file=fragment_file)

    accuracy, concept, _, _, _, _ = definition_extraction(
        fragment_file,
        "P.txt",
        "N.txt",
        sig,
        concept_name,
        language=language,
        inverse_roles=inverse,
        max_size=size,
    )

    definition = ALCConcept.to_dl_concept(concept)

    results.append(
        {
            "run": run,
            "train_acc": accuracy[0],
            "overall_acc": accuracy[1],
            "definition": definition,
        }
    )

df = pd.DataFrame(results)

print("\n=== SUMMARY ===")
print(df[["train_acc", "overall_acc"]].describe())

print("\nSTD:")
print(df[["train_acc", "overall_acc"]].std())

plt.figure(figsize=(6, 4))
sns.boxplot(data=df[["train_acc", "overall_acc"]])
plt.title(f"Variance over {runs} runs ({concept_name})")

plt.savefig("boxplot.png", dpi=300, bbox_inches="tight")
plt.close()
