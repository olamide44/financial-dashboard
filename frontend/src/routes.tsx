import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import RequireAuth from "./components/RequireAuth";
import Dashboard from "./pages/Dashboard";
import Instrument from "./pages/Instrument";
import Login from "./pages/Login";
import Portfolio from "./pages/Portfolio";

const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  {
    path: "/",
    element: (
      <RequireAuth>
        <App />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      { path: "instrument/:id", element: <Instrument /> },
      { path: "portfolio/:id", element: <Portfolio /> },
    ],
  },
]);

export default router;
