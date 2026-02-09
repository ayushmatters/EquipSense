import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import SummaryCards from '../components/SummaryCards';
import { TypeDistributionChart, ParameterAveragesChart } from '../components/Charts';
import DataTable from '../components/DataTable';
import { datasetAPI } from '../services/api';

const Dashboard = ({ darkMode, toggleDarkMode }) => {
  const [loading, setLoading] = useState(true);
  const [summaryData, setSummaryData] = useState(null);
  const [typeDistribution, setTypeDistribution] = useState({});

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch summary data
      const summary = await datasetAPI.getSummary();
      setSummaryData(summary);

      // Fetch type distribution
      const distribution = await datasetAPI.getTypeDistribution();
      setTypeDistribution(distribution.type_distribution);
    } catch (error) {
      if (error.response?.data?.error === 'No datasets found for this user') {
        toast.info('Welcome! Upload your first CSV file to get started.');
        setSummaryData({
          statistics: {
            total_equipment: 0,
            avg_flowrate: 0,
            avg_pressure: 0,
            avg_temperature: 0,
          },
          equipment_list: [],
        });
        setTypeDistribution({});
      } else {
        toast.error('Failed to load dashboard data');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-6">
            <div className="space-y-6">
              {/* Loading Skeletons */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="skeleton h-32 rounded-xl" />
                ))}
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {[...Array(2)].map((_, i) => (
                  <div key={i} className="skeleton h-96 rounded-xl" />
                ))}
              </div>
              <div className="skeleton h-96 rounded-xl" />
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
      
      <div className="flex">
        <Sidebar />
        
        <main className="flex-1 p-6">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Overview of your equipment data and analytics
            </p>
          </motion.div>

          {/* Summary Cards */}
          <div className="mb-6">
            <SummaryCards statistics={summaryData?.statistics} />
          </div>

          {/* Charts */}
          {summaryData?.statistics?.total_equipment > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <TypeDistributionChart 
                typeDistribution={typeDistribution} 
                darkMode={darkMode} 
              />
              <ParameterAveragesChart 
                statistics={summaryData?.statistics} 
                darkMode={darkMode} 
              />
            </div>
          )}

          {/* Data Table */}
          <DataTable data={summaryData?.equipment_list || []} />
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
