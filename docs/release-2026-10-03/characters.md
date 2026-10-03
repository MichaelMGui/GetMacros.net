# Original GetMacros food characters

Implemented on 3 October 2026. This is an original, code-drawn SVG family created for GetMacros. No stock characters, emoji artwork, external character art, restaurant branding, or third-party illustration assets were copied or downloaded.

## Artwork and interaction

The sprite contains sixteen independent recognizable silhouettes: steak, chicken, salmon, shrimp, egg, tofu, beans, apple, banana, strawberry, orange, blueberry, avocado, carrot, broccoli, and pear. Rounded ink strokes, simple limbs, small smiles, restrained highlights and natural food colors form one family. The art represents foods generally; it does not depict exact restaurant orders or nutritional advice.

Steak, tofu and avocado wave; chicken, beans and banana nod; salmon, egg and blueberry blink; shrimp and the remaining produce characters wiggle a small botanical or tail detail. Every motion is a single 620 ms gesture, initiated by hover, focus or intentional tap. There is no loop, sound, animation library, or count-up effect. Reduced motion preserves the greeting and disables movement.

The steak greeting says **Hi!**. Other short greetings are Hi!, Hey! or Hello!. A reserved line beneath the illustration holds the greeting, so it never overlays nutrition values, controls or advertising and does not move neighboring content when it appears. Escape dismisses it. A second tap or an outside tap dismisses a pinned touch greeting. Pointer users can move onto the tooltip without it disappearing. Keyboard focus remains visible. Interactive instances have native button semantics, an explicit accessible name and an associated tooltip. Decorative instances have no button or tab stop and are excluded from the accessibility tree.

Colored food bodies use their own coordinated palette. Limbs inherit the surrounding theme's text color; greeting surfaces, borders, text and focus inherit Market semantic tokens. Both retained themes were rendered and checked.

## Integration

Include `tools/food-characters.css` once in the publication stylesheet build, and load `/js/food-characters.js` once using `defer`. The helper enhances declarative hosts once, leaving static SVG artwork visible without JavaScript. Interactive art is inlined from the same local sprite to make its individual gesture groups animatable. Failure to retrieve that enhancement leaves the already rendered external SVG instance intact.

```html
<span class="food-character" data-food-character="steak" data-interactive="true">
  <svg viewBox="0 0 160 160" aria-hidden="true" focusable="false">
    <use href="/images/food-characters.svg#food-steak"></use>
  </svg>
</span>
```

For a decorative instance, use `data-interactive="false" aria-hidden="true"`. Set `--food-size` on the host or a composition-specific class. Default size is 112 px. Avoid placing every character on the same page; prefer one relevant guide or illustration in a region. Do not position a character to draw attention to an ad or imply a health endorsement.

```js
const guide = GetMacrosCharacters.create('steak', { interactive: true, size: 128 });
container.append(guide);
// An explicit user-triggered completion can request a greeting.
GetMacrosCharacters.setPose(guide, 'greeting');
GetMacrosCharacters.setPose(guide, 'rest');
// Newly rendered fragments can be enhanced without duplicating buttons.
GetMacrosCharacters.enhance(fragment);
```

`create` supports identity, size, interactive mode, optional short greeting, and rest/greeting pose. The theme treatment inherits the active page. Do not replace short greetings with long copy: longer explanatory text belongs in ordinary page content beside the character.

## Actual verification

Command: `node tools/test-food-characters.cjs`.

Passed 8 Chromium theme/width combinations: light and dark at 320, 390, 768 and 1440 CSS pixels. Checks cover all 16 symbol identities, render completion, no horizontal overflow, hover greeting, hover persistence on the tooltip, keyboard focus and Escape, actual touch tap at phone widths, outside dismissal, stable character height before/after greeting, one-shot wave presence, reduced-motion absence of animation, decorative semantics and no runtime errors.

Screenshots are in `docs/release-2026-10-03/characters/`: `gallery-{theme}-{width}.png` and `greeting-{theme}-{width}.png`. Results are recorded in `checks.json`. The fixture is served through the test's request interception only; no public gallery route or indexable test page was created.

The light desktop gallery and dark mobile greeting gallery were visually inspected. This verifies the standalone components; the release owner must also inspect their final placement on actual site pages. These checks are not a claim of full WCAG conformance or real-user performance measurement.
