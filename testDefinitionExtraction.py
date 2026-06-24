from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept

sig = signature.Signature()

# SETTINGS
size = 8
samples = 100
mode = "full_approx"
fragment_file = "yago-fragment.owl"
inverse = True
language = "alc"

result = {
    concept: (0.00, None)
    for concept in sorted(sig.domain_signature)
}

for concept_name in sig.domain_signature:
    extract_Examples(concept_name, sig, samples, fragment_file=fragment_file)
    accuracy, concept, _, _, _, _ = definition_extraction(fragment_file,
                          "P.txt",
                          "N.txt",
                          sig,
                          concept_name,
                          language=language,
                          inverse_roles=inverse,
                          max_size=size,
                          md = mode)
    
    definition = ALCConcept.to_dl_concept(concept)
    
    result[concept_name] = (accuracy, definition)

print(f"The Definition Extraction for {fragment_file} has been completed for all concept names:")
print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    
for concept_name, (accuracy, definition) in result.items():
    print(f"Result for {concept_name}:")
    print()
    print(f"Accuracy on training data: {accuracy[0]}")
    print(f"Accuracy on overall data: {accuracy[1]}")
    print(f"--- The extracted Definition is: ---")
    print(definition)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

# The Definition Extraction for yago-fragment.owl has been completed for all concept names:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Actor>:

# Accuracy on training data: 0.935
# Accuracy on overall data: 0.9214345508216945
# --- The extracted Definition is: ---
# (http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408 AND NEG http://yago-knowledge.org/resource/Painter)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Composer>:

# Accuracy on training data: 1.0
# Accuracy on overall data: 0.9976825131074591
# --- The extracted Definition is: ---
# (http://yago-knowledge.org/resource/Musician AND http://yago-knowledge.org/resource/Author)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Film_director>:

# Accuracy on training data: 0.99
# Accuracy on overall data: 0.9941490064766269
# --- The extracted Definition is: ---
# (http://yago-knowledge.org/resource/Visual_Artist_Q3391743 AND (http://yago-knowledge.org/resource/Writer OR NEG http://yago-knowledge.org/resource/Painter))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Painter>:

# Accuracy on training data: 0.99
# Accuracy on overall data: 0.9492620170066529
# --- The extracted Definition is: ---
# (http://yago-knowledge.org/resource/Visual_Artist_Q3391743 AND ALL.inv(http://schema.org/director) EX.http://schema.org/director EX.http://schema.org/award TOP)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Scientist>:

# Accuracy on training data: 0.92
# Accuracy on overall data: 0.9451116887694408
# --- The extracted Definition is: ---
# (http://schema.org/Person AND NEG http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Singer>:

# Accuracy on training data: 1.0
# Accuracy on overall data: 0.9967484689606556
# --- The extracted Definition is: ---
# (http://yago-knowledge.org/resource/Musician AND http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Writer>:

# Accuracy on training data: 0.965
# Accuracy on overall data: 0.9893554214213333
# --- The extracted Definition is: ---
# (http://yago-knowledge.org/resource/Author AND NEG http://yago-knowledge.org/resource/Composer)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -