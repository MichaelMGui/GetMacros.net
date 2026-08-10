// ---------------------------------------------------------------------
// Game 1: Macro Memory Match — classic flip-and-match memory game using
// real foods, color-coded by their dominant macronutrient.
// ---------------------------------------------------------------------
function initMemoryGame(rootId, pairs) {
  var root = document.getElementById(rootId);
  if (!root) return;

  var deck = [];
  pairs.forEach(function (p, i) {
    deck.push({ pairId: i, emoji: p.emoji, name: p.name, macro: p.macro });
    deck.push({ pairId: i, emoji: p.emoji, name: p.name, macro: p.macro });
  });

  var moves = 0;
  var matches = 0;
  var seconds = 0;
  var timer = null;
  var flipped = []; // indices currently face up, unmatched
  var locked = false;

  function shuffle(arr) {
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = arr[i];
      arr[i] = arr[j];
      arr[j] = t;
    }
    return arr;
  }

  function startTimer() {
    if (timer) return;
    timer = setInterval(function () {
      seconds++;
      updateStats();
    }, 1000);
  }

  function updateStats() {
    var stats = document.getElementById("mm-stats");
    if (!stats) return;
    stats.innerHTML =
      '<div class="stat"><span class="num">' + moves + '</span><span class="lbl">Moves</span></div>' +
      '<div class="stat"><span class="num">' + matches + "/" + pairs.length + '</span><span class="lbl">Matched</span></div>' +
      '<div class="stat"><span class="num">' + seconds + 's</span><span class="lbl">Time</span></div>';
  }

  function render() {
    shuffle(deck);
    var html = '<div class="game-stats" id="mm-stats"></div><div class="memory-grid" id="mm-grid">';
    deck.forEach(function (card, i) {
      html +=
        '<div class="memory-card" data-i="' + i + '"><div class="flip-inner">' +
        '<div class="face face-back">?</div>' +
        '<div class="face face-front"><span class="emoji">' + card.emoji + "</span><span>" + card.name +
        '</span><span class="pill ' + card.macro + '" style="margin:0;">' + card.macro + "</span></div>" +
        "</div></div>";
    });
    html += "</div>";
    root.innerHTML = html;
    updateStats();

    root.querySelectorAll(".memory-card").forEach(function (el) {
      el.addEventListener("click", function () {
        onCardClick(parseInt(el.getAttribute("data-i"), 10), el);
      });
    });
  }

  function onCardClick(i, el) {
    if (locked || el.classList.contains("flipped") || el.classList.contains("matched")) return;
    startTimer();
    el.classList.add("flipped");
    flipped.push({ i: i, el: el });

    if (flipped.length === 2) {
      moves++;
      updateStats();
      var a = flipped[0];
      var b = flipped[1];
      if (deck[a.i].pairId === deck[b.i].pairId) {
        a.el.classList.add("matched");
        b.el.classList.add("matched");
        flipped = [];
        matches++;
        updateStats();
        if (matches === pairs.length) {
          clearInterval(timer);
          setTimeout(showWin, 500);
        }
      } else {
        locked = true;
        setTimeout(function () {
          a.el.classList.remove("flipped");
          b.el.classList.remove("flipped");
          flipped = [];
          locked = false;
        }, 800);
      }
    }
  }

  function showWin() {
    root.innerHTML =
      '<div class="quiz-result">' +
      '<div class="score-badge" style="--pct:100"><span class="score-num">🎉</span><span class="score-den">Solved!</span></div>' +
      "<h2>Nice work</h2>" +
      '<p class="verdict">' + matches + " pairs matched in " + moves + " moves and " + seconds + " seconds.</p>" +
      '<div class="btn-row"><button type="button" class="btn btn-primary" id="mm-retry">Play again</button>' +
      '<a href="play.html" class="btn btn-outline" style="border-color:var(--color-primary-dark);color:var(--color-primary-dark);">More games</a></div>' +
      "</div>";
    document.getElementById("mm-retry").addEventListener("click", reset);
    if (typeof launchConfetti === "function") launchConfetti();
  }

  function reset() {
    moves = 0;
    matches = 0;
    seconds = 0;
    flipped = [];
    locked = false;
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    render();
  }

  reset();
}

// ---------------------------------------------------------------------
// Game 2: Build-a-Plate — pick foods to hit a randomly assigned macro
// target as closely as possible, graded on accuracy.
// ---------------------------------------------------------------------
function initPlateGame(rootId, foods, targets) {
  var root = document.getElementById(rootId);
  if (!root) return;

  var target = null;
  var counts = {}; // foodId -> serving count

  function pickTarget() {
    target = targets[Math.floor(Math.random() * targets.length)];
    counts = {};
    foods.forEach(function (f) {
      counts[f.id] = 0;
    });
  }

  function totals() {
    var t = { protein: 0, fat: 0, carb: 0 };
    foods.forEach(function (f) {
      var n = counts[f.id] || 0;
      t.protein += f.protein * n;
      t.fat += f.fat * n;
      t.carb += f.carb * n;
    });
    return t;
  }

  function pct(val, goal) {
    return Math.max(0, Math.min(100, Math.round((val / goal) * 100)));
  }

  function render() {
    var html =
      '<div class="plate-target">' +
      "<h3>Target: " + target.name + "</h3>" +
      '<p class="section-intro">' + target.desc + "</p>" +
      '<div id="pg-progress"></div>' +
      '<button type="button" class="calc-submit" id="pg-submit" style="margin-top:1rem;">Submit my plate</button>' +
      '<button type="button" class="btn btn-outline" id="pg-reset" style="margin-top:.6rem;width:100%;border-color:var(--color-border);color:var(--color-text);">Clear plate</button>' +
      "</div>" +
      '<div><h3 style="margin-top:0;">Pick foods</h3><div class="food-picker" id="pg-picker"></div></div>';
    root.innerHTML = html;

    var picker = document.getElementById("pg-picker");
    foods.forEach(function (f) {
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "food-chip";
      chip.innerHTML =
        '<span class="emoji">' + f.emoji + "</span>" + f.name +
        '<span class="count" id="pg-count-' + f.id + '"></span>';
      chip.addEventListener("click", function () {
        counts[f.id] = (counts[f.id] || 0) + 1;
        if (counts[f.id] > 6) counts[f.id] = 0;
        updateProgress();
      });
      picker.appendChild(chip);
    });

    document.getElementById("pg-submit").addEventListener("click", submit);
    document.getElementById("pg-reset").addEventListener("click", function () {
      foods.forEach(function (f) {
        counts[f.id] = 0;
      });
      updateProgress();
    });

    updateProgress();
  }

  function updateProgress() {
    var t = totals();
    var progress = document.getElementById("pg-progress");
    if (progress) {
      progress.innerHTML =
        macroBar("protein", "Protein", t.protein, target.protein) +
        macroBar("fat", "Fat", t.fat, target.fat) +
        macroBar("carbs", "Carb", t.carb, target.carb);
    }
    foods.forEach(function (f) {
      var el = document.getElementById("pg-count-" + f.id);
      if (el) el.textContent = counts[f.id] ? "×" + counts[f.id] : "";
      var chip = el ? el.closest(".food-chip") : null;
      if (chip) chip.classList.toggle("active", counts[f.id] > 0);
    });
  }

  function macroBar(cls, label, val, goal) {
    return (
      '<div class="macro-progress ' + cls + '"><div class="row"><span>' + label + "</span><span>" +
      Math.round(val) + "g / " + goal + 'g</span></div><div class="track"><span style="width:' +
      pct(val, goal) + '%"></span></div></div>'
    );
  }

  function grade(accuracy) {
    if (accuracy >= 90) return "S";
    if (accuracy >= 75) return "A";
    if (accuracy >= 55) return "B";
    if (accuracy >= 35) return "C";
    return "D";
  }

  function submit() {
    var t = totals();
    var errs = ["protein", "fat", "carb"].map(function (k) {
      var goal = target[k];
      return Math.min(1, Math.abs(t[k] - goal) / goal);
    });
    var avgErr = errs.reduce(function (a, b) { return a + b; }, 0) / errs.length;
    var accuracy = Math.round((1 - avgErr) * 100);
    var g = grade(accuracy);

    root.innerHTML =
      '<div class="quiz-result">' +
      '<div class="score-badge" style="--pct:' + accuracy + '"><span class="score-num">' + g +
      '</span><span class="score-den">' + accuracy + "% accurate</span></div>" +
      "<h2>Plate graded</h2>" +
      '<p class="verdict">Protein ' + Math.round(t.protein) + "g / " + target.protein + "g &middot; Fat " +
      Math.round(t.fat) + "g / " + target.fat + "g &middot; Carb " + Math.round(t.carb) + "g / " + target.carb + "g</p>" +
      '<div class="btn-row"><button type="button" class="btn btn-primary" id="pg-retry">New target</button>' +
      '<a href="play.html" class="btn btn-outline" style="border-color:var(--color-primary-dark);color:var(--color-primary-dark);">More games</a></div>' +
      "</div>";
    document.getElementById("pg-retry").addEventListener("click", reset);
    if (accuracy >= 75 && typeof launchConfetti === "function") launchConfetti();
  }

  function reset() {
    pickTarget();
    render();
  }

  reset();
}
