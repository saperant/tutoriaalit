import { test } from "node:test";
import assert from "node:assert/strict";
import { cors, corsHaavoittuva } from "./cors.ts";

test("CORS: alkuperän heijastus sallii kenet tahansa evästeineen", () => {
  const vieras = "https://hyokkaaja.example";
  assert.deepEqual(corsHaavoittuva(vieras), {
    "Access-Control-Allow-Origin": vieras,
    "Access-Control-Allow-Credentials": "true" });

  const sallitut = new Set(["https://app.pankki.example"]);
  assert.deepEqual(cors(vieras, sallitut), { Vary: "Origin" });
  assert.deepEqual(cors("null", sallitut), { Vary: "Origin" });
  // Alkuosa ei riitä: tämä on hyökkääjän verkkotunnus.
  assert.deepEqual(cors("https://app.pankki.example.hyokkaaja.example",
                        sallitut), { Vary: "Origin" });
  assert.equal(cors("https://app.pankki.example", sallitut)
    ["Access-Control-Allow-Origin"], "https://app.pankki.example");
});
