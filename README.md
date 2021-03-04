# Geography Quiz for Naval Intelligence Officers
#### Video Demo:  <URL HERE>
#### Project Website: www.arcticzombiefire.com
#### Github link: https://github.com/L-R-Ryan/NavyGeoQuiz
#### Description:

The Navy gives a geography test to it's incoming Intelligence Officers. The study
materials are a series of powerpoints that aren't interactive. I digitized the
study materials in a quiz app to make it easy for me and my co-selectees to study.

The landing page shows the user all of the potential quiz slides and allow the
user to tailor the quiz to their needs by allowing them to choose which slides
on which to be tested. There is also a "check-all" button for ease.

When the user selects the slides and hits the "Start Quiz" button, the first
slide is presented. I hard-coded the location of the form input boxes to be placed
on top of the blank boxes that were already present on the study materials provided.
The result on the app is a messy appearance - I may choose to make the boxes invisible
so that the user has a cleaner view. I haven't decided yet which is more user friendly.

The "Submit" button is has a hard-coded location to the left of the image. Currently,
this means that the website cannot be used on mobile. Future plans for this
website may include a mobile-friendly version with the buttons in a different
spot and the forms changing to multi-select rather than free text fields.

When the answers are submitted, the user views a table with the correct answer,
the submitted answer, and whether or not the submitted answer was correct. If the
answer is incorrect, then the text "Incorrect!" appears in red. A slide appears at
the bottom of a table for reference. Another point for future development is to
make the slide at the bottom contain the answers so that users can check exactly
where the locations were. I haven't done this yet because I am not keen to edit
another 20 slides unless I think other sailors will actually use this tool!

When the user clicks "Continue" the next chosen slide is presented and the cycle
repeats until the user is presented with a final score.

The project has evolved considerably since I wrote it for CS50. I have adapted it
to google app engines so that I can host the project on an actual website. I am
also using google's sql engine to manage the underlying sql tables. The sql tables
are all tagged with a unique user id so that multiple people can take the quiz
at the same time. A cron job deletes the created sql tables on a regular basis.   
