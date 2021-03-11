---
title: Caching the RDF graph in development
---

## Context

When developing locally with `mkdocs serve`, we oftentimes (especially at [vocabulari.es](https://vocabulari.es/)) have long delays before the site updates after every file change. That's because reading the files (say, [schema.org](https://schema.org) ontology) and then running inference rules on them is time consuming.

On every file change, MkDocs forces us to rebuild the graph from ground up.

We could probably reduce those delays if we could only reload parts of the graph that were actually changed. That is possible because every source file is stored in its own named graph.

## Decision

We see that the `OctaDocsPlugin` object is recreated every time we change a file while running `mkdocs serve`.

```
<octadocs.plugin.OctaDocsPlugin object at 0x7fcc8337eee0>
<octadocs.plugin.OctaDocsPlugin object at 0x7fcc7fa7e670>
```

We are going to use `@functools.lru_cache` as an easy caching method. When loading every file into the graph, we will also store the last modification time of the file in a dictionary in memory. When reloading, we only will reload those files which have changed since last time we read them.

Using SPARQL `CLEAR NAMED` statement, we will drop the contents of a file and then read it into the memory again.

We will also use `CLEAR DEFAULT` to wipe previous inference results.

## Consequences

Without large scale modifications of the code, we will speed up development experience a little bit. We will also postpone introductions of any persistent databases a little longer.
