{% set title = query(
    'SELECT ?label WHERE {
        ?entity rdfs:isDefinedBy ?iri .    
    
        OPTIONAL {
            GRAPH ?iri {
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
    iri=iri_of(page),
).0.label %}

# {{ title }}
