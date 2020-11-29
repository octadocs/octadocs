---
label: RDF & RDFS Inference Rules
---

{% include "header.md" with context %}

{% macro link(location) -%}
    {{ query(
        'SELECT ?iri WHERE {
            ?location rdfs:isDefinedBy ?iri .
            ?location a rdfs:Page .
        }',
        location=rdfs.Resource,
    ) }}
{%- endmacro %}


<table class="ui table">
    <thead>
        <tr>
            <th colspan="2">Given</th>
            <th>Inferred</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="3"><code>?s ?p ?o</code></td>
            <td rowspan="3">⇒</td>
            <td><code>?p a rdf:Property</code></td>
        </tr>
        <tr>
            <td><code>?s a {{ link('rdfs:Resource') }}</code></td>
        </tr>
        <tr>
            <td><code>?o a rdfs:Resource</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?p <a href="/rdfs/domain/">rdfs:domain</a> ?class .<br/>
                    ?s ?p ?o .
                </code>
            </td>
            <td>⇒</td>
            <td><code>?p a ?class</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?p <a href="/rdfs/range/">rdfs:range</a> ?class .<br/>
                    ?s ?p ?o .
                </code>
            </td>
            <td>⇒</td>
            <td><code>?o a ?class</code></td>
        </tr>
    </tbody>
</table>
