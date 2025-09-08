import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import RequireAuth from "./components/RequireAuth";
import Dashboard from "./pages/Dashboard";
import Instrument from "./pages/Instrument";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import Portfolio from "./pages/Portfolio";
import Signup from "./pages/Signup";


const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  {path: "/signup", element: <Signup />},
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
      { path: "*", element: <NotFound /> },

    ],
  },
]);

export default router;
