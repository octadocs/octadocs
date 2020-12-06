---
$id: "rdfs:"
label: "RDF Schema (RDFS)"
schema:image: rdfs/logo.svg
rdfs:comment: Basic notions of classes, properties, and relations between them.
---

{% include "header.md" with context %}

{% set rdfs_url = query('
    SELECT ?rdfs WHERE {
        BIND(rdfs: AS ?rdfs)
    }
').0.rdfs %}

<div class="ui container">
    <div class="ui large fluid action labeled input">
      <div class="ui label">
        rdfs:
      </div>
      <input readonly type="text" placeholder="" value="{{ rdfs_url }}">
      <a class="ui green button" href="{{ rdfs_url }}">
        <i class="external alternate icon"></i>
      </a>
    </div>
</div>

<br/>

{% set cards = query('
    SELECT * WHERE {
        GRAPH <local:rdfs/rdfs.n3> {
            ?term rdfs:comment ?default_comment .
            ?term rdfs:label ?default_label .
        }
        
        ?term rdfs:isDefinedBy ?page .
        ?page a octa:Page .
        ?page octa:url ?url .
        
        GRAPH ?page {
            OPTIONAL {
                ?term rdfs:label ?readable_label .
            }
            
            OPTIONAL {
                ?term rdfs:comment ?readable_comment .
            }
        }
        
        ?term a ?category .
        ?category a <local:Category> .
        ?category rdfs:label ?category_label .
        ?category rdfs:comment ?category_comment .
        ?category <local:color> ?color .
        
        OPTIONAL {
            ?term <local:symbol> ?symbol .
        }

        BIND(999 AS ?default_priority)
        OPTIONAL {
            ?category <local:priority> ?priority .
        }
        BIND(COALESCE(?priority, ?default_priority) AS ?priority)

        ?term rdfs:isDefinedBy rdfs: .
    } ORDER BY ?priority ?default_label
') %}

<div class="ui four cards">
{% for card in cards %}
    <a class="ui {{ card.color }} raised card" href="/{{ card.url|default('?') }}">
        <div class="content">
            <div class="header">
                {% if card.symbol %}
                    {{ card.symbol }}
                {% endif %}
                {{ card.readable_label | d(card.default_label) }}
            </div>
            <div class="description">
                {{ card.readable_comment | default(card.default_comment) }}
            </div>
        </div>
        <div class="extra content">
            <span title="{{ card.category_comment }}">{{ card.category_label }}</span>
            <span class="right floated">
                rdfs:{{ card.default_label }}
            </span>
        </div>
    </a>
{% endfor %}
</div>

## Also

- [Logical Inference Rules](/rdfs/inference/)
