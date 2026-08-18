(function () {
  "use strict";
  var questions = [
    {prompt:"You want at least 600 calories and 40 g protein after a hard training day. Which documented order clears both targets?",answers:["Subway Footlong Rotisserie Chicken","McDonald’s Apple Slices","Dunkin’ Egg & Cheese Wake-Up Wrap"],correct:0,explanation:"The footlong lists 640 calories and 58 g protein. Its 1,280 mg sodium is a real tradeoff—not a reason to hide the match."},
    {prompt:"Eight grilled nuggets provide 130 calories and 25 g protein. You are hungry for a full lunch. What is the most useful next move?",answers:["Treat the nuggets as automatically complete because protein is high","Add food that fits your appetite, then count the full order","Choose the lowest-calorie sauce and ignore the side"],correct:1,explanation:"The nuggets are a compact entrée. A full lunch may need carbohydrate, produce, fat or simply more total food. Compare the order you will actually eat."},
    {prompt:"You want a portable vegetarian breakfast with more published protein and fibre. Which snapshot fits better?",answers:["Starbucks Eggs & Cheddar Protein Box","Dunkin’ Egg & Cheese Wake-Up Wrap","McDonald’s Apple Slices"],correct:0,explanation:"The Starbucks box lists 22 g protein and 5 g fibre. The Dunkin’ wrap lists 7 g protein and 0 g fibre; apple slices are a side."},
    {prompt:"Among these published standard builds, which has the lowest listed sodium?",answers:["McDonald’s Hamburger — 510 mg","Subway 6-inch Rotisserie Chicken — 640 mg","KFC grilled breast with green beans and corn — 1,040 mg"],correct:0,explanation:"The hamburger is lowest among these three at 510 mg. That does not make it a universal best meal; portion and the rest of the order still matter."},
    {prompt:"You want a substantial plant-based meal with published protein and fibre. Which choice is the strongest starting point?",answers:["Chipotle Sofritas Bowl","Panda Express Super Greens by itself","McDonald’s Apple Slices by itself"],correct:0,explanation:"The Sofritas Bowl lists 620 calories, 23 g protein and 15 g fibre. Super Greens and apple slices can be useful sides, but they are not comparable full meals."},
    {prompt:"A standard build has no obvious wheat ingredient, but you have celiac disease. What is the sound decision?",answers:["Assume gluten-aware means celiac-safe","Check the current allergen guide and ask about shared equipment","Only compare the calorie number"],correct:1,explanation:"Ingredient screening is not a cross-contact assessment. Shared fryers, surfaces, utensils and location practices can matter for celiac safety."},
    {prompt:"A restaurant publishes calories for a bowl but not a stable protein or sodium value. What should a trustworthy comparison do?",answers:["Estimate from a similar restaurant","Leave the values missing and link to the live nutrition tool","Treat missing sodium as zero"],correct:1,explanation:"Unknown is not zero. Leaving a value blank prevents false precision and tells the reader what still needs verification."},
    {prompt:"The entrée number does not include the sauce packet and side you plan to eat. Which total describes your meal?",answers:["The entrée only","Entrée plus the amounts of sauce and side actually eaten","Whichever number is lower"],correct:1,explanation:"The complete order determines the meal. Packets, dressings, sides and drinks count when they are used."}
  ];
  var index = 0, score = 0, locked = false;
  var card = document.querySelector("#challenge-card"), count = document.querySelector("#challenge-count"), scoreText = document.querySelector("#challenge-score"), bar = document.querySelector("#challenge-bar");
  if (!card || !count || !scoreText || !bar) return;
  function render() {
    locked = false;
    if (index === questions.length) {
      var message = score >= 7 ? "Strong restaurant decision-making." : score >= 5 ? "Good foundation—review the explanations you missed." : "Open the meal finder, use the numbers, then try again.";
      count.textContent = "Complete"; bar.style.width = "100%";
      card.innerHTML = '<p class="takeout-kicker">Your result</p><h2>' + score + " / " + questions.length + "</h2><p>" + message + '</p><div class="takeout-actions"><button class="takeout-button primary" id="play-again" type="button">Play again</button><a class="takeout-button" href="restaurant-meal-finder.html">Find my meals</a></div>';
      document.querySelector("#play-again").addEventListener("click", function () { index = 0; score = 0; scoreText.textContent = "Score: 0"; render(); }); return;
    }
    var question = questions[index];
    count.textContent = "Question " + (index + 1) + " of " + questions.length; bar.style.width = (index / questions.length * 100) + "%";
    card.innerHTML = '<p class="takeout-kicker">Make the call</p><h2 tabindex="-1">' + question.prompt + '</h2><div class="takeout-answers">' + question.answers.map(function (answer, answerIndex) { return '<button type="button" data-answer="' + answerIndex + '">' + answer + "</button>"; }).join("") + '</div><p class="takeout-feedback" id="challenge-feedback" role="status"></p><button class="takeout-button primary" id="challenge-next" type="button" hidden>' + (index === questions.length - 1 ? "See my score" : "Next question") + "</button>";
    card.querySelectorAll("[data-answer]").forEach(function (button) { button.addEventListener("click", function () { choose(Number(button.dataset.answer)); }); });
    document.querySelector("#challenge-next").addEventListener("click", function () { index += 1; render(); }); card.querySelector("h2").focus({preventScroll:true});
  }
  function choose(choice) {
    if (locked) return; locked = true; var question = questions[index];
    Array.from(card.querySelectorAll("[data-answer]")).forEach(function (button, answerIndex) { button.disabled = true; if (answerIndex === question.correct) button.classList.add("correct"); if (answerIndex === choice && choice !== question.correct) button.classList.add("wrong"); });
    if (choice === question.correct) { score += 1; scoreText.textContent = "Score: " + score; }
    document.querySelector("#challenge-feedback").innerHTML = "<strong>" + (choice === question.correct ? "That fits." : "Not the strongest choice.") + "</strong> " + question.explanation;
    document.querySelector("#challenge-next").hidden = false; bar.style.width = ((index + 1) / questions.length * 100) + "%";
  }
  render();
})();
