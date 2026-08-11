from yago_fragmentation import signature
from spell.fitting_alc import OP
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept
from spell.fitting import mode


def clean_name(uri):
    return (
        uri.replace("<http://yago-knowledge.org/resource/", "")
        .replace("<http://schema.org/", "")
        .replace(">", "")
        .replace("http://yago-knowledge.org/resource/", "")
        .replace("http://schema.org/", "")
    )


# SETTINGS - CHANGE HERE
target_concept = "<http://yago-knowledge.org/resource/Journalist>"
sig = signature.Signature()
samples = 0
example_mode = "nec_crit"
fragment_file = "fragment-tiny-sample-10-08.owl"
only_focus = False

language = "alc_pos"
inverse = True
size = 5
mode = mode.exact
exclude_atomic = [OP.TOP, OP.BOT]
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
    exclude_atomic=exclude_atomic,
)

definition = ALCConcept.to_dl_concept(concept)

print(
    "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
)

print(
    f"The Extraction of a Necessary Criterion for {clean_name(target_concept)} has been completed:"
)

print(f"Extracted Concept: {clean_name(definition)}")

print(f"Training Accuracy: {accuracy[0]}")

print(f"Overall Accuracy: {accuracy[1]}")
