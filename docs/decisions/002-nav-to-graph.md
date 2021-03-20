---
title: Represent the navigation tree in graph
---

## Context

We would like to represent the structure of navigation tree inside the RDFLib graph of the site. Perhaps we could export the tree as a YAML-LD file for the system to read it?

## Decision

Not likely. To capture the tree we have to use [on_nav](https://www.mkdocs.org/user-guide/plugins/#on_nav) method, which is executed *after* all the pages and files are already consumed by the site generator.

Thus, we will have to call the graph generation routine from inside of `on_nav` and write directly to the graph.

## Consequences

This feature will greatly simplify creation of index and list pages using SPARQL queries.
