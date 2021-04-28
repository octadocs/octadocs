---
title: Choosing database engine
source:
  - https://en.wikipedia.org/wiki/Comparison_of_triplestores
  - https://www.w3.org/2001/sw/wiki/ToolTable
  - http://www.michelepasin.org/blog/2011/02/24/survey-of-pythonic-tools-for-rdf-and-linked-data-programming/
---

## Context

At this point, I consider the transient in-memory storage of RDF graph (the one RDFLib provides us with) a blocker for further development because:

- OWL RL reasoning on this graph is extremely slow;
- It is impossible to use information from the graph for third-party instruments;
- There is no interactive UI to debug the graph;
- The graph is rebuilt from scratch every time we build (or serve) the site.

I believe we need to choose a database we are going to persist our data in.

## Decision



## Consequences
