import React from 'react';

/* eslint-disable react/no-unescaped-entities */

function Privacy() {
  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Privacy Policy</h1>
          <p className="page-subtitle">
            Last updated: November 7, 2025
          </p>
        </div>
      </section>

      <section className="section legal-section">
        <div className="legal-content">
          <div className="legal-block">
            <h2>1. Introduction</h2>
            <p>
              Welcome to Perceptron ("we," "our," or "us"). We are committed to protecting your personal information and your right to privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our intelligence platform and related services.
            </p>
          </div>

          <div className="legal-block">
            <h2>2. Information We Collect</h2>
            <h3>2.1 Personal Information</h3>
            <p>We collect personal information that you voluntarily provide to us when you:</p>
            <ul>
              <li>Register for an account</li>
              <li>Use our services</li>
              <li>Contact our support team</li>
              <li>Subscribe to our newsletter</li>
            </ul>
            <p>This information may include:</p>
            <ul>
              <li>Name and email address</li>
              <li>Company name and job title</li>
              <li>Billing and payment information</li>
              <li>Communication preferences</li>
            </ul>

            <h3>2.2 Automatically Collected Information</h3>
            <p>When you access our platform, we automatically collect certain information, including:</p>
            <ul>
              <li>IP address and device information</li>
              <li>Browser type and version</li>
              <li>Usage data and analytics</li>
              <li>Cookies and similar tracking technologies</li>
            </ul>

            <h3>2.3 Intelligence Data</h3>
            <p>Our platform processes and analyzes data from various sources. We collect:</p>
            <ul>
              <li>Content aggregated from configured data sources</li>
              <li>Keywords and signals extracted by our NLP algorithms</li>
              <li>Team configurations and preferences</li>
              <li>Custom source integrations</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>3. How We Use Your Information</h2>
            <p>We use the collected information for the following purposes:</p>
            <ul>
              <li><strong>Service Delivery:</strong> To provide, operate, and maintain our intelligence platform</li>
              <li><strong>Account Management:</strong> To manage your account and provide customer support</li>
              <li><strong>Communication:</strong> To send you updates, security alerts, and administrative messages</li>
              <li><strong>Improvement:</strong> To analyze usage patterns and improve our services</li>
              <li><strong>Security:</strong> To detect, prevent, and address technical issues and security threats</li>
              <li><strong>Compliance:</strong> To comply with legal obligations and enforce our terms</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>4. Data Processing and NLP</h2>
            <p>
              Perceptron uses advanced natural language processing (NLP) and machine learning algorithms to analyze content. Our processing includes:
            </p>
            <ul>
              <li>Keyword extraction using TF-IDF, spaCy, and YAKE</li>
              <li>Sentiment analysis using VADER algorithm</li>
              <li>Content deduplication and normalization</li>
              <li>Real-time signal detection and classification</li>
            </ul>
            <p>
              All data processing is performed in accordance with this Privacy Policy and applicable data protection laws.
            </p>
          </div>

          <div className="legal-block">
            <h2>5. Data Sharing and Disclosure</h2>
            <p>We do not sell your personal information. We may share your information in the following circumstances:</p>
            <ul>
              <li><strong>Service Providers:</strong> With third-party vendors who perform services on our behalf</li>
              <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
              <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
              <li><strong>With Your Consent:</strong> When you explicitly authorize us to share information</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>6. Data Security</h2>
            <p>
              We implement appropriate technical and organizational security measures to protect your information, including:
            </p>
            <ul>
              <li>Encryption of data in transit and at rest</li>
              <li>Regular security assessments and audits</li>
              <li>Access controls and authentication mechanisms</li>
              <li>Employee training on data protection</li>
            </ul>
            <p>
              However, no method of transmission over the internet is 100% secure, and we cannot guarantee absolute security.
            </p>
          </div>

          <div className="legal-block">
            <h2>7. Data Retention</h2>
            <p>
              We retain your personal information for as long as necessary to fulfill the purposes outlined in this Privacy Policy, unless a longer retention period is required by law. Intelligence data and processed signals are retained according to your subscription plan and configuration settings.
            </p>
          </div>

          <div className="legal-block">
            <h2>8. Your Privacy Rights</h2>
            <p>Depending on your location, you may have the following rights:</p>
            <ul>
              <li><strong>Access:</strong> Request access to your personal information</li>
              <li><strong>Correction:</strong> Request correction of inaccurate data</li>
              <li><strong>Deletion:</strong> Request deletion of your personal information</li>
              <li><strong>Portability:</strong> Request transfer of your data to another service</li>
              <li><strong>Objection:</strong> Object to processing of your personal information</li>
              <li><strong>Withdrawal:</strong> Withdraw consent at any time</li>
            </ul>
            <p>To exercise these rights, please contact us at privacy@perceptron.io</p>
          </div>

          <div className="legal-block">
            <h2>9. Cookies and Tracking</h2>
            <p>
              We use cookies and similar tracking technologies to enhance your experience. You can control cookies through your browser settings. However, disabling cookies may affect the functionality of our platform.
            </p>
          </div>

          <div className="legal-block">
            <h2>10. International Data Transfers</h2>
            <p>
              Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place to protect your information in accordance with this Privacy Policy.
            </p>
          </div>

          <div className="legal-block">
            <h2>11. Children's Privacy</h2>
            <p>
              Our services are not intended for individuals under the age of 18. We do not knowingly collect personal information from children. If you believe we have collected information from a child, please contact us immediately.
            </p>
          </div>

          <div className="legal-block">
            <h2>12. Changes to This Privacy Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new Privacy Policy on this page and updating the "Last updated" date. Your continued use of our services after such changes constitutes acceptance of the updated policy.
            </p>
          </div>

          <div className="legal-block">
            <h2>13. Contact Us</h2>
            <p>If you have any questions about this Privacy Policy or our privacy practices, please contact us:</p>
            <ul>
              <li>Email: privacy@perceptron.io</li>
              <li>Address: Perceptron Privacy Team</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Privacy;
