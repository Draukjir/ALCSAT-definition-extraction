This repository contains our implementation of bounded fitting for the description logic ALCQI(f) (ALCSAT). Given an instance of a learning problem in the form of a knowledge base, positive and negative examples, the tool searches for a description logic concept that covers all positive examples, excludes all negative examples and is of minimal size. Any syntactic fragment of the description logic ALC is supported as well as extensions of ALC with number restrictions, inverse roles and data values.

As this is a Fork of <https://github.com/spell-system/SPELL>, it also contains SPELL, a tool to learn concepts in the description logic EL.
## Definition Extraction
yago-fragment.owl can be obtained by following https://github.com/Draukjir/simple-yago-fragmentation and then added to the actor_example folder

This repository contains our implementation of bounded fitting for the description logic ALC (ALSAT). As this is a Fork of <https://github.com/spell-system/SPELL>, it also contains SPELL, a tool to learn concepts in the description logic EL.

## Requirements
- Installation of Python 3
- uv package manager obtainable from https://github.com/astral-sh/uv

- Packages from `requirements.txt`

## Run
For full instructions on how to run either ALCSAT of SPELL, run

`uv run spell_cli.py --help`

The `--language` option can be used to choose a syntactic fragment of ALCQI(f). The following fragments are available.
- `el`: exists, and (using SPELL, default)
- `el`_alcsat: exists, and (using ALCSAT)
- `fl0`: forall, and
- `ex-or`: exists, or
- `all-or`: forall, or
- `elu`: exists, and, or 
- `alc`:  forall, exists, and, or, neg
- `alcq`: number restrictions, forall, exists, and, or, neg    
    - when chosing alcq, the option `--max_q` becomes available to set the maximum values in number restrictions (defaults to 2)

Further options influencing the language in which concepts are learned are:
- `--inverse`: this is a flag that adds inverse roles to the language
- `--feature_values`: this is a flag that adds feature values to the language
    - when using this flag, the number of thresholds used to form feature values is set with the `--max_thresholds` option
    

The `--mode` options allows switching between exact mode and approximate mode.
- `exact`: only consider exact fittings: concepts that cover all positive examples and exclude all negative examples
- `neg_approx`: (SPELL only) search for an approximate fitting, that covers all positive examples but not necessarily excludes all negative examples
- `full_approx`: search for an approximate fitting that may not cover some positive examples and may cover some negative examples (incremental search for fittings with increasing accuracy)

The `--workers` option can be used to set the number of worker processes (defaults to 1)

## IJCAI2026 Benchmark Reproduction
Instructions to reproduce experimental results reported in our paper _Bounded Fitting for Expressive Description Logics_ accepted at IJCAI-ECAI 2026 can be found in the following repository: https://github.com/SAT-based-Concept-Learning/ALCSAT-IJCAI-reproduce

## ISWC2025 Benchmark Reproduction
Results shown in our paper _Bounded Fitting for the Description Logic ALC_ accepted at ISWC 2025 can be reproduced as follows. Instructions to reproduce the family benchmarks are in the folder alc_benchmarks in a separate README file. Instructions and required files to reproduce the results on the SML benchmarks can be found in the following repository.
https://github.com/SAT-based-Concept-Learning/ALC-SAT-eval