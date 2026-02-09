import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FaShieldAlt, FaSignOutAlt, FaUser, FaEnvelope, FaLock } from 'react-icons/fa';
import authService from '../services/authService';

const AdminSettings = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(authService.getCurrentUser());
    const [loading, setLoading] = useState(false);

    const handleLogout = async () => {
        try {
            await authService.logout();
            toast.success('Logged out successfully');
            navigate('/auth/login');
        } catch (error) {
            console.error('Logout error:', error);
            navigate('/auth/login');
        }
    };

    if (!user) {
        navigate('/auth/login');
        return null;
    }

    return (
        <div style={styles.container}>
            <div style={styles.sidebar}>
                <div style={styles.logo}>
                    <FaShieldAlt size={32} color="#f59e0b" />
                    <h2 style={styles.logoText}>Admin Portal</h2>
                </div>
                <nav style={styles.nav}>
                    <a href="/admin-dashboard" style={styles.navItem}>
                        Dashboard
                    </a>
                    <a href="/admin-dashboard/manage-users" style={styles.navItem}>
                        Manage Users
                    </a>
                    <a href="/admin-dashboard/settings" style={{...styles.navItem, background: 'rgba(255,255,255,0.2)'}}>
                        Settings
                    </a>
                </nav>
            </div>
            
            <div style={styles.main}>
                <header style={styles.header}>
                    <h1 style={styles.title}>Admin Settings</h1>
                    <div style={styles.userInfo}>
                        <span style={styles.userName}>Admin: {user.username}</span>
                        <button onClick={handleLogout} style={styles.logoutBtn}>
                            <FaSignOutAlt /> Logout
                        </button>
                    </div>
                </header>
                
                <div style={styles.content}>
                    <div style={styles.card}>
                        <h2 style={styles.cardTitle}>Profile Information</h2>
                        <div style={styles.infoGrid}>
                            <div style={styles.infoItem}>
                                <div style={styles.iconWrapper}>
                                    <FaUser color="#667eea" />
                                </div>
                                <div>
                                    <div style={styles.label}>Username</div>
                                    <div style={styles.value}>{user.username}</div>
                                </div>
                            </div>
                            <div style={styles.infoItem}>
                                <div style={styles.iconWrapper}>
                                    <FaEnvelope color="#667eea" />
                                </div>
                                <div>
                                    <div style={styles.label}>Email</div>
                                    <div style={styles.value}>{user.email}</div>
                                </div>
                            </div>
                            <div style={styles.infoItem}>
                                <div style={styles.iconWrapper}>
                                    <FaShieldAlt color="#f59e0b" />
                                </div>
                                <div>
                                    <div style={styles.label}>Role</div>
                                    <div style={styles.value}>
                                        <span style={styles.roleBadge}>Administrator</span>
                                    </div>
                                </div>
                            </div>
                            {user.first_name && (
                                <div style={styles.infoItem}>
                                    <div style={styles.iconWrapper}>
                                        <FaUser color="#667eea" />
                                    </div>
                                    <div>
                                        <div style={styles.label}>Full Name</div>
                                        <div style={styles.value}>
                                            {user.first_name} {user.last_name || ''}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    <div style={styles.card}>
                        <h2 style={styles.cardTitle}>System Settings</h2>
                        <p style={styles.comingSoon}>Additional settings coming soon...</p>
                        <div style={styles.settingsGrid}>
                            <div style={styles.settingItem}>
                                <div>
                                    <div style={styles.settingLabel}>Email Notifications</div>
                                    <div style={styles.settingDesc}>Receive email notifications for important events</div>
                                </div>
                                <label style={styles.switch}>
                                    <input type="checkbox" defaultChecked />
                                    <span style={styles.slider}></span>
                                </label>
                            </div>
                            <div style={styles.settingItem}>
                                <div>
                                    <div style={styles.settingLabel}>Security Alerts</div>
                                    <div style={styles.settingDesc}>Get notified of security-related activities</div>
                                </div>
                                <label style={styles.switch}>
                                    <input type="checkbox" defaultChecked />
                                    <span style={styles.slider}></span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        minHeight: '100vh',
        background: '#f3f4f6'
    },
    sidebar: {
        width: '250px',
        background: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '24px'
    },
    logo: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '32px'
    },
    logoText: {
        margin: 0,
        fontSize: '20px'
    },
    nav: {
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
    },
    navItem: {
        padding: '12px 16px',
        borderRadius: '8px',
        color: 'white',
        textDecoration: 'none',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        transition: 'background 0.3s',
        cursor: 'pointer'
    },
    main: {
        flex: 1,
        padding: '0'
    },
    header: {
        background: 'white',
        padding: '24px 32px',
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
    },
    title: {
        margin: 0,
        fontSize: '24px',
        color: '#111827'
    },
    userInfo: {
        display: 'flex',
        alignItems: 'center',
        gap: '16px'
    },
    userName: {
        color: '#6b7280',
        fontSize: '14px'
    },
    logoutBtn: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 16px',
        background: '#ef4444',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '14px'
    },
    content: {
        padding: '32px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px'
    },
    card: {
        background: 'white',
        padding: '32px',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    },
    cardTitle: {
        margin: '0 0 24px 0',
        fontSize: '20px',
        color: '#111827',
        fontWeight: '600'
    },
    infoGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '24px'
    },
    infoItem: {
        display: 'flex',
        gap: '16px',
        alignItems: 'start'
    },
    iconWrapper: {
        width: '40px',
        height: '40px',
        background: '#f3f4f6',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    },
    label: {
        fontSize: '12px',
        color: '#6b7280',
        marginBottom: '4px'
    },
    value: {
        fontSize: '16px',
        color: '#111827',
        fontWeight: '500'
    },
    roleBadge: {
        display: 'inline-block',
        padding: '4px 12px',
        background: '#f59e0b',
        color: 'white',
        borderRadius: '12px',
        fontSize: '14px'
    },
    comingSoon: {
        color: '#6b7280',
        fontSize: '14px',
        fontStyle: 'italic',
        marginBottom: '16px'
    },
    settingsGrid: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
    },
    settingItem: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px',
        background: '#f9fafb',
        borderRadius: '8px'
    },
    settingLabel: {
        fontSize: '16px',
        color: '#111827',
        fontWeight: '500',
        marginBottom: '4px'
    },
    settingDesc: {
        fontSize: '14px',
        color: '#6b7280'
    },
    switch: {
        position: 'relative',
        display: 'inline-block',
        width: '50px',
        height: '24px'
    },
    slider: {
        position: 'absolute',
        cursor: 'pointer',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: '#ccc',
        transition: '0.4s',
        borderRadius: '24px'
    }
};

export default AdminSettings;
