from yago_fragmentation import signature
from spell.fitting_alc import OP
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept


def clean_name(uri):
    return (
        uri.replace("<http://yago-knowledge.org/resource/", "")
        .replace("<http://schema.org/", "")
        .replace(">", "")
        .replace("http://yago-knowledge.org/resource/", "")
        .replace("http://schema.org/", "")
    )


import json

with open("extracted_signature.json", "r", encoding="utf-8") as f:
    loaded_sig = json.load(f)

sig = signature.Signature(
    concept_names=loaded_sig["concept_names"], role_names=loaded_sig["role_names"]
)

# sig = signature.Signature()

# SETTINGS - CHANGE HERE
target_concept = "<http://yago-knowledge.org/resource/Political_party>"
samples = 250
example_mode = "definition"
fragment_file = "fragment-auto-07-08.owl"
only_focus = False
language = "alc_pos"
inverse = True
size = 4
mode = "full_approx"
exclude_atomic = []
timeout = 180
# END SETTINGS

extract_Examples(target_concept, sig, samples, example_mode, fragment_file, only_focus)

accuracy, concept, _, _, _, _ = definition_extraction(
    fragment_file,
    "P.txt",
    "N.txt",
    sig,
    target_concept,
    language,
    inverse,
    max_size=size,
    md=mode,
    timeout=timeout,
    exclude_atomic=exclude_atomic,
)

definition = ALCConcept.to_dl_concept(concept)

print(
    "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
)

print(f"The Direct Extraction for {clean_name(target_concept)} has been completed:")

print(f"Extracted Concept: {clean_name(definition)}")

print(f"Training Accuracy: {accuracy[0]}")

print(f"Overall Accuracy: {accuracy[1]}")
