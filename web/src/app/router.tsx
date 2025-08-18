// src/app/router.tsx
import React, { Suspense, lazy } from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "../components/ProtectedRoute";
import Layout from "./Layout";

// Lazy-load page bundles
const LoginPage = lazy(() => import("../features/auth/LoginPage"));
const SummaryPage = lazy(() => import("../features/summary/SummaryPage"));
const TransactionsPage = lazy(() => import("../features/transactions/TransactionsPage"));
const BudgetsPage = lazy(() => import("../features/budgets/BudgetsPage"));
const CategoriesPage = lazy(() => import("../features/categories/CategoriesPage"));
const TransfersPage = lazy(() => import("../features/transfers/TransfersPage")); // ← NEW

const Fallback = <div className="p-4 text-sm text-gray-500">Loading…</div>;

export const router = createBrowserRouter([
  {
    element: (
      <Suspense fallback={Fallback}>
        <Layout />
      </Suspense>
    ),
    children: [
      {
        index: true,
        element: (
          <ProtectedRoute>
            <Suspense fallback={Fallback}>
              <SummaryPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: "transactions",
        element: (
          <ProtectedRoute>
            <Suspense fallback={Fallback}>
              <TransactionsPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: "budgets",
        element: (
          <ProtectedRoute>
            <Suspense fallback={Fallback}>
              <BudgetsPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: "categories",
        element: (
          <ProtectedRoute>
            <Suspense fallback={Fallback}>
              <CategoriesPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: "transfers", // ← NEW
        element: (
          <ProtectedRoute>
            <Suspense fallback={Fallback}>
              <TransfersPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: "login",
        element: (
          <Suspense fallback={Fallback}>
            <LoginPage />
          </Suspense>
        ),
      },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);

export default router;
