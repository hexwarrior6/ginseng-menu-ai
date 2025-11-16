import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './layouts/Header';
import Footer from './layouts/Footer';
import HomePage from './pages/HomePage';
import MenuPage from './pages/MenuPage';
import RecommendationPage from './pages/RecommendationPage';
import DishDetailPage from './pages/DishDetailPage';
import UserProfilePage from './pages/UserProfilePage';
import DishUploadPage from './pages/DishUploadPage';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/menu" element={<MenuPage />} />
            <Route path="/recommendations" element={<RecommendationPage />} />
            <Route path="/dish/:id" element={<DishDetailPage />} />
            <Route path="/profile" element={<UserProfilePage />} />
            <Route path="/upload" element={<DishUploadPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
