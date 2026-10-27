
import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="w-full max-w-7xl mx-auto flex justify-end items-center px-6 py-4">
      <nav className="flex items-center gap-4 sm:gap-8">
        <Link
          to="/"
          className={`px-3 py-2 rounded-md text-sm font-medium transition ${
            isActive("/")
              ? "text-violet-400 bg-violet-900/30"
              : "text-gray-300 hover:text-violet-400"
          }`}
        >
          Home
        </Link>

        <Link
          to="/detect"
          className={`px-3 py-2 rounded-md text-sm font-medium transition ${
            isActive("/detect")
              ? "text-violet-400 bg-violet-900/30"
              : "text-gray-300 hover:text-violet-400"
          }`}
        >
          Detect Review
        </Link>

        <Link
          to="/upload"
          className={`px-3 py-2 rounded-md text-sm font-medium transition ${
            isActive("/upload")
              ? "text-violet-400 bg-violet-900/30"
              : "text-gray-300 hover:text-violet-400"
          }`}
        >
          Upload File
        </Link>

        <Link
          to="/history"
          className={`px-3 py-2 rounded-md text-sm font-medium transition ${
            isActive("/history")
              ? "text-violet-400 bg-violet-900/30"
              : "text-gray-300 hover:text-violet-400"
          }`}
        >
          History
        </Link>
      </nav>
    </header>
  );
};

export default Navbar;
