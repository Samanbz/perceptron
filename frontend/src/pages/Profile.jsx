import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Profile.css';

function Profile() {
    const { user, logout } = useAuth();
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: user && user.name ? user.name : '',
        email: user && user.email ? user.email : '',
    });
    const [imagePreview, setImagePreview] = useState(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        const savedImage = localStorage.getItem(`profile_picture_${user && user.email ? user.email : ''}`);
        if (savedImage) {
            setImagePreview(savedImage);
        }
    }, [user]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => setImagePreview(reader.result);
            reader.readAsDataURL(file);
        }
    };

    const handleImageClick = () => {
        if (fileInputRef.current) fileInputRef.current.click();
    };

    const handleRemoveImage = () => {
        setImagePreview(null);
        if (user && user.email) {
            localStorage.removeItem(`profile_picture_${user.email}`);
        }
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const handleSave = (e) => {
        e.preventDefault();
        setIsEditing(false);
        // Simulate save
    };

    return (
        <div className="profile-page">
            <div className="profile-container">
                <header className="profile-header">
                    <h1 className="profile-title">Profile Settings</h1>
                    <p className="profile-subtitle">Manage your account information and preferences</p>
                </header>
                <main className="profile-content">
                    <form onSubmit={handleSave} className="profile-form" aria-labelledby="profile-title">
                        <section className="profile-section profile-picture-section" aria-labelledby="picture-heading">
                            <h2 id="picture-heading" className="section-title">Profile Picture</h2>
                            <div className="picture-upload-area">
                                <div
                                    className="picture-container"
                                    onClick={handleImageClick}
                                    role="button"
                                    tabIndex={0}
                                    aria-label="Click to upload profile picture"
                                    style={{ cursor: 'pointer' }}
                                >
                                    {imagePreview ? (
                                        <img src={imagePreview} alt="Profile preview" className="profile-avatar-large" />
                                    ) : (
                                        <div className="profile-avatar-large profile-avatar-placeholder">
                                            {user && user.name ? user.name[0].toUpperCase() : 'U'}
                                        </div>
                                    )}
                                </div>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    id="profile-picture"
                                    accept="image/jpeg,image/png,image/gif,image/webp"
                                    onChange={handleImageChange}
                                    className="file-input"
                                    aria-label="Upload profile picture"
                                    disabled={!isEditing}
                                />
                                {isEditing && (
                                    <button type="button" onClick={handleRemoveImage} className="btn-danger-outline" aria-label="Remove profile picture">
                                        Remove
                                    </button>
                                )}
                            </div>
                        </section>
                        <section className="profile-section" aria-labelledby="info-heading">
                            <h2 id="info-heading" className="section-title">Personal Information</h2>
                            <div className="form-grid">
                                <div className="form-group">
                                    <label htmlFor="name" className="form-label">Full Name</label>
                                    <input
                                        type="text"
                                        id="name"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        disabled={!isEditing}
                                        required
                                        className="form-input"
                                        aria-required="true"
                                    />
                                </div>
                                <div className="form-group">
                                    <label htmlFor="email" className="form-label">Email Address</label>
                                    <input
                                        type="email"
                                        id="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        disabled={!isEditing}
                                        required
                                        className="form-input"
                                        aria-required="true"
                                    />
                                </div>
                            </div>
                        </section>
                        <section className="profile-section" aria-labelledby="actions-heading">
                            <h2 id="actions-heading" className="section-title">Account Actions</h2>
                            <div className="action-buttons">
                                {!isEditing ? (
                                    <button type="button" onClick={() => setIsEditing(true)} className="btn-primary">Edit Profile</button>
                                ) : (
                                    <>
                                        <button type="submit" className="btn-primary">Save Changes</button>
                                        <button type="button" onClick={() => setIsEditing(false)} className="btn-secondary">Cancel</button>
                                    </>
                                )}
                                <button type="button" onClick={logout} className="btn-danger">Log Out</button>
                            </div>
                        </section>
                    </form>
                </main>
            </div>
        </div>
    );
}

export default Profile;


