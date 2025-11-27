import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
import Markdown from 'react-markdown';
import { Send, LogOut, Activity, User, Bot, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const { logout } = useAuth();
    const navigate = useNavigate();
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const formatTimestamp = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        const now = new Date();
        const isToday = date.toDateString() === now.toDateString();

        if (isToday) {
            return date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        } else {
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await api.get('/chat/history');
                setMessages(response.data);
            } catch (error) {
                console.error("Failed to fetch history", error);
                if (error.response?.status === 401) {
                    logout();
                    navigate('/login');
                }
            }
        };
        fetchHistory();
    }, [logout, navigate]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input, timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await api.post('/chat/message', { message: userMessage.content });
            setMessages(prev => [...prev, response.data]);
        } catch (error) {
            console.error("Failed to send message", error);
            const errorMessage = error.response?.data?.detail ||
                error.message ||
                "Error: Could not reach the server.";
            setMessages(prev => [...prev, { role: 'model', content: errorMessage }]);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (index) => {
        try {
            const response = await api.delete(`/chat/messages/${index}`);
            const deletedIndices = response.data.deleted_indices;

            setMessages(prev => prev.filter((_, i) => !deletedIndices.includes(i)));
        } catch (error) {
            console.error("Failed to delete message", error);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-teal-50/30 to-slate-100 relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] right-[-5%] w-96 h-96 bg-teal-200/20 rounded-full blur-3xl"></div>
                <div className="absolute bottom-[-10%] left-[-5%] w-96 h-96 bg-blue-200/20 rounded-full blur-3xl"></div>
            </div>

            {/* Header */}
            <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 px-6 py-4 flex justify-between items-center shadow-sm z-10">
                <div className="flex items-center space-x-3">
                    <div className="bg-gradient-to-tr from-teal-600 to-teal-500 p-2 rounded-xl shadow-lg shadow-teal-200/50">
                        <Activity className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Med AI</h1>
                        <p className="text-xs text-teal-600 font-medium flex items-center">
                            <span className="w-2 h-2 bg-teal-500 rounded-full mr-1 animate-pulse"></span>
                            Online & Ready
                        </p>
                    </div>
                </div>
                <button
                    onClick={handleLogout}
                    className="text-slate-400 hover:text-red-600 transition-colors p-2 rounded-full hover:bg-red-50"
                    title="Logout"
                >
                    <LogOut className="w-5 h-5" />
                </button>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-8 z-10 scroll-smooth">
                <AnimatePresence initial={false}>
                    {messages.map((msg, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} group`}
                        >
                            <div className={`flex max-w-[85%] md:max-w-[75%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start gap-4`}>
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-md ${msg.role === 'user' ? 'bg-slate-800' : 'bg-gradient-to-br from-teal-500 to-teal-600'
                                    }`}>
                                    {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
                                </div>

                                <div className="flex flex-col gap-1 relative">
                                    <div className={`p-5 rounded-2xl shadow-sm relative group-hover:shadow-md transition-shadow ${msg.role === 'user'
                                        ? 'bg-slate-800 text-white rounded-tr-none'
                                        : 'bg-white/90 backdrop-blur-sm text-slate-800 border border-slate-100 rounded-tl-none'
                                        }`}>
                                        <div className="prose prose-sm max-w-none dark:prose-invert">
                                            <Markdown>{msg.content}</Markdown>
                                        </div>

                                        {/* Delete Button - Visible on Hover */}
                                        <button
                                            onClick={() => handleDelete(idx)}
                                            className={`absolute -top-3 ${msg.role === 'user' ? '-left-3' : '-right-3'} 
                                                p-1.5 rounded-full bg-white border border-slate-200 shadow-sm 
                                                opacity-0 group-hover:opacity-100 transition-opacity duration-200
                                                text-slate-400 hover:text-red-500 hover:border-red-200`}
                                            title="Delete message"
                                        >
                                            <Trash2 className="w-3.5 h-3.5" />
                                        </button>
                                    </div>
                                    {msg.timestamp && (
                                        <span className={`text-xs text-slate-400 ${msg.role === 'user' ? 'text-right' : 'text-left'} px-2`}>
                                            {formatTimestamp(msg.timestamp)}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {loading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex justify-start"
                    >
                        <div className="flex max-w-[80%] flex-row items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-teal-600 flex items-center justify-center flex-shrink-0 shadow-md">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                            <div className="bg-white p-5 rounded-2xl rounded-tl-none border border-slate-100 shadow-sm">
                                <div className="flex space-x-2 items-center h-6">
                                    <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white/80 backdrop-blur-md border-t border-slate-200 p-6 z-10">
                <form onSubmit={handleSend} className="max-w-4xl mx-auto relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Describe your symptoms or ask a medical question..."
                        className="w-full pl-6 pr-14 py-4 bg-slate-50 border border-slate-200 rounded-full focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none transition-all shadow-inner text-slate-700 placeholder:text-slate-400"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="absolute right-2 top-2 p-2.5 bg-gradient-to-r from-teal-600 to-teal-500 text-white rounded-full hover:from-teal-700 hover:to-teal-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
                <p className="text-center text-xs text-slate-400 mt-3">
                    Med AI can make mistakes. Always consult a professional doctor for serious conditions.
                </p>
            </div>
        </div>
    );
};

export default ChatInterface;
