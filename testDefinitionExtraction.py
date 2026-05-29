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
    result[concept] = definition_extraction("yago_fragmentation/yago-fragment.owl",
                          "P.txt",
                          "N.txt",
                          sig,
                          concept,
                          max_size=9)
    
for concept, (accuracy, definition) in result.items():
    print("------------------------------------------------------------\n")
    print(f"The Definition Extraction for {concept} has acchieved an accuracy of: {accuracy}")
    print(f"The extracted Definition is: \n{definition}")
    print("------------------------------------------------------------\n")


# Beispiel
# The Definition Extraction for <http://yago-knowledge.org/resource/Actor> has acchieved an accuracy of: 0.88
# The extracted Definition is: 
# (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Single_music> has acchieved an accuracy of: -1
# The extracted Definition is: 
# None
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Scientist> has acchieved an accuracy of: 0.805
# The extracted Definition is: 
# (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Musician OR EX.http://schema.org/award TOP))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Musician> has acchieved an accuracy of: 0.695
# The extracted Definition is: 
# (http://schema.org/Person AND (ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR NEG http://yago-knowledge.org/resource/Author))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Author> has acchieved an accuracy of: 0.785
# The extracted Definition is: 
# (http://schema.org/Person AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse http://schema.org/Person)
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Album> has acchieved an accuracy of: 1.0
# The extracted Definition is: 
# (http://schema.org/CreativeWork AND ALL.http://schema.org/actor http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_)
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Film_director> has acchieved an accuracy of: 1.0
# The extracted Definition is: 
# http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Chef_Q3499072> has acchieved an accuracy of: -1
# The extracted Definition is: 
# None
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://schema.org/Movie> has acchieved an accuracy of: 0.945
# The extracted Definition is: 
# (EX.http://schema.org/director http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (EX.http://schema.org/actor http://schema.org/Thing OR EX.http://schema.org/productionCompany TOP))
# ------------------------------------------------------------