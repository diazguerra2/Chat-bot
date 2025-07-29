import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  MessageSquare, 
  Award, 
  BookOpen, 
  Brain,
  Users,
  Star
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();

  const quickActions = [
    {
      title: 'Start Chatting',
      description: 'Get instant answers about ISTQB certifications',
      href: '/chat',
      icon: MessageSquare,
      color: 'bg-blue-500',
      gradient: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Browse Certifications',
      description: 'Explore all available ISTQB certifications',
      href: '/certifications',
      icon: Award,
      color: 'bg-green-500',
      gradient: 'from-green-500 to-green-600'
    },
    {
      title: 'Find Training',
      description: 'Discover accredited training providers',
      href: '/training',
      icon: BookOpen,
      color: 'bg-purple-500',
      gradient: 'from-purple-500 to-purple-600'
    },
    {
      title: 'Get Advice',
      description: 'Personalized certification recommendations',
      href: '/advice',
      icon: Brain,
      color: 'bg-orange-500',
      gradient: 'from-orange-500 to-orange-600'
    }
  ];

  const stats = [
    {
      label: 'Available Certifications',
      value: '7+',
      icon: Award,
      description: 'Foundation to Specialist levels'
    },
    {
      label: 'Training Providers',
      value: '5+',
      icon: Users,
      description: 'Accredited worldwide'
    },
    {
      label: 'Career Paths',
      value: '4',
      icon: Brain,
      description: 'Tailored recommendations'
    },
    {
      label: 'Average Study Time',
      value: '3-6',
      icon: BookOpen,
      description: 'Months per certification'
    }
  ];

  const popularCertifications = [
    {
      id: 'CTFL',
      name: 'Foundation Level',
      description: 'Perfect starting point for all testers',
      level: 'Foundation',
      popularity: 95
    },
    {
      id: 'CTAL-TA',
      name: 'Test Analyst',
      description: 'Advanced technical testing skills',
      level: 'Advanced',
      popularity: 78
    },
    {
      id: 'CTAL-TAE',
      name: 'Test Automation Engineering',
      description: 'High-demand automation expertise',
      level: 'Advanced',
      popularity: 85
    },
    {
      id: 'CT-AI',
      name: 'AI Testing',
      description: 'Future-proof AI/ML testing skills',
      level: 'Specialist',
      popularity: 72
    }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-istqb-blue to-blue-600 rounded-lg p-8 text-white">
        <div className="max-w-3xl">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.name || 'Tester'}! 👋
          </h1>
          <p className="text-blue-100 text-lg mb-6">
            Ready to advance your testing career with ISTQB certifications? 
            I'm here to help you find the perfect certification path.
          </p>
          <Link
            to="/chat"
            className="inline-flex items-center space-x-2 bg-white text-istqb-blue px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors duration-200"
          >
            <MessageSquare className="w-5 h-5" />
            <span>Start Chatting Now</span>
          </Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.href}
                to={action.href}
                className="group bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow duration-200"
              >
                <div className={`w-12 h-12 bg-gradient-to-r ${action.gradient} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {action.title}
                </h3>
                <p className="text-gray-600 text-sm">
                  {action.description}
                </p>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Stats */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Overview</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-2xl font-bold text-gray-900">
                    {stat.value}
                  </div>
                  <Icon className="w-6 h-6 text-istqb-blue" />
                </div>
                <div className="text-sm font-medium text-gray-900 mb-1">
                  {stat.label}
                </div>
                <div className="text-xs text-gray-500">
                  {stat.description}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Popular Certifications */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Popular Certifications</h2>
          <Link
            to="/certifications"
            className="text-istqb-blue hover:text-blue-700 font-medium text-sm transition-colors duration-200"
          >
            View All →
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {popularCertifications.map((cert) => (
            <Link
              key={cert.id}
              to={`/certifications/${cert.id}`}
              className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow duration-200 group"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 group-hover:text-istqb-blue transition-colors duration-200">
                    {cert.name}
                  </h3>
                  <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${
                    cert.level === 'Foundation' ? 'bg-green-100 text-green-800' :
                    cert.level === 'Advanced' ? 'bg-blue-100 text-blue-800' :
                    'bg-purple-100 text-purple-800'
                  }`}>
                    {cert.level}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  <span className="text-sm text-gray-600">{cert.popularity}%</span>
                </div>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                {cert.description}
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-istqb-blue h-2 rounded-full transition-all duration-300"
                  style={{ width: `${cert.popularity}%` }}
                ></div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Getting Started Tips */}
      <div className="bg-gray-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Getting Started Tips</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="space-y-2">
            <div className="w-8 h-8 bg-istqb-blue rounded-full flex items-center justify-center text-white font-bold text-sm">
              1
            </div>
            <h3 className="font-semibold text-gray-900">Assess Your Level</h3>
            <p className="text-sm text-gray-600">
              Start by telling our chatbot about your testing experience to get personalized recommendations.
            </p>
          </div>
          <div className="space-y-2">
            <div className="w-8 h-8 bg-istqb-blue rounded-full flex items-center justify-center text-white font-bold text-sm">
              2
            </div>
            <h3 className="font-semibold text-gray-900">Choose Your Path</h3>
            <p className="text-sm text-gray-600">
              Explore Foundation, Advanced, or Specialist certifications based on your career goals.
            </p>
          </div>
          <div className="space-y-2">
            <div className="w-8 h-8 bg-istqb-blue rounded-full flex items-center justify-center text-white font-bold text-sm">
              3
            </div>
            <h3 className="font-semibold text-gray-900">Find Training</h3>
            <p className="text-sm text-gray-600">
              Get connected with accredited training providers and choose the format that works for you.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
