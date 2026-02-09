import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import { FiCheckCircle } from 'react-icons/fi';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import FileUploader from '../components/FileUploader';
import { datasetAPI } from '../services/api';

const UploadPage = ({ darkMode, toggleDarkMode }) => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadedData, setUploadedData] = useState(null);

  const handleFileSelect = async (file) => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);
    setUploadSuccess(false);

    try {
      const response = await datasetAPI.upload(file, (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setUploadProgress(percentCompleted);
      });

      setUploadedData(response);
      setUploadSuccess(true);
      toast.success('File uploaded successfully!');
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Upload failed';
      toast.error(errorMessage);
      setUploadSuccess(false);
    } finally {
      setUploading(false);
    }
  };

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
              Upload Dataset
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Upload your CSV file containing equipment parameters
            </p>
          </motion.div>

          <div className="max-w-4xl mx-auto">
            {/* File Uploader */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <FileUploader
                onFileSelect={handleFileSelect}
                isUploading={uploading}
                uploadProgress={uploadProgress}
              />
            </motion.div>

            {/* Success Message */}
            {uploadSuccess && uploadedData && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 bg-green-50 dark:bg-green-900/20 border-2 border-green-500 rounded-xl p-6"
              >
                <div className="flex items-center space-x-3 mb-4">
                  <FiCheckCircle className="text-3xl text-green-600 dark:text-green-400" />
                  <h3 className="text-xl font-bold text-green-800 dark:text-green-200">
                    Upload Successful!
                  </h3>
                </div>
                
                <div className="space-y-2 text-gray-700 dark:text-gray-300">
                  <p><strong>Filename:</strong> {uploadedData.dataset?.filename}</p>
                  <p><strong>Total Equipment:</strong> {uploadedData.statistics?.total_equipment}</p>
                  <p><strong>Average Flowrate:</strong> {uploadedData.statistics?.avg_flowrate?.toFixed(2)}</p>
                  <p><strong>Average Pressure:</strong> {uploadedData.statistics?.avg_pressure?.toFixed(2)}</p>
                  <p><strong>Average Temperature:</strong> {uploadedData.statistics?.avg_temperature?.toFixed(2)}</p>
                </div>

                <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                  Redirecting to dashboard...
                </p>
              </motion.div>
            )}

            {/* Instructions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4">
                📋 Upload Instructions
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400">
                <li className="flex items-start">
                  <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">1.</span>
                  Prepare your CSV file with the required columns
                </li>
                <li className="flex items-start">
                  <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">2.</span>
                  Drag and drop the file or click to browse
                </li>
                <li className="flex items-start">
                  <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">3.</span>
                  Wait for the upload to complete
                </li>
                <li className="flex items-start">
                  <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">4.</span>
                  View your data analytics on the dashboard
                </li>
              </ul>
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default UploadPage;
