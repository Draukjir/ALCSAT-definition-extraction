# Definition Extraction
This repository contains an implementation of Definition Extraction for the description logic ALCI. 

This is a fork of the ALC-SAT tool <https://github.com/SAT-based-Concept-Learning/ALCSAT.git>.
 
It uses it to find definitions for concept names of the Knowledge Base YAGO. The ALC-SAT tool does find fitting concepts for a given set of positive and negative examples.

## Obtain Yago 4.5.0.2
Download YAGO using:

```
wget https://yago-knowledge.org/data/yago4.5/yago-4.5.0.2.zip
```
## Extracting the needed files
Extract the required YAGO files:

```
unzip yago-4.5.0.2.zip yago-schema.ttl yago-taxonomy.ttl yago-facts.ttl
```
Make sure that all files are in the `yago_fragmentation` folder
## Extracting fragments
Before performing definition extraction, a fragment of YAGO has to be extracted. Three Methods are available:
- Standard Fragment:
```uv run -m yago_fragmentation.extract```
- Sampled Fragment:
``` uv run -m yago_fragmentation.extract --samples=<AMOUNT>```
- Pattern based Fragment:
```uv run -m yago_fragmentation.extractAuto```

You can change the focus of the fragments by modifying the concept and role names in `signature.py`

The extraction scripts use the [uv package manager](https://github.com/astral-sh/uv) and require the [lightrdf library](https://github.com/ozekik/lightrdf).

Depending on the selected extraction method, the resulting files are, for example: 
```
custom-schema.owl
result.nt
```

## Convert to OWL
The extracted fragment can be converted into a single OWL file using [ROBOT](https://github.com/ontodev/robot).
```
robot merge --input custom-schema.owl --input result.nt --output fragment.owl
```

## Definition Extraction
The repository contains several scripts for direct definition extraction and approximation-based extraction.

Before running an extraction, make sure that the configuration parameters in the respective script are set correctly for the selected fragment and target concepts.

For pattern-based fragments, the signature is generated automatically and stored in `extracted_signature.json`. In this case, the corresponding signature can be instantiated using this file. An example of this is provided in the respective scripts.

### Available Scripts:
relevant for the bachelor thesis:
* `testSingleExtraction`: performs one definition extraction for a single concept
* `testDefinitionExtraction`: performs definition extraction for all target concepts
* `testMultipleRuns`: performs multiple extractions for one concept to evaluate variation between runs
* `testApproximation`: performs approximation-based definition extraction
* `individual_definition_extraction`: performs definition extraction for individual concepts

others:
* `testNecCritExtraction`: performs necessary-condition extraction
* `testSuffCritExtraction`: performs sufficient-criterion extraction
* `testRecursiveApprox`: performs recursive approximation

you can start each script equally with e.g.
``` uv run testSingleExtraction```
 
The same procedure applies to the other scripts.

### Parameters and Options for these scripts:
Definition Extraction
- `fragment_file`: specifies the input fragment file e.g. "fragment.owl"
- `mode`: specifies the extraction mode
    - `"full_approx"`: uses approximative alc-sat
    - `mode.exact`: uses exact alc-sat
- `size`: specifies the maximum size of the extracted definition
- `inverse`:
    - `True`:  enables inverse roles (ALCI)
    - `False`: disables inverse roles (ALC)
- `language`: specifies the syntactic fragments of ALC/ALCI used for the extraction
    - `"alc"`: basic ALC/ALCI with all Operators
    - `"alc_pos"`: removes negation
    - `"alc_no_all"`: removes the universal quantifier
    - `"alc_pos_no_all"`: removes negation and universal quantifier
- `timeout`: specifies the maximum time allowed for each definition extraction
- `exclude_atomic`: specifies whether `TOP` and `BOT` are excluded from the extracted definition
    - `[OP.TOP, OP.BOT]`: excludes both `TOP` and `BOT`
    - `[]`: does not exclude any atomic concepts
- `exclude_top_classes`:
    - `True`: top-level classes such as Person are excluded from the extraction
    - `False`: top-level classes such as Person are included in the extraction, which can result in trivial solutions

Example Selection
- `samples`: specifies the number of randomly selected positive and negative examples, with |P| = |N| (Does only work with example_mode `"definition"`)
- `example_mode`: specifies how the examples are selected
    - `"definition"`: (default) |P| = |N| 
    - `"nec_crit"`: uses the necessary criterion
    - `"suf_crit"`: uses the sufficient criterion
- `only_focus`
    - `False`: (default) negative examples are sampled from the entire domain
    - `True`: negative examples are sampled only from concepts related to the domains signature

# Description for ALCSAT:
This repository contains our implementation of bounded fitting for the description logic ALC (ALSAT). As this is a Fork of <https://github.com/spell-system/SPELL>, it also contains SPELL, a tool to learn concepts in the description logic EL.

This repository contains our implementation of bounded fitting for the description logic ALCQI(f) (ALCSAT). Given an instance of a learning problem in the form of a knowledge base, positive and negative examples, the tool searches for a description logic concept that covers all positive examples, excludes all negative examples and is of minimal size. Any syntactic fragment of the description logic ALC is supported as well as extensions of ALC with number restrictions, inverse roles and data values.

As this is a Fork of <https://github.com/spell-system/SPELL>, it also contains SPELL, a tool to learn concepts in the description logic EL.
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