---
layout: landing
title: Home
subject: chemistry
---

<h2>Welcome to JABchem</h2>
<p class="text-secondary">A website for revision of Scottish SQA Exams in Chemistry, Maths, Physics and Biology at National 5, Higher and Advanced Higher. Included are SQA Past Papers, Marking Schemes, Traffic Light Evaluation Summaries, SQA Question Maps and so much more.</p>

<div class="h-100 p-5 mt-5 bg-light border rounded-3">
  <h2>A new look, JABchem <span class="badge bg-primary">V2</span></h2>
  <p>Some things have changed around here! Don't worry, all the same content you are used to from JABchem is still here, but it is now easier than ever to find and use. Dive right in to the subject you are after from the menus at the top or bottom of the page!</p>
</div>

<div class="col-12">
    <div class="row justify-content-center">
        <div class="col-md-3 my-2">
            <div class="card d-flex flex-column h-100" style="background-color:#{{site.chemcolour}};">
                <div class="card-body d-grid gap-2">
                    <h5 class="card-title">Chemistry {{site.chemlogo}}</h5>
                    <p>Past papers, JABchem Marking Schemes, Self-Evaluation materials - all you could need!</p>
                    <a href="{{'/chemistry' | relative_url}}" class="btn btn-primary mt-auto">Chemistry {{site.chemlogo}}</a>
                </div>
            </div>
        </div>
        <div class="col-md-3 my-2">
            <div class="card d-flex flex-column h-100" style="background-color:#{{site.mathcolour}};">
                <div class="card-body d-grid gap-2">
                    <h5 class="card-title">Maths {{site.mathlogo}}</h5>
                    <p>Past papers old and new, plenty to keep you busy revising!</p>
                    <a href="{{'/maths' | relative_url}}" class="btn btn-primary mt-auto">Maths {{site.mathlogo}}</a>
                </div>
            </div>
        </div>
        <div class="col-md-3 my-2">
            <div class="card d-flex flex-column h-100" style="background-color:#{{site.physicscolour}};">
                <div class="card-body d-grid gap-2">
                    <h5 class="card-title">Physics {{site.physicslogo}}</h5>
                    <p>Loads of past papers and intriguing study materials to fuel your Physics revision sessions!</p>
                    <a href="{{'/physics' | relative_url}}" class="btn btn-primary mt-auto">Physics {{site.physicslogo}}</a>
                </div>
            </div>
        </div>
        <div class="col-md-3 my-2">
            <div class="card d-flex flex-column h-100" style="background-color:#{{site.biocolour}};">
                <div class="card-body d-grid gap-2">
                    <h5 class="card-title">Biology {{site.biologo}}</h5>
                    <p>From old to new, a treasure trove of past papers awaits to enhance your Biology studies!</p>
                    <a href="{{'/biology' | relative_url}}" class="btn btn-primary mt-auto">Biology {{site.biologo}}</a>
                </div>
            </div>
        </div>
    </div>
</div>



<div class="h-100 p-5 mt-5 bg-primary text-light border rounded-3">
  <h2>We're looking for feedback!</h2>
  <p>With the launch of JABchem <span class="badge bg-light text-primary">V2</span> we are looking for feedback about how the new site is! Is it easy to navigate, does it look better? Tell us what you think below:</p>
  <a href="{{site.reporturl}}?indexfeedbackcall" class="btn btn-light">Give feeback</a>
</div>

