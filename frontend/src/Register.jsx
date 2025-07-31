import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Register() {

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert("Vous n'êtes pas connecté");
      navigate('/');
    }
  }, []);
  //elements a enregistrer
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role: 'user'
  });

  const [error, setError] = useState({
    message: '',
    fields: {}
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const currentUser = JSON.parse(localStorage.getItem('user'));
  const isAdmin = currentUser?.role === 'admin';


  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Efface les erreurs de validation quand l'utilisateur modifie
    if (error.fields[e.target.name]) {
      setError({
        ...error,
        fields: {
          ...error.fields,
          [e.target.name]: null
        }
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError({ message: '', fields: {} });
    
    const token = localStorage.getItem('token');

    try {
      const response = await axios.post(
        'http://localhost:5000/register',
        {
          username: formData.username,
          password: formData.password,
          role: formData.role 
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Succès
      navigate('/users', {
        state: { 
          success: `Utilisateur ${response.data.user.username} créé avec succès!`,
          newUser: response.data.user
        }
      });
      
    } catch (error) {
      if (error.response) {
        // Erreurs structurées du backend
        if (error.response.status === 409) {
          setError({
            message: error.response.data.msg,
            fields: { username: 'Ce nom est déjà pris' }
          });
        } else if (error.response.status === 400) {
          // Gestion des erreurs de validation
          const fieldErrors = {};
          if (error.response.data.missing_fields) {
            error.response.data.missing_fields.forEach(field => {
              fieldErrors[field] = 'Ce champ est requis';
            });
          }
          setError({
            message: error.response.data.msg,
            fields: fieldErrors
          });
        } else if (error.response.status === 403) {
          setError({
            message: "Action non autorisée - Privilèges admin requis",
            fields: {}
          });
        } else {
          setError({
            message: error.response.data.msg || "Erreur lors de l'enregistrement",
            fields: {}
          });
        }
      } else {
        setError({
          message: "Erreur réseau ou serveur indisponible",
          fields: {}
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-indigo-600 p-6">
    <form 
      onSubmit={handleSubmit}
      className="max-w-md w-full mx-auto bg-white p-8 rounded-xl shadow-lg"
    >
      <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Créer un nouvel utilisateur</h2>
      
      {error.message && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-center">
          {error.message}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <input
            type="text"
            name="username"
            placeholder="Nom d'utilisateur"
            value={formData.username}
            onChange={handleChange}
            className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 ${
              error.fields.username 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-indigo-500'
            }`}
            disabled={isSubmitting}
            required
          />
          {error.fields.username && (
            <p className="mt-1 text-sm text-red-500">{error.fields.username}</p>
          )}
        </div>

        <div>
          <input
            type="password"
            name="password"
            placeholder="Mot de passe"
            value={formData.password}
            onChange={handleChange}
            className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 ${
              error.fields.password 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-indigo-500'
            }`}
            disabled={isSubmitting}
            required
          />
          {error.fields.password && (
            <p className="mt-1 text-sm text-red-500">{error.fields.password}</p>
          )}
        </div>

        <div>
          <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              disabled={isSubmitting}
            >
  <option value="user">Utilisateur</option>
  {isAdmin && <option value="admin">Administrateur</option>}
</select>
        </div>



        <button
          type="submit"
          className={`w-full py-3 px-6 mt-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition duration-200 transform hover:-translate-y-1 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
            isSubmitting ? 'opacity-75' : ''
          }`}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Création en cours...' : 'Créer l\'utilisateur'}
        </button>
      </div>
    </form>
  </div>
  );
}

export default Register;