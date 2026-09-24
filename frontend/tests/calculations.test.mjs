import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {calculate as evaluate, searchLibrary} from '../scripts/calculations.mjs';
const tools = JSON.parse(readFileSync(new URL('../data/tools.json', import.meta.url), 'utf8'));

const calculate = (kind, values, definition) => evaluate(kind, values, definition, tools._messages);

test('BMI uses metric units and rejects zero or impossible inputs', () => {
  assert.equal(calculate('bmi', {weight: 72, height: 180}, tools.bmi).toFixed(2), '22.22');
  for (const height of [0, -1, 'invalid', Infinity, 400]) {
    assert.throws(() => calculate('bmi', {weight: 72, height}, tools.bmi));
  }
});
test('CKD-EPI 2021 known adult examples, both branches and sex coefficients', () => {
  assert.equal(calculate('egfr', {age: 50, creatinine: 1, sex: 'male'}, tools.egfr).toFixed(1), '91.7');
  assert.equal(calculate('egfr', {age: 50, creatinine: 1, sex: 'female'}, tools.egfr).toFixed(1), '68.6');
  assert.equal(calculate('egfr', {age: 40, creatinine: .6, sex: 'female'}, tools.egfr).toFixed(1), '116.3');
  assert.throws(() => calculate('egfr', {age: 17, creatinine: 1, sex: 'male'}, tools.egfr));
  assert.throws(() => calculate('egfr', {age: 30, creatinine: 1, sex: 'unknown'}, tools.egfr));
});
test('AF scores have mutually exclusive age brackets and independent risk components', () => {
  for (const [age, stroke, bleed] of [[64, 0, 0], [65, 1, 0], [66, 1, 1], [74, 1, 1], [75, 2, 1]]) {
    assert.deepEqual(calculate('scores', {age}, tools.scores), {stroke, bleed});
  }
  const maximum = {age: 80};
  for (const group of tools.scores.groups) for (const field of group.fields) maximum[`${group.id}_${field.name}`] = 'on';
  assert.deepEqual(calculate('scores', maximum, tools.scores), {stroke: 9, bleed: 9});
});
test('PICO drafts preserve user text without recursive substitution', () => {
  const result = calculate('pico', {population:'adults', intervention:'walking', comparison:'rest', outcome:'{population}'}, tools.pico);
  assert.equal(result, 'In adults, how does walking, compared with rest, affect {population}?');
  assert.throws(() => calculate('pico', {population:'adults'}, tools.pico));
});
test('Search ranks relevant titles and handles empty or unmatched queries', () => {
  const items = [{title:'Medical AI', category:'Insights', excerpt:'Research'}, {title:'Research', category:'Tools', excerpt:'Medical AI'}];
  assert.equal(searchLibrary(items, 'medical', 1)[0].title, 'Medical AI');
  assert.deepEqual(searchLibrary(items, '', 10), []);
  assert.deepEqual(searchLibrary(items, 'zzzzzz', 10), []);
});
