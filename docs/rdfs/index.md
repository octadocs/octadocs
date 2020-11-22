---
"@id": "rdfs:"
---

# RDF Schema (RDFS)

{% set cards = graph | sparql('
    SELECT * WHERE {
        ?url rdfs:label ?label .
        ?url rdfs:comment ?comment .

        ?url rdfs:isDefinedBy rdfs: .
    }
') | gallery %}

<div class="ui link cards">
{% for card in cards %}
    <div class="card" data-url="{{ card.url }}">
        <div class="content">
            <div class="header">{{ card.label }}</div>
            <div class="description">{{ card.comment }}</div>
        </div>
        <div class="extra-content">
            <span class="right floated">
                rdfs:{{ card.label }}
            </span>
        </div>
    </div>
{% endfor %}
</div>




<div class="gallery">
{% for card in cards %}
    <div class="card">
        <div class="card-header">{{ card.label }}</div>
        <div class="card-body">{{ card.comment }}</div>
        <div class="card-footer">
            <small>rdfs:{{ card.label }}</small>
        </div>
        
        <!--div class="card-footer">{{ card.url }}</div-->
    </div>
{% endfor %}
</div>

<!--style>
.gallery {
    justify-content: flex-start;
    display: flex;
    flex-wrap: wrap;
}

.card {
    width: 30%;
    margin: 16px;
    border-radius: 8px;
    padding: 8px;
    background-color: cornflowerblue;
}

.card-header {
    font-weight: bold;
}

.card-footer {
    text-align: right;
}
</style-->

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/1.11.8/semantic.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/1.11.8/semantic.min.js"></script>
