import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <section className="text-center py-12">
        <h1 className="text-4xl md:text-6xl font-bold text-green-600 mb-6">
          Welcome to Menu.ai
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Personalized dietary menu recommendations powered by IoT sensors and artificial intelligence
        </p>
        <div className="flex justify-center gap-4">
          <Link
            to="/recommendations"
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-full transition duration-300"
          >
            Get Recommendations
          </Link>
          <Link
            to="/menu"
            className="bg-white hover:bg-gray-100 text-green-600 border border-green-600 font-bold py-3 px-6 rounded-full transition duration-300"
          >
            View Menu
          </Link>
        </div>
      </section>

      <section className="py-12">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-green-600 text-2xl font-bold">1</span>
            </div>
            <h3 className="text-xl font-bold mb-2">IoT Sensing</h3>
            <p className="text-gray-600">
              Our IoT sensors detect your physiological state and environmental factors
            </p>
          </div>
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-green-600 text-2xl font-bold">2</span>
            </div>
            <h3 className="text-xl font-bold mb-2">AI Analysis</h3>
            <p className="text-gray-600">
              Advanced AI algorithms analyze your data to understand your dietary needs
            </p>
          </div>
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-green-600 text-2xl font-bold">3</span>
            </div>
            <h3 className="text-xl font-bold mb-2">Personalized Menu</h3>
            <p className="text-gray-600">
              Receive customized menu recommendations tailored to your unique requirements
            </p>
          </div>
        </div>
      </section>

      <section className="py-12 bg-green-50 rounded-lg">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Transform Your Dining Experience?</h2>
          <p className="text-gray-600 mb-8 text-lg">
            Join thousands of satisfied customers who have revolutionized their eating habits with Menu.ai
          </p>
          <Link
            to="/recommendations"
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-full transition duration-300 inline-block"
          >
            Start Your Journey
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;