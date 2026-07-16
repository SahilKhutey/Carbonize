import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";
import { AccessibleKpiCard } from "../../kpi/AccessibleKpiCard";
import { LiveRegion } from "../LiveRegion";
import React from "react";

expect.extend(toHaveNoViolations);

describe("Accessibility primitives", () => {
  it("AccessibleKpiCard should have no a11y violations", async () => {
    const { container } = render(
      <main>
        <AccessibleKpiCard
          label="Test KPI"
          value={42}
          unit="%"
          status="good"
          trend="up"
          trendValue="1.2%"
          target={40}
        />
      </main>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("LiveRegion should have no a11y violations", async () => {
    const { container } = render(
      <main>
        <LiveRegion message="Test message" />
      </main>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
