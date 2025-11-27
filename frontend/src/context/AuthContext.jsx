import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../lib/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            // Ideally verify token with backend here, for now just assume logged in if token exists
            setUser({ token });
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const response = await api.post('/auth/login', formData);
            const { access_token } = response.data;

            localStorage.setItem('token', access_token);
            setUser({ token: access_token });
            return true;
        } catch (error) {
            console.error("Login failed:", error.response?.data || error.message);
            throw error;  // Throw error to be caught by Login component
        }
    };

    const register = async (email, password, fullName) => {
        try {
            const response = await api.post('/auth/register', {
                email,
                password,
                full_name: fullName
            });
            const { access_token } = response.data;

            localStorage.setItem('token', access_token);
            setUser({ token: access_token });
            return true;
        } catch (error) {
            console.error("Registration failed:", error.response?.data || error.message);
            throw error;  // Throw error to be caught by Login component
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
