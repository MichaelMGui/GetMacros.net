// Reusable quiz engine. Each quiz page defines its own question array and
// calls renderQuiz('quiz-root', QUESTIONS, { title, tiers }).
// Question shape: { q, options: [...], correct: index, explain, link: {href, label} }
function renderQuiz(rootId, questions, opts) {
  opts = opts || {};
  var root = document.getElementById(rootId);
  if (!root) return;

  var current = 0;
  var score = 0;
  var picked = new Array(questions.length).fill(null);

  function progressPct() {
    return Math.round((current / questions.length) * 100);
  }

  function renderQuestion() {
    var item = questions[current];
    var html =
      '<div class="quiz-progress"><span style="width:' + progressPct() + '%"></span></div>' +
      '<p class="section-intro">Question ' + (current + 1) + ' of ' + questions.length + '</p>' +
      '<div class="quiz-q">' +
      "<h3>" + item.q + "</h3>" +
      '<div class="quiz-options">' +
      item.options
        .map(function (opt, i) {
          return '<button type="button" class="quiz-option" data-i="' + i + '">' + opt + "</button>";
        })
        .join("") +
      "</div>" +
      '<div class="quiz-explain" id="quiz-explain"></div>' +
      "</div>" +
      '<div id="quiz-nav"></div>';
    root.innerHTML = html;

    root.querySelectorAll(".quiz-option").forEach(function (btn) {
      btn.addEventListener("click", function () {
        selectOption(parseInt(btn.getAttribute("data-i"), 10));
      });
    });
  }

  function selectOption(i) {
    if (picked[current] !== null) return; // already answered
    var item = questions[current];
    picked[current] = i;
    var correct = i === item.correct;
    if (correct) score++;

    root.querySelectorAll(".quiz-option").forEach(function (btn, idx) {
      btn.disabled = true;
      if (idx === item.correct) btn.classList.add("correct");
      else if (idx === i) btn.classList.add("incorrect");
    });

    var explain = document.getElementById("quiz-explain");
    explain.innerHTML =
      (correct ? "<strong>Correct.</strong> " : "<strong>Not quite.</strong> ") +
      item.explain +
      (item.link ? ' <a href="' + item.link.href + '">' + item.link.label + " →</a>" : "");
    explain.classList.add("show");

    var nav = document.getElementById("quiz-nav");
    var isLast = current === questions.length - 1;
    nav.innerHTML =
      '<button type="button" class="calc-submit" id="quiz-next">' +
      (isLast ? "See my results" : "Next question →") +
      "</button>";
    document.getElementById("quiz-next").addEventListener("click", function () {
      if (isLast) {
        showResults();
      } else {
        current++;
        renderQuestion();
      }
    });
  }

  function tierMessage(pct) {
    var tiers = opts.tiers || [
      { min: 90, msg: "Macro expert. You clearly know this material cold." },
      { min: 70, msg: "Solid grasp of the fundamentals — a couple of gaps to close." },
      { min: 40, msg: "You're picking it up. Worth another pass through the articles." },
      { min: 0, msg: "A good starting point — the linked articles will fill in the gaps." },
    ];
    for (var i = 0; i < tiers.length; i++) {
      if (pct >= tiers[i].min) return tiers[i].msg;
    }
    return "";
  }

  function showResults() {
    var pct = Math.round((score / questions.length) * 100);
    root.innerHTML =
      '<div class="quiz-result">' +
      '<div class="score-badge" style="--pct:' + pct + '"><span class="score-num">' +
      score +
      '/' + questions.length + '</span><span class="score-den">' + pct + "% correct</span></div>" +
      "<h2>" + (opts.title || "Quiz complete") + "</h2>" +
      '<p class="verdict">' + tierMessage(pct) + "</p>" +
      '<div class="btn-row">' +
      '<button type="button" class="btn btn-primary" id="quiz-retry">Try again</button>' +
      (opts.moreHref ? '<a href="' + opts.moreHref + '" class="btn btn-outline" style="border-color:var(--color-primary-dark);color:var(--color-primary-dark);">More quizzes</a>' : "") +
      "</div></div>";

    document.getElementById("quiz-retry").addEventListener("click", function () {
      current = 0;
      score = 0;
      picked = new Array(questions.length).fill(null);
      renderQuestion();
    });

    if (pct >= 80 && typeof launchConfetti === "function") {
      launchConfetti();
    }
  }

  renderQuestion();
}
