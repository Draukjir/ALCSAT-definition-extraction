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
            "<http://yago-knowledge.org/resource/Actor>",
            "<http://yago-knowledge.org/resource/Film_director>",
            "<http://schema.org/Movie>",
            "<http://yago-knowledge.org/resource/Author>",
            "<http://yago-knowledge.org/resource/Scientist>",
            "<http://yago-knowledge.org/resource/Musician>",
            "<http://yago-knowledge.org/resource/Chef>",
            #"<http://yago-knowledge.org/resource/Single_music>",
            "<http://yago-knowledge.org/resource/Album>"
        }
        
        # concept_names which will be in the domain - 3rd pass
        # determines which concepts will stay in the domain
        self.concept_names = {
            "<http://yago-knowledge.org/resource/Actor>",
            "<http://yago-knowledge.org/resource/Film_director>",
            "<http://schema.org/Movie>",
            "<http://yago-knowledge.org/resource/Author>",
            "<http://yago-knowledge.org/resource/Scientist>",
            "<http://yago-knowledge.org/resource/Musician>",
            "<http://yago-knowledge.org/resource/Chef>",
            #"<http://yago-knowledge.org/resource/Single_music>",
            "<http://yago-knowledge.org/resource/Album>"
        }

        # role_names - 2nd pass
        self.role_names = {
            "<http://schema.org/spouse>",
            "<http://schema.org/actor>",
            "<http://schema.org/director>",
            "<http://schema.org/award>",
            "<http://schema.org/author>",
            "<http://schema.org/musicBy>",
            "<http://schema.org/birthPlace>",
            "<http://schema.org/alumniOf>",
            "<http://schema.org/productionCompany>",
            "<http://yago-knowledge.org/resource/partOf>"

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