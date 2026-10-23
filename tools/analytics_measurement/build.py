"""Consent-based GA4 for public content, applied after all page generators."""
from pathlib import Path
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_flagship_release import pages, replace
from normalize_calculator_layouts import Document

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_FAMILIES = {
    'home', 'article', 'restaurant', 'editorial-index', 'journal', 'legal',
    'trust', 'methodology', 'guide', 'reference-index', 'editorial',
    'restaurant-index', 'country-index', 'collection',
}


def privacy(text):
    doc = Document(text)
    heading = next(n for n in doc.nodes if n['attrs'].get('id') == 'traffic-measurement')
    paragraph = next(n for n in doc.nodes if n['tag'] == 'p' and n['start'] >= heading['end'])
    copy = '''<p>Google Analytics 4 measures visits to public GetMacros pages only after you choose Allow analytics. It uses first-party analytics cookies (configured to expire after 90 days) and sends Google a published page address, page title, referring site, and technical visit information. Search queries and fragments are excluded from measurement. Google Signals and advertising personalization are disabled in this site's tag configuration. This is optional: choosing No thanks keeps the Google tag unloaded.</p><p>The Google tag is not loaded on the diary, finder, calculators, food search, comparison, saved-food or contact tools. GetMacros does not forward food logs, notes, goals, body measurements, calculator answers or search terms to Google Analytics. Consent and the optional browser exclusion are saved locally until changed or browser storage is cleared. Open <button class="analytics-link" type="button" data-analytics-preferences>Analytics preferences</button> to change your choice or exclude your own testing browser. Withdrawing permission removes this site's Google Analytics cookies and reloads the page to stop the tag. It does not delete data already received by Google. See <a href="https://policies.google.com/privacy">Google’s privacy policy</a> and <a href="https://support.google.com/analytics/answer/6004245">Google Analytics data safeguards</a>.</p><p>Cloudflare’s separate Web Analytics beacon measures visits and page performance. Hosting and Cloudflare reports are different from GA4 sessions. GetMacros does not send diary entries, notes or calculator inputs to that beacon. See <a href="https://developers.cloudflare.com/web-analytics/about/">Cloudflare Web Analytics</a> and <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare’s privacy policy</a>. No advertising provider is enabled by this analytics integration.</p>'''
    # Own this entire disclosure through the next heading, including earlier versions.
    next_heading = next(n for n in doc.nodes if n['tag'] == 'h2' and n['start'] >= paragraph['end'])
    text = text[:paragraph['start']] + copy + text[next_heading['start']:]
    text = re.sub(r'Last updated [A-Za-z]+ \d{1,2}, \d{4}', 'Last updated October 23, 2026', text)
    return text


def scope(text, name):
    doc = Document(text)
    main = next(n for n in doc.nodes if n['tag'] == 'main')
    body = next(n for n in doc.nodes if n['tag'] == 'body')
    family = main['attrs'].get('data-family') or body['attrs'].get('data-family')
    # Saved-food shelf is a personal workflow despite its historical trust template.
    return 'public' if family in PUBLIC_FAMILIES and name != 'food-shelf.html' else 'private'


def apply():
    rows = []
    for path in pages():
        name = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding='utf-8')
        mode = scope(text, name)
        text = re.sub(r' data-analytics-page="[^"]*"', '', text)
        text = text.replace('<body', '<body data-analytics-page="'+mode+'"', 1)
        # Only public documents allow the consent-gated Google endpoints.
        for node in reversed(Document(text).nodes):
            if node['tag'] != 'meta' or node['attrs'].get('http-equiv','').lower() != 'content-security-policy':
                continue
            directives = []
            for directive in node['attrs']['content'].split(';'):
                tokens = directive.split()
                if not tokens: continue
                additions = {'script-src': ['https://www.googletagmanager.com'],
                    'connect-src': ['https://www.google-analytics.com', 'https://region1.google-analytics.com'],
                    'img-src': ['https://www.google-analytics.com', 'https://region1.google-analytics.com']}.get(tokens[0], [])
                tokens = [token for token in tokens if token not in additions]
                if mode == 'public': tokens += additions
                directives.append(' '.join(tokens))
            original = text[node['start']:node['end']]
            updated = re.sub(r'content="[^"]*"', 'content="'+'; '.join(directives)+'"', original)
            text = replace(text, node, updated)
        if name == 'privacy.html': text = privacy(text)
        if 'data-analytics-footer' not in text:
            doc = Document(text)
            nav = next((n for n in doc.nodes if n['tag']=='nav' and n['attrs'].get('aria-label')=='Site information'), None)
            if not nav: raise ValueError('Missing policy navigation: '+name)
            text = text[:nav['close']] + '<button class="analytics-link" type="button" data-analytics-preferences data-analytics-footer>Analytics preferences</button>' + text[nav['close']:]
        if 'id="analytics-preferences"' not in text:
            markup = '''<aside class="analytics-notice" data-analytics-notice aria-label="Optional analytics" hidden><p>Allow anonymous visit measurement on public pages? Your food log and calculator inputs stay out of Google Analytics. <a href="/privacy.html#traffic-measurement">Privacy</a></p><div class="analytics-actions"><button type="button" data-analytics-choice="granted">Allow analytics</button><button type="button" data-analytics-choice="denied">No thanks</button></div></aside><dialog class="analytics-preferences" id="analytics-preferences" aria-labelledby="analytics-preferences-title"><header><h2 id="analytics-preferences-title">Analytics preferences</h2><button class="analytics-close" type="button" data-analytics-close aria-label="Close analytics preferences">×</button></header><p>Optional Google Analytics helps us understand public-page visits. Private food logs, calculator inputs and searches are excluded. <a href="/privacy.html#traffic-measurement">How measurement works</a></p><p data-analytics-status role="status"></p><label><input type="checkbox" data-analytics-exclude>Exclude this browser, including my own testing</label><p data-analytics-error role="status"></p><div class="analytics-actions"><button type="button" data-analytics-choice="granted">Allow analytics</button><button type="button" data-analytics-choice="denied">No thanks</button></div></dialog>'''
            # Never call GA4 pseudonymous cookie identifiers anonymous.
            markup = markup.replace('Allow anonymous visit measurement', 'Allow visit measurement')
            text = text.replace('</body>', markup+'</body>')
        if 'css/analytics-consent.css' not in text:
            text = text.replace('</head>', '<link rel="stylesheet" href="/css/analytics-consent.css"></head>')
        if 'js/analytics.js' not in text:
            text = text.replace('</body>', '<script src="/js/analytics.js" defer></script></body>')
        path.write_text(text, encoding='utf-8')
        rows.append({'file': name, 'scope': mode})
    out = ROOT/'docs/analytics-2026-10-23'
    out.mkdir(exist_ok=True)
    (out/'route-scope.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    print('GA4 consent integration:',len(rows),'routes;',sum(r['scope']=='public' for r in rows),'public-content routes eligible after opt-in.')


if __name__ == '__main__': apply()
