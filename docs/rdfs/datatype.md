---
"@id": rdfs:Datatype
"@type": rdfs/entities.md
label: Data Type
---

{% set info = graph | sparql('
SELECT ?label WHERE {
    OPTIONAL {
        GRAPH <rdfs/datatype.md> {
            rdfs:Datatype rdfs:label ?readable_label .
        }
    }

    OPTIONAL {
        GRAPH <rdfs/rdfs.n3> {
            rdfs:Datatype rdfs:label ?default_label .
        }
    }
    
    BIND(COALESCE(?readable_label, ?default_label) AS ?label)
}
') | gallery | first %}

# {{ info.label }}
