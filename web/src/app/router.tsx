// src/app/router.tsx
import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "../components/ProtectedRoute";
import Layout from "./Layout";
import LoginPage from "../features/auth/LoginPage";
import SummaryPage from "../features/summary/SummaryPage";
import TransactionsPage from "../features/transactions/TransactionsPage";
import BudgetsPage from "../features/budgets/BudgetsPage"; // ← NEW

export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      {
        index: true,
        element: (
          <ProtectedRoute>
            <SummaryPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "transactions",
        element: (
          <ProtectedRoute>
            <TransactionsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "budgets",                               // ← NEW
        element: (
          <ProtectedRoute>
            <BudgetsPage />
          </ProtectedRoute>
        ),
      },
      { path: "login", element: <LoginPage /> },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);

export default router;
