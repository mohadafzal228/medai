import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Activity, Shield, Clock, ArrowRight, CheckCircle } from 'lucide-react';

const Home = () => {
    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
            {/* Hero Section */}
            <div className="relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80')] bg-cover bg-center opacity-5"></div>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 relative">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="text-center max-w-3xl mx-auto"
                    >
                        <div className="inline-flex items-center px-4 py-2 rounded-full bg-teal-50 border border-teal-100 text-teal-700 mb-8">
                            <span className="flex h-2 w-2 rounded-full bg-teal-500 mr-2"></span>
                            AI-Powered Medical Assistance
                        </div>
                        <h1 className="text-5xl md:text-6xl font-bold text-slate-900 tracking-tight mb-6">
                            Your Personal <span className="text-teal-600">Health Companion</span>
                        </h1>
                        <p className="text-xl text-slate-600 mb-10 leading-relaxed">
                            Experience the future of medical guidance with Med AI.
                            Instant, accurate, and evidence-based answers to your health questions,
                            powered by advanced AI.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link
                                to="/register"
                                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-xl text-white bg-teal-600 hover:bg-teal-700 transition-all shadow-lg hover:shadow-teal-500/30"
                            >
                                Get Started Free
                                <ArrowRight className="ml-2 h-5 w-5" />
                            </Link>
                            <Link
                                to="/login"
                                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-xl text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 transition-all shadow-sm"
                            >
                                Sign In
                            </Link>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Features Section */}
            <div className="py-24 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-slate-900 mb-4">Why Choose Med AI?</h2>
                        <p className="text-lg text-slate-600">Advanced technology meets medical expertise.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            {
                                icon: <Activity className="h-8 w-8 text-teal-600" />,
                                title: "Instant Analysis",
                                description: "Get immediate insights into your symptoms and health concerns with our advanced AI engine."
                            },
                            {
                                icon: <Shield className="h-8 w-8 text-teal-600" />,
                                title: "Verified Sources",
                                description: "All medical information is referenced from trusted global health organizations (WHO, CDC)."
                            },
                            {
                                icon: <Clock className="h-8 w-8 text-teal-600" />,
                                title: "24/7 Availability",
                                description: "Access professional medical guidance anytime, anywhere, without the wait."
                            }
                        ].map((feature, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.2 }}
                                viewport={{ once: true }}
                                className="p-8 rounded-2xl bg-slate-50 border border-slate-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                            >
                                <div className="w-14 h-14 rounded-xl bg-teal-50 flex items-center justify-center mb-6">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xl font-semibold text-slate-900 mb-3">{feature.title}</h3>
                                <p className="text-slate-600 leading-relaxed">{feature.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Trust Section */}
            <div className="py-20 bg-slate-900 text-white overflow-hidden">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-2 gap-12 items-center">
                        <div>
                            <h2 className="text-3xl md:text-4xl font-bold mb-6">Trusted by Users Worldwide</h2>
                            <div className="space-y-4">
                                {[
                                    "Evidence-based medical information",
                                    "Secure and private conversations",
                                    "Regularly updated medical database",
                                    "User-friendly interface"
                                ].map((item, index) => (
                                    <div key={index} className="flex items-center space-x-3">
                                        <CheckCircle className="h-6 w-6 text-teal-400" />
                                        <span className="text-lg text-slate-300">{item}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="relative">
                            <div className="absolute inset-0 bg-teal-500 blur-3xl opacity-20 rounded-full"></div>
                            <img
                                src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
                                alt="Medical Technology"
                                className="relative rounded-2xl shadow-2xl border border-slate-700"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
