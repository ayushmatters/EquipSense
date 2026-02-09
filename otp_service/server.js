/**
 * EquipSense OTP Email Service
 * Node.js + Express + Nodemailer
 * 
 * Handles OTP email delivery for authentication
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
require('dotenv').config();

const otpRoutes = require('./routes/otpRoutes');
const { errorHandler } = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 3001;

// ===================================
// MIDDLEWARE
// ===================================

// Security middleware
app.use(helmet());

// CORS configuration
const corsOptions = {
    origin: [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:8000',
        'http://127.0.0.1:8000'
    ],
    credentials: true,
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type', 'Authorization']
};
app.use(cors(corsOptions));

// Request logging
app.use(morgan('dev'));

// Body parser
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rate limiting - prevent OTP spam
const otpLimiter = rateLimit({
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 5, // 5 requests per window
    message: {
        success: false,
        message: 'Too many OTP requests. Please try again later.'
    },
    standardHeaders: true,
    legacyHeaders: false,
});

// ===================================
// ROUTES
// ===================================

// Health check
app.get('/health', (req, res) => {
    res.json({
        success: true,
        message: 'OTP Service is running',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// OTP routes with rate limiting
app.use('/api/otp', otpLimiter, otpRoutes);

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        success: false,
        message: 'Endpoint not found'
    });
});

// Error handler
app.use(errorHandler);

// ===================================
// SERVER START
// ===================================

app.listen(PORT, () => {
    console.log('');
    console.log('========================================');
    console.log('🚀 EquipSense OTP Service Started');
    console.log('========================================');
    console.log(`📧 Email Service: ${process.env.EMAIL_SERVICE || 'Gmail'}`);
    console.log(`📍 Port: ${PORT}`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`⏱️  OTP Validity: ${process.env.OTP_VALIDITY_MINUTES || 5} minutes`);
    console.log('========================================');
    console.log('');
    
    // Check critical environment variables
    if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS) {
        console.warn('⚠️  WARNING: Email credentials not configured!');
        console.warn('   Please set EMAIL_USER and EMAIL_PASS in .env file');
        console.warn('   See .env.example for instructions');
    }
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM signal received: closing server');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT signal received: closing server');
    process.exit(0);
});

module.exports = app;
