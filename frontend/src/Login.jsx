import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    //event submit, change of value
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const res = await axios.post('http://localhost:5000/login', {
        username,
        password
      });
      
      // Stockage des données
      localStorage.setItem('token', res.data.token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      
      // Redirection basée sur le rôle
      if (res.data.user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/client');
      }
      
    } catch (err) {
      setError(err.response?.data?.msg || "Échec de la connexion");
    } finally {
      setIsLoading(false);
    }

 
};

 const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  navigate('/'); // ou la route de ton choix
  };

  return (
    <div className="min-h-screen justify-center flex flex-col items-center  bg-indigo-600 p-4">

      <form 
  onSubmit={handleLogin}
  className="max-w-md mx-auto mt-1 bg-white p-8 rounded-lg shadow-md"
>
  <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Connexion</h2>
  
  <div className="mb-4">
    <input
      type="text"
      placeholder="Nom d'utilisateur"
      value={username}
      onChange={(e) => setUsername(e.target.value)}
      required
      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
    />
  </div>
  
  <div className="mb-6">
    <input
      type="password"
      placeholder="Mot de passe"
      value={password}
      onChange={(e) => setPassword(e.target.value)}
      required
      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
    />
  </div>
  
  {error && (
  <div className="mb-4 text-red-600 text-sm text-center">
    {error}
  </div>
)}

  <button
    type="submit"
    className="w-full py-3 px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition duration-200 transform hover:-translate-y-1 shadow-md hover:shadow-lg"
  >
    Se connecter
  </button>
   <p className="mt-6 text-center text-sm text-gray-600">
        Vous n’avez pas de compte ?
        <a href="/register" className="text-indigo-600 hover:underline ml-1">Créer un compte</a>
      </p>

      <button 
      onClick={handleLogout}
    className="w-full py-3 px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition duration-200 transform hover:-translate-y-1 shadow-md hover:shadow-lg"
  >
    Déconnecter
  </button>
</form>
    </div>
  );
}

export default LoginForm;