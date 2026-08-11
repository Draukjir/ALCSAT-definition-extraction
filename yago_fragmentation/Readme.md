This is a tool to extract sample fragments of the knowledge graph YAGO 4.5.
The current example signature is based on the topics of the Movie World (Actors, Film Directors, Movies, ...).
You can change the signature by searching out the needed URIs and change the sets of the domain_signature, concept_names and role_names in the signature.py file. Then you can define the target_concept you want to find a definition for (Example: Actor). With the following steps you can then obtain two fragments of yago

# Obtain Yago 4.5.0.2 

```
wget https://yago-knowledge.org/data/yago4.5/yago-4.5.0.2.zip
```

## Extracting the needed files

```
unzip yago-4.5.0.2.zip yago-schema.ttl yago-taxonomy.ttl yago-facts.ttl
```

## Extract the fragments
You need two fragments, one with our target concept class and one without it.

I recommend using the script with the uv package manager: [ https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

The script also requires the lightrdf library[ https://github.com/ozekik/lightrdf](https://github.com/ozekik/lightrdf)

```
uv run extract.py
```

You will then obtain three files: custom-schema.owl, result-nt, result_without_target.nt

## Convert to OWL

This requires <https://github.com/ontodev/robot>

```
robot merge --input custom-schema.owl --input result.nt --output yago-fragment.owl
```