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

I believe we need to choose a method we are going to persist our data with.

## Candidates

### TerminusDB

<table>
  <thead>
    <tr>
      <th></th>
      <th>Features</th>
      <th>Shortcomings</th>
    <tr>
  </thead>
  <tbody>
    <tr>
      <th>Relevant</th>
      <td>
        <ul>
          <li>Very nice admin UI</li>
          <li>WOQL is JSON-LD based</li>
          <li>Python query DSL</li>
        </ul>
      </td>
      <td>
        <ul>
          <li>Lack for SPARQL support</li>
          <li>Have to run a separate server process</li>
        </ul>
      </td>
    </tr>
    <tr>
      <th>Irrelevant</th>
      <td>
        <ul>
          <li>Git-like versioning</li>
          <li></li>
        </ul>
      </td>
      <td>
        <ul>
          <li>?</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

## Notes

The most important problem in the list above is performance. OWL RL performance is extremely slow and makes the editing experience quite bad even on a modest size documentation database, which I experienced on [https://vocabulari.es](vocabulari.es). 

This does not yet justify completely rejecting SPARQL as a query standard, or abandoning the principle when you do not need to run an extra DB server to use Octadocs. You just run `mkdocs serve` and everything works, out of the box. 

## Consequences

I will:

- Enable SQlite storage for RDFLib as the default method;
- Look into methods to optimize the speed;
- Optimize context generation and store modification times in the graph rather then in a special dictionary in RAM;
- Perhaps look into supporting Oxigraph and other SPARQL-enabled stores.
