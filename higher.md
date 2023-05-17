---
layout: main-side
title: Higher Chemistry
subject: Chemistry
sidebar-title: testing12345
headings:
  - id: databooks
    title: Data Booklets
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
                {% if item.category == "data-booklets" %}
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