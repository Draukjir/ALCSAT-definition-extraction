class Signature:
    def __init__(self, concept_names=None, role_names=None):
        # file_names
        self.TAXONOMY = "yago_fragmentation/yago-taxonomy.ttl"
        self.SCHEMA = "yago_fragmentation/yago-schema.ttl"
        self.FACTS = "yago_fragmentation/yago-facts.ttl"

        # important rdf_relations
        self.SUBCLASS = "<http://www.w3.org/2000/01/rdf-schema#subClassOf>"
        self.TYPE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"

        # determines the focus of which individuals will be in the domain
        self.domain_signature = {
            "<http://yago-knowledge.org/resource/Actor>",
            "<http://yago-knowledge.org/resource/Composer>",
            "<http://yago-knowledge.org/resource/Film_director>",
            "<http://yago-knowledge.org/resource/Painter>",
            "<http://yago-knowledge.org/resource/Scientist>",
            "<http://yago-knowledge.org/resource/Singer>",
            "<http://yago-knowledge.org/resource/Writer>",
            "<http://yago-knowledge.org/resource/Politician>",
            "<http://yago-knowledge.org/resource/SportsPerson>",
            "<http://yago-knowledge.org/resource/Journalist>",
        }

        if concept_names is not None:
            self.concept_names = set(concept_names)
        else:
            self.concept_names = {
                "<http://yago-knowledge.org/resource/Actor>",
                "<http://yago-knowledge.org/resource/Composer>",
                "<http://yago-knowledge.org/resource/Film_director>",
                "<http://yago-knowledge.org/resource/Painter>",
                "<http://yago-knowledge.org/resource/Scientist>",
                "<http://yago-knowledge.org/resource/Singer>",
                "<http://yago-knowledge.org/resource/Writer>",
                "<http://yago-knowledge.org/resource/Politician>",
                "<http://yago-knowledge.org/resource/SportsPerson>",
                "<http://yago-knowledge.org/resource/Journalist>",
                "<http://yago-knowledge.org/resource/Album>",
                "<http://yago-knowledge.org/resource/Art>",
                "<http://schema.org/Movie>",
                "<http://schema.org/MusicComposition>",
                "<http://yago-knowledge.org/resource/University>",
                "<http://yago-knowledge.org/resource/Work_of_art>",
                "<http://yago-knowledge.org/resource/Award>",
                "<http://yago-knowledge.org/resource/Election>",
                "<http://yago-knowledge.org/resource/Political_organisation>",
                "<http://yago-knowledge.org/resource/Association_Q15911314>",
                "<http://schema.org/Corporation>",
                "<http://yago-knowledge.org/resource/Sports_club>",
                "<http://yago-knowledge.org/resource/Sports_competition>",
            }

        if role_names is not None:
            self.role_names = set(role_names)
        else:
            self.role_names = {
                "<http://schema.org/actor>",
                "<http://schema.org/alumniOf>",
                "<http://schema.org/author>",
                "<http://schema.org/award>",
                "<http://schema.org/director>",
                "<http://schema.org/memberOf>",
                "<http://schema.org/musicBy>",
                "<http://yago-knowledge.org/resource/notableWork>",
                "<http://schema.org/performer>",
                "<http://yago-knowledge.org/resource/candidateIn>",
                "<http://schema.org/worksFor>",
                "<http://yago-knowledge.org/resource/leader>",
                "<http://yago-knowledge.org/resource/participant>",
                "<http://yago-knowledge.org/resource/playsIn>",
                "<http://schema.org/lyricist>",
            }

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

        self.unwanted_roles = {
            "<http://www.w3.org/2000/01/rdf-schema#label>",
            "<http://www.w3.org/2000/01/rdf-schema#comment>",
            "<http://schema.org/mainEntityOfPage>",
            "<http://schema.org/alternateName>",
            "<http://schema.org/sameAs>",
            "<http://schema.org/gender>",
            "<http://www.w3.org/2002/07/owl#sameAs>",
            "<http://schema.org/birthDate>",
            "<http://schema.org/birthPlace>",
            "<http://schema.org/nationality>",
            "<http://schema.org/knowsLanguage>",
            "<http://schema.org/deathDate>",
            "<http://schema.org/image>",
            "<http://schema.org/deathPlace>",
            "<http://schema.org/url>",
            "<http://schema.org/children>",
            "<http://schema.org/spouse>",
            "<http://schema.org/homeLocation>",
            "<http://yago-knowledge.org/resource/beliefSystem>",
            "<http://yago-knowledge.org/resource/influencedBy>",
            "<http://yago-knowledge.org/resource/doctoralAdvisor>",
        }

    def write_custom_schema(self, out_file="custom-schema.owl"):

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

    def clean_name(uri: str):
        return (
            uri.replace("<http://yago-knowledge.org/resource/", "")
            .replace("<http://schema.org/", "")
            .replace(">", "")
        )


def main():
    sig = Signature()

    sig.write_custom_schema()


if __name__ == "__main__":
    main()
