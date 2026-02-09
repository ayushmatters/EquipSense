import React from 'react';
import { motion } from 'framer-motion';
import { FiPackage, FiActivity, FiThermometer, FiWind } from 'react-icons/fi';

const SummaryCards = ({ statistics }) => {
  const cards = [
    {
      title: 'Total Equipment',
      value: statistics?.total_equipment || 0,
      icon: FiPackage,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      title: 'Avg Flowrate',
      value: statistics?.avg_flowrate?.toFixed(2) || '0.00',
      icon: FiWind,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    },
    {
      title: 'Avg Pressure',
      value: statistics?.avg_pressure?.toFixed(2) || '0.00',
      icon: FiActivity,
      color: 'from-pink-500 to-pink-600',
      bgColor: 'bg-pink-50 dark:bg-pink-900/20',
    },
    {
      title: 'Avg Temperature',
      value: statistics?.avg_temperature?.toFixed(2) || '0.00',
      icon: FiThermometer,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 card-hover"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  {card.title}
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
                  {card.value}
                </p>
              </div>
              <div className={`p-4 rounded-lg ${card.bgColor}`}>
                <Icon className={`text-3xl bg-gradient-to-r ${card.color} bg-clip-text text-transparent`} />
              </div>
            </div>
            <div className="mt-4">
              <div className={`h-2 bg-gradient-to-r ${card.color} rounded-full`} />
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default SummaryCards;
