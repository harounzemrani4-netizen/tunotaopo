"use strict";

var fs = require("fs");
var path = require("path");
var vm = require("vm");

var root = path.join(__dirname, "..");
var code = fs.readFileSync(path.join(root, "js", "engine", "scoring.js"), "utf8");
var ctx = { globalThis: null };
ctx.globalThis = ctx;
vm.runInNewContext(code, ctx);
if (!ctx.NotaOpoEngine) {
  process.stderr.write("NotaOpoEngine no se cargo\n");
  process.exit(2);
}

var fixtures = JSON.parse(fs.readFileSync(path.join(root, "tests", "fixtures.json"), "utf8"));
var configDir = path.join(root, "data", "oposiciones");
var configs = {};
fs.readdirSync(configDir).forEach(function (name) {
  if (!name.endsWith(".json")) return;
  configs[name.replace(/\.json$/, "")] = JSON.parse(fs.readFileSync(path.join(configDir, name), "utf8"));
});

function lookup(data, keyPath) {
  return keyPath.split(".").reduce(function (current, part) {
    if (current == null || !(part in current)) {
      throw new Error("missing " + keyPath);
    }
    return current[part];
  }, data);
}

function nearlyEqual(actual, expected) {
  if (typeof expected === "boolean" || expected === null) {
    return actual === expected;
  }
  if (typeof expected === "number" && typeof actual === "number") {
    return Math.abs(actual - expected) < 1e-9;
  }
  return actual === expected;
}

var failed = 0;
var ran = 0;
fixtures.cases.forEach(function (testCase) {
  ran += 1;
  var config = configs[testCase.config];
  var expected = testCase.expected;
  try {
    var result = ctx.NotaOpoEngine.evaluate(config, testCase.inputs);
    if (expected.error === true) {
      failed += 1;
      process.stdout.write("[FAIL] " + testCase.id + ": expected error, got result\n");
      return;
    }
    Object.keys(expected).forEach(function (key) {
      if (key === "error") return;
      var actual = lookup(result, key);
      if (!nearlyEqual(actual, expected[key])) {
        failed += 1;
        process.stdout.write(
          "[FAIL] " + testCase.id + ": " + key + " expected " + JSON.stringify(expected[key]) + ", got " + JSON.stringify(actual) + "\n"
        );
      }
    });
  } catch (err) {
    if (expected.error === true) {
      process.stdout.write("[OK] " + testCase.id + " (error: " + err.message + ")\n");
      return;
    }
    failed += 1;
    process.stdout.write("[FAIL] " + testCase.id + ": unexpected error: " + err.message + "\n");
  }
});

if (failed) {
  process.stdout.write("JS engine: " + failed + " failure(s) / " + ran + "\n");
  process.exit(1);
}
process.stdout.write("[OK] JS engine " + ran + " case(s)\n");
