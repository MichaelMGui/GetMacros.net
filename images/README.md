# Image manifest — GetMacros.net

This environment's network sandbox blocks every external image host (Wikimedia,
Unsplash, Pexels, government sites, even google.com — confirmed by testing 20+
domains, all returning 403 at the egress proxy). So none of the photos below
could be downloaded from inside this session.

The site is built to need **zero code changes** once real files land here:
every page references an `<img>` at the exact path listed below, with a
`class="photo"` fallback that shows a clean placeholder until the real file
exists. Drop a correctly-named file into `/images/` and it appears automatically.

## How to add a real photo

1. Go to the candidate Wikimedia Commons file (search the title below at
   https://commons.wikimedia.org/ — titles are unverified leads, not confirmed
   URLs, so **confirm the file still exists and check its actual license tag**
   on the file page before using it).
2. Click "Original file" and download it.
3. Rename it to the **Target filename** below and place it in this `/images/`
   folder.
4. Add the required attribution line to the caption in the corresponding HTML
   page (each page already has a `<figcaption>` with a `<!-- TODO: attribution -->`
   placeholder comment next to each photo) — include title, author, and license
   per Commons' reuse requirements.
5. Commit and push.

If a Commons candidate doesn't pan out, any other real photo works as long as
you have the rights to use it and you fill in honest attribution.

## Candidates (unverified — confirm license on the actual file page)

| Target filename | Wikimedia Commons candidate (search this title) | Used on |
|---|---|---|
| `images/hero-healthy-food.jpg` | search "assorted healthy food flat lay" | Homepage hero |
| `images/protein-chicken-breast.jpg` | "Grilled Chicken Breasts" | Protein page |
| `images/protein-eggs.jpg` | "Egg-rmh.jpg" or "Bowl of Eggs" | Protein page |
| `images/protein-salmon.jpg` | "Salmon fillet" / "Raw salmon fillets" | Protein page |
| `images/protein-legumes.jpg` | "Puy lentils wooden bowl" | Protein page |
| `images/protein-greek-yogurt.jpg` | "Fresh greek yoghurt" | Protein page |
| `images/fats-avocado.jpg` | "Avocado Hass - single and halved" | Fats page |
| `images/fats-olive-oil.jpg` | "Bottle of olive oil" | Fats page |
| `images/fats-nuts.jpg` | "Mixed nuts" | Fats page |
| `images/fats-salmon-fatty-fish.jpg` | "Atlantic mackerel (Scomber scombrus)" | Fats page |
| `images/carbs-whole-grains.jpg` | "Multigrain bread" / "Oat groats" | Carbs page |
| `images/carbs-brown-rice.jpg` | "Brownrice.jpg" | Carbs page |
| `images/carbs-fruits-vegetables.jpg` | "Fruits and vegetables" | Carbs page |
| `images/carbs-legumes-quinoa.jpg` | "Quinoa Chenopodium quinoa" | Carbs page |
| `images/muscle-anatomy.jpg` | "Anterior and Posterior Views of Muscles" (OpenStax, CC BY 4.0) | Protein page |
| `images/glycogen-structure.jpg` | "Glycogen structure" | Carbs page |

Every `<img>` on the site already has descriptive `alt` text and a
`data-icon` emoji fallback, so the site looks intentional even before these
are added.
