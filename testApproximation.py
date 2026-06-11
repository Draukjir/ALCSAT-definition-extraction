from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept
from approximation import approximation

sig = signature.Signature()
iterations = 2

result = {
    concept: (0.00, None)
    for concept in sig.concept_names
}

for concept in sig.concept_names:
    improvement, definition = approximation(concept, sig, iterations)
    
    definition = ALCConcept.to_dl_concept(definition)
    
    result[concept] = (improvement, definition)

print(f"The result of the Approximation for the training data after {iterations} are the following:")
    
for concept, (improvement, definition) in result.items():
    print("------------------------------------------------------------\n")
    print(f"The Approximation for {concept} has acchieved an improvement of: {improvement}")
    print(f"The extracted approximated Definition is: \n{definition}")
    print("------------------------------------------------------------\n")

# Beispiel:
# ----------------------------------------------------------------------------
# Accuracy before approximation: 0.7088801943229529
# Accuracy after approximation: 0.77
# The accuracy has increased by 0.06111980567704711
# The result of the Approximation for the training data after 2 are the following:
# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Chef> has acchieved an improvement of: 0.35323046716510487
# The extracted approximated Definition is: 
# (((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Artist OR http://yago-knowledge.org/resource/Author))) OR (EX.http://schema.org/award TOP AND NEG (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) OR (http://yago-knowledge.org/resource/Author AND (ALL.http://schema.org/birthPlace http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND EX.http://schema.org/award TOP)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Album> has acchieved an improvement of: -0.0045629878405164526
# The extracted approximated Definition is: 
# (((http://schema.org/CreativeWork AND NEG http://schema.org/Movie) OR BOT) OR BOT)
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Author> has acchieved an improvement of: 0.0443327029872328
# The extracted approximated Definition is: 
# (((((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND (http://yago-knowledge.org/resource/Musician OR NEG http://yago-knowledge.org/resource/Artist))) AND (EX.http://schema.org/birthPlace TOP OR NEG http://yago-knowledge.org/resource/Actor)) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND (http://yago-knowledge.org/resource/Musician OR NEG http://yago-knowledge.org/resource/Artist))) AND (http://yago-knowledge.org/resource/Musician AND EX.http://schema.org/birthPlace TOP))) AND NEG (http://yago-knowledge.org/resource/Artist AND EX.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)) OR (NEG (((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND (http://yago-knowledge.org/resource/Musician OR NEG http://yago-knowledge.org/resource/Artist))) AND (EX.http://schema.org/birthPlace TOP OR NEG http://yago-knowledge.org/resource/Actor)) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND (http://yago-knowledge.org/resource/Musician OR NEG http://yago-knowledge.org/resource/Artist))) AND (http://yago-knowledge.org/resource/Musician AND EX.http://schema.org/birthPlace TOP))) AND http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Musician> has acchieved an improvement of: -0.007340874846509582
# The extracted approximated Definition is: 
# (((((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408 AND ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) AND (EX.http://schema.org/birthPlace TOP OR (ALL.http://schema.org/award http://yago-knowledge.org/resource/Actor AND ALL.http://schema.org/spouse BOT))) OR (NEG (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408 AND ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) AND (ALL.http://schema.org/award http://www.w3.org/1999/02/22-rdf-syntax-ns#Description AND (EX.http://schema.org/birthPlace TOP AND ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)))) AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (ALL.http://schema.org/alumniOf http://yago-knowledge.org/resource/Actor OR NEG http://yago-knowledge.org/resource/Actor))) OR (NEG (((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408 AND ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) AND (EX.http://schema.org/birthPlace TOP OR (ALL.http://schema.org/award http://yago-knowledge.org/resource/Actor AND ALL.http://schema.org/spouse BOT))) OR (NEG (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408 AND ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) AND (ALL.http://schema.org/award http://www.w3.org/1999/02/22-rdf-syntax-ns#Description AND (EX.http://schema.org/birthPlace TOP AND ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)))) AND EX.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Film_director> has acchieved an improvement of: 0.09555329850343441
# The extracted approximated Definition is: 
# (((((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Actor AND EX.http://schema.org/spouse http://yago-knowledge.org/resource/Actor))) AND (ALL.http://schema.org/spouse http://schema.org/Person AND (EX.http://schema.org/birthPlace TOP OR ALL.http://schema.org/alumniOf http://yago-knowledge.org/resource/Actor))) OR (NEG (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Actor AND EX.http://schema.org/spouse http://yago-knowledge.org/resource/Actor))) AND (http://yago-knowledge.org/resource/Actor AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/award TOP))) AND NEG (EX.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR (EX.http://schema.org/award TOP AND ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) OR (NEG (((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Actor AND EX.http://schema.org/spouse http://yago-knowledge.org/resource/Actor))) AND (ALL.http://schema.org/spouse http://schema.org/Person AND (EX.http://schema.org/birthPlace TOP OR ALL.http://schema.org/alumniOf http://yago-knowledge.org/resource/Actor))) OR (NEG (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Actor AND EX.http://schema.org/spouse http://yago-knowledge.org/resource/Actor))) AND (http://yago-knowledge.org/resource/Actor AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/award TOP))) AND (http://yago-knowledge.org/resource/Actor AND EX.http://schema.org/spouse (EX.http://schema.org/birthPlace TOP AND EX.http://schema.org/spouse EX.http://schema.org/spouse http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Scientist> has acchieved an improvement of: 0.08066892352019095
# The extracted approximated Definition is: 
# (((((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Actor AND ALL.http://schema.org/spouse EX.http://schema.org/birthPlace TOP)) AND (ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP)) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Actor AND ALL.http://schema.org/spouse EX.http://schema.org/birthPlace TOP)) AND BOT)) AND http://schema.org/Person) OR (NEG (((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Actor AND ALL.http://schema.org/spouse EX.http://schema.org/birthPlace TOP)) AND (ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP)) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Actor AND ALL.http://schema.org/spouse EX.http://schema.org/birthPlace TOP)) AND BOT)) AND BOT))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://schema.org/Movie> has acchieved an improvement of: 0.04902599909559047
# The extracted approximated Definition is: 
# ((http://schema.org/CreativeWork AND http://schema.org/CreativeWork) AND http://schema.org/CreativeWork)
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Actor> has acchieved an improvement of: 0.06111980567704711
# The extracted approximated Definition is: 
# (((((EX.http://schema.org/birthPlace TOP AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/spouse EX.http://schema.org/award TOP) AND http://schema.org/Person) OR (NEG (EX.http://schema.org/birthPlace TOP AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/spouse EX.http://schema.org/award TOP) AND (http://schema.org/Person AND (ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description AND ALL.http://schema.org/spouse http://schema.org/CreativeWork)))) AND http://schema.org/Person) OR (NEG (((EX.http://schema.org/birthPlace TOP AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/spouse EX.http://schema.org/award TOP) AND http://schema.org/Person) OR (NEG (EX.http://schema.org/birthPlace TOP AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/spouse EX.http://schema.org/award TOP) AND (http://schema.org/Person AND (ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description AND ALL.http://schema.org/spouse http://schema.org/CreativeWork)))) AND BOT))