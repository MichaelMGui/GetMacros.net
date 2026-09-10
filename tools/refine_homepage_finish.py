"""Keep the homepage's final layout repeatable after the earlier content stages."""
import re


def refine_homepage(text):
    text = text.replace('class="home-intro"', 'class="home-intro home-garden"')
    text = text.replace('Meals from 15 restaurant chains, matched to your appetite and goals.',
                        'Find meals from 15 restaurant chains that fit your appetite and goals.')
    text = re.sub(r'<div class="home-play-art"><img[^>]*>(?:<div class="home-art-caption"[^>]*>.*?</div>)?</div>',
        '<div class="home-play-art"><img src="images/home-meal-bowl.svg" width="600" height="460" '
        'alt="An illustrated meal bowl with grilled chicken, rice and colourful vegetables" fetchpriority="high">'
        '<div class="home-art-caption" aria-hidden="true"><span>Protein</span><span>Carbs</span><span>Fats</span></div></div>',
        text, count=1, flags=re.S)
    # These three cards repeated the same two actions directly above them.
    text = re.sub(r'<section class="home-decisions".*?</section>', '', text, flags=re.S)
    text = text.replace('Use the free macro calculator to estimate your calories and macros.',
                        'Get a daily calorie and macro target for your goal.')
    text = text.replace('Use the fast-food meal finder to find meals that fit your goals.',
                        'Pick what matters to you. Compare meals that fit.')
    text = text.replace('Eating in?<br>Make the numbers easier.', 'Good food.<br>Less guesswork.')
    text = text.replace('Find out which food gives you more protein for your money.',
                        'Get more protein for your money.')
    return text
