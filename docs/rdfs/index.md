---
$id: "rdfs:"
label: "RDF Schema (RDFS)"
schema:image: rdfs/logo.svg
rdfs:comment: Basic notions of classes, properties, and relations between them.
---

<style>
.ui.tangible.card,
a.ui.card:hover,
.ui.link.card:hover,
.ui.cards a.card:hover,
.ui.link.cards .card:hover {
    background: url(backgrounds/classy_fabric/classy_fabric/classy_fabric.png);
}

.ui.tangible.card .content .header {
    color: white;
}

a.ui.tangible.card {
    padding-bottom: 36px;
    padding-top: 36px;
}
</style>


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

{% set categories = query('
    SELECT * WHERE {
        ?iri
            a :Category ;
            :priority ?priority ;
            rdfs:label ?label ;
            :column_width ?column_width .
    } ORDER BY ?priority
') %}

{% macro cards_for_category(category) %}
    {% set cards_per_category = query('
        SELECT * WHERE {
            ?term
                a ?category ;
                octa:subjectOf / octa:url ?url .
            
            GRAPH <local:rdfs/rdfs.n3> {
                ?term rdfs:label ?label .
            }
        } ORDER BY ?label
    ', category=URIRef(category)) %}
    
    {% set card_count = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
    }[cards_per_category.__len__()] %}

    <div class="ui {{ card_count }} cards">
        {% for card in cards_per_category %}
            <a class="ui tangible raised card" href="{{ card.url|default('#') }}">
                <div class="ui content">
                    <div class="header center aligned">
                        {{ card.label }}
                    </div>
                </div>
            </a>
        {% endfor %}
    </div>
{% endmacro %}

<div class="ui grid">
    {% for category in categories %}
    <div class="{{ category.column_width }} wide column">
        <h2>{{ category.label }}</h2>
        {{ cards_for_category(category.iri) }}
    </div>
    {% endfor %}
</div>

## Also

- [Logical Inference Rules](/rdfs/inference/)
