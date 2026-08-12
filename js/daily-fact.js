(function () {
  var FACTS = [
    { text: "Protein has the highest thermic effect of any macronutrient — your body burns 20-30% of its calories just digesting it.", href: "thermic-effect-of-food-explained.html", label: "The thermic effect of food explained" },
    { text: "One gram of stored glycogen holds about 3 grams of water alongside it — why cutting carbs causes a fast, mostly-water weight drop.", href: "water-weight-vs-fat-loss.html", label: "Water weight vs. fat loss" },
    { text: "Fat has 9 calories per gram — more than double protein or carbs at 4 each.", href: "fats.html", label: "What fat actually does" },
    { text: "Muscle protein synthesis can stay elevated for up to 48 hours after a single resistance training session.", href: "protein-for-muscle-growth.html", label: "Protein for muscle growth" },
    { text: "Usain Bolt ate roughly 1,000 chicken nuggets over 10 days at the 2008 Beijing Olympics — and still broke 3 world records.", href: "famous-athlete-diets-fact-checked.html", label: "6 famous athlete diets, fact-checked" },
    { text: "The “Michael Phelps ate 12,000 calories a day” claim was a myth — the real number was closer to 8,000-10,000 on his heaviest days.", href: "famous-athlete-diets-fact-checked.html", label: "6 famous athlete diets, fact-checked" },
    { text: "Quinoa is one of the only plant foods that supplies all 9 essential amino acids on its own.", href: "complete-vs-incomplete-protein.html", label: "Complete vs. incomplete protein" },
    { text: "Your brain runs almost entirely on glucose and uses about 20% of your body's total energy at rest.", href: "carbs.html", label: "What carbohydrates actually do" },
    { text: "Norway flew in over 1,000kg of food — including salmon and cheese — for the 2026 World Cup.", href: "world-cup-2026-team-nutrition.html", label: "What World Cup 2026 teams are actually eating" },
    { text: "The “anabolic window” myth of needing protein within 30-60 minutes of a workout has been debunked — total daily intake matters far more.", href: "post-workout-anabolic-window.html", label: "The post-workout anabolic window" },
    { text: "Alcohol provides about 7 calories per gram — despite not being an official macronutrient.", href: "alcohol-and-macros.html", label: "Alcohol and macros" },
    { text: "Vitamins A, D, E, and K are fat-soluble — your body needs dietary fat present to absorb them.", href: "fats.html", label: "What fat actually does" },
    { text: "Creatine is one of the most-researched supplements in sports nutrition and is considered safe at doses up to 30g/day.", href: "creatine-explained.html", label: "Creatine explained" },
    { text: "A standard ketogenic diet keeps carbs under about 50g per day to maintain ketosis.", href: "ketogenic-diet-explained.html", label: "The ketogenic diet explained" },
    { text: "Most adults need 25g (women) to 38g (men) of fiber per day — and most people fall short.", href: "fiber-benefits.html", label: "Fiber benefits" },
    { text: "“Keto flu” isn't about ketones at all — it's mostly caused by rapid sodium and water loss.", href: "keto-flu-explained.html", label: "Keto flu explained" },
    { text: "The RDA of 0.8g protein/kg is the minimum to prevent deficiency — not an optimal target for anyone who trains.", href: "how-much-protein-per-day.html", label: "How much protein do you need per day?" },
    { text: "“Net carbs” isn't an FDA-regulated term — different brands calculate it differently.", href: "net-carbs-vs-total-carbs.html", label: "Net carbs vs. total carbs" },
    { text: "Regular seafood intake (about 8oz/week) is linked to roughly 36% lower risk of death from heart disease.", href: "pescatarian-diet-explained.html", label: "The pescatarian diet explained" },
    { text: "The carnivore diet's biggest documented risk is deficiency in vitamin C, magnesium, and calcium — all normally sourced from plants.", href: "carnivore-diet-explained.html", label: "The carnivore diet explained" },
    { text: "A tablespoon of olive oil is almost pure fat — about 14 grams.", href: "healthy-high-fat-foods.html", label: "Healthy high-fat foods" },
    { text: "Severe protein deficiency is called kwashiorkor and causes swelling, a swollen liver, and impaired growth.", href: "protein-deficiency-symptoms.html", label: "Signs of protein deficiency" },
    { text: "The paleo diet typically runs high protein (19-35%), moderate fat (28-58%), and low carb (22-40%) of total calories.", href: "paleo-diet-explained.html", label: "The paleo diet explained" },
    { text: "Cristiano Ronaldo reportedly eats about six small meals every 2-4 hours to keep his blood sugar steady.", href: "famous-athlete-diets-fact-checked.html", label: "6 famous athlete diets, fact-checked" },
    { text: "A pear with the skin on has about 5.5 grams of fiber — more than most people get from an entire meal.", href: "high-fiber-foods-list.html", label: "15 high-fiber foods" },
    { text: "The National Academies recommend about 3.7L/day of total water for men and 2.7L/day for women, from all food and drink combined.", href: "how-much-water-should-you-drink-per-day.html", label: "How much water should you drink per day?" },
    { text: "Non-celiac athletes who go gluten-free show no measurable performance difference in controlled trials.", href: "do-elimination-diets-improve-performance.html", label: "Do elimination diets improve performance?" },
    { text: "Trans fat is mainly created through partial hydrogenation — pumping hydrogen into liquid oil to make it shelf-stable.", href: "trans-fat-explained.html", label: "What is trans fat?" },
    { text: "Sarcopenia — age-related muscle loss — can be slowed significantly with adequate protein intake and resistance training.", href: "protein-deficiency-symptoms.html", label: "Signs of protein deficiency" },
    { text: "Body recomposition (building muscle and losing fat at once) works best for beginners or people returning after a training break.", href: "body-recomposition-explained.html", label: "Body recomposition explained" }
  ];

  function dayOfYear(d) {
    var start = new Date(d.getFullYear(), 0, 0);
    var diff = d - start;
    return Math.floor(diff / 86400000);
  }

  function init() {
    var el = document.getElementById("daily-fact");
    if (!el) return;
    var fact = FACTS[dayOfYear(new Date()) % FACTS.length];
    el.querySelector(".fact-text").textContent = fact.text;
    var link = el.querySelector(".fact-link");
    link.href = fact.href;
    link.textContent = "Read: " + fact.label + " →";
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
