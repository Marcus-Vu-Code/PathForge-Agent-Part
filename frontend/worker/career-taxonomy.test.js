import test from "node:test";
import assert from "node:assert/strict";

import { generateSpecializations, requirementsForGoal, sectors } from "./career-taxonomy.js";

test("every target role has a distinct, domain-specific specialization menu", () => {
  const menus = [];

  assert.equal(sectors.length, 10);
  for (const sector of sectors) {
    assert.equal(sector.roles.length, 10);
    for (const role of sector.roles) {
      const options = generateSpecializations(sector.value, role.value);
      const labels = options.map((option) => option.label);
      assert.ok(options.length >= 4);
      assert.ok(!labels.includes("Career Transition Story"));
      assert.ok(!labels.includes("Portfolio / Experience Evidence"));
      menus.push(labels.join("|"));
    }
  }

  assert.equal(menus.length, 100);
  assert.equal(new Set(menus).size, 100);
});

test("representative roles use sector and role-specific tracks", () => {
  const cases = [
    ["business_operations", "Project Coordinator", "Project Delivery"],
    ["healthcare_wellness", "Clinical Research Coordinator", "Study Coordination"],
    ["education_training", "Corporate Trainer", "Facilitation / Delivery"],
    ["skilled_trades_construction", "Maintenance Planner", "Preventive Maintenance Strategy"],
    ["public_service_government", "Public Administration Analyst", "Government Program Analysis"],
    ["arts_media_design", "Digital Marketing Designer", "Campaign Creative"],
    ["law_policy_compliance", "Privacy Analyst", "Privacy Operations"],
    ["sales_marketing_customer", "Growth Marketing Analyst", "Growth Experimentation"],
    ["finance_accounting_real_estate", "Financial Analyst", "Financial Modeling"],
    ["science_engineering_environment", "Robotics Engineer", "Robot Perception"],
  ];

  for (const [sector, role, expected] of cases) {
    assert.equal(generateSpecializations(sector, role)[0].label, expected);
  }
});

test("the selected specialization leads hosted plan requirements", () => {
  const requirements = requirementsForGoal({
    target_sector: "finance_accounting_real_estate",
    target_role: "Financial Analyst",
    target_function: "financial_analyst__financial_modeling",
  });

  assert.deepEqual(requirements.slice(0, 4), [
    "Financial Modeling",
    "quantitative analysis",
    "accuracy controls",
    "decision-ready reporting",
  ]);
});

test("custom roles receive a sector-specific fallback", () => {
  const labels = generateSpecializations("healthcare_wellness", "Custom Care Role").map((option) => option.label);
  assert.deepEqual(labels, ["Care Coordination", "Health Records / Quality", "Health Program Delivery", "Patient Experience"]);
});
