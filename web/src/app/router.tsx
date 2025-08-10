import { createBrowserRouter } from "react-router-dom";
import { Layout } from "./layout";
import SummaryPage from "../features/summary/SummaryPage";
import TransactionsPage from "../features/transactions/TransactionsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <SummaryPage /> },
      { path: "transactions", element: <TransactionsPage /> },
      // add: budgets, goals, debts, transfers, recurring…
    ],
  },
]);
