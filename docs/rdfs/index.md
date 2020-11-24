---
"@id": "rdfs:"
---

# RDF Schema (RDFS)

{% set rdfs_url = (graph | sparql('
    SELECT ?rdfs WHERE {
        BIND(rdfs: AS ?rdfs)
    }
') | gallery | first).rdfs %}

<div class="ui container">
    <div class="ui large fluid labeled input">
      <div class="ui label">
        rdfs:
      </div>
      <input readonly type="text" placeholder="" value="{{ rdfs_url }}">
    </div>
</div>

<br/>

{% set cards = graph | sparql('
    SELECT * WHERE {
        GRAPH <rdfs/rdfs.n3> {
            ?url rdfs:comment ?default_comment .
            ?url rdfs:label ?default_label .
        }

        OPTIONAL {
            GRAPH ?g {
                ?url rdfs:label ?readable_label .
            }
            FILTER (?g != <rdfs/rdfs.n3>)
        }

        OPTIONAL {
            GRAPH ?g {
                ?url rdfs:comment ?readable_comment .
            }
            FILTER (?g != <rdfs/rdfs.n3>)
        }

        ?url a ?category .
        ?category a <kb://Category/> .
        ?category rdfs:label ?category_label .
        ?category rdfs:comment ?category_comment .
        ?category :color ?color .

        BIND(999 AS ?default_priority)
        OPTIONAL {
            ?category :priority ?priority .
        }
        BIND(COALESCE(?priority, ?default_priority) AS ?priority)

        ?url rdfs:isDefinedBy rdfs: .
    } ORDER BY ?priority ?default_label
') | gallery %}

<div class="ui four cards">
{% for card in cards %}
    <div class="ui {{ card.color }} raised card" data-href="{{ card.url }}">
        <div class="content">
            <div class="header">
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
    </div>
{% endfor %}
</div>
