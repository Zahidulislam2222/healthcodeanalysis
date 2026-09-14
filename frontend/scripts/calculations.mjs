/** Pure educational calculations; coefficients and input limits belong to tools.json. */
export function calculate(kind, values, definition, messages) {
  if (kind === 'bmi' || kind === 'egfr') {
    for (const field of definition.fields) {
      const value = Number(values[field.name]);
      if (!Number.isFinite(value) || value < field.min || value > field.max ||
          (field.step === '1' && !Number.isInteger(value))) throw new Error(messages.input);
    }
  }
  const c = definition.coefficients;
  if (kind === 'bmi') return Number(values.weight) / (Number(values.height) / c.centimeters_per_meter) ** 2;
  if (kind === 'egfr') {
    if (!['female', 'male'].includes(values.sex)) throw new Error(messages.sex);
    const sex = c[values.sex];
    const ratio = Number(values.creatinine) / sex.k;
    return c.base * Math.min(ratio, 1) ** sex.alpha * Math.max(ratio, 1) ** c.high_exponent *
      c.age_factor ** Number(values.age) * sex.factor;
  }
  if (kind === 'scores') {
    const age = Number(values.age);
    if (!Number.isInteger(age) || age < definition.age.min || age > definition.age.max) {
      throw new Error(messages.age);
    }
    const totals = Object.fromEntries(definition.groups.map(group => [group.id,
      group.fields.reduce((sum, field) => sum + (values[`${group.id}_${field.name}`] ? field.value : 0), 0)]));
    totals.stroke += age >= definition.age.stroke_high ? 2 : age >= definition.age.stroke_low ? 1 : 0;
    totals.bleed += age > definition.age.bleed_above ? 1 : 0;
    return totals;
  }
  if (definition.kind === 'text') {
    for (const field of definition.fields) if (!String(values[field.name] || '').trim()) {
      throw new Error(messages.fields);
    }
    return definition.template.replace(/\{(\w+)\}/g, (_, key) => String(values[key]).trim());
  }
  throw new Error(messages.unavailable);
}

export function searchLibrary(items, query, limit) {
  const words = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
  if (!words.length) return [];
  return items.map(item => {
    const title = `${item.title} ${item.category}`.toLocaleLowerCase();
    const body = `${title} ${item.excerpt}`.toLocaleLowerCase();
    return {item, score: words.reduce((sum, word) => sum + (title.includes(word) ? 2 : body.includes(word) ? 1 : 0), 0)};
  }).filter(match => match.score > 0).sort((a, b) => b.score - a.score).slice(0, limit).map(match => match.item);
}
