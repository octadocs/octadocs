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

{{ graph | sparql('CONSTRUCT WHERE { ?s rdfs:label ?o }') | attr('graph') | graph }}

{{ graph | sparql('
    SELECT * WHERE {
        ?thing rdfs:isDefinedBy rdfs: .
        ?thing rdfs:label ?label .
        ?thing rdfs:comment ?description .
        ?thing <kb://category> ?category .
    }
') | table }}

{% raw %}
{{ graph | sparql('
    CONSTRUCT {
        ?thing <kb://title> ?label .
        ?thing <kb://category> ?category .
        ?thing <kb://description> ?description .
        rdfs: <kb://cards> ?thing .
    } WHERE {
        ?thing rdfs:isDefinedBy rdfs: .
        ?thing rdfs:label ?label .
        ?thing rdfs:comment ?description .
        ?thing <kb://category> ?category .
    }
').graph | n3 }}

{% endraw %}
