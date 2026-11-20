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
  const guideList = root.document?.querySelector('[data-pillar-guides]');
  if (guideList) {
    const filters = guideList.querySelector('form');
    const status = guideList.querySelector('[role="status"]');
    const guides = [...guideList.querySelectorAll('[data-guide-topic]')];
    filters.addEventListener('input', () => {
      let shown = 0;
      for (const guide of guides) {
        guide.hidden = !matchesClaim(guide.textContent, guide.dataset.guideTopic,
          filters.elements.query.value, filters.elements.topic.value);
        if (!guide.hidden) shown++;
      }
      status.textContent = shown ? shown + (shown === 1 ? ' guide shown.' : ' guides shown.') : 'No guides match.';
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

  function amountLabel(record, basis) {
    if (basis === '100g') return '100 g';
    if (basis === 'portion') return record.portion ? record.portion.label + ' · ' + record.portion.grams + ' g' : 'No listed portion weight';
    return record.values.cal > 0 ? format.format(10000 / record.values.cal) + ' g' : 'Unknown energy basis';
  }

  function rowWithValues(record, basis, values, compact = false) {
    const tr = document.createElement('tr');
    const name = document.createElement('th');
    name.scope = 'row';
    name.textContent = record.label;
    tr.append(name);
    const measure = amountLabel(record, basis);
    for (const value of compact ? values : [measure, ...values]) {
      const cell = document.createElement('td');
      cell.textContent = value;
      tr.append(cell);
    }
    const link = document.createElement('a');
    link.href = 'https://fdc.nal.usda.gov/food-details/' + record.id + '/nutrients';
    link.textContent = 'USDA record ' + record.id;
    if (compact) {
      const portion = document.createElement('small');
      portion.textContent = measure;
      name.append(portion, link);
    } else {
      const source = document.createElement('td');
      source.append(link);
      tr.append(source);
    }
    return tr;
  }

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
      const value = row.amount === null ? 'Unknown' : format.format(row.amount) + ' ' + field.unit;
      fragment.append(rowWithValues(row, basis, [value]));
    }
    body.replaceChildren(fragment);
  }
  form.addEventListener('input', render);
  form.addEventListener('submit', event => event.preventDefault());
  form.hidden = false;
  render();

  const comparison = panel.querySelector('[data-macro-pair]');
  if (comparison) {
    const choices = comparison.querySelector('form');
    const comparisonBody = comparison.querySelector('tbody');
    const recordById = new Map(rows.map(row => [String(row.id), row]));
    function renderComparison() {
      const {first, second, basis} = choices.elements;
      const selected = [recordById.get(first.value), recordById.get(second.value)];
      const entries = selected.map(record => {
        const values = ['p', 'f'].map(nutrient => {
          const value = amount(record, nutrient, basis.value);
          return value === null ? 'Unknown' : format.format(value) + ' g';
        });
        return rowWithValues(record, basis.value, values, true);
      });
      comparisonBody.replaceChildren(...entries);
    }
    choices.addEventListener('input', renderComparison);
    choices.addEventListener('submit', event => event.preventDefault());
    renderComparison();
    comparison.hidden = false;
    root.document.querySelector('[data-macro-pair-link]').hidden = false;
  }
})(typeof window === 'object' ? window : globalThis);
