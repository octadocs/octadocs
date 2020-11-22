---
title: "RDF Schema (RDFS)"
"@graph":
    - "@id": http://www.w3.org/2000/01/rdf-schema#Class
      category: Entities
    - "@id": http://www.w3.org/2000/01/rdf-schema#Resource
      category: Entities
    - "@id": http://www.w3.org/2000/01/rdf-schema#Literal
      category: Entities
    - "@id": http://www.w3.org/2000/01/rdf-schema#DataType
      category: Entities
view: gallery
template: gallery.html
---

## To show a naked RDF graph

```zet
query: /rdfs/rdfs.sparql
template: /rdfs/template.html
```

## To show a list of things

```zet
query: /rdfs/entities.sparql
frame: /rdfs/entities.jsonld
template: /rdfs/entities.html
```

## More high level

```zet
properties: $self
```

...this one encapsulates querying, framing and rendering (and also possibly some Python powered processing, I don't know) in one macro command.
