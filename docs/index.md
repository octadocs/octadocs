# OctaDocs

OctaDocs is a plugin for [MkDocs](https://www.mkdocs.org/) to make it smarter.

{{ q.test().first }}

### To think about:

```jinja2
{% raw %}
{{ owl.Ontology.objects | cards(
    title=rdfs.label,
    image=schema.image,
    url=octa.subjectOf/octa.url,
) }}
{% endraw %}
```
