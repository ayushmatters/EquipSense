/**
 * OTP Controller
 * Handles OTP email sending logic
 */

const nodemailer = require('nodemailer');
const { generateOTPEmail } = require('../utils/emailTemplates');

/**
 * Nodemailer transporter configuration
 */
const createTransporter = () => {
    return nodemailer.createTransport({
        service: process.env.EMAIL_SERVICE || 'gmail',
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASS
        }
    });
};

/**
 * Send OTP Email
 * POST /api/otp/send
 * 
 * Request body:
 * {
 *   email: string,
 *   otp: string,
 *   firstName: string,
 *   lastName: string,
 *   purpose: 'registration' | 'login' | 'password_reset'
 * }
 */
exports.sendOTP = async (req, res, next) => {
    try {
        const { email, otp, firstName, lastName, purpose } = req.body;
        
        // Validation
        if (!email || !otp) {
            return res.status(400).json({
                success: false,
                message: 'Email and OTP are required'
            });
        }
        
        // Email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return res.status(400).json({
                success: false,
                message: 'Invalid email format'
            });
        }
        
        // OTP format validation
        if (!/^\d{6}$/.test(otp)) {
            return res.status(400).json({
                success: false,
                message: 'OTP must be 6 digits'
            });
        }
        
        // Generate email content
        const emailHTML = generateOTPEmail({
            firstName: firstName || 'User',
            lastName: lastName || '',
            otp,
            purpose: purpose || 'registration',
            validityMinutes: parseInt(process.env.OTP_VALIDITY_MINUTES) || 5
        });
        
        // Determine subject based on purpose
        let subject = 'Verify Your Email - EquipSense';
        if (purpose === 'password_reset') {
            subject = 'Password Reset OTP - EquipSense';
        } else if (purpose === 'login') {
            subject = 'Login Verification OTP - EquipSense';
        }
        
        // Create transporter
        const transporter = createTransporter();
        
        // Send email
        const info = await transporter.sendMail({
            from: process.env.EMAIL_FROM || `"EquipSense" <${process.env.EMAIL_USER}>`,
            to: email,
            subject: subject,
            html: emailHTML
        });
        
        console.log(`✅ OTP sent to ${email} - Message ID: ${info.messageId}`);
        
        res.json({
            success: true,
            message: 'OTP sent successfully',
            messageId: info.messageId,
            expiresIn: (parseInt(process.env.OTP_VALIDITY_MINUTES) || 5) * 60 // in seconds
        });
        
    } catch (error) {
        console.error('❌ Error sending OTP:', error);
        
        // Handle specific Nodemailer errors
        if (error.code === 'EAUTH') {
            return res.status(500).json({
                success: false,
                message: 'Email authentication failed. Please check email credentials.'
            });
        }
        
        if (error.code === 'ECONNECTION') {
            return res.status(500).json({
                success: false,
                message: 'Failed to connect to email server.'
            });
        }
        
        next(error);
    }
};
