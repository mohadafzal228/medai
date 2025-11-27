import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, Key, ArrowRight, CheckCircle, Loader2, RefreshCw } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../lib/api';

const ForgotPassword = () => {
    const [step, setStep] = useState(1); // 1: Email, 2: OTP, 3: New Password
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [timer, setTimer] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
        let interval;
        if (timer > 0) {
            interval = setInterval(() => {
                setTimer((prev) => prev - 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [timer]);

    const handleSendOTP = async (e) => {
        if (e) e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await api.post('/auth/forgot-password', { email });
            setStep(2);
            setSuccess('OTP sent to your email');
            setTimer(60); // Start 60s cooldown
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to send OTP');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyOTP = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await api.post('/auth/verify-otp', { email, otp });
            setStep(3);
            setSuccess('OTP verified successfully');
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid OTP');
        } finally {
            setLoading(false);
        }
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await api.post('/auth/reset-password', { email, otp, new_password: newPassword });
            setSuccess('Password reset successfully! Redirecting to login...');
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to reset password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8"
            >
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-slate-900">Reset Password</h2>
                    <p className="text-slate-600 mt-2">Follow the steps to recover your account</p>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-lg text-sm">
                        {error}
                    </div>
                )}

                {success && (
                    <div className="mb-6 p-4 bg-green-50 text-green-600 rounded-lg text-sm flex items-center">
                        <CheckCircle className="h-4 w-4 mr-2" />
                        {success}
                    </div>
                )}

                <AnimatePresence mode="wait">
                    {step === 1 && (
                        <motion.form
                            key="step1"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            onSubmit={handleSendOTP}
                            className="space-y-6"
                        >
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">Email Address</label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                                    <input
                                        type="email"
                                        required
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                                        placeholder="you@example.com"
                                    />
                                </div>
                            </div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-semibold transition-all flex items-center justify-center"
                            >
                                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : (
                                    <>
                                        Send OTP <ArrowRight className="ml-2 h-5 w-5" />
                                    </>
                                )}
                            </button>
                        </motion.form>
                    )}

                    {step === 2 && (
                        <motion.form
                            key="step2"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            onSubmit={handleVerifyOTP}
                            className="space-y-6"
                        >
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">Enter OTP</label>
                                <div className="relative">
                                    <Key className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                                    <input
                                        type="text"
                                        required
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                                        placeholder="Enter 6-digit code"
                                    />
                                </div>
                            </div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-semibold transition-all flex items-center justify-center"
                            >
                                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Verify OTP'}
                            </button>

                            <div className="text-center">
                                <button
                                    type="button"
                                    onClick={() => handleSendOTP()}
                                    disabled={loading || timer > 0}
                                    className="text-sm text-teal-600 hover:text-teal-700 font-medium flex items-center justify-center mx-auto disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {timer > 0 ? (
                                        `Resend OTP in ${timer}s`
                                    ) : (
                                        <>
                                            <RefreshCw className="h-4 w-4 mr-1" /> Resend OTP
                                        </>
                                    )}
                                </button>
                            </div>
                        </motion.form>
                    )}

                    {step === 3 && (
                        <motion.form
                            key="step3"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            onSubmit={handleResetPassword}
                            className="space-y-6"
                        >
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">New Password</label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                                    <input
                                        type="password"
                                        required
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                                        placeholder="Enter new password"
                                    />
                                </div>
                            </div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-semibold transition-all flex items-center justify-center"
                            >
                                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Reset Password'}
                            </button>
                        </motion.form>
                    )}
                </AnimatePresence>

                <div className="mt-6 text-center">
                    <Link to="/login" className="text-sm text-teal-600 hover:text-teal-700 font-medium">
                        Back to Login
                    </Link>
                </div>
            </motion.div>
        </div>
    );
};

export default ForgotPassword;
