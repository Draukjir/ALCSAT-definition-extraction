from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction

sig = signature.Signature()

accuracy = {
    concept: 0.00
    for concept in sig.concept_names
}

for concept in sig.concept_names:
    extract_Examples(concept, sig)
    accuracy[concept] = definition_extraction("yago_fragmentation/yago-fragment.owl",
                          "P.txt",
                          "N.txt",
                          sig,
                          concept)
    
for concept in accuracy:
    print(f"The Definition Extraction for {concept} has acchieved an accuracy of: {accuracy[concept]}")


# Beispiel
# The Definition Extraction for <http://yago-knowledge.org/resource/Film_director> has acchieved an accuracy of: 1.0
# The Definition Extraction for <http://yago-knowledge.org/resource/Actor> has acchieved an accuracy of: 0.88
# The Definition Extraction for <http://yago-knowledge.org/resource/Musician> has acchieved an accuracy of: 0.88
# The Definition Extraction for <http://yago-knowledge.org/resource/Chef_Q3499072> has acchieved an accuracy of: 0.85
# The Definition Extraction for <http://yago-knowledge.org/resource/Single_music> has acchieved an accuracy of: 0.89
# The Definition Extraction for <http://yago-knowledge.org/resource/Scientist> has acchieved an accuracy of: 0.825
# The Definition Extraction for <http://yago-knowledge.org/resource/Author> has acchieved an accuracy of: 0.77
# The Definition Extraction for <http://yago-knowledge.org/resource/Album> has acchieved an accuracy of: 0.77
# The Definition Extraction for <http://schema.org/Movie> has acchieved an accuracy of: 0.73