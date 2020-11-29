---
$id: rdfs:subClassOf
$type: rdfs/class_to_class.md
label: SubClass Of

$graph:
    - $id: Robot
      $type: rdfs:Class
    - $id: Rover
      rdfs:subClassOf: Robot
    - $id: opportunity
      $type: Rover
      label: Opportunity
---

{% include "header.md" with context %}

{{ construct(
    'construct { ?s ?p ?o } where { graph ?g { ?s ?p ?o . } }',
    g=src_path_to_iri(page.file.src_path),
) | n3 }}

{{ query('SELECT * WHERE { GRAPH ?g { ?s ?p "Opportunity" } }') }}
