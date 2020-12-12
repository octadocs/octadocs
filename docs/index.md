# OctaDocs

OctaDocs is a plugin for [MkDocs](https://www.mkdocs.org/) to make it smarter.

# 📚 Vocabularies

{% set cards = query('
    SELECT * WHERE {
        ?ontology
            a owl:Ontology ;
            rdfs:label ?title ;
            rdfs:comment ?description ;
            schema:image ?image ;
            rdfs:isDefinedBy/octa:url ?url .
    }
') %}

<div class="ui four cards">
{% for card in cards %}
    <a class="ui raised card" href="/{{ card.url }}">
        <div class="image">
            <img src="{{ card.image }}" />
        </div>
        <div class="content">
            <div class="header">{{ card.title }}</div>
            <div class="description">{{ card.description }}</div>
        </div>
    </a>
{% endfor %}
</div>

{#
### To think about:

```jinja2
{{ owl.Ontology.objects | cards(
    title=rdfs.label,
    image=schema.image,
    url=rdfs.isDefinedBy / octa.url,
) }}
```
#}
