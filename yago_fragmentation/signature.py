class Signature:
    def __init__(self):
        # file_names
        self.TAXONOMY = "yago_fragmentation/yago-taxonomy.ttl"
        self.SCHEMA = "yago_fragmentation/yago-schema.ttl"
        self.FACTS = "yago_fragmentation/yago-facts.ttl"

        # important rdf_relations
        self.SUBCLASS = "<http://www.w3.org/2000/01/rdf-schema#subClassOf>"
        self.TYPE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"

        # concepts or roles which we are looking for in the 1st pass
        # determines the focus of which individuals will be in the domain
        self.domain_signature = {
            "<http://yago-knowledge.org/resource/Actor>", # person who acts in a dramatic or comic production and works in film, television, theatre, or radio
            "<http://yago-knowledge.org/resource/Composer>",
            "<http://yago-knowledge.org/resource/Film_director>", 
            "<http://yago-knowledge.org/resource/Painter>",
            "<http://yago-knowledge.org/resource/Scientist>",
            "<http://yago-knowledge.org/resource/Singer>",
            "<http://yago-knowledge.org/resource/Writer>" # person who uses written words to communicate ideas and to produce literary works
        }
        
        # concept_names which will be in the domain - 3rd pass
        # determines which concepts will stay in the domain
        self.concept_names = {
            "<http://yago-knowledge.org/resource/Actor>", # person who acts in a dramatic or comic production and works in film, television, theatre, or radio
            "<http://yago-knowledge.org/resource/Composer>",
            "<http://yago-knowledge.org/resource/Film_director>", 
            "<http://yago-knowledge.org/resource/Painter>",
            "<http://yago-knowledge.org/resource/Scientist>",
            "<http://yago-knowledge.org/resource/Singer>",
            "<http://yago-knowledge.org/resource/Writer>", # person who uses written words to communicate ideas and to produce literary works

            # Supporting Concepts:
            "<http://yago-knowledge.org/resource/Album>",
            "<http://yago-knowledge.org/resource/Art>", #general concept that creates expressive work for its beauty or emotional power (use Q838948 for the resulting work, use Q2018526 for the group of creative disciplines)
            "<http://schema.org/Movie>",
            "<http://schema.org/MusicComposition>",
            "<http://yago-knowledge.org/resource/Prize>",
            "<http://yago-knowledge.org/resource/Restaurant>",
            "<http://yago-knowledge.org/resource/University>",
            "<http://yago-knowledge.org/resource/Work_of_art>" #aesthetic item or artistic creation
        }

        # role_names - 2nd pass
        self.role_names = {
            "<http://schema.org/actor>",
            "<http://schema.org/alumniOf>",
            "<http://schema.org/author>", #The author of a CreativeWork or FictionalEntity
            "<http://schema.org/award>",
            "<http://schema.org/director>",
            "<http://yago-knowledge.org/resource/fieldOfWork>",
            "<http://schema.org/memberOf>",
            "<http://schema.org/musicBy>",
            "<http://yago-knowledge.org/resource/notableWork>",
            "<http://schema.org/performer>",
            "<http://yago-knowledge.org/resource/ownedBy>"
        }

        # target concept for definition extraction
        self.target_concept = "<http://yago-knowledge.org/resource/Actor>"

        # top level classes, needed if we want to find the most general class for a individual
        self.top_level_classes = [
            "<http://schema.org/Person>",
            "<http://schema.org/Organization>",
            "<http://schema.org/CreativeWork>",
            "<http://schema.org/Place>",
            "<http://schema.org/Event>",
            "<http://schema.org/Product>",
            "<http://schema.org/Taxon>",
            "<http://schema.org/Intangible>",
            "<http://yago-knowledge.org/resource/FictionalEntity>",
        ]

        self.THING = "<http://schema.org/Thing>"

    def write_custom_schema(self, out_file):

        with open(out_file, "w", encoding="utf-8") as f:

            f.write("""<?xml version="1.0"?>\n""")

            f.write("""<rdf:RDF
 xmlns="http://www.w3.org/2002/07/owl#"
 xml:base="http://www.w3.org/2002/07/owl"
 xmlns:owl="http://www.w3.org/2002/07/owl#"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">\n\n""")

            f.write("<Ontology/>\n\n")

            f.write("<!-- Classes -->\n")
            for c in sorted(self.concept_names):
                f.write(f'<Class rdf:about="{c.strip("<>")}"/>\n')

            f.write("\n<!-- Object Properties -->\n")
            for r in sorted(self.role_names):
                f.write(f'<ObjectProperty rdf:about="{r.strip("<>")}"/>\n')

            f.write("\n</rdf:RDF>\n")