---
title: OWL Restrictions
---

What about this?

```python
from octarine import owl, rdfs, var

with var.term as term:
    owl.Restriction(
         variable=term,
         on_property=rdfs.isDefinedBy,
         some_values_from=owl.Ontology,
    )
```
