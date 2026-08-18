#!/usr/bin/env python3
"""Build es/index.html and fr/index.html from the English homepage.

The localized homepages are the same document as index.html: same sections,
same classes, same markup order. Only the copy, the language metadata and the
relative paths differ, so they are generated rather than maintained by hand.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

# Visible copy, in the order it appears in index.html. Every source string must
# be unique in the document so the substitution cannot land in the wrong place.
STRINGS = [
    # (english, spanish, french)
    ("GetMacros — Nutrition That Fits Real Life",
     "GetMacros — Nutrición que encaja en la vida real",
     "GetMacros — La nutrition adaptée à la vraie vie"),
    ("Practical nutrition tools, macro guides, healthy fast-food picks and clear explainers built for real decisions.",
     "Herramientas prácticas de nutrición, guías de macros, opciones saludables de comida rápida y explicaciones claras para decisiones reales.",
     "Des outils de nutrition pratiques, des guides de macros, des choix de restauration rapide plus sains et des explications claires pour de vraies décisions."),
    # Nav
    ('<a href="../index.html" aria-current="page">Home</a>',
     '<a href="../index.html">Inicio</a>',
     '<a href="../index.html">Accueil</a>'),
    (">Articles</a>", ">Artículos</a>", ">Articles</a>"),
    (">Calculators</a>", ">Calculadoras</a>", ">Calculatrices</a>"),
    (">Quizzes &amp; Games</a>", ">Cuestionarios y juegos</a>", ">Quiz et jeux</a>"),
    (">Healthy Fast Food</a>", ">Comida rápida saludable</a>", ">Restauration rapide saine</a>"),
    (">Glossary</a>", ">Glosario</a>", ">Glossaire</a>"),
    (">Sources</a>", ">Fuentes</a>", ">Sources</a>"),
    (">Search</a>", ">Buscar</a>", ">Recherche</a>"),
    (">Contact</a>", ">Contacto</a>", ">Contact</a>"),
    ('>Find my meal</a>', '>Encontrar mi comida</a>', '>Trouver mon repas</a>'),
    ("Skip to main content", "Saltar al contenido principal", "Aller au contenu principal"),
    ("GetMacros.net home", "Inicio de GetMacros.net", "Accueil de GetMacros.net"),
    ("Main navigation", "Navegación principal", "Navigation principale"),
    # Hero
    ("Nutrition without the noise", "Nutrición sin ruido", "La nutrition sans le bruit"),
    ("Eat with more clarity.<br><em>Live with less math.</em>",
     "Come con más claridad.<br><em>Vive con menos cálculos.</em>",
     "Mangez plus clairement.<br><em>Vivez avec moins de calculs.</em>"),
    ("Useful answers for groceries, training and the drive-thru—grounded in credible sources, made for ordinary days.",
     "Respuestas útiles para el supermercado, el entrenamiento y la ventanilla del auto: basadas en fuentes fiables y pensadas para el día a día.",
     "Des réponses utiles pour les courses, l’entraînement et le service au volant : fondées sur des sources fiables et pensées pour le quotidien."),
    (">Find a fast-food meal</a>", ">Buscar comida rápida</a>", ">Trouver un repas rapide</a>"),
    (">Calculate my macros</a>", ">Calcular mis macros</a>", ">Calculer mes macros</a>"),
    ("<strong>340</strong> focused guides", "<strong>340</strong> guías enfocadas", "<strong>340</strong> guides ciblés"),
    ("<strong>15</strong> restaurant chains", "<strong>15</strong> cadenas de restaurantes", "<strong>15</strong> chaînes de restaurants"),
    # Value-first like the other two stats, so the label wraps under the number.
    ("<strong>Free</strong> practical tools", "<strong>100%</strong> gratis y práctico", "<strong>100 %</strong> gratuit et pratique"),
    ("Macro balance illustration", "Ilustración del equilibrio de macros", "Illustration de l’équilibre des macros"),
    ("<span>Protein</span><strong>build + repair</strong>",
     "<span>Proteína</span><strong>construir + reparar</strong>",
     "<span>Protéines</span><strong>construire + réparer</strong>"),
    ("<span>Carbs</span><strong>fuel + focus</strong>",
     "<span>Carbohidratos</span><strong>energía + concentración</strong>",
     "<span>Glucides</span><strong>énergie + concentration</strong>"),
    ("<span>Fats</span><strong>support + satisfy</strong>",
     "<span>Grasas</span><strong>sostener + saciar</strong>",
     "<span>Lipides</span><strong>soutenir + rassasier</strong>"),
    ("<span>your</span><strong>real life</strong>",
     "<span>tu</span><strong>vida real</strong>",
     "<span>votre</span><strong>vraie vie</strong>"),
    # Paths section
    ("Start with what you need", "Empieza por lo que necesitas", "Commencez par ce dont vous avez besoin"),
    ("Three useful paths. No content maze.",
     "Tres caminos útiles. Sin laberinto de contenido.",
     "Trois parcours utiles. Sans labyrinthe de contenu."),
    (">Most practical</span>", ">Lo más práctico</span>", ">Le plus pratique</span>"),
    ("<h3>Healthy fast food</h3>", "<h3>Comida rápida saludable</h3>", "<h3>Restauration rapide saine</h3>"),
    ("Ready-made orders with macros, dietary filters and a goal-based recommender.",
     "Pedidos ya preparados con macros, filtros dietéticos y un recomendador según tu objetivo.",
     "Des commandes prêtes à l’emploi avec macros, filtres alimentaires et recommandations selon votre objectif."),
    (">See the picks →</span>", ">Ver las opciones →</span>", ">Voir la sélection →</span>"),
    ("<h3>Know your numbers</h3>", "<h3>Conoce tus números</h3>", "<h3>Connaissez vos chiffres</h3>"),
    ("Estimate macros, energy needs, recipe portions and hydration with transparent assumptions.",
     "Estima macros, necesidades energéticas, porciones de recetas e hidratación con supuestos transparentes.",
     "Estimez vos macros, vos besoins énergétiques, les portions de recettes et l’hydratation avec des hypothèses transparentes."),
    (">Use a calculator →</span>", ">Usar una calculadora →</span>", ">Utiliser une calculatrice →</span>"),
    ("<h3>Understand the why</h3>", "<h3>Entiende el porqué</h3>", "<h3>Comprenez le pourquoi</h3>"),
    ("Browse a curated topic map instead of scrolling through hundreds of disconnected links.",
     "Explora un mapa de temas seleccionado en vez de recorrer cientos de enlaces sueltos.",
     "Parcourez une carte thématique organisée au lieu de faire défiler des centaines de liens épars."),
    (">Choose a topic →</span>", ">Elegir un tema →</span>", ">Choisir un thème →</span>"),
    # Spotlight
    ("Tonight’s shortcut", "El atajo de hoy", "Le raccourci du soir"),
    ("Tell us what matters.<br>We’ll narrow the menu.",
     "Dinos qué te importa.<br>Reducimos el menú.",
     "Dites-nous ce qui compte.<br>Nous réduisons le menu."),
    ("Pick a goal, eating pattern and calorie range. The finder ranks compatible restaurant meals and explains why each one fits.",
     "Elige un objetivo, un patrón de alimentación y un rango de calorías. El buscador ordena las comidas compatibles y explica por qué encaja cada una.",
     "Choisissez un objectif, un mode d’alimentation et une plage de calories. L’outil classe les repas compatibles et explique pourquoi chacun convient."),
    (">Get my recommendation</a>", ">Ver mi recomendación</a>", ">Voir ma recommandation</a>"),
    (">Best match</span>", ">Mejor coincidencia</span>", ">Meilleure correspondance</span>"),
    ("<h3>High-Protein Bowl</h3>", "<h3>Bol alto en proteína</h3>", "<h3>Bol riche en protéines</h3>"),
    ("<strong>46g</strong> protein", "<strong>46 g</strong> de proteína", "<strong>46 g</strong> de protéines"),
    ("<strong>14g</strong> fibre", "<strong>14 g</strong> de fibra", "<strong>14 g</strong> de fibres"),
    # Calculator
    ("Your numbers, explained", "Tus números, explicados", "Vos chiffres, expliqués"),
    ("<h2>Quick macro calculator</h2>", "<h2>Calculadora rápida de macros</h2>", "<h2>Calculatrice rapide de macros</h2>"),
    ("Estimate daily calories, protein, fat and carbohydrates with the same transparent Mifflin–St Jeor method used in the full calculator.",
     "Estima calorías, proteína, grasa y carbohidratos diarios con el mismo método transparente de Mifflin–St Jeor que usa la calculadora completa.",
     "Estimez vos calories, protéines, lipides et glucides quotidiens avec la même méthode transparente de Mifflin–St Jeor que la calculatrice complète."),
    ("<li>Change any input and recalculate</li>", "<li>Cambia cualquier dato y vuelve a calcular</li>", "<li>Modifiez une valeur et recalculez</li>"),
    ("<li>See BMR and estimated TDEE</li>", "<li>Consulta el TMB y el GET estimado</li>", "<li>Consultez le MB et la DEJ estimée</li>"),
    ("<li>Open the full calculator for unit controls and deeper context</li>",
     "<li>Abre la calculadora completa para cambiar unidades y ver más contexto</li>",
     "<li>Ouvrez la calculatrice complète pour les unités et plus de contexte</li>"),
    (">Open every calculator →</a>", ">Abrir todas las calculadoras →</a>", ">Ouvrir toutes les calculatrices →</a>"),
    (">Age</label>", ">Edad</label>", ">Âge</label>"),
    (">Equation sex</label>", ">Sexo para la ecuación</label>", ">Sexe pour l’équation</label>"),
    ('<option value="female">Female</option><option value="male">Male</option>',
     '<option value="female">Mujer</option><option value="male">Hombre</option>',
     '<option value="female">Femme</option><option value="male">Homme</option>'),
    (">Weight (lb)</label>", ">Peso (lb)</label>", ">Poids (lb)</label>"),
    (">Height (in)</label>", ">Altura (in)</label>", ">Taille (in)</label>"),
    (">Activity</label>", ">Actividad</label>", ">Activité</label>"),
    ('<option value="1.2">Mostly sitting</option>', '<option value="1.2">Mayormente sentado</option>', '<option value="1.2">Principalement assis</option>'),
    ('<option value="1.375">Light activity, 1–3 days/week</option>',
     '<option value="1.375">Actividad ligera, 1–3 días/semana</option>',
     '<option value="1.375">Activité légère, 1–3 jours/semaine</option>'),
    ('<option value="1.55" selected>Moderate activity, 3–5 days/week</option>',
     '<option value="1.55" selected>Actividad moderada, 3–5 días/semana</option>',
     '<option value="1.55" selected>Activité modérée, 3–5 jours/semaine</option>'),
    ('<option value="1.725">High activity, 6–7 days/week</option>',
     '<option value="1.725">Actividad alta, 6–7 días/semana</option>',
     '<option value="1.725">Activité élevée, 6–7 jours/semaine</option>'),
    ('<option value="1.9">Very high activity or physical job</option>',
     '<option value="1.9">Actividad muy alta o trabajo físico</option>',
     '<option value="1.9">Activité très élevée ou métier physique</option>'),
    (">Goal</label>", ">Objetivo</label>", ">Objectif</label>"),
    ('<option value="lose">Gradual fat loss</option>', '<option value="lose">Pérdida de grasa gradual</option>', '<option value="lose">Perte de graisse progressive</option>'),
    ('<option value="maintain" selected>Maintain weight</option>',
     '<option value="maintain" selected>Mantener el peso</option>',
     '<option value="maintain" selected>Maintenir le poids</option>'),
    ('<option value="gain">Build muscle</option>', '<option value="gain">Ganar músculo</option>', '<option value="gain">Prendre du muscle</option>'),
    ('type="submit">Calculate my macros</button>', 'type="submit">Calcular mis macros</button>', 'type="submit">Calculer mes macros</button>'),
    ("<span>Estimated daily target</span>", "<span>Objetivo diario estimado</span>", "<span>Objectif quotidien estimé</span>"),
    ("<small>calories</small>", "<small>calorías</small>", "<small>calories</small>"),
    ('<b id="hc-protein">—</b>protein', '<b id="hc-protein">—</b>proteína', '<b id="hc-protein">—</b>protéines'),
    ('<b id="hc-carbs">—</b>carbs', '<b id="hc-carbs">—</b>carbohidratos', '<b id="hc-carbs">—</b>glucides'),
    ('<b id="hc-fat">—</b>fat', '<b id="hc-fat">—</b>grasa', '<b id="hc-fat">—</b>lipides'),
    ("For educational use by generally healthy adults. Estimates are not medical prescriptions and may not fit pregnancy, growth, illness or eating-disorder recovery.",
     "Para uso educativo en adultos sanos. Las estimaciones no son prescripciones médicas y pueden no servir en embarazo, crecimiento, enfermedad o recuperación de un trastorno alimentario.",
     "À usage éducatif pour des adultes en bonne santé. Ces estimations ne sont pas des prescriptions médicales et peuvent ne pas convenir en cas de grossesse, de croissance, de maladie ou de rétablissement d’un trouble alimentaire."),
    # Everything hub
    ("Everything is still here", "Todo sigue aquí", "Tout est toujours là"),
    ("One organized door to the whole site.", "Una puerta ordenada a todo el sitio.", "Une porte d’entrée organisée vers tout le site."),
    ("The homepage is shorter now, but nothing useful is buried. Choose a collection or open the complete searchable library.",
     "La portada es más corta, pero nada útil queda enterrado. Elige una colección o abre la biblioteca completa con buscador.",
     "La page d’accueil est plus courte, mais rien d’utile n’est enfoui. Choisissez une collection ou ouvrez la bibliothèque complète."),
    ("<h3>Articles &amp; explainers</h3>", "<h3>Artículos y explicaciones</h3>", "<h3>Articles et explications</h3>"),
    ("All 340 evidence-led articles, from macro basics to deeper health topics.",
     "Los 340 artículos basados en evidencia, desde lo básico de las macros hasta temas de salud más profundos.",
     "Les 340 articles fondés sur les preuves, des bases des macros aux sujets de santé plus poussés."),
    (">Browse all articles <b>→</b></a>", ">Ver todos los artículos <b>→</b></a>", ">Voir tous les articles <b>→</b></a>"),
    (">Search the entire site <b>→</b></a>", ">Buscar en todo el sitio <b>→</b></a>", ">Rechercher sur tout le site <b>→</b></a>"),
    (">Open the glossary <b>→</b></a>", ">Abrir el glosario <b>→</b></a>", ">Ouvrir le glossaire <b>→</b></a>"),
    ("<h3>Tools &amp; calculators</h3>", "<h3>Herramientas y calculadoras</h3>", "<h3>Outils et calculatrices</h3>"),
    ("Macro targets, recipe scaling, protein value, nutrition labels, hydration and planning tools.",
     "Objetivos de macros, escalado de recetas, valor proteico, etiquetas nutricionales, hidratación y planificación.",
     "Objectifs de macros, mise à l’échelle des recettes, valeur protéique, étiquettes nutritionnelles, hydratation et planification."),
    (">All calculators <b>→</b></a>", ">Todas las calculadoras <b>→</b></a>", ">Toutes les calculatrices <b>→</b></a>"),
    (">Recipe macro scaler <b>→</b></a>", ">Escalador de macros de recetas <b>→</b></a>", ">Mise à l’échelle des recettes <b>→</b></a>"),
    (">Compare labels <b>→</b></a>", ">Comparar etiquetas <b>→</b></a>", ">Comparer les étiquettes <b>→</b></a>"),
    (">Budget meal builder <b>→</b></a>", ">Comidas económicas <b>→</b></a>", ">Repas à petit budget <b>→</b></a>"),
    ("<h3>Games &amp; quizzes</h3>", "<h3>Juegos y cuestionarios</h3>", "<h3>Jeux et quiz</h3>"),
    ("Practice food labels, meal building, macros, hydration, myths and safety.",
     "Practica con etiquetas, armado de comidas, macros, hidratación, mitos y seguridad alimentaria.",
     "Entraînez-vous sur les étiquettes, la composition des repas, les macros, l’hydratation, les mythes et la sécurité."),
    (">All games and quizzes <b>→</b></a>", ">Todos los juegos y cuestionarios <b>→</b></a>", ">Tous les jeux et quiz <b>→</b></a>"),
    (">Macro Sprint <b>→</b></a>", ">Macro Sprint <b>→</b></a>", ">Macro Sprint <b>→</b></a>"),
    (">Label Detective <b>→</b></a>", ">Detective de etiquetas <b>→</b></a>", ">Détective des étiquettes <b>→</b></a>"),
    (">Takeout Challenge <b>→</b></a>", ">Reto de comida para llevar <b>→</b></a>", ">Défi plats à emporter <b>→</b></a>"),
    ("<h3>Food in real life</h3>", "<h3>La comida en la vida real</h3>", "<h3>L’alimentation au quotidien</h3>"),
    ("Meals, groceries, budgets, storage, allergies and eating away from home.",
     "Comidas, compras, presupuesto, conservación, alergias y comer fuera de casa.",
     "Repas, courses, budget, conservation, allergies et repas hors du domicile."),
    (">Healthy fast food <b>→</b></a>", ">Comida rápida saludable <b>→</b></a>", ">Restauration rapide saine <b>→</b></a>"),
    (">Meal-building guides <b>→</b></a>", ">Guías para armar comidas <b>→</b></a>", ">Guides de composition des repas <b>→</b></a>"),
    (">Budget and pantry <b>→</b></a>", ">Presupuesto y despensa <b>→</b></a>", ">Budget et garde-manger <b>→</b></a>"),
    (">Food safety <b>→</b></a>", ">Seguridad alimentaria <b>→</b></a>", ">Sécurité alimentaire <b>→</b></a>"),
    ("<strong>Nutrition collections</strong>", "<strong>Colecciones de nutrición</strong>", "<strong>Collections nutrition</strong>"),
    ("<small>Macros, micronutrients, performance, hydration, life stages and health guides</small>",
     "<small>Macros, micronutrientes, rendimiento, hidratación, etapas de la vida y guías de salud</small>",
     "<small>Macros, micronutriments, performance, hydratation, étapes de la vie et guides santé</small>"),
    ("<b>Browse all topics</b>", "<b>Ver todos los temas</b>", "<b>Voir tous les thèmes</b>"),
    ("<h3>Nutrition foundations</h3>", "<h3>Fundamentos de nutrición</h3>", "<h3>Les bases de la nutrition</h3>"),
    (">Everyday nutrition</a>", ">Nutrición diaria</a>", ">Nutrition au quotidien</a>"),
    (">Protein</a>", ">Proteína</a>", ">Protéines</a>"),
    (">Carbohydrates</a>", ">Carbohidratos</a>", ">Glucides</a>"),
    (">Fats</a>", ">Grasas</a>", ">Lipides</a>"),
    (">Vitamins and minerals</a>", ">Vitaminas y minerales</a>", ">Vitamines et minéraux</a>"),
    (">Food measurement</a>", ">Medición de alimentos</a>", ">Mesure des aliments</a>"),
    ("<h3>Performance &amp; lifestyle</h3>", "<h3>Rendimiento y estilo de vida</h3>", "<h3>Performance et mode de vie</h3>"),
    (">Training and recovery</a>", ">Entrenamiento y recuperación</a>", ">Entraînement et récupération</a>"),
    (">Hydration</a>", ">Hidratación</a>", ">Hydratation</a>"),
    (">Children and teens</a>", ">Niños y adolescentes</a>", ">Enfants et adolescents</a>"),
    (">Pregnancy and breastfeeding</a>", ">Embarazo y lactancia</a>", ">Grossesse et allaitement</a>"),
    (">Healthy aging</a>", ">Envejecimiento saludable</a>", ">Vieillir en bonne santé</a>"),
    ("<h3>Health-focused guides</h3>", "<h3>Guías centradas en la salud</h3>", "<h3>Guides axés sur la santé</h3>"),
    (">Heart health</a>", ">Salud cardiovascular</a>", ">Santé cardiaque</a>"),
    (">Blood sugar</a>", ">Azúcar en sangre</a>", ">Glycémie</a>"),
    (">Digestive health</a>", ">Salud digestiva</a>", ">Santé digestive</a>"),
    (">Iron and anemia</a>", ">Hierro y anemia</a>", ">Fer et anémie</a>"),
    (">Thyroid health</a>", ">Salud tiroidea</a>", ">Santé thyroïdienne</a>"),
    ("<h3>More collections</h3>", "<h3>Más colecciones</h3>", "<h3>Autres collections</h3>"),
    (">Kidney health</a>", ">Salud renal</a>", ">Santé rénale</a>"),
    (">Liver health</a>", ">Salud hepática</a>", ">Santé du foie</a>"),
    (">Menopause</a>", ">Menopausia</a>", ">Ménopause</a>"),
    ("<strong>View complete topic directory →</strong>", "<strong>Ver el directorio completo de temas →</strong>", "<strong>Voir l’annuaire complet des thèmes →</strong>"),
    # Trust
    ("Built to earn trust", "Hecho para ganarse tu confianza", "Conçu pour mériter votre confiance"),
    ("Useful enough to return to.", "Lo bastante útil para volver.", "Assez utile pour y revenir."),
    ("No fake doctor bylines. No miracle language. No hiding uncertainty.",
     "Sin firmas médicas falsas. Sin lenguaje milagroso. Sin ocultar la incertidumbre.",
     "Pas de fausses signatures de médecins. Pas de promesses miracles. Pas d’incertitude cachée."),
    ("<h3>Sources you can open</h3>", "<h3>Fuentes que puedes abrir</h3>", "<h3>Des sources consultables</h3>"),
    ("Primary public-health, academic and official restaurant data sit close to the claim.",
     "Los datos de salud pública, académicos y oficiales de los restaurantes van junto a cada afirmación.",
     "Les données de santé publique, universitaires et officielles des restaurants accompagnent chaque affirmation."),
    ("<h3>Context over commandments</h3>", "<h3>Contexto antes que mandamientos</h3>", "<h3>Le contexte plutôt que les règles</h3>"),
    ("Food choices depend on appetite, culture, budget and medical needs—not internet morality.",
     "Lo que comes depende del apetito, la cultura, el presupuesto y tus necesidades médicas, no de la moral de internet.",
     "Les choix alimentaires dépendent de l’appétit, de la culture, du budget et des besoins médicaux, pas de la morale d’internet."),
    ("<h3>Tools that explain</h3>", "<h3>Herramientas que explican</h3>", "<h3>Des outils qui expliquent</h3>"),
    ("Results show assumptions and limits so a number never pretends to be a diagnosis.",
     "Los resultados muestran supuestos y límites para que ningún número pretenda ser un diagnóstico.",
     "Les résultats affichent les hypothèses et les limites : un chiffre ne prétend jamais être un diagnostic."),
    # Final CTA
    ("Keep it simple", "Hazlo simple", "Restons simples"),
    ("What do you want to do next?", "¿Qué quieres hacer ahora?", "Que voulez-vous faire ensuite ?"),
    (">Choose a restaurant meal</a>", ">Elegir una comida de restaurante</a>", ">Choisir un repas au restaurant</a>"),
    (">Search a nutrition question</a>", ">Buscar una duda de nutrición</a>", ">Poser une question nutrition</a>"),
    (">Play a quick game</a>", ">Jugar una partida rápida</a>", ">Jouer une partie rapide</a>"),
    # Footer
    ("Clear nutrition tools for real decisions. Independent, evidence-led and judgment-free.",
     "Herramientas de nutrición claras para decisiones reales. Independientes, basadas en evidencia y sin juicios.",
     "Des outils de nutrition clairs pour de vraies décisions. Indépendants, fondés sur les preuves et sans jugement."),
    ("<strong>Explore</strong>", "<strong>Explorar</strong>", "<strong>Explorer</strong>"),
    (">Healthy fast food</a>", ">Comida rápida saludable</a>", ">Restauration rapide saine</a>"),
    (">Calculators</a>", ">Calculadoras</a>", ">Calculatrices</a>"),
    (">Articles</a>", ">Artículos</a>", ">Articles</a>"),
    (">Quizzes &amp; games</a>", ">Cuestionarios y juegos</a>", ">Quiz et jeux</a>"),
    ("<strong>Reference</strong>", "<strong>Referencia</strong>", "<strong>Référence</strong>"),
    (">Glossary</a>", ">Glosario</a>", ">Glossaire</a>"),
    (">Editorial policy</a>", ">Política editorial</a>", ">Politique éditoriale</a>"),
    ("<strong>Company</strong>", "<strong>Sobre nosotros</strong>", "<strong>À propos</strong>"),
    (">About</a>", ">Quiénes somos</a>", ">Qui sommes-nous</a>"),
    (">Privacy</a>", ">Privacidad</a>", ">Confidentialité</a>"),
    (">Terms of use</a>", ">Términos de uso</a>", ">Conditions d’utilisation</a>"),
    ("© 2026 GetMacros.net · Educational information, not individualized medical advice.",
     "© 2026 GetMacros.net · Información educativa, no consejo médico individualizado.",
     "© 2026 GetMacros.net · Information éducative, pas un avis médical individualisé."),
]

# Strings the calculator script reads off the form at run time.
CALC_DATA = {
    "es": {
        "err-text": "Revisa la edad, el peso y la altura.",
        "goal-lose": "pérdida de grasa gradual",
        "goal-maintain": "mantenimiento",
        "goal-gain": "ganancia muscular",
        "bmr-label": "TMB",
        "tdee-label": "GET estimado",
    },
    "fr": {
        "err-text": "Vérifiez l’âge, le poids et la taille.",
        "goal-lose": "perte de graisse progressive",
        "goal-maintain": "maintien",
        "goal-gain": "prise de muscle",
        "bmr-label": "MB",
        "tdee-label": "DEJ estimée",
    },
}

LOCALES = {
    "es": {"lang": "es", "code": "ES", "other": ("EN", "FR"), "dir": "es"},
    "fr": {"lang": "fr", "code": "FR", "other": ("EN", "ES"), "dir": "fr"},
}


def localize(src, loc):
    """Turn the English homepage into the es/ or fr/ homepage."""
    idx = 1 if loc == "es" else 2
    html = src

    # 1. Relative paths move one directory down.
    html = re.sub(r'(href|src)="(?!https?:|#|/|\.\./)([^"]+)"', r'\1="../\2"', html)

    # 2. Language metadata.
    html = html.replace('<html lang="en">', f'<html lang="{LOCALES[loc]["lang"]}">')
    # index.html carries its own hreflang cluster. Drop it before rewriting
    # self-referencing URLs, otherwise the blanket getmacros.net/ substitution
    # below turns the "en" and "x-default" alternates into this locale and the
    # page ships two conflicting clusters.
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*"\s*/?>', "", html)
    html = html.replace('href="https://getmacros.net/"', f'href="https://getmacros.net/{loc}/"')
    html = html.replace('content="https://getmacros.net/"', f'content="https://getmacros.net/{loc}/"')
    html = html.replace('"url":"https://getmacros.net/"', f'"url":"https://getmacros.net/{loc}/"')
    html = html.replace(
        '<link rel="canonical"',
        '<link rel="alternate" hreflang="en" href="https://getmacros.net/">'
        '<link rel="alternate" hreflang="es" href="https://getmacros.net/es/">'
        '<link rel="alternate" hreflang="fr" href="https://getmacros.net/fr/">'
        '<link rel="alternate" hreflang="x-default" href="https://getmacros.net/">'
        '<link rel="canonical"',
        1,
    )

    # 3. Language switcher: current locale active, siblings relative to here.
    old_switch = ('<div class="lang-switch"><a href="../index.html" aria-current="page">EN</a>'
                  '<a href="../es/">ES</a><a href="../fr/">FR</a></div>')
    if loc == "es":
        new_switch = ('<div class="lang-switch"><a href="../index.html">EN</a>'
                      '<a href="index.html" aria-current="page">ES</a><a href="../fr/">FR</a></div>')
    else:
        new_switch = ('<div class="lang-switch"><a href="../index.html">EN</a>'
                      '<a href="../es/">ES</a><a href="index.html" aria-current="page">FR</a></div>')
    assert old_switch in html, "language switcher markup changed in index.html"
    html = html.replace(old_switch, new_switch)

    # 4. Localized runtime strings for the calculator.
    data_attrs = "".join(f' data-{k}="{v}"' for k, v in CALC_DATA[loc].items())
    html = html.replace('<form id="home-macro-form" class="home-calc-form">',
                        f'<form id="home-macro-form" class="home-calc-form"{data_attrs}>', 1)

    # 5. Copy.
    missing = []
    for row in STRINGS:
        en, target = row[0], row[idx]
        if en not in html:
            missing.append(en[:60])
            continue
        html = html.replace(en, target)
    return html, missing


def main():
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    for loc in ("es", "fr"):
        html, missing = localize(src, loc)
        out = os.path.join(ROOT, loc, "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"wrote {out}")
        if missing:
            print(f"  WARNING {len(missing)} source string(s) not found:")
            for m in missing:
                print("   -", m)


if __name__ == "__main__":
    sys.exit(main())
