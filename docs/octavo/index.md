---
title: Octavo
$type: https://en.wikipedia.org/wiki/Book
---

Octavo is the greatest spell book of all.

And this section is a set of random examples of Octadocs spells.

{{ query('CONSTRUCT { ?s ?p ?o } WHERE {
    GRAPH <local:octavo/index.md> {
        ?s ?p ?o .
    }
}
') | graph }}
