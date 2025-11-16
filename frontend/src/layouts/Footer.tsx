const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">Menu.ai</h3>
            <p className="text-gray-400">
              Personalized dietary menu recommendations powered by IoT and AI.
            </p>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-white">
                  Home
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white">
                  Menu
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white">
                  Recommendations
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white">
                  Profile
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-4">Contact Us</h4>
            <address className="not-italic text-gray-400">
              <p>123 Smart Restaurant St.</p>
              <p>Foodville, FD 12345</p>
              <p>Email: info@menu.ai</p>
              <p>Phone: (123) 456-7890</p>
            </address>
          </div>
        </div>
        <div className="border-t border-gray-700 mt-8 pt-6 text-center text-gray-400">
          <p>&copy; {new Date().getFullYear()} Menu.ai. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;