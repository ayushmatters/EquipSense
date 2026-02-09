import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiHome, FiUpload, FiClock } from 'react-icons/fi';
import { motion } from 'framer-motion';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', icon: FiHome, label: 'Dashboard' },
    { path: '/upload', icon: FiUpload, label: 'Upload Data' },
    { path: '/history', icon: FiClock, label: 'History' },
  ];

  return (
    <motion.div
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-64 bg-white dark:bg-gray-800 h-[calc(100vh-4rem)] shadow-xl sticky top-16 hidden lg:block"
    >
      <div className="p-6">
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="text-xl" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Info Card */}
        <div className="mt-8 p-4 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-700 dark:to-gray-600 rounded-lg">
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">
            Quick Tip
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Upload your CSV files to visualize equipment parameters and generate detailed reports.
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar;
