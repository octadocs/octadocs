{% set headers = query(
    'SELECT ?label WHERE {
        ?entity rdfs:isDefinedBy ?iri .    
    
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

{% set summaries = query('
    SELECT ?summary WHERE { 
        ?term rdfs:isDefinedBy ?iri .
        
        GRAPH ?iri {
            ?term rdfs:comment ?summary .
        }
    }
', iri=page|iri_by_page) %}

{% if headers %}
<h1 class="ui header">
    {{ headers.0.label }}
    {% if summaries %}
        <div class="sub header">
            {{ summaries.0.summary }}        
        </div>
    {% endif %}
</h1>
{% else %}
# Page title is not available 😟
{% endif %}

{% set superclasses = query('
    SELECT ?link ?label ?link WHERE {
        ?term rdfs:isDefinedBy ?iri .
        ?term rdfs:subClassOf ?superclass .
        ?superclass rdfs:isDefinedBy/octa:url ?link .
        ?superclass rdfs:label ?label .
        FILTER(?superclass != ?term)
    }
', iri=page|iri_by_page) %}

{% set domains = query('
    SELECT ?link ?label WHERE {
        ?term rdfs:isDefinedBy ?iri .
        ?term rdfs:domain ?domain .
        
        ?domain rdfs:isDefinedBy/octa:url ?link .
        ?domain rdfs:label ?label .
    }
', iri=page|iri_by_page) %}


{% set classes = query('
    SELECT ?link ?label WHERE {
        ?term rdfs:isDefinedBy ?iri .
        
        GRAPH <local:rdfs/rdfs.n3> {
            ?term a ?class .
        }
        
        ?class rdfs:label ?label .
        
        OPTIONAL {
            ?class rdfs:isDefinedBy/octa:url ?link .
        }
    }
', iri=page|iri_by_page) %}

{% set ranges = query('
    SELECT ?link ?label WHERE {
        ?term rdfs:isDefinedBy ?iri .
        ?term rdfs:range ?range .
        ?range rdfs:isDefinedBy/octa:url ?link .
        ?range rdfs:label ?label .
    }
', iri=page|iri_by_page) %}

{% set is_property = query('ASK {
    ?term rdfs:isDefinedBy ?page .
    ?term rdf:type rdf:Property
}', page=page|iri_by_page) %}

<div class="ui relaxed horizontal list">
{% if classes %}
    <div class="item">
        <div class="content">
            <div class="header">Instance of:</div>
            {% for class in classes %}
                <a href="{{ class.link }}">{{ class.label }}</a>{% filter trim %}
                {% if not loop.last %}, {% endif %}
                {% endfilter %}
            {% endfor %}
        </div>
    </div>
{% endif %}

{% if superclasses %}
    <div class="item">
        <div class="content">
            <div class="header">Subclass of:</div>
            {% for superclass in superclasses %}
                <a href="{{ superclass.link }}">{{ superclass.label }}</a>{% filter trim %}
                {% if not loop.last %}, {% endif %}
                {% endfilter %}
            {% endfor %}
        </div>
    </div>
{% endif %}

{% if is_property %}
    <div class="item">
        <div class="content">
            <div class="header">Property:</div> 
            {% for range in ranges %}
                <a href="{{ range.link }}">{{ range.label }}</a>
                {% if loop.revindex == 2 %} or {% elif not loop.last %}, {% endif %}
            {% endfor %}
            
            →
            
            {% for domain in domains %}
                <a href="{{ domain.link }}">{{ domain.label }}</a>
                {% if loop.revindex == 2 %} or {% elif not loop.last %}, {% endif %}
            {% endfor %}
        </div>
    </div>
{% endif %}
</div>