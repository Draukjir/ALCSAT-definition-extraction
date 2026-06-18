from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept

sig = signature.Signature()

depth = 9
samples = 500

result = {
    concept: (0.00, None)
    for concept in sig.concept_names
}

for concept_name in sig.concept_names:
    extract_Examples(concept_name, sig, samples)
    accuracy, concept, _, _, _, _ = definition_extraction("yago-fragment.owl",
                          "P.txt",
                          "N.txt",
                          sig,
                          concept_name,
                          max_size=depth)
    
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
# The result of the Approximation for the training data after 2 Iterations are the following:
# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Musician>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND (http://yago-knowledge.org/resource/Actor OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Executive_Q978044)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://schema.org/Person AND (http://yago-knowledge.org/resource/Actor OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Executive_Q978044))) AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://yago-knowledge.org/resource/Author OR (NEG http://yago-knowledge.org/resource/Actor OR EX.http://schema.org/birthPlace http://schema.org/Thing)))) OR (NEG (http://schema.org/Person AND (http://yago-knowledge.org/resource/Actor OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Executive_Q978044))) AND (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND NEG (ALL.http://schema.org/birthPlace http://schema.org/Thing OR ALL.http://schema.org/alumniOf http://schema.org/Thing)))) AND NEG EX.http://schema.org/spouse (http://yago-knowledge.org/resource/Actor OR ALL.http://schema.org/spouse (http://yago-knowledge.org/resource/Author AND ALL.http://schema.org/spouse http://yago-knowledge.org/resource/Author))) OR (NEG (((http://schema.org/Person AND (http://yago-knowledge.org/resource/Actor OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Executive_Q978044))) AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://yago-knowledge.org/resource/Author OR (NEG http://yago-knowledge.org/resource/Actor OR EX.http://schema.org/birthPlace http://schema.org/Thing)))) OR (NEG (http://schema.org/Person AND (http://yago-knowledge.org/resource/Actor OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Executive_Q978044))) AND (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND NEG (ALL.http://schema.org/birthPlace http://schema.org/Thing OR ALL.http://schema.org/alumniOf http://schema.org/Thing)))) AND (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND (http://yago-knowledge.org/resource/Author AND (ALL.http://schema.org/award http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND EX.http://schema.org/alumniOf TOP)))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.792
# Accuracy AFTER Approximation: 0.829

# The Approximation has acchieved an IMPROVEMENT of: 0.03699999999999992
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.9190419335062316
# Accuracy AFTER Approximation: 0.8911482248726945

# The Approximation has acchieved an DECLINE of 0.02789370863353713
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Scientist>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Artist OR EX.http://schema.org/alumniOf EX.http://schema.org/award TOP))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Artist OR EX.http://schema.org/alumniOf EX.http://schema.org/award TOP)) AND (ALL.http://schema.org/birthPlace http://yago-knowledge.org/resource/Artist OR (NEG http://yago-knowledge.org/resource/Author OR EX.http://schema.org/alumniOf TOP))) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Artist OR EX.http://schema.org/alumniOf EX.http://schema.org/award TOP)) AND (NEG http://yago-knowledge.org/resource/Actor AND (EX.http://schema.org/award TOP AND EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization)))) AND (NEG http://yago-knowledge.org/resource/Artisan AND ALL.http://schema.org/spouse (http://schema.org/Person AND ALL.http://schema.org/spouse EX.http://schema.org/birthPlace TOP))) OR (NEG (((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Artist OR EX.http://schema.org/alumniOf EX.http://schema.org/award TOP)) AND (ALL.http://schema.org/birthPlace http://yago-knowledge.org/resource/Artist OR (NEG http://yago-knowledge.org/resource/Author OR EX.http://schema.org/alumniOf TOP))) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Artist OR EX.http://schema.org/alumniOf EX.http://schema.org/award TOP)) AND (NEG http://yago-knowledge.org/resource/Actor AND (EX.http://schema.org/award TOP AND EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization)))) AND (EX.http://schema.org/spouse http://yago-knowledge.org/resource/Artist AND NEG http://yago-knowledge.org/resource/Creative_And_Performing_Artist_Q108289408)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.877
# Accuracy AFTER Approximation: 0.899

# The Approximation has acchieved an IMPROVEMENT of: 0.02200000000000002
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.8543069380372167
# Accuracy AFTER Approximation: 0.8770816167126319

# The Approximation has acchieved an IMPROVEMENT of: 0.02277467867541516
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Author>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (EX.http://schema.org/award TOP OR NEG http://yago-knowledge.org/resource/Actor)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://schema.org/Person AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (EX.http://schema.org/award TOP OR NEG http://yago-knowledge.org/resource/Actor))) AND (ALL.http://schema.org/award http://schema.org/Person OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization))) OR (NEG (http://schema.org/Person AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (EX.http://schema.org/award TOP OR NEG http://yago-knowledge.org/resource/Actor))) AND (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/spouse (http://schema.org/Person AND NEG ALL.http://schema.org/alumniOf http://schema.org/EducationalOrganization)))) AND (EX.http://schema.org/birthPlace TOP OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND EX.http://schema.org/alumniOf http://schema.org/Thing))) OR (NEG (((http://schema.org/Person AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (EX.http://schema.org/award TOP OR NEG http://yago-knowledge.org/resource/Actor))) AND (ALL.http://schema.org/award http://schema.org/Person OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization))) OR (NEG (http://schema.org/Person AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (EX.http://schema.org/award TOP OR NEG http://yago-knowledge.org/resource/Actor))) AND (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/spouse (http://schema.org/Person AND NEG ALL.http://schema.org/alumniOf http://schema.org/EducationalOrganization)))) AND (EX.http://schema.org/birthPlace EX.http://schema.org/award TOP OR (http://yago-knowledge.org/resource/Musician AND NEG ALL.http://schema.org/birthPlace http://schema.org/Thing))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.807
# Accuracy AFTER Approximation: 0.84

# The Approximation has acchieved an IMPROVEMENT of: 0.03299999999999992
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.8006947510281851
# Accuracy AFTER Approximation: 0.8292542552830212

# The Approximation has acchieved an IMPROVEMENT of: 0.02855950425483611
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://schema.org/Movie>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/CreativeWork AND NEG http://yago-knowledge.org/resource/Album)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((http://schema.org/CreativeWork AND NEG http://yago-knowledge.org/resource/Album) OR BOT) OR BOT)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.998
# Accuracy AFTER Approximation: 0.998

# The Approximation has acchieved NO CHANGE
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.9995629878405164
# Accuracy AFTER Approximation: 0.9995629878405164

# The Approximation has acchieved NO CHANGE
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Chef>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Artist)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# ((((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Artist))) OR (http://yago-knowledge.org/resource/Actor AND (NEG EX.http://schema.org/alumniOf http://schema.org/Thing AND ALL.http://schema.org/spouse EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization))) AND (EX.http://schema.org/spouse http://yago-knowledge.org/resource/Artist OR NEG (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_))) OR (NEG ((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Artist))) OR (http://yago-knowledge.org/resource/Actor AND (NEG EX.http://schema.org/alumniOf http://schema.org/Thing AND ALL.http://schema.org/spouse EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization))) AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Artist OR ALL.http://schema.org/birthPlace http://schema.org/AdministrativeArea))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.895
# Accuracy AFTER Approximation: 0.908

# The Approximation has acchieved an IMPROVEMENT of: 0.013000000000000012
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.5817695328348952
# Accuracy AFTER Approximation: 0.669037911921942

# The Approximation has acchieved an IMPROVEMENT of: 0.08726837908704677
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Film_director>:

# Extracted definition BEFORE Approximation:
# (http://yago-knowledge.org/resource/Actor OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://yago-knowledge.org/resource/Actor OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (http://yago-knowledge.org/resource/Actor OR (NEG http://yago-knowledge.org/resource/Author OR EX.http://schema.org/birthPlace TOP))) OR (NEG (http://yago-knowledge.org/resource/Actor OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (http://yago-knowledge.org/resource/Musician AND (EX.http://schema.org/spouse http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/birthPlace EX.http://schema.org/award TOP)))) AND (http://yago-knowledge.org/resource/Author OR (EX.http://schema.org/birthPlace http://schema.org/Thing OR NEG http://yago-knowledge.org/resource/Actor))) OR (NEG (((http://yago-knowledge.org/resource/Actor OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (http://yago-knowledge.org/resource/Actor OR (NEG http://yago-knowledge.org/resource/Author OR EX.http://schema.org/birthPlace TOP))) OR (NEG (http://yago-knowledge.org/resource/Actor OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (http://yago-knowledge.org/resource/Musician AND (EX.http://schema.org/spouse http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/birthPlace EX.http://schema.org/award TOP)))) AND (ALL.http://schema.org/birthPlace http://schema.org/EducationalOrganization AND NEG ALL.http://schema.org/spouse http://yago-knowledge.org/resource/Author)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.84
# Accuracy AFTER Approximation: 0.871

# The Approximation has acchieved an IMPROVEMENT of: 0.031000000000000028
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.8454004693635708
# Accuracy AFTER Approximation: 0.7606567515250742

# The Approximation has acchieved an DECLINE of 0.08474371783849666
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Album>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/CreativeWork AND NEG http://schema.org/Movie)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((http://schema.org/CreativeWork AND NEG http://schema.org/Movie) OR BOT) OR BOT)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.997
# Accuracy AFTER Approximation: 0.997

# The Approximation has acchieved NO CHANGE
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.9995629878405164
# Accuracy AFTER Approximation: 0.9995629878405164

# The Approximation has acchieved NO CHANGE
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Actor>:

# Extracted definition BEFORE Approximation:
# (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (NEG http://yago-knowledge.org/resource/Musician OR (EX.http://schema.org/alumniOf TOP OR EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/AdministrativeArea))) OR (NEG (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR ALL.http://schema.org/spouse http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND NEG (http://yago-knowledge.org/resource/Artisan OR (http://yago-knowledge.org/resource/Author AND ALL.http://schema.org/birthPlace http://schema.org/EducationalOrganization))) OR (NEG (((http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (NEG http://yago-knowledge.org/resource/Musician OR (EX.http://schema.org/alumniOf TOP OR EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/AdministrativeArea))) OR (NEG (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR ALL.http://schema.org/spouse http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (EX.http://schema.org/award TOP AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR ALL.http://schema.org/birthPlace http://schema.org/Thing))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.882
# Accuracy AFTER Approximation: 0.906

# The Approximation has acchieved an IMPROVEMENT of: 0.02400000000000002
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.7457634843721235
# Accuracy AFTER Approximation: 0.7334654796141424

# The Approximation has acchieved an DECLINE of 0.01229800475798104
# ------------------------------------------------------------