/* Small, local-only tools for the source-backed editorial comparisons. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (!root.document) return;
  root.document.querySelectorAll('[data-article-tool]').forEach(function (panel) {
    const model = JSON.parse(panel.querySelector('[data-tool-model]').textContent);
    const form = panel.querySelector('form');
    const results = panel.querySelector('[data-tool-results]');
    const error = panel.querySelector('[data-tool-error]');
    const explanation = panel.querySelector('[data-tool-selection]');
    function render() {
      let rows, amount;
      try {
        if (model.kind === 'scale') {
          amount = Number(form.elements.grams.value);
          if (!form.elements.grams.value.trim()) throw Error('Enter the weight of your portion.');
          rows = api.scale(model.rows, amount, model.baseGrams, model.fields);
        } else {
          const choices = [model.mains[Number(form.elements.main.value)]];
          const drink = form.elements.drink.value;
          if (drink !== '') choices.push(model.drinks[Number(drink)]);
          if (form.elements.side && form.elements.side.checked) choices.push(model.side);
          rows = [api.sum(choices, model.fields)];
          explanation.textContent = choices.map(function (r) { return r.name; }).join(' + ') + '. One listed portion each.';
        }
        if (model.kind === 'breakfast') {
          const summary = root.document.createElement('dl'); summary.className = 'article-tool-totals';
          model.fields.forEach(function (field) {
            const group = root.document.createElement('div'), label = root.document.createElement('dt'), value = root.document.createElement('dd');
            label.textContent = field.key === 'cal' ? 'Calories' : field.label.replace(' (g)', '');
            value.textContent = api.format(rows[0][field.key]) + (field.key === 'cal' ? ' kcal' : ' g');
            group.append(label, value); summary.append(group);
          });
          results.replaceChildren(summary); results.removeAttribute('tabindex');
        } else {
        const table = root.document.createElement('table');
        const caption = table.createCaption();
        caption.textContent = model.kind === 'scale' ? 'Calculated comparison · ' + api.format(amount) + ' g each' : 'Calculated breakfast · selected components only';
        const heading = table.createTHead().insertRow();
        [model.kind === 'scale' ? 'Product' : 'Order'].concat(model.fields.map(function (f) { return f.label; })).forEach(function (label) {
          const th = root.document.createElement('th'); th.scope = 'col'; th.textContent = label; heading.append(th);
        });
        const body = table.createTBody();
        rows.forEach(function (row) {
          const tr = body.insertRow(), th = root.document.createElement('th');
          th.scope = 'row'; th.textContent = row.name; tr.append(th);
          model.fields.forEach(function (field) {
            const td = tr.insertCell(); td.textContent = api.format(row[field.key]);
          });
        });
        results.replaceChildren(table);
        }
        error.textContent = '';
        if (form.elements.grams) form.elements.grams.removeAttribute('aria-invalid');
      } catch (e) {
        results.replaceChildren();
        error.textContent = e.message;
        if (form.elements.grams) form.elements.grams.setAttribute('aria-invalid', 'true');
      }
    }
    form.hidden = false;
    form.addEventListener('submit', function (event) { event.preventDefault(); render(); });
    form.addEventListener('input', render);
    form.addEventListener('change', render);
    render();
  });
})(typeof window === 'undefined' ? {} : window, function () {
  function scale(rows, grams, base, fields) {
    if (!Number.isFinite(grams) || grams < 0.1 || grams > 2000) throw Error('Choose a weight from 0.1 to 2,000 g.');
    if (!Number.isFinite(base) || base <= 0) throw Error('The source serving is unavailable.');
    return rows.map(function (row) {
      const value = { name: row.name };
      fields.forEach(function (field) { value[field.key] = Number.isFinite(row[field.key]) ? row[field.key] * grams / base : null; });
      return value;
    });
  }
  function sum(rows, fields) {
    if (!rows.length || rows.some(function (r) { return !r; })) throw Error('Choose a supported item.');
    if (new Set(rows.map(function (r) { return r.market; }).filter(Boolean)).size > 1) throw Error('Choose components from the same country.');
    const total = { name: 'Your selected breakfast' };
    fields.forEach(function (field) {
      total[field.key] = rows.every(function (r) { return Number.isFinite(r[field.key]); }) ? rows.reduce(function (n, r) { return n + r[field.key]; }, 0) : null;
    });
    return total;
  }
  function format(value) { return Number.isFinite(value) ? new Intl.NumberFormat('en', { maximumFractionDigits: 1 }).format(value) : 'Not reported'; }
  return { scale: scale, sum: sum, format: format };
});
