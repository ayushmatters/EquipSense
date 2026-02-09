/**
 * Email Templates
 * Professional HTML email templates for OTP delivery
 */

/**
 * Generate OTP Email HTML
 * @param {Object} params
 * @param {string} params.firstName - User's first name
 * @param {string} params.lastName - User's last name
 * @param {string} params.otp - 6-digit OTP code
 * @param {string} params.purpose - Purpose of OTP (registration, login, password_reset)
 * @param {number} params.validityMinutes - OTP validity duration
 * @returns {string} HTML email content
 */
exports.generateOTPEmail = ({ firstName, lastName, otp, purpose, validityMinutes }) => {
    const fullName = `${firstName} ${lastName}`.trim() || 'User';
    
    // Message based on purpose
    let heading = 'Verify Your Email';
    let message = 'Thank you for registering with EquipSense. Please use the following OTP to complete your registration:';
    
    if (purpose === 'password_reset') {
        heading = 'Reset Your Password';
        message = 'You requested to reset your password. Use the following OTP to proceed:';
    } else if (purpose === 'login') {
        heading = 'Verify Your Login';
        message = 'Please use the following OTP to verify your login attempt:';
    }
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${heading} - EquipSense</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        .email-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .logo {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }
        .email-body {
            padding: 50px 40px;
        }
        .greeting {
            font-size: 24px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 20px;
        }
        .message {
            font-size: 16px;
            color: #4a5568;
            line-height: 1.6;
            margin-bottom: 35px;
        }
        .otp-container {
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            margin: 30px 0;
            border: 2px dashed #cbd5e0;
        }
        .otp-label {
            font-size: 14px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .otp-code {
            font-size: 42px;
            font-weight: bold;
            color: #667eea;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }
        .validity {
            font-size: 14px;
            color: #e53e3e;
            margin-top: 15px;
            font-weight: 600;
        }
        .warning-box {
            background: #fff5f5;
            border-left: 4px solid #e53e3e;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
        }
        .warning-box p {
            font-size: 14px;
            color: #742a2a;
            line-height: 1.6;
            margin: 0;
        }
        .footer {
            background: #f7fafc;
            padding: 30px;
            text-align: center;
            font-size: 13px;
            color: #718096;
            border-top: 1px solid #e2e8f0;
        }
        .footer-links {
            margin: 15px 0;
        }
        .footer-links a {
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
        }
        .social-icons {
            margin: 15px 0;
        }
        .social-icons a {
            display: inline-block;
            margin: 0 8px;
            color: #718096;
            text-decoration: none;
            font-size: 14px;
        }
        @media only screen and (max-width: 600px) {
            .email-body {
                padding: 30px 25px;
            }
            .otp-code {
                font-size: 36px;
                letter-spacing: 6px;
            }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="email-header">
            <div class="logo">⚙️ EquipSense</div>
            <p style="font-size: 16px; opacity: 0.9;">Chemical Equipment Parameter Visualizer</p>
        </div>
        
        <!-- Body -->
        <div class="email-body">
            <div class="greeting">Hello ${fullName}!</div>
            
            <div class="message">
                ${message}
            </div>
            
            <!-- OTP Display -->
            <div class="otp-container">
                <div class="otp-label">Your Verification Code</div>
                <div class="otp-code">${otp}</div>
                <div class="validity">⏱️ Valid for ${validityMinutes} minutes</div>
            </div>
            
            <!-- Warning Box -->
            <div class="warning-box">
                <p>
                    <strong>🔒 Security Notice:</strong><br>
                    Never share this OTP with anyone. EquipSense staff will never ask for your OTP. 
                    If you didn't request this code, please ignore this email or contact support immediately.
                </p>
            </div>
            
            <div class="message">
                If you have any questions or need assistance, feel free to reach out to our support team.
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-links">
                <a href="#">Privacy Policy</a> | 
                <a href="#">Terms of Service</a> | 
                <a href="#">Contact Support</a>
            </div>
            
            <div class="social-icons">
                <a href="#">LinkedIn</a> | 
                <a href="#">Twitter</a> | 
                <a href="#">GitHub</a>
            </div>
            
            <p style="margin-top: 15px;">
                © ${new Date().getFullYear()} EquipSense. All rights reserved.<br>
                Chemical Equipment Parameter Visualizer
            </p>
            
            <p style="margin-top: 15px; font-size: 12px; opacity: 0.7;">
                This is an automated email. Please do not reply to this message.
            </p>
        </div>
    </div>
</body>
</html>
    `;
};
