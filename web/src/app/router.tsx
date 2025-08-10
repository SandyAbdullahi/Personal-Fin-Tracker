import { createBrowserRouter, Navigate } from "react-router-dom";
import ProtectedRoute from "../components/ProtectedRoute";
import Layout from "./layout";

import LoginPage from "../features/auth/LoginPage";
import SummaryPage from "../features/summary/SummaryPage";
import TransactionsPage from "../features/transactions/TransactionsPage";

const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },

  {
    element: <ProtectedRoute />, // everything inside here requires auth
    children: [
      {
        path: "/",
        element: <Layout />,
        children: [
          { index: true, element: <SummaryPage /> },
          { path: "transactions", element: <TransactionsPage /> },
        ],
      },
    ],
  },

  { path: "*", element: <Navigate to="/" replace /> },
]);

export default router;
