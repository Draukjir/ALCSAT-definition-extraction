from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction

sig = signature.Signature()

result = {
    concept: (0.00, None)
    for concept in sig.concept_names
}

for concept in sig.concept_names:
    extract_Examples(concept, sig)
    result[concept] = definition_extraction("yago-fragment.owl",
                          "P.txt",
                          "N.txt",
                          sig,
                          concept)
    
for concept, (accuracy, definition) in result.items():
    print("------------------------------------------------------------\n")
    print(f"The Definition Extraction for {concept} has acchieved an accuracy of: {accuracy}")
    print(f"The extracted Definition is: \n{definition}")
    print("------------------------------------------------------------\n")


# Beispiel
# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Actor> has acchieved an accuracy of: 0.885
# The extracted Definition is: 
# (http://schema.org/Person AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (EX.http://schema.org/spouse http://schema.org/Person OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Author))))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Musician> has acchieved an accuracy of: 0.825
# The extracted Definition is: 
# (http://schema.org/Person AND ((http://yago-knowledge.org/resource/Author OR ALL.http://schema.org/spouse http://yago-knowledge.org/resource/Erudite_Person_Q20826540) AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Album> has acchieved an accuracy of: 1.0
# The extracted Definition is: 
# (http://schema.org/CreativeWork AND NEG http://schema.org/Movie)
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Chef> has acchieved an accuracy of: 0.85
# The extracted Definition is: 
# (http://schema.org/Person AND (ALL.http://schema.org/spouse EX.http://schema.org/spouse http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Film_director> has acchieved an accuracy of: 0.775
# The extracted Definition is: 
# (http://schema.org/Person AND (EX.http://schema.org/spouse TOP OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Author> has acchieved an accuracy of: 0.785
# The extracted Definition is: 
# (http://schema.org/Person AND (EX.http://schema.org/spouse TOP OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://schema.org/Movie> has acchieved an accuracy of: 0.93
# The extracted Definition is: 
# (EX.http://schema.org/actor TOP OR EX.http://schema.org/director http://schema.org/Person)
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Scientist> has acchieved an accuracy of: 0.795
# The extracted Definition is: 
# (http://schema.org/Person AND (EX.http://schema.org/alumniOf TOP OR (EX.http://schema.org/award TOP OR ALL.http://schema.org/birthPlace http://schema.org/CreativeWork)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Single_music> has acchieved an accuracy of: -1
# The extracted Definition is: 
# None
# ------------------------------------------------------------