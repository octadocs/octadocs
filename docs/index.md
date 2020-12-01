# {{ config.site_name }}


{{ query('
    SELECT * WHERE {
        ?ontology a owl:Ontology .
        ?ontology rdfs:isDefinedBy ?page .
        ?page octa:url ?url .
    }
') }}
