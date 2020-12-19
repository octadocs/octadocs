---
$id: rdfs:Class
$type: Entities
comment: Class, group, category.
symbol: 🔴

$included:
    - $id: flying
      label: 🛸 Flying Things
      $type: rdfs:Class
    - $id: magical
      label: 🧙 Magical Things
      $type: rdfs:Class
    - $id: talking
      label: 🗨️ Talking Things
      $type: rdfs:Class
    - $id: plane
      $type: flying
    - $id: rincewind
      $type: talking
    - $id: unicorn
      $type: magical
    - $id: dragon
      $type:
        - flying
        - magical
        - talking
---

Classes are categories of things. One thing can belong to multiple classes if it wishes so.

{% set get_label_for_class = '
    SELECT ?label WHERE { ?class rdfs:label ?label }
' %}

{% set flying = query(get_label_for_class, class=local.flying).0.label %}
{% set magical = query(get_label_for_class, class=local.magical).0.label %}
{% set talking = query(get_label_for_class, class=local.talking).0.label %}

{% include "rdfs/class/classes.svg" with context %}

{{ construct('
    CONSTRUCT { 
        ?s ?p ?o
    } WHERE {
        GRAPH ?page_iri {
            ?s ?p ?o
            
            FILTER(?s != rdfs:Class)
            FILTER NOT EXISTS {
                ?s a octa:Page .
            }
        }
    }
', page_iri=page|iri_by_page) | n3 }}
