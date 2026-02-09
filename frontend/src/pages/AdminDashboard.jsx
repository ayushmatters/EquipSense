import React from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import adminService from '../services/adminService';
import { toast } from '../utils/toast';
import { FaShieldAlt, FaUsers, FaChartLine, FaCog, FaSignOutAlt, FaCheckCircle } from 'react-icons/fa';

const AdminDashboard = () => {
    const navigate = useNavigate();
    const [user, setUser] = React.useState(null);
    const [stats, setStats] = React.useState({
        totalUsers: 0,
        activeSessions: 0,
        systemStatus: 'online',
        totalAdmins: 0,
        verifiedUsers: 0,
        recentRegistrations: 0
    });
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const currentUser = authService.getCurrentUser();
        if (currentUser) {
            setUser(currentUser);
            fetchDashboardStats();
        } else {
            navigate('/auth/login');
        }
    }, [navigate]);

    const fetchDashboardStats = async () => {
        try {
            const response = await adminService.getDashboardStats();
            if (response.success) {
                setStats(response.data);
            }
        } catch (error) {
            console.error('Failed to fetch stats:', error);
            toast.error('Failed to load dashboard statistics');
        } finally {
            setLoading(false);
        }
    };

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

    if (!user || loading) {
        return <div style={styles.loading}>Loading...</div>;
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
                        <FaChartLine /> Dashboard
                    </a>
                    <a href="/admin-dashboard/manage-users" style={styles.navItem}>
                        <FaUsers /> Manage Users
                    </a>
                    <a href="/admin-dashboard/settings" style={styles.navItem}>
                        <FaCog /> Settings
                    </a>
                </nav>
            </div>
            
            <div style={styles.main}>
                <header style={styles.header}>
                    <h1 style={styles.title}>Admin Dashboard</h1>
                    <div style={styles.userInfo}>
                        <span style={styles.userName}>Admin: {user.username}</span>
                        <button onClick={handleLogout} style={styles.logoutBtn}>
                            <FaSignOutAlt /> Logout
                        </button>
                    </div>
                </header>
                
                <div style={styles.content}>
                    <div style={styles.welcomeCard}>
                        <h2>Welcome, {user.first_name || user.username}! 🎉</h2>
                        <p>You have admin access to the EquipSense system.</p>
                        <div style={styles.statsGrid}>
                            <div style={styles.statCard}>
                                <FaUsers size={32} color="#667eea" />
                                <h3>Total Users</h3>
                                <p style={styles.statNumber}>{stats.totalUsers}</p>
                            </div>
                            <div style={styles.statCard}>
                                <FaChartLine size={32} color="#f59e0b" />
                                <h3>Active Sessions</h3>
                                <p style={styles.statNumber}>{stats.activeSessions}</p>
                            </div>
                            <div style={styles.statCard}>
                                <FaCheckCircle size={32} color="#10b981" />
                                <h3>System Status</h3>
                                <p style={{...styles.statNumber, color: '#10b981'}}>✓ {stats.systemStatus}</p>
                            </div>
                            <div style={styles.statCard}>
                                <FaShieldAlt size={32} color="#f59e0b" />
                                <h3>Verified Users</h3>
                                <p style={styles.statNumber}>{stats.verifiedUsers}</p>
                            </div>
                            <div style={styles.statCard}>
                                <h3>Total Admins</h3>
                                <p style={styles.statNumber}>{stats.totalAdmins}</p>
                            </div>
                            <div style={styles.statCard}>
                                <h3>Recent Sign-ups (7d)</h3>
                                <p style={styles.statNumber}>{stats.recentRegistrations}</p>
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
        padding: '32px'
    },
    welcomeCard: {
        background: 'white',
        padding: '32px',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    },
    statsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '24px',
        marginTop: '24px'
    },
    statCard: {
        padding: '24px',
        background: '#f9fafb',
        borderRadius: '8px',
        textAlign: 'center'
    },
    statNumber: {
        fontSize: '32px',
        fontWeight: 'bold',
        color: '#667eea',
        margin: '8px 0 0 0'
    }
};

export default AdminDashboard;
