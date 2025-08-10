// src/features/summary/SummaryPage.test.tsx
import { render, screen } from "@testing-library/react";
import SummaryPage from "./SummaryPage";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../../app/queryClient";

test("renders dashboard title", () => {
  render(
    <QueryClientProvider client={queryClient}>
      <SummaryPage />
    </QueryClientProvider>
  );
  expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
});
