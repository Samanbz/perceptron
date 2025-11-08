import React from 'react';
import { Link } from 'react-router-dom';
import './PaymentCancel.css';

function PaymentCancel() {
    return (
        <div className="page payment-cancel-page">
            <div className="container">
                <div className="cancel-card">
                    <div className="cancel-icon">
                        <svg viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg">
                            <circle className="cancel-circle" cx="26" cy="26" r="25" fill="none" />
                            <line className="cancel-line1" x1="16" y1="16" x2="36" y2="36" />
                            <line className="cancel-line2" x1="36" y1="16" x2="16" y2="36" />
                        </svg>
                    </div>

                    <h1>Payment Cancelled</h1>
                    <p className="cancel-message">
                        Your payment was cancelled. No charges have been made to your account.
                    </p>

                    <div className="cancel-info">
                        <h3>What happened?</h3>
                        <p>
                            You can return to the pricing page to try again, or explore our free plan features first.
                        </p>
                    </div>

                    <div className="cancel-reasons">
                        <h3>Common reasons for cancellation:</h3>
                        <ul>
                            <li>Changed your mind about upgrading</li>
                            <li>Want to explore free features first</li>
                            <li>Need to check with your team</li>
                            <li>Technical issues with payment</li>
                        </ul>
                    </div>

                    <div className="cancel-actions">
                        <Link to="/pricing" className="btn-primary btn-full">
                            Back to Pricing
                        </Link>
                        <Link to="/dashboard" className="btn-secondary btn-full">
                            Go to Dashboard
                        </Link>
                    </div>

                    <div className="help-text">
                        <p>
                            Have questions? Contact us at{' '}
                            <a href="mailto:support@perceptron.com">support@perceptron.com</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PaymentCancel;