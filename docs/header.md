{% set results = query(
    'SELECT ?label WHERE {
        ?entity octa:subjectOf ?iri .
    
        OPTIONAL {
            GRAPH ?iri {
                ?entity rdfs:label ?readable_label .
            }
        }

        OPTIONAL {
            GRAPH <local:rdfs/rdfs.n3> {
                ?entity rdfs:label ?default_label .
            }
        }

        BIND(COALESCE(?readable_label, ?default_label) AS ?label)
    }',
    iri=src_path_to_iri(page.file.src_path),
) %}

{% if results %}
# {{ results.0.label }}
{% else %}
# Page title is not available 😟
{% endif %}
