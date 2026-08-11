from definition_extraction import definition_extraction
from extractExamples import extract_Examples
from spell.fitting import mode
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


# SETTINGS - CHANGE HEREE
target_concept = "<http://yago-knowledge.org/resource/Journalist>"
sig = signature.Signature()
samples = 0
example_mode = "suf_crit"
fragment_file = "fragment-tiny-sample-10-08.owl"
only_focus = False

language = "alc"
inverse = True
size = 15
md = "full_approx"
exclude_atomic = [OP.TOP, OP.BOT]
timeout = 500
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
    md=md,
    timeout=timeout,
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
