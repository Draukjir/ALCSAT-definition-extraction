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
    print("---------------------------")
    print(f"Accuracy on training data: {accuracy[0]}")
    print(f"Accuracy on overall data: {accuracy[1]}")
    print(f"--- The extracted Definition is: ---")
    print(definition)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")


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


######OVERALL DATA
# #########################################################################################################################################################################
# The Definition Extraction for <http://yago-knowledge.org/resource/Musician> has acchieved an accuracy of: 0.8959482091438316 for the Overall Data
# The extracted Definition is: 
# (http://schema.org/Person AND (ALL.http://schema.org/spouse http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND (http://yago-knowledge.org/resource/Actor OR (ALL.http://schema.org/award http://schema.org/Person AND NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540))))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Album> has acchieved an accuracy of: 0.9995629878405164 for the Overall Data
# The extracted Definition is: 
# (http://schema.org/CreativeWork AND NEG http://schema.org/Movie)
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Scientist> has acchieved an accuracy of: 0.7715552449502306 for the Overall Data
# The extracted Definition is: 
# (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408 OR (http://yago-knowledge.org/resource/Author AND (EX.http://schema.org/award TOP AND ALL.http://schema.org/birthPlace http://schema.org/Person))))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Actor> has acchieved an accuracy of: 0.7891063324759912 for the Overall Data
# The extracted Definition is: 
# (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (EX.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR (http://yago-knowledge.org/resource/Author AND ALL.http://schema.org/spouse http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Film_director> has acchieved an accuracy of: 0.7928446184946406 for the Overall Data
# The extracted Definition is: 
# (EX.http://schema.org/birthPlace TOP AND (EX.http://schema.org/spouse http://schema.org/Thing OR (ALL.http://schema.org/alumniOf http://schema.org/Thing AND ALL.http://schema.org/spouse http://yago-knowledge.org/resource/Author)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Author> has acchieved an accuracy of: 0.7391645113953825 for the Overall Data
# The extracted Definition is: 
# (http://schema.org/Person AND (ALL.http://schema.org/spouse ALL.http://schema.org/award BOT AND (EX.http://schema.org/alumniOf TOP OR ALL.http://schema.org/birthPlace ALL.http://schema.org/award http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://yago-knowledge.org/resource/Chef> has acchieved an accuracy of: 0.5514342756947958 for the Overall Data
# The extracted Definition is: 
# (http://schema.org/Person AND (ALL.http://schema.org/spouse http://www.w3.org/1999/02/22-rdf-syntax-ns#Description AND (ALL.http://schema.org/award http://schema.org/Thing OR ALL.http://schema.org/alumniOf http://schema.org/Thing)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Definition Extraction for <http://schema.org/Movie> has acchieved an accuracy of: 0.9632748922662253 for the Overall Data
# The extracted Definition is: 
# (EX.http://schema.org/actor http://schema.org/Thing OR EX.http://schema.org/director http://schema.org/Thing)