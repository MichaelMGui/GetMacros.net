// Filters a small, source-linked projection of the existing reference catalogue.
(function (root) {
  'use strict';

  function amount(record, nutrient, basis) {
    const value = record.values[nutrient];
    if (!Number.isFinite(value)) return null;
    if (basis === '100g') return value;
    if (basis === 'portion') return record.portion ? value * record.portion.grams / 100 : null;
    return record.values.cal > 0 ? value * 100 / record.values.cal : null;
  }

  function select(records, {nutrient, basis, category, query, includeUnknown}) {
    const tokens = query.toLowerCase().trim().split(/\s+/);
    return records.filter(row => (!category || row.group === category) &&
      tokens.every(token => (row.label + ' ' + row.name).toLowerCase().includes(token)))
      .map(row => ({...row, amount: amount(row, nutrient, basis)}))
      .filter(row => includeUnknown || row.amount !== null)
      .sort((a, b) => (b.amount ?? -Infinity) - (a.amount ?? -Infinity) || a.label.localeCompare(b.label));
  }

  function matchesClaim(copy, topic, query, filter) {
    const tokens = query.toLowerCase().trim().split(/\s+/);
    return (!filter || topic === filter) && tokens.every(token => copy.toLowerCase().includes(token));
  }

  if (typeof module === 'object') module.exports = {amount, select, matchesClaim};
  const claims = root.document?.querySelector('[data-claim-library]');
  if (claims) {
    const filters = claims.querySelector('form');
    const status = claims.querySelector('[role="status"]');
    const entries = [...claims.querySelectorAll('[data-claim-example]')];
    filters.addEventListener('input', () => {
      let count = 0;
      for (const entry of entries) {
        entry.hidden = !matchesClaim(entry.textContent, entry.dataset.topic, filters.elements.claim.value, filters.elements.topic.value);
        if (!entry.hidden) count++;
      }
      status.textContent = count ? count + (count === 1 ? ' claim shown.' : ' claims shown.') : 'No matching claims. Try another topic or search term.';
    });
    filters.addEventListener('submit', event => event.preventDefault());
    filters.hidden = false;
  }
  const panel = root.document?.querySelector('[data-nutrient-explorer]');
  if (!panel) return;

  const {rows, nutrients} = JSON.parse(panel.querySelector('[type="application/json"]').textContent);
  const form = panel.querySelector('form');
  const status = panel.querySelector('[role="status"]');
  const body = panel.querySelector('tbody');
  const heading = panel.querySelector('[data-amount-label]');
  const format = new Intl.NumberFormat('en', {maximumSignificantDigits: 4});

  function render() {
    const values = form.elements;
    const nutrient = values.nutrient.value;
    const basis = values.basis.value;
    const matches = select(rows, {nutrient, basis, category: values.category.value,
      query: values.food.value, includeUnknown: values.unknown.checked});
    const field = nutrients[nutrient];
    const basisLabel = {portion: 'per listed portion', '100g': 'per 100 g', '100kcal': 'per 100 kcal'}[basis];
    heading.textContent = field.label + ' ' + basisLabel;
    status.textContent = matches.length ? matches.length + ' reference foods shown.' : 'No rows match. Try another food or category, or include unknown values.';
    const fragment = document.createDocumentFragment();
    for (const row of matches) {
      const tr = document.createElement('tr');
      const name = document.createElement('th');
      name.scope = 'row';
      name.textContent = row.label;
      const measure = document.createElement('td');
      measure.textContent = basis === 'portion' ? row.portion ? row.portion.label + ' · ' + row.portion.grams + ' g' : 'No listed portion weight' : basis === '100g' ? '100 g' : row.values.cal > 0 ? format.format(10000 / row.values.cal) + ' g' : 'Unknown energy basis';
      const value = document.createElement('td');
      value.textContent = row.amount === null ? 'Unknown' : format.format(row.amount) + ' ' + field.unit;
      const source = document.createElement('td');
      const link = document.createElement('a');
      link.href = 'https://fdc.nal.usda.gov/food-details/' + row.id + '/nutrients';
      link.textContent = 'USDA record ' + row.id;
      source.append(link);
      tr.append(name, measure, value, source);
      fragment.append(tr);
    }
    body.replaceChildren(fragment);
  }
  form.addEventListener('input', render);
  form.addEventListener('submit', event => event.preventDefault());
  form.hidden = false;
  render();
})(typeof window === 'object' ? window : globalThis);
