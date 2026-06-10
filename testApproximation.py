from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept
from approximation import approximation

sig = signature.Signature()
iterations = 1

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
# The Approximation for <http://yago-knowledge.org/resource/Album> has acchieved an improvement of: -0.0045629878405164526
# The extracted approximated Definition is: 
# (((http://schema.org/CreativeWork AND NEG http://schema.org/Movie) AND TOP) OR (NEG (http://schema.org/CreativeWork AND NEG http://schema.org/Movie) AND BOT))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Film_director> has acchieved an improvement of: 0.0645995306364292
# The extracted approximated Definition is: 
# (((http://yago-knowledge.org/resource/Actor OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Musician))) AND NEG (EX.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR EX.http://schema.org/spouse http://yago-knowledge.org/resource/Erudite_Person_Q20826540)) OR (NEG (http://yago-knowledge.org/resource/Actor OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Musician))) AND (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND (http://yago-knowledge.org/resource/Author AND (EX.http://schema.org/award TOP OR EX.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)))))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Scientist> has acchieved an improvement of: 0.05717530175287455
# The extracted approximated Definition is: 
# (((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Artisan OR (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Actor))) AND (ALL.http://schema.org/spouse EX.http://schema.org/award TOP AND NEG (http://yago-knowledge.org/resource/Author AND EX.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) OR (NEG (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Artisan OR (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Actor))) AND (NEG http://yago-knowledge.org/resource/Actor AND (EX.http://schema.org/award TOP OR EX.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Actor> has acchieved an improvement of: -0.0005416716564101698
# The extracted approximated Definition is: 
# (((http://schema.org/Person AND (EX.http://schema.org/spouse http://yago-knowledge.org/resource/Musician OR NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Musician))) AND (ALL.http://schema.org/award http://schema.org/Person OR (EX.http://schema.org/spouse http://schema.org/Person OR ALL.http://schema.org/alumniOf http://yago-knowledge.org/resource/Musician))) OR (NEG (http://schema.org/Person AND (EX.http://schema.org/spouse http://yago-knowledge.org/resource/Musician OR NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Musician)))AND (http://yago-knowledge.org/resource/Musician AND (ALL.http://schema.org/alumniOf http://yago-knowledge.org/resource/Author AND NEG http://yago-knowledge.org/resource/Author))))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://schema.org/Movie> has acchieved an improvement of: -0.013175183786402034
# The extracted approximated Definition is: 
# (((EX.http://schema.org/director http://schema.org/Thing OR (EX.http://schema.org/musicBy http://schema.org/Thing OR EX.http://schema.org/actor http://schema.org/Thing)) AND http://schema.org/CreativeWork) OR (NEG (EX.http://schema.org/director http://schema.org/Thing OR (EX.http://schema.org/musicBy http://schema.org/Thing OR EX.http://schema.org/actor http://schema.org/Thing)) AND http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Musician> has acchieved an improvement of: 0.14236138492638717
# The extracted approximated Definition is: 
# (((http://yago-knowledge.org/resource/Author OR (http://schema.org/Person AND (ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) AND (ALL.http://schema.org/spouse http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Author OR ALL.http://schema.org/award BOT))) OR (NEG (http://yago-knowledge.org/resource/Author OR (http://schema.org/Person AND (ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR ALL.http://schema.org/birthPlace http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) AND http://yago-knowledge.org/resource/Author))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Author> has acchieved an improvement of: 0.1101598624439436
# The extracted approximated Definition is: 
# (((http://schema.org/Person AND (ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP AND NEG EX.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)) AND (ALL.http://schema.org/award http://schema.org/Person OR (ALL.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description OR EX.http://schema.org/birthPlace ALL.http://schema.org/award http://www.w3.org/1999/02/22-rdf-syntax-ns#Description))) OR (NEG (http://schema.org/Person AND (ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP AND NEG EX.http://schema.org/alumniOf http://www.w3.org/1999/02/22-rdf-syntax-ns#Description)) AND (http://schema.org/Person AND ALL.http://schema.org/award BOT)))
# ------------------------------------------------------------

# ------------------------------------------------------------

# The Approximation for <http://yago-knowledge.org/resource/Chef> has acchieved an improvement of: 0.15331885265093903
# The extracted approximated Definition is: 
# (((http://schema.org/Person AND (ALL.http://schema.org/alumniOf http://schema.org/Person OR ALL.http://schema.org/award http://schema.org/CreativeWork)) AND (ALL.http://schema.org/alumniOf ALL.http://schema.org/award BOT AND ALL.http://schema.org/spouse ALL.http://schema.org/alumniOf BOT)) OR (NEG (http://schema.org/Person AND (ALL.http://schema.org/alumniOf http://schema.org/Person OR ALL.http://schema.org/award http://schema.org/CreativeWork)) AND (http://schema.org/Person AND ALL.http://schema.org/birthPlace http://schema.org/Person)))
# ------------------------------------------------------------