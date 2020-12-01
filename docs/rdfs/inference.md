---
label: RDF & RDFS Inference Rules
---

{% include "header.md" with context %}

<div class="ui warning icon message">
  <i class="exclamation icon"></i>
  <div class="content">
    <div class="header">
      This page is not smart enough
    </div>
    <p>In the code of this page, inference rules are just hard coded. You cannot filter them or query them. This is going to be fixed later as we choose a formalism to properly describe these rules in the graph.</p>
  </div>
</div>

{% macro link_to(uri_ref) %}
{% set labels = query(
    "SELECT * WHERE { GRAPH <local:rdfs/rdfs.n3> { ?resource rdfs:label ?label . } }",
    resource=uri_ref,
) %}
{% if labels %}
    <a href="{{ uri_ref|url }}">rdfs:{{ labels.0.label }}</a>
{% else %}
    <div class="ui red horizontal label">{{ uri_ref }}</div>
{% endif %}
{% endmacro %}

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
            <td><code>?s a {{ link_to(rdfs.Resource) }}</code></td>
        </tr>
        <tr>
            <td><code>?o a {{ link_to(rdfs.Resource) }}</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?p {{ link_to(rdfs.domain) }} ?class .<br/>
                    ?s ?p ?o .
                </code>
            </td>
            <td>⇒</td>
            <td><code>?p a ?class</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?p {{ link_to(rdfs.range) }} ?class .<br/>
                    ?s ?p ?o .
                </code>
            </td>
            <td>⇒</td>
            <td><code>?o a ?class</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?x {{ link_to(rdfs.subPropertyOf) }} ?y .<br/>
                    ?y {{ link_to(rdfs.subPropertyOf) }} ?z .<br/>
                </code>
            </td>
            <td>⇒</td>
            <td><code>?x {{ link_to(rdfs.subPropertyOf) }} ?z</code></td>
        </tr>
        <tr>
            <td>
                <code>?x a rdf.Property</code>
            </td>
            <td>⇒</td>
            <td><code>?x {{ link_to(rdfs.subPropertyOf) }} ?x</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?s ?sub_property ?o .<br/>
                    ?sub_property {{ link_to(rdfs.subPropertyOf) }} ?super_property .
                </code>
            </td>
            <td>⇒</td>
            <td><code>?s ?super_property ?o</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?class a {{ link_to(rdfs.Class) }}
                </code>
            </td>
            <td>⇒</td>
            <td><code>?class {{ link_to(rdfs.subClassOf) }} {{ link_to(rdfs.Resource) }}</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?sub_class {{ link_to(rdfs.subClassOf) }} ?super_class .<br/>
                    ?something a ?sub_class .
                </code>
            </td>
            <td>⇒</td>
            <td><code>?something a ?super_class</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?class a {{ link_to(rdfs.Class) }}
                </code>
            </td>
            <td>⇒</td>
            <td><code>?class {{ link_to(rdfs.subClassOf) }} ?class</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?sub_class {{ link_to(rdfs.subClassOf) }} ?parent_class .<br/>
                    ?parent_class {{ link_to(rdfs.subClassOf) }} ?grandparent_class .
                </code>
            </td>
            <td>⇒</td>
            <td><code>?sub_class {{ link_to(rdfs.subClassOf) }} ?grandparent_class</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?property a {{ link_to(rdfs.ContainerMembershipProperty) }}
                </code>
            </td>
            <td>⇒</td>
            <td><code>?property {{ link_to(rdfs.subPropertyOf) }} {{ link_to(rdfs.member) }}</code></td>
        </tr>
        <tr>
            <td>
                <code>
                    ?data_type a {{ link_to(rdfs.Datatype) }}
                </code>
            </td>
            <td>⇒</td>
            <td>
                <code>
                    ?data_type
                    {{ link_to(rdfs.subClassOf) }} {{ link_to(rdfs.Literal) }}
                </code>
            </td>
        </tr>
    </tbody>
</table>

Rules adapted from paper [arXiv:1601.02650: Dominik Tomaszuk / Inference rules for RDF(S) and OWL in N3Logic](https://arxiv.org/abs/1601.02650).

{#
## Possible YAML syntax for inference rules

```yaml
rules:
  - name: "Every triple implies types for its parts"
    given: [_:subject, _:predicate, _:object]
    implies:
      - [_:subject, rdf:type, rdfs:Resource]
      - [_:predicate, rdf:type, rdf:Property]
      - [_:object, rdf:type, rdfs:Resource]
```

## These inference rules can be easily expressed as set theory formulas

...

## Variables should be colored

- Every variable should have its own color

#}
