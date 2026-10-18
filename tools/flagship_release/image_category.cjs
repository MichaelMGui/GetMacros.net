/* Shared by the image manifest and browser adapter. Order matters. */
'use strict';
function category(record){
 const text=[record.name,record.sourceGroup,record.category].filter(Boolean).join(' ').toLowerCase();
 if(/\b(?:sauce|dressing|dip|ketchup|mustard|mayonnaise|aioli|salsa|gravy)\b/.test(text)&&!/(?:sandwich|burger|pizza|bowl|wrap|sub|salad)/.test(text))return 'sauce';
 if(/\b(?:coffee|latte|cappuccino|espresso|macchiato|americano|flat white|cold brew|mocha)\b/.test(text))return 'coffee';
 if(/\b(?:shake|milkshake|juice|soda|coca.cola|sprite|fanta|lemonade|smoothie|tea|water|drink|beverage)\b/.test(text))return 'drink';
 if(/\b(?:sushi|maki|nigiri|sashimi|california roll)\b/.test(text))return 'sushi';
 if(/\b(?:pizza|calzone)\b/.test(text))return 'pizza';
 if(/\b(?:bowl|rice|noodle|pasta|macaroni|chilli|chili|porridge|oatmeal)\b/.test(text))return 'bowl';
 if(/\b(?:salad|kale crunch)\b/.test(text))return 'salad';
 if(/\b(?:wrap|burrito|taco|quesadilla|pita)\b/.test(text))return 'wrap';
 if(/\b(?:burger|whopper|big mac|mcdouble|quarter pounder)\b/.test(text))return 'burger';
 if(/\b(?:sandwich|sub|baguette|panini|mcmuffin|mcgriddle|biscuit|croissant|muffin)\b/.test(text))return 'sandwich';
 if(/\b(?:fries|chips|hash brown|taters|poutine)\b/.test(text))return 'fries';
 if(/\b(?:sundae|ice cream|cookie|brownie|cake|dessert|donut|doughnut|pie|chocolate)\b/.test(text))return 'dessert';
 if(/\b(?:breakfast|egg|omelet|omelette|pancake|waffle|toast)\b/.test(text))return 'breakfast';
 if(/\b(?:chicken|wing|nugget|tender|strip|fillet|grill)\b/.test(text))return 'chicken';
 return 'side';
}
module.exports={category};
