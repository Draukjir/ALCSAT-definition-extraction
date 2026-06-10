from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept

sig = signature.Signature()

result = {
    concept: (0.00, None)
    for concept in sig.concept_names
}

for concept_name in sig.concept_names:
    extract_Examples(concept_name, sig)
    accuracy, concept, _, _, _ = definition_extraction("yago-fragment.owl",
                          "P.txt",
                          "N.txt",
                          sig,
                          concept_name)
    
    definition = ALCConcept.to_dl_concept(concept)
    
    result[concept_name] = (accuracy, definition)

print("The Definition Extraction has been completed for all concept names:")
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

# Beispielausgabe
# The Definition Extraction has been completed for all concept names:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://schema.org/Movie>:
# ---------------------------
# Accuracy on training data: 0.995
# Accuracy on overall data: 0.9995629878405164
# --- The extracted Definition is: ---
# (http://schema.org/CreativeWork AND NEG http://yago-knowledge.org/resource/Album)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Author>:
# ---------------------------
# Accuracy on training data: 0.82
# Accuracy on overall data: 0.847000166225484
# --- The extracted Definition is: ---
# (http://yago-knowledge.org/resource/Musician OR (http://schema.org/Person AND NEG (ALL.http://schema.org/spouse http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Scientist>:
# ---------------------------
# Accuracy on training data: 0.84
# Accuracy on overall data: 0.8281746833225793
# --- The extracted Definition is: ---
# (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Artist OR (http://yago-knowledge.org/resource/Musician AND (ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description AND ALL.http://schema.org/alumniOf http://schema.org/Thing))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Actor>:
# ---------------------------
# Accuracy on training data: 0.735
# Accuracy on overall data: 0.6866738995604855
# --- The extracted Definition is: ---
# (http://schema.org/Person AND NEG (ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description AND (http://yago-knowledge.org/resource/Musician OR EX.http://schema.org/award TOP)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Film_director>:
# ---------------------------
# Accuracy on training data: 0.78
# Accuracy on overall data: 0.6789694377467689
# --- The extracted Definition is: ---
# (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Artisan OR (http://yago-knowledge.org/resource/Musician OR (EX.http://schema.org/alumniOf TOP AND ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Album>:
# ---------------------------
# Accuracy on training data: 0.995
# Accuracy on overall data: 0.9812370750749355
# --- The extracted Definition is: ---
# (http://schema.org/CreativeWork AND (ALL.http://schema.org/actor http://yago-knowledge.org/resource/Artisan AND ALL.http://schema.org/director http://yago-knowledge.org/resource/Artisan))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Musician>:
# ---------------------------
# Accuracy on training data: 0.765
# Accuracy on overall data: 0.6395060779543899
# --- The extracted Definition is: ---
# (http://schema.org/Person AND (ALL.http://schema.org/award BOT OR (ALL.http://schema.org/alumniOf BOT AND ALL.http://schema.org/spouse http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Result for <http://yago-knowledge.org/resource/Chef>:
# ---------------------------
# Accuracy on training data: 0.68
# Accuracy on overall data: 0.5659084043962173
# --- The extracted Definition is: ---
# (http://schema.org/Person AND (EX.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR (ALL.http://schema.org/award BOT AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -