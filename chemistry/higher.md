---
layout: main-side
title: Higher Chemistry
subject: Chemistry
permalink: /chemistry/higher
sidebar-title: Additional materials
headings:
  - id: databooks
    title: Data Booklets
  - id: reactionsummaries
    title: Reactions Summaries
---

<div class="col">
    <!-- Intro text for AH CHemistry page -->
    <div class="container mt-5 mb-5">
        <h1>Additional Chemistry Resources</h1>
        <p class="lead">Materials for the study of all SQA Chemistry courses.</p>
        <!-- Table for data booklets -->
        <h2 style="padding-top:60px" id="databooks">Data Booklets</h2>
        <table class="table table-sm">
            <thead>
                <tr>
                    <th scope="col">Level Of Study</th>
                    <th scope="col">Data Book</th>
                </tr>
            </thead>
            <tbody>
                {% for item in site.downloads %}
                {% if item.category == "data-booklet" %}
                <tr>
                        <th scope="row">{{item.level}}</th>
                        <td><a href="/files/{{item.download}}">{{item.title}}</a></td>
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
                        <td><a href="/files/{{item.download}}">{{item.title}}</a></td>
                </tr>
                {% endif %}
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>