import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import { FiDownload, FiCalendar, FiPackage, FiClock } from 'react-icons/fi';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { datasetAPI } from '../services/api';

const HistoryPage = ({ darkMode, toggleDarkMode }) => {
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);
  const [downloading, setDownloading] = useState({});

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await datasetAPI.getHistory();
      setHistory(response.datasets || []);
    } catch (error) {
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async (datasetId) => {
    setDownloading({ ...downloading, [datasetId]: true });
    try {
      await datasetAPI.downloadReport(datasetId);
      toast.success('Report downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download report');
    } finally {
      setDownloading({ ...downloading, [datasetId]: false });
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-6">
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton h-32 rounded-xl" />
              ))}
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
              Upload History
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              View and manage your uploaded datasets (Last 5 uploads)
            </p>
          </motion.div>

          {/* History List */}
          {history.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center"
            >
              <FiClock className="text-6xl text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-700 dark:text-gray-300 mb-2">
                No Upload History
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                You haven't uploaded any datasets yet. Start by uploading your first CSV file!
              </p>
            </motion.div>
          ) : (
            <div className="space-y-4">
              {history.map((dataset, index) => (
                <motion.div
                  key={dataset.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 card-hover"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Dataset Info */}
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                          <FiPackage className="text-2xl text-white" />
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                            {dataset.filename}
                          </h3>
                          <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                            <FiCalendar className="text-sm" />
                            <span>{formatDate(dataset.uploaded_at)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Statistics Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                            Equipment Count
                          </p>
                          <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                            {dataset.equipment_count}
                          </p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                            Avg Flowrate
                          </p>
                          <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
                            {dataset.avg_flowrate?.toFixed(2)}
                          </p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                            Avg Pressure
                          </p>
                          <p className="text-xl font-bold text-purple-600 dark:text-purple-400">
                            {dataset.avg_pressure?.toFixed(2)}
                          </p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                            Avg Temperature
                          </p>
                          <p className="text-xl font-bold text-pink-600 dark:text-pink-400">
                            {dataset.avg_temperature?.toFixed(2)}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Download Button */}
                    <button
                      onClick={() => handleDownloadReport(dataset.id)}
                      disabled={downloading[dataset.id]}
                      className="ml-4 flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {downloading[dataset.id] ? (
                        <>
                          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <FiDownload />
                          <span>Download PDF</span>
                        </>
                      )}
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {/* Info Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-6 bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-xl p-6"
          >
            <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-2">
              ℹ️ Information
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Only the last 5 uploaded datasets are stored. Older datasets are automatically removed
              when you upload new ones.
            </p>
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default HistoryPage;
