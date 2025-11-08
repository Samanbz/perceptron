import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import './PaymentSuccess.css';

function PaymentSuccess() {
    const [searchParams] = useSearchParams();
    const [, setSessionInfo] = useState(null);
    const sessionId = searchParams.get('session_id');

    useEffect(() => {
        // Optional: Fetch session details from your backend if needed
        // For now, we'll just show a success message
        if (sessionId) {
            setSessionInfo({ id: sessionId });
        }
    }, [sessionId]);

    return (
        <div className="page payment-success-page">
            <div className="container">
                <div className="success-card">
                    <div className="success-icon">
                        <svg viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg">
                            <circle className="success-circle" cx="26" cy="26" r="25" fill="none" />
                            <path className="success-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
                        </svg>
                    </div>

                    <h1>Payment Successful!</h1>
                    <p className="success-message">
                        Thank you for subscribing to Perceptron Pro. Your account has been upgraded and you now have access to all premium features.
                    </p>

                    {sessionId && (
                        <div className="session-info">
                            <p className="session-id">Order ID: {sessionId.substring(0, 20)}...</p>
                        </div>
                    )}

                    <div className="success-features">
                        <h3>What&apos;s Next?</h3>
                        <ul>
                            <li>
                                <svg className="feature-icon" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                Access AI-powered filtering and advanced analytics
                            </li>
                            <li>
                                <svg className="feature-icon" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                Unlimited team invites and keyword extraction
                            </li>
                            <li>
                                <svg className="feature-icon" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                Priority email support from our team
                            </li>
                        </ul>
                    </div>

                    <div className="success-actions">
                        <Link to="/dashboard" className="btn-primary btn-full">
                            Go to Dashboard
                        </Link>
                        <Link to="/settings" className="btn-secondary btn-full">
                            Manage Subscription
                        </Link>
                    </div>

                    <div className="help-text">
                        <p>
                            Need help? Contact us at{' '}
                            <a href="mailto:support@perceptron.com">support@perceptron.com</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PaymentSuccess;