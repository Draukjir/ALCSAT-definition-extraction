import json

from definition_extraction import definition_extraction
from extractExamples import extract_Examples
from spell.fitting_alc import OP
from spell.instance import ALCConcept
from yago_fragmentation import signature


def clean_name(uri):
    return (
        uri.replace("<http://yago-knowledge.org/resource/", "")
        .replace("<http://schema.org/", "")
        .replace(">", "")
        .replace("http://yago-knowledge.org/resource/", "")
        .replace("http://schema.org/", "")
    )

# LOAD JSON SIGNATURE IF USING PATTERN BASED EXTRACTION
# with open("extracted_signature.json", "r", encoding="utf-8") as f:
#     loaded_sig = json.load(f)

# sig = signature.Signature(
#     concept_names=loaded_sig["concept_names"], role_names=loaded_sig["role_names"]
# )

sig = signature.Signature()

# SETTINGS - CHANGE HERE
size = 8
samples = 1000
mode = "full_approx"
fragment_file = "fragment-sample-22-07.owl"
inverse = True
language = "alc_pos"        # Options: alc, alc_pos, alc_pos_no_all
exclude_atomic = []         # Options:[OP.TOP, OP.BOT]
timeout = 360
example_mode = "definition"
only_focus = False
# SETTINGS

result = {concept: (0.00, None) for concept in sorted(sig.domain_signature)}

for concept_name in sig.domain_signature:
    extract_Examples(
        concept_name, sig, samples, example_mode, fragment_file, only_focus
    )
    accuracy, concept, _, _, _, _ = definition_extraction(
        fragment_file,
        "P.txt",
        "N.txt",
        sig,
        concept_name,
        language=language,
        inverse_roles=inverse,
        max_size=size,
        md=mode,
        timeout=timeout,
        exclude_atomic=exclude_atomic,
    )

    definition = ALCConcept.to_dl_concept(concept)

    result[concept_name] = (accuracy, definition)

print(
    f"The Definition Extraction for {fragment_file} has been completed for all concept names:"
)
print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

for concept_name, (accuracy, definition) in result.items():
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print(f"Result for target concept A = {clean_name(concept_name)}:")
    print()
    print(f"Accuracy Training Data: {accuracy[0]}")
    print(f"Accuracy Overall Data: {accuracy[1]}")
    print("--- The extracted Definition is: ---")
    print(f"C = {clean_name(definition)}")
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")