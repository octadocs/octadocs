---
$id: rdfs:subClassOf
$type: Sub
label: SubClass Of
symbol: ⊂

$included:
    - $id: Robot
      $type: rdfs:Class
    - $id: Rover
      rdfs:subClassOf: Robot
    - $id: opportunity
      $type: Rover
      label: Opportunity
---

{{ construct(
    'CONSTRUCT { ?s ?p ?o } where { graph ?g { ?s ?p ?o . } }',
    g=src_path_to_iri(page.file.src_path),
) | n3 }}

{{ query('SELECT * WHERE { <local:opportunity> a ?type }') }}

```html
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@4"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>

<div id="view"></div>
<script>
vegaEmbed(
  '#view',
  'https://vega.github.io/vega/examples/bar-chart.vg.json'
);
</script>
```
