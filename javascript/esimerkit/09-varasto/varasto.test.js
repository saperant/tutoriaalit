import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { luoVarasto } from "./varasto.js";

describe("varasto", () => {
  it("laskee saldon kirjauksista", () => {
    const v = luoVarasto();
    v.kirjaa("kahvi", 10);
    v.kirjaa("kahvi", -3);
    assert.equal(v.saldo("kahvi"), 7);
  });

  it("listaa rajan alittavat tuotteet", () => {
    const v = luoVarasto([["kahvi", 12], ["tee", 4]]);
    assert.deepEqual(v.tilattavat(), [{ tuote: "tee", maara: 4 }]);
  });

  it("hylkää negatiivisen saldon ja nollamuutoksen", () => {
    const v = luoVarasto([["tee", 1]]);
    assert.throws(() => v.kirjaa("tee", -2), /saldo ei riitä/);
    assert.throws(() => v.kirjaa("tee", 0), RangeError);
    assert.equal(v.saldo("tee"), 1);
  });
});
