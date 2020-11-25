---
"@id": rdfs:Datatype
"@type": rdfs/entities.md
label: Data Type
---

{% set title = select(
    'SELECT ?label WHERE {
        OPTIONAL {
            GRAPH <rdfs/datatype.md> {
                ?entity rdfs:label ?readable_label .
            }
        }

        OPTIONAL {
            GRAPH <rdfs/rdfs.n3> {
                ?entity rdfs:label ?default_label .
            }
        }

        BIND(COALESCE(?readable_label, ?default_label) AS ?label)
    }',
    entity=rdfs.Datatype,
).0.label %}

# {{ title }}
