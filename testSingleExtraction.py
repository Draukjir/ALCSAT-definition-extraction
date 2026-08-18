from yago_fragmentation import signature
from spell.fitting_alc import OP
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept
from spell.structures import ind, Structure


def clean_name(uri):
    return (
        uri.replace("<http://yago-knowledge.org/resource/", "")
        .replace("<http://schema.org/", "")
        .replace(">", "")
        .replace("http://yago-knowledge.org/resource/", "")
        .replace("http://schema.org/", "")
    )


import json

# with open("extracted_signature.json", "r", encoding="utf-8") as f:
#     loaded_sig = json.load(f)

# sig = signature.Signature(
#     concept_names=loaded_sig["concept_names"], role_names=loaded_sig["role_names"]
# )

sig = signature.Signature()

# SETTINGS - CHANGE HERE
target_concept = "<http://schema.org/Movie>"
samples = 250
example_mode = "definition"
fragment_file = "fragment-sample-22-07.owl"
only_focus = False
language = "alc_pos_no_all"
inverse = True
size = 5
mode = "full_approx"
exclude_atomic = []
timeout = 180
exclude_top_classes = True
# END SETTINGS

extract_Examples(target_concept, sig, samples, example_mode, fragment_file, only_focus)

accuracy, concept, A, _, _, _ = definition_extraction(
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
    exclude_top_classes=exclude_top_classes
)

definition = ALCConcept.to_dl_concept(concept)

print(
    "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
)

print(f"The Direct Extraction for {clean_name(target_concept)} has been completed:")

print(f"Extracted Concept: {clean_name(definition)}")

print(f"Training Accuracy: {accuracy[0]}")

print(f"Overall Accuracy: {accuracy[1]}")
