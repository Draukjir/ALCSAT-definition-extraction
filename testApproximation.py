from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.instance import ALCConcept
from approximation import approximation

sig = signature.Signature()
iterations = 1
size = 4
fragment_file = "yago-fragment.owl"

result = {
    concept: (None, None, 0.00, 0.00, 0.00, 0.00) # (old_def, new_def, old_training_acc, new_training_acc, old_overall_acc, new_overall_acc)
    for concept in sig.domain_signature
}

for concept_name in sig.domain_signature:
    old_definition, new_definition, old_training_accuracy, new_training_accuracy, old_overall_accuracy, new_overall_accuracy = approximation(concept_name, sig, iterations, size, fragment_file)

    result[concept_name] = (old_definition, new_definition, old_training_accuracy, new_training_accuracy, old_overall_accuracy, new_overall_accuracy)

print(f"The result of the Approximation for the training data after {iterations} Iterations are the following:")
    
for concept_name, (old_definition, new_definition, old_training_accuracy, new_training_accuracy, old_overall_accuracy, new_overall_accuracy) in result.items():
    print("------------------------------------------------------------\n")
    print(f"Result for concept name {concept_name}:\n")

    print("Extracted definition BEFORE Approximation:")
    print(old_definition)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    print("Extracted definition AFTER Approximation:")
    print(new_definition)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    print(f"TRAINING DATA:")

    print(f"Accuracy BEFORE Approximation: {old_training_accuracy}")
    print(f"Accuracy AFTER Approximation: {new_training_accuracy}\n")

    improvement = new_training_accuracy - old_training_accuracy
    if new_training_accuracy > old_training_accuracy:    
       print(f"The Approximation has acchieved an IMPROVEMENT of: {improvement}")
    elif new_training_accuracy == old_training_accuracy:
        print(f"The Approximation has acchieved NO CHANGE")
    else:
        print(f"The Approximation has acchieved an DECLINE of {abs(improvement)}")

    print("------------------------------------------------------------\n")

    print(f"OVERALL DATA:")

    print(f"Accuracy BEFORE Approximation: {old_overall_accuracy}")
    print(f"Accuracy AFTER Approximation: {new_overall_accuracy}\n")

    improvement = new_overall_accuracy - old_overall_accuracy
    if new_overall_accuracy > old_overall_accuracy:    
       print(f"The Approximation has acchieved an IMPROVEMENT of: {improvement}")
    elif new_overall_accuracy == old_overall_accuracy:
        print(f"The Approximation has acchieved NO CHANGE")
    else:
        print(f"The Approximation has acchieved an DECLINE of {abs(improvement)}")

    print("------------------------------------------------------------\n")

# Beispiel: für 500 samples pos/neg
# The result of the Approximation for the training data after 2 Iterations are the following:
# The result of the Approximation for the training data after 2 Iterations are the following:
# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Chef>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Artist OR (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Author)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# ((((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Artist OR (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Author))) OR (http://yago-knowledge.org/resource/Actor AND (ALL.http://schema.org/spouse http://schema.org/EducationalOrganization AND (http://yago-knowledge.org/resource/Author OR EX.http://schema.org/award TOP)))) AND NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND ALL.http://schema.org/alumniOf http://schema.org/EducationalOrganization))) OR (NEG ((http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Artist OR (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Author))) OR (http://yago-knowledge.org/resource/Actor AND (ALL.http://schema.org/spouse http://schema.org/EducationalOrganization AND (http://yago-knowledge.org/resource/Author OR EX.http://schema.org/award TOP)))) AND NEG (http://yago-knowledge.org/resource/Artist OR (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR ALL.http://schema.org/birthPlace http://schema.org/Thing))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.898
# Accuracy AFTER Approximation: 0.919

# The Approximation has acchieved an IMPROVEMENT of: 0.02100000000000002
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.5817695328348952
# Accuracy AFTER Approximation: 0.6251704704896145

# The Approximation has acchieved an IMPROVEMENT of: 0.04340093765471931
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Actor>:

# Extracted definition BEFORE Approximation:
# (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/EducationalOrganization OR NEG (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_))) OR (NEG (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (EX.http://schema.org/spouse http://schema.org/Thing OR (http://yago-knowledge.org/resource/Musician AND EX.http://schema.org/alumniOf ALL.http://schema.org/award http://schema.org/Person)))) AND (http://yago-knowledge.org/resource/Author OR NEG (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND EX.http://schema.org/alumniOf http://schema.org/Thing))) OR (NEG (((http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/EducationalOrganization OR NEG (http://yago-knowledge.org/resource/Musician OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_))) OR (NEG (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR (http://schema.org/Person AND NEG (http://yago-knowledge.org/resource/Author OR http://yago-knowledge.org/resource/Erudite_Person_Q20826540))) AND (EX.http://schema.org/spouse http://schema.org/Thing OR (http://yago-knowledge.org/resource/Musician AND EX.http://schema.org/alumniOf ALL.http://schema.org/award http://schema.org/Person)))) AND (http://yago-knowledge.org/resource/Author AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR EX.http://schema.org/alumniOf (http://schema.org/Thing AND EX.http://schema.org/award TOP)))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.878
# Accuracy AFTER Approximation: 0.908

# The Approximation has acchieved an IMPROVEMENT of: 0.030000000000000027
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.9255783485051324
# Accuracy AFTER Approximation: 0.9034194190687441

# The Approximation has acchieved an DECLINE of 0.022158929436388308
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Musician>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND (EX.http://schema.org/spouse http://schema.org/Thing OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://schema.org/Person AND (EX.http://schema.org/spouse http://schema.org/Thing OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_))) AND ALL.http://schema.org/spouse (EX.http://schema.org/spouse EX.http://schema.org/award TOP OR ALL.http://schema.org/spouse EX.http://schema.org/birthPlace http://schema.org/Thing)) OR (NEG (http://schema.org/Person AND (EX.http://schema.org/spouse http://schema.org/Thing OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_))) AND (EX.http://schema.org/birthPlace http://schema.org/Thing AND (EX.http://schema.org/alumniOf TOP AND NEG EX.http://schema.org/alumniOf http://schema.org/Thing)))) AND (ALL.http://schema.org/award http://schema.org/Person OR (EX.http://schema.org/birthPlace http://schema.org/Thing OR ALL.http://schema.org/alumniOf http://schema.org/Person))) OR (NEG (((http://schema.org/Person AND (EX.http://schema.org/spouse http://schema.org/Thing OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_))) AND ALL.http://schema.org/spouse (EX.http://schema.org/spouse EX.http://schema.org/award TOP OR ALL.http://schema.org/spouse EX.http://schema.org/birthPlace http://schema.org/Thing)) OR (NEG (http://schema.org/Person AND (EX.http://schema.org/spouse http://schema.org/Thing OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_))) AND (EX.http://schema.org/birthPlace http://schema.org/Thing AND (EX.http://schema.org/alumniOf TOP AND NEG EX.http://schema.org/alumniOf http://schema.org/Thing)))) AND (http://yago-knowledge.org/resource/Author AND (ALL.http://schema.org/alumniOf http://schema.org/EducationalOrganization AND NEG ALL.http://schema.org/spouse ALL.http://schema.org/alumniOf http://schema.org/Thing))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.794
# Accuracy AFTER Approximation: 0.81

# The Approximation has acchieved an IMPROVEMENT of: 0.016000000000000014
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.7659956280910344
# Accuracy AFTER Approximation: 0.766707001667617

# The Approximation has acchieved an IMPROVEMENT of: 0.0007113735765825746
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://schema.org/Movie>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/CreativeWork AND (EX.http://schema.org/musicBy http://schema.org/Thing OR NEG http://yago-knowledge.org/resource/Album))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((http://schema.org/CreativeWork AND (EX.http://schema.org/musicBy http://schema.org/Thing OR NEG http://yago-knowledge.org/resource/Album)) OR BOT) OR BOT)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.999
# Accuracy AFTER Approximation: 0.999

# The Approximation has acchieved NO CHANGE
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.9995647752113119
# Accuracy AFTER Approximation: 0.9995647752113119

# The Approximation has acchieved NO CHANGE
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Author>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/EducationalOrganization))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/EducationalOrganization)) AND (ALL.http://schema.org/award http://schema.org/EducationalOrganization OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND ALL.http://schema.org/alumniOf http://schema.org/Thing))) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/EducationalOrganization)) AND (EX.http://schema.org/spouse http://schema.org/Person OR (EX.http://schema.org/birthPlace http://schema.org/Thing AND EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization)))) AND (EX.http://schema.org/award TOP OR ALL.http://schema.org/spouse ALL.http://schema.org/spouse ALL.http://schema.org/alumniOf http://schema.org/Intangible)) OR (NEG (((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/EducationalOrganization)) AND (ALL.http://schema.org/award http://schema.org/EducationalOrganization OR NEG (http://yago-knowledge.org/resource/Erudite_Person_Q20826540 AND ALL.http://schema.org/alumniOf http://schema.org/Thing))) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Erudite_Person_Q20826540 OR EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/EducationalOrganization)) AND (EX.http://schema.org/spouse http://schema.org/Person OR (EX.http://schema.org/birthPlace http://schema.org/Thing AND EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization)))) AND (ALL.http://schema.org/spouse http://schema.org/AdministrativeArea AND (ALL.http://schema.org/alumniOf http://schema.org/Person AND EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/Thing))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.772
# Accuracy AFTER Approximation: 0.791

# The Approximation has acchieved an IMPROVEMENT of: 0.019000000000000017
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.7679090085275461
# Accuracy AFTER Approximation: 0.7661716841143846

# The Approximation has acchieved an DECLINE of 0.001737324413161434
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Scientist>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP)) AND (ALL.http://schema.org/author ALL.http://schema.org/birthPlace http://schema.org/Thing AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/spouse ALL.http://schema.org/birthPlace http://schema.org/Thing)) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP)) AND (EX.http://schema.org/birthPlace http://schema.org/Thing AND (EX.http://schema.org/award TOP AND NEG EX.http://schema.org/spouse http://schema.org/Person)))) AND (ALL.http://schema.org/birthPlace http://schema.org/Thing OR ALL.http://schema.org/spouse EX.http://schema.org/award TOP)) OR (NEG (((http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP)) AND (ALL.http://schema.org/author ALL.http://schema.org/birthPlace http://schema.org/Thing AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/spouse ALL.http://schema.org/birthPlace http://schema.org/Thing)) OR (NEG (http://schema.org/Person AND (NEG http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND ALL.http://schema.org/spouse ALL.http://schema.org/spouse EX.http://schema.org/alumniOf TOP)) AND (EX.http://schema.org/birthPlace http://schema.org/Thing AND (EX.http://schema.org/award TOP AND NEG EX.http://schema.org/spouse http://schema.org/Person)))) AND (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ AND EX.http://schema.org/spouse (http://yago-knowledge.org/resource/Director__u0028_creative_work_u0029_ OR NEG ALL.http://schema.org/birthPlace http://schema.org/AdministrativeArea))))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.768
# Accuracy AFTER Approximation: 0.778

# The Approximation has acchieved an IMPROVEMENT of: 0.010000000000000009
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.6806620778900445
# Accuracy AFTER Approximation: 0.6776315907063868

# The Approximation has acchieved an DECLINE of 0.0030304871836577263
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Film_director>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/Person AND (EX.http://schema.org/birthPlace http://schema.org/Thing OR NEG EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# (((((http://schema.org/Person AND (EX.http://schema.org/birthPlace http://schema.org/Thing OR NEG EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization)) AND ALL.http://schema.org/spouse (EX.http://schema.org/spouse EX.http://schema.org/alumniOf http://schema.org/Thing OR ALL.http://schema.org/spouse EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/Person)) OR (NEG (http://schema.org/Person AND (EX.http://schema.org/birthPlace http://schema.org/Thing OR NEG EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization)) AND EX.http://schema.org/spouse EX.http://schema.org/birthPlace TOP)) AND (ALL.http://schema.org/author http://schema.org/AdministrativeArea AND (ALL.http://schema.org/alumniOf http://schema.org/AdministrativeArea OR ALL.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/Thing))) OR (NEG (((http://schema.org/Person AND (EX.http://schema.org/birthPlace http://schema.org/Thing OR NEG EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization)) AND ALL.http://schema.org/spouse (EX.http://schema.org/spouse EX.http://schema.org/alumniOf http://schema.org/Thing OR ALL.http://schema.org/spouse EX.http://schema.org/birthPlace ALL.http://schema.org/award http://schema.org/Person)) OR (NEG (http://schema.org/Person AND (EX.http://schema.org/birthPlace http://schema.org/Thing OR NEG EX.http://schema.org/alumniOf http://schema.org/EducationalOrganization)) AND EX.http://schema.org/spouse EX.http://schema.org/birthPlace TOP)) AND (EX.http://schema.org/birthPlace http://schema.org/Thing AND EX.http://schema.org/award TOP)))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.698
# Accuracy AFTER Approximation: 0.711

# The Approximation has acchieved an IMPROVEMENT of: 0.013000000000000012
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.5767925988550102
# Accuracy AFTER Approximation: 0.5787220656286809

# The Approximation has acchieved an IMPROVEMENT of: 0.0019294667736706739
# ------------------------------------------------------------

# ------------------------------------------------------------

# Result for concept name <http://yago-knowledge.org/resource/Album>:

# Extracted definition BEFORE Approximation:
# (http://schema.org/CreativeWork AND (ALL.http://schema.org/actor http://schema.org/EducationalOrganization AND ALL.http://schema.org/director http://schema.org/EducationalOrganization))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extracted definition AFTER Approximation:
# ((((http://schema.org/CreativeWork AND (ALL.http://schema.org/actor http://schema.org/EducationalOrganization AND ALL.http://schema.org/director http://schema.org/EducationalOrganization)) AND (ALL.http://schema.org/musicBy BOT AND ALL.http://schema.org/productionCompany BOT)) OR (NEG (http://schema.org/CreativeWork AND (ALL.http://schema.org/actor http://schema.org/EducationalOrganization AND ALL.http://schema.org/director http://schema.org/EducationalOrganization)) AND (ALL.http://schema.org/actor http://schema.org/Intangible AND (ALL.http://schema.org/musicBy http://schema.org/AdministrativeArea AND EX.http://schema.org/director EX.http://schema.org/award TOP)))) AND http://schema.org/CreativeWork)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TRAINING DATA:
# Accuracy BEFORE Approximation: 0.986
# Accuracy AFTER Approximation: 0.989

# The Approximation has acchieved an IMPROVEMENT of: 0.0030000000000000027
# ------------------------------------------------------------

# OVERALL DATA:
# Accuracy BEFORE Approximation: 0.9812406498165264
# Accuracy AFTER Approximation: 0.9806079205549428

# The Approximation has acchieved an DECLINE of 0.0006327292615835312
# ------------------------------------------------------------