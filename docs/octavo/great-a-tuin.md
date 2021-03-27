---
$id: https://discworld.fandom.com/wiki/Great_A%27Tuin
$type: https://wiki.lspace.org/mediawiki/Chelys_Galactica
title: The Great A'Tuin
position: -1
---

{{ query('CONSTRUCT { ?s ?p ?o } WHERE {
    GRAPH <local:octavo/great-a-tuin.md> {
        ?s ?p ?o .
    }
}
') | graph }}
