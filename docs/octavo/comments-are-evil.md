---
title: Comments are Evil
---

The YAML format (which we prevalently use in the whole Octadocs system) supports comments:

```yaml
# The greatest spell book of all
$id: Octavo
```

Comments written like that are considered a bad practice because they are not available to the graph. It is better to use `rdfs:label`, `rdfs:comment` or even `octa:title` properties to define all human-readable content in a way available for subsequent analysis.

```yaml
$id: Octavo
comment: The greatest spell book of all
```
