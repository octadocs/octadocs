---
title: Calculate a part of Context from ontologies available in the graph
---

## Context *(pun not intended)*

The problem I meet most often when writing YAML-LD is that, by default, in the document like this

```yaml
$id: OntologyTerm
label: Class of terms defined by ontologies (RDFS, OWL and others).
owl:equivalentClass:
  $type: owl:Restriction
  owl:onProperty: rdfs:isDefinedBy
  owl:someValuesFrom: owl:Ontology
```

the terms `owl:Ontology` and `rdfs:isDefinedBy` are interpreted as literals. We want to interpret them as IRIs of course.

That can be deduced from definitions in OWL ontology:

```turtle
owl:onProperty a rdf:Property ;
     rdfs:label "onProperty" ;
     rdfs:comment "The property that determines the property that a property restriction refers to." ;
     rdfs:domain owl:Restriction ;
     rdfs:isDefinedBy <http://www.w3.org/2002/07/owl#> ;
     rdfs:range rdf:Property . 
```

The `rdfs:range` leaves no question as to how to interpret this.

## Decision

We need to select the subset of the graph (for example, the subset encompassing our basic reusable ontologies) which is going to be used to calculate the context object. Then, the context object will be generated from these ontologies, based on definitions like `rdf:type`, `rdfs:domain`, `rdfs:range` and others.  

## Consequences

That will ensure the users will not see unexpected and weird frustrations when trying to input information in YAML-LD format.
