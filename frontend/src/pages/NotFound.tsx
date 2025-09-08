import { Link } from "react-router-dom";
export default function NotFound() {
  return (
    <div className="mt-24 text-center">
      <h1 className="text-3xl font-semibold mb-2">404</h1>
      <p className="opacity-70 mb-4">Page not found</p>
      <Link to="/" className="underline">Go home</Link>
    </div>
  );
}
