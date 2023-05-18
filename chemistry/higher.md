---
layout: content
title: Higher Chemistry
subject: Chemistry
level: Higher
permalink: /chemistry/higher
hero: Additional Chemistry Resources
subtext: Materials for the study of all SQA Chemistry courses.
headings:
  - id: databooks
    title: Data Booklets
  - id: reactionsummaries
    title: Reactions Summaries
  - id: multiplechoicedata
    title: Multiple Choice Data
tables:
  - title: Data Booklets
    description: Materials for the study of all SQA Chemistry courses.
    id: databbooks
    cols:
      - heading: Level of Study
      - heading: Data Book
  - title: Reaction Summaries
    description: false
    id: reactionsummaries
    cols:
      - heading: Level of Study
      - heading: Reaction Summary
---
    <!--
    <!-- Intro text for AH CHemistry page -->
    <div class="container">
    <h1>Additional Chemistry Resources</h1>
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
-->
<p>lorem  <br><br><br><br><br><br><br><br><br><br><br><br>
