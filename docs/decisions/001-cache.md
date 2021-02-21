---
title: Caching the RDF graph in development
---

## Context

When developing locally with `mkdocs serve`, we oftentimes (especially at [vocabulari.es](https://vocabulari.es/)) have long delays before the site updates after every file change. That's because reading the files (say, [schema.org](https://schema.org) ontology) and then running inference rules on them is time consuming.

The deepest reason is that our graph is rebuilt from ground up on every file change.

We could probably reduce those delays if we could only reload parts of the graph that were actually changed. That is possible because every source file is stored in its own named graph.

## Decision

We see that the `OctaDocsPlugin` object is recreated every time we change a file while running `mkdocs serve`.

```
<octadocs.plugin.OctaDocsPlugin object at 0x7fcc8337eee0>
<octadocs.plugin.OctaDocsPlugin object at 0x7fcc7fa7e670>
```

We are going to use `@functools.lru_cache` as an easy caching method. When loading every file into the graph, we will also store the last modification time of the file. When reloading, we only will reload those files which have changed since last load.

Unfortunately, OWL RL and SPARQL inference rules will have to be rerun anyway, and that may be a major performance penalty. At this point, I do not see ways around that.

## Consequences

Without large scale modifications of the code, we will speed up development experience a little bit.

### Adverse effect

- If there was a triple `t1` which was used by inference to create another triple `t2`,
- and if the user removed `t1` from the graph,
- `t2` will still remain in the graph which may confuse the user.

This can be resolved by removing everything from the global graph, but that needs to be carefully investigated.

boo
foo
