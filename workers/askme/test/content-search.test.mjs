import assert from "node:assert/strict";
import test from "node:test";

import { fallbackSearchTerms } from "../src/index.js";

test("fallback keeps one eligible word after filtering a short term", () => {
  assert.deepEqual(fallbackSearchTerms("ai radiology"), ["radiology"]);
});

test("fallback tries long phrases before individual words", () => {
  assert.deepEqual(fallbackSearchTerms("blood pressure wearable"), [
    "blood pressure",
    "pressure wearable",
    "blood",
    "pressure",
    "wearable",
  ]);
});
