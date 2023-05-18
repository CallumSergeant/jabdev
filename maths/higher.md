---
layout: main
title: Higher Maths
subject: Maths
permalink: /maths/higher
headings: false
---

<!-- Intro text for AH CHemistry page -->
<div class="container">
<h1>Additional Maths Resources</h1>
<p class="lead">Materials for the study of all SQA Chemistry courses.</p>
<!-- Table for data booklets -->
<h2 style="padding-right:60px" id="databooks">Data Booklets</h2>
<table class="table table-sm">
    <thead>
        <tr>
            <th scope="col">Level Of Study</th>
            <th scope="col">Data Book</th>
        </tr>
    </thead>
    <tbody>
        {% for item in site.downloads %}
        {% if item.category == "data-booklet" and page.subject == item.subject %}
        <tr>
                <th scope="row">{{item.level}}</th>
                <td><a href="/files/{{item.download}}"><i class="bi bi-filetype-pdf"></i></a></td>
        </tr>
        {% endif %}
        {% endfor %}
    </tbody>
</table>
<!-- Table for data booklets -->
<h2 style="padding-top:60px" id="reactionsummaries">Reaction Summaries</h2>
<table class="table table-sm">
    <thead>
        <tr>
            <th scope="col">Level Of Study</th>
            <th scope="col">Reaction Summary</th>
        </tr>
    </thead>
    <tbody>
        {% for item in site.downloads %}
        {% if item.category == "reaction-summary" %}
        <tr>
                <th scope="row">{{item.level}}</th>
                <td><a href="/files/{{item.download}}"><i class="bi bi-filetype-pdf"></i></a></td>
        </tr>
        {% endif %}
        {% endfor %}
    </tbody>
</table>

<p>lorem  <br><br><br><br><br><br><br><br><br><br><br><br>


{% include tables.html %}
