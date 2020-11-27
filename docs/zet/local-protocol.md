# `local:` protocol

Since we are building semantic graph from MkDocs site pages, every page should have its own unique identifier formed as IRI.

Unfortunately, we cannot use relative IRIs like `zet/local-protocol/` because they are not supported in RDF data model. More information is available, say, in [this GitHub thread](https://github.com/digitalbazaar/jsonld.js/pull/225).

So we have to assign an **absolute IRI** to every MkDocs page, under which it will be accessible in queries.

An interesting idea would be to use the real absolute URL, like, https://zet.wiki/zet/local-protocol/ but that will make the site unportable and hardly accessible via different protocols (say, IPFS and HTTP both).

So, the suggestion is to use a fake schema, say `local:` which will be transformed to a relative URL when printed on page.

## local:zet/local-protocol/ or local:zet/local-protocol.md?

The first method is preferred because it can be directly (in an easier way) transformed into a resolvable URL.

However, besides `.md` files, MkDocs + Zet system can contain `.csv`, `.n3`, `.json`, image files, and many others - everything that can be loaded into the RDF graph. But only Markdown files can be rendered into HTML pages, which means changing their URLs. 

Thus I believe we should use internal file name in its full form to address things in Zet.

