from yago_fragmentation import signature
from recursive_approx import approx_start
from spell.fitting_alc import OP
import json


def clean_name(uri):
    return (
        uri.replace("<http://yago-knowledge.org/resource/", "")
        .replace("<http://schema.org/", "")
        .replace(">", "")
        .replace("http://yago-knowledge.org/resource/", "")
        .replace("http://schema.org/", "")
    )


# with open("extracted_signature.json", "r", encoding="utf-8") as f:
#     loaded_sig = json.load(f)

# sig = signature.Signature(
#     concept_names=loaded_sig["concept_names"], role_names=loaded_sig["role_names"]
# )

sig = signature.Signature()

# SETTINGS
samples = 100
iterations = 1
size = 4
fragment_file = "fragment-sample-22-07.owl"
language = "alc_pos"
inverse = True
exclude_atomic = []  # noch nicht integriert in approximation!
threshold = 10
# SETTINGS 

result = {
    concept_name: {
        "old_def": "empty",
        "new def": "empty",
        "old_train_acc": 0.00,
        "new_train_acc": 0.00,
        "old_all_acc": 0.00,
        "new_all_acc": 0.00,
    }
    for concept_name in sig.domain_signature
}

for concept_name in sig.domain_signature:
    (
        result[concept_name]["old_def"],
        result[concept_name]["new_def"],
        result[concept_name]["old_train_acc"],
        result[concept_name]["new_train_acc"],
        result[concept_name]["old_all_acc"],
        result[concept_name]["new_all_acc"],
    ) = approx_start(
        concept_name,
        sig,
        iterations,
        size,
        fragment_file,
        samples,
        language=language,
        inverse=inverse,
        threshold=threshold,
    )

print(
    f"The result of RECURSIV APPROX for the training data after {iterations} Iterations are the following:"
)

for concept_name, res in result.items():
    print("------------------------------------------------------------\n")
    print(f"Result for concept name {clean_name(concept_name)}:\n")

    print("Extracted definition BEFORE Approximation:")
    print(clean_name(res["old_def"]))
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    print("Extracted definition AFTER Approximation:")
    print(clean_name(res["new_def"]))
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    print("TRAINING DATA:")
    old_train_acc = res["old_train_acc"]
    new_train_acc = res["new_train_acc"]

    print(f"Accuracy BEFORE Approximation: {old_train_acc}")
    print(f"Accuracy AFTER Approximation: {new_train_acc}\n")

    improvement = new_train_acc - old_train_acc
    if improvement > 0:
        print(f"The Approximation has acchieved an IMPROVEMENT of: {improvement}")
    elif improvement == 0:
        print("The Approximation has acchieved NO CHANGE")
    else:
        print(f"The Approximation has acchieved an DECLINE of {abs(improvement)}")

    print("------------------------------------------------------------\n")

    print("OVERALL DATA:")
    old_all_acc = res["old_all_acc"]
    new_all_acc = res["new_all_acc"]

    print(f"Accuracy BEFORE Approximation: {old_all_acc}")
    print(f"Accuracy AFTER Approximation: {new_all_acc}\n")

    improvement = new_all_acc - old_all_acc
    if improvement > 0:
        print(f"The Approximation has acchieved an IMPROVEMENT of: {improvement}")
    elif improvement == 0:
        print("The Approximation has acchieved NO CHANGE")
    else:
        print(f"The Approximation has acchieved an DECLINE of {abs(improvement)}")

    print("------------------------------------------------------------\n")
