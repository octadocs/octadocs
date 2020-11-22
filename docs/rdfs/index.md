---
title: "RDF Schema (RDFS)"
"@graph":
    - "@id": http://www.w3.org/2000/01/rdf-schema#Class
      category: Entities
    - "@id": http://www.w3.org/2000/01/rdf-schema#Resource
      category: Entities
    - "@id": http://www.w3.org/2000/01/rdf-schema#Literal
      category: Entities
    - "@id": http://www.w3.org/2000/01/rdf-schema#DataType
      category: Entities
---

{{ graph | sparql('CONSTRUCT WHERE { ?s rdfs:label ?o }') | graph }}
