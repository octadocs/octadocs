---
"@id": rdfs:Class
"@type": rdfs/entities.md
comment: Class, group, category.
---

{% set info = graph | sparql('
SELECT ?label WHERE {
    rdfs:Class rdfs:label ?label .
}
') | gallery | first %}

# {{ info.label }}
