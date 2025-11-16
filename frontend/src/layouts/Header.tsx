import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="bg-green-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold">Menu.ai</Link>
          <nav>
            <ul className="flex space-x-6">
              <li><Link to="/" className="hover:text-green-200 transition-colors">Home</Link></li>
              <li><Link to="/menu" className="hover:text-green-200 transition-colors">Menu</Link></li>
              <li><Link to="/recommendations" className="hover:text-green-200 transition-colors">Recommendations</Link></li>
              <li><Link to="/upload" className="hover:text-green-200 transition-colors">Upload</Link></li>
              <li><Link to="/profile" className="hover:text-green-200 transition-colors">Profile</Link></li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;