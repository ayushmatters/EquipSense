import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FaEdit, FaTrash, FaToggleOn, FaToggleOff, FaSearch, FaShieldAlt, FaSignOutAlt } from 'react-icons/fa';
import authService from '../services/authService';
import adminService from '../services/adminService';

const ManageUsers = () => {
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [roleFilter, setRoleFilter] = useState('');
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [showRoleModal, setShowRoleModal] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);
    const [newRole, setNewRole] = useState('');
    const user = authService.getCurrentUser();

    useEffect(() => {
        fetchUsers();
    }, [searchTerm, roleFilter]);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const filters = {};
            if (searchTerm) filters.search = searchTerm;
            if (roleFilter) filters.role = roleFilter;
            
            const response = await adminService.getAllUsers(filters);
            console.log('Users response:', response);
            if (response.success && Array.isArray(response.data)) {
                setUsers(response.data);
            } else if (response.data && Array.isArray(response.data.users)) {
                setUsers(response.data.users);
            } else {
                setUsers([]);
                console.warn('Unexpected response format:', response);
            }
        } catch (error) {
            console.error('Failed to fetch users:', error);
            toast.error('Failed to load users. Please try again.');
            setUsers([]); // Ensure users is always an array
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteUser = async () => {
        if (!selectedUser) return;
        
        try {
            const response = await adminService.deleteUser(selectedUser.id);
            if (response.success) {
                toast.success(`User ${selectedUser.username} deleted successfully`);
                setShowDeleteModal(false);
                setSelectedUser(null);
                fetchUsers();
            }
        } catch (error) {
            console.error('Failed to delete user:', error);
            toast.error(error.response?.data?.error || 'Failed to delete user');
        }
    };

    const handleToggleStatus = async (userId, currentStatus) => {
        try {
            const response = await adminService.toggleUserStatus(userId);
            if (response.success) {
                toast.success(`User ${currentStatus ? 'disabled' : 'enabled'} successfully`);
                fetchUsers();
            }
        } catch (error) {
            console.error('Failed to toggle user status:', error);
            toast.error(error.response?.data?.error || 'Failed to update user status');
        }
    };

    const handleChangeRole = async () => {
        if (!selectedUser || !newRole) return;
        
        try {
            const response = await adminService.changeUserRole(selectedUser.id, newRole);
            if (response.success) {
                toast.success(`User role changed to ${newRole} successfully`);
                setShowRoleModal(false);
                setSelectedUser(null);
                setNewRole('');
                fetchUsers();
            }
        } catch (error) {
            console.error('Failed to change user role:', error);
            toast.error(error.response?.data?.error || 'Failed to change user role');
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

    const openDeleteModal = (user) => {
        setSelectedUser(user);
        setShowDeleteModal(true);
    };

    const openRoleModal = (user) => {
        setSelectedUser(user);
        setNewRole(user.role);
        setShowRoleModal(true);
    };

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
                    <a href="/admin-dashboard/manage-users" style={{...styles.navItem, background: 'rgba(255,255,255,0.2)'}}>
                        Manage Users
                    </a>
                    <a href="/admin-dashboard/settings" style={styles.navItem}>
                        Settings
                    </a>
                </nav>
            </div>
            
            <div style={styles.main}>
                <header style={styles.header}>
                    <h1 style={styles.title}>Manage Users</h1>
                    <div style={styles.userInfo}>
                        <span style={styles.userName}>Admin: {user?.username}</span>
                        <button onClick={handleLogout} style={styles.logoutBtn}>
                            <FaSignOutAlt /> Logout
                        </button>
                    </div>
                </header>
                
                <div style={styles.content}>
                    <div style={styles.filterBar}>
                        <div style={styles.searchBox}>
                            <FaSearch style={styles.searchIcon} />
                            <input
                                type="text"
                                placeholder="Search by username or email..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                style={styles.searchInput}
                            />
                        </div>
                        <select
                            value={roleFilter}
                            onChange={(e) => setRoleFilter(e.target.value)}
                            style={styles.filterSelect}
                        >
                            <option value="">All Roles</option>
                            <option value="user">User</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>

                    {loading ? (
                        <div style={styles.loading}>Loading users...</div>
                    ) : !Array.isArray(users) || users.length === 0 ? (
                        <div style={styles.noData}>No users found</div>
                    ) : (
                        <div style={styles.tableContainer}>
                            <table style={styles.table}>
                                <thead>
                                    <tr style={styles.tableHeader}>
                                        <th style={styles.th}>Username</th>
                                        <th style={styles.th}>Email</th>
                                        <th style={styles.th}>Role</th>
                                        <th style={styles.th}>Status</th>
                                        <th style={styles.th}>Verified</th>
                                        <th style={styles.th}>Joined</th>
                                        <th style={styles.th}>Logins</th>
                                        <th style={styles.th}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {users.map((u) => (
                                        <tr key={u.id} style={styles.tableRow}>
                                            <td style={styles.td}>{u.username}</td>
                                            <td style={styles.td}>{u.email}</td>
                                            <td style={styles.td}>
                                                <span style={{
                                                    ...styles.badge,
                                                    background: u.role === 'admin' ? '#f59e0b' : '#667eea'
                                                }}>
                                                    {u.role}
                                                </span>
                                            </td>
                                            <td style={styles.td}>
                                                <span style={{
                                                    ...styles.badge,
                                                    background: u.is_active ? '#10b981' : '#ef4444'
                                                }}>
                                                    {u.is_active ? 'Active' : 'Disabled'}
                                                </span>
                                            </td>
                                            <td style={styles.td}>
                                                {u.is_verified ? '✓' : '✗'}
                                            </td>
                                            <td style={styles.td}>
                                                {new Date(u.date_joined).toLocaleDateString()}
                                            </td>
                                            <td style={styles.td}>{u.login_count || 0}</td>
                                            <td style={styles.td}>
                                                <div style={styles.actions}>
                                                    <button
                                                        onClick={() => openRoleModal(u)}
                                                        style={styles.actionBtn}
                                                        title="Change Role"
                                                    >
                                                        <FaEdit />
                                                    </button>
                                                    <button
                                                        onClick={() => handleToggleStatus(u.id, u.is_active)}
                                                        style={{...styles.actionBtn, background: u.is_active ? '#f59e0b' : '#10b981'}}
                                                        title={u.is_active ? 'Disable User' : 'Enable User'}
                                                    >
                                                        {u.is_active ? <FaToggleOn /> : <FaToggleOff />}
                                                    </button>
                                                    <button
                                                        onClick={() => openDeleteModal(u)}
                                                        style={{...styles.actionBtn, background: '#ef4444'}}
                                                        title="Delete User"
                                                    >
                                                        <FaTrash />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {/* Delete Confirmation Modal */}
            {showDeleteModal && (
                <div style={styles.modal}>
                    <div style={styles.modalContent}>
                        <h2>Confirm Delete</h2>
                        <p>Are you sure you want to delete user <strong>{selectedUser?.username}</strong>?</p>
                        <p style={{color: '#ef4444', fontSize: '14px'}}>This action cannot be undone.</p>
                        <div style={styles.modalActions}>
                            <button
                                onClick={() => {
                                    setShowDeleteModal(false);
                                    setSelectedUser(null);
                                }}
                                style={styles.cancelBtn}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleDeleteUser}
                                style={styles.deleteBtn}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Change Role Modal */}
            {showRoleModal && (
                <div style={styles.modal}>
                    <div style={styles.modalContent}>
                        <h2>Change User Role</h2>
                        <p>Change role for user <strong>{selectedUser?.username}</strong></p>
                        <select
                            value={newRole}
                            onChange={(e) => setNewRole(e.target.value)}
                            style={styles.modalSelect}
                        >
                            <option value="user">User</option>
                            <option value="admin">Admin</option>
                        </select>
                        <div style={styles.modalActions}>
                            <button
                                onClick={() => {
                                    setShowRoleModal(false);
                                    setSelectedUser(null);
                                    setNewRole('');
                                }}
                                style={styles.cancelBtn}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleChangeRole}
                                style={styles.confirmBtn}
                            >
                                Change Role
                            </button>
                        </div>
                    </div>
                </div>
            )}
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
    filterBar: {
        display: 'flex',
        gap: '16px',
        marginBottom: '24px',
        background: 'white',
        padding: '16px',
        borderRadius: '8px'
    },
    searchBox: {
        flex: 1,
        position: 'relative'
    },
    searchIcon: {
        position: 'absolute',
        left: '12px',
        top: '50%',
        transform: 'translateY(-50%)',
        color: '#9ca3af'
    },
    searchInput: {
        width: '100%',
        padding: '10px 12px 10px 40px',
        border: '1px solid #d1d5db',
        borderRadius: '6px',
        fontSize: '14px'
    },
    filterSelect: {
        padding: '10px 16px',
        border: '1px solid #d1d5db',
        borderRadius: '6px',
        fontSize: '14px',
        cursor: 'pointer'
    },
    tableContainer: {
        background: 'white',
        borderRadius: '8px',
        overflow: 'hidden',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    },
    table: {
        width: '100%',
        borderCollapse: 'collapse'
    },
    tableHeader: {
        background: '#f9fafb',
        borderBottom: '1px solid #e5e7eb'
    },
    th: {
        padding: '12px 16px',
        textAlign: 'left',
        fontSize: '12px',
        fontWeight: '600',
        color: '#6b7280',
        textTransform: 'uppercase'
    },
    tableRow: {
        borderBottom: '1px solid #e5e7eb',
        transition: 'background 0.2s'
    },
    td: {
        padding: '12px 16px',
        fontSize: '14px',
        color: '#111827'
    },
    badge: {
        display: 'inline-block',
        padding: '4px 12px',
        borderRadius: '12px',
        color: 'white',
        fontSize: '12px',
        fontWeight: '500'
    },
    actions: {
        display: 'flex',
        gap: '8px'
    },
    actionBtn: {
        padding: '6px 10px',
        background: '#667eea',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'opacity 0.2s'
    },
    loading: {
        textAlign: 'center',
        padding: '40px',
        color: '#6b7280',
        fontSize: '16px'
    },
    noData: {
        textAlign: 'center',
        padding: '40px',
        color: '#6b7280',
        fontSize: '16px',
        background: 'white',
        borderRadius: '8px'
    },
    modal: {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
    },
    modalContent: {
        background: 'white',
        padding: '32px',
        borderRadius: '12px',
        minWidth: '400px',
        maxWidth: '500px'
    },
    modalSelect: {
        width: '100%',
        padding: '10px 12px',
        border: '1px solid #d1d5db',
        borderRadius: '6px',
        fontSize: '14px',
        marginTop: '16px',
        marginBottom: '24px'
    },
    modalActions: {
        display: 'flex',
        justifyContent: 'flex-end',
        gap: '12px',
        marginTop: '24px'
    },
    cancelBtn: {
        padding: '10px 20px',
        background: '#e5e7eb',
        color: '#374151',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '14px'
    },
    deleteBtn: {
        padding: '10px 20px',
        background: '#ef4444',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '14px'
    },
    confirmBtn: {
        padding: '10px 20px',
        background: '#667eea',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '14px'
    }
};

export default ManageUsers;
