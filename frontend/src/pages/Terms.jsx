import React from 'react';

/* eslint-disable react/no-unescaped-entities */

function Terms() {
  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Terms of Service</h1>
          <p className="page-subtitle">
            Last updated: November 7, 2025
          </p>
        </div>
      </section>

      <section className="section legal-section">
        <div className="legal-content">
          <div className="legal-block">
            <h2>1. Agreement to Terms</h2>
            <p>
              By accessing or using Perceptron ("Service," "Platform," or "we"), you agree to be bound by these Terms of Service ("Terms"). If you disagree with any part of these terms, you may not access the Service.
            </p>
          </div>

          <div className="legal-block">
            <h2>2. Description of Service</h2>
            <p>
              Perceptron is a Software as a Service (SaaS) platform that provides AI-powered signal intelligence through:
            </p>
            <ul>
              <li>Multi-source data aggregation from RSS feeds, APIs, and custom integrations</li>
              <li>Natural language processing using spaCy, scikit-learn, and YAKE</li>
              <li>Real-time keyword extraction and sentiment analysis</li>
              <li>Specialized intelligence teams for different market sectors</li>
              <li>Interactive visualizations and analytics dashboards</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>3. Account Registration</h2>
            <h3>3.1 Eligibility</h3>
            <p>
              You must be at least 18 years old and capable of forming a binding contract to use this Service. By creating an account, you represent that you meet these requirements.
            </p>

            <h3>3.2 Account Security</h3>
            <p>You are responsible for:</p>
            <ul>
              <li>Maintaining the confidentiality of your account credentials</li>
              <li>All activities that occur under your account</li>
              <li>Notifying us immediately of any unauthorized access</li>
              <li>Ensuring your account information is accurate and current</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>4. Subscription Plans and Billing</h2>
            <h3>4.1 Subscription Tiers</h3>
            <p>Perceptron offers various subscription plans with different features and usage limits. Current pricing and plan details are available on our website.</p>

            <h3>4.2 Payment Terms</h3>
            <ul>
              <li>Subscriptions are billed on a recurring basis (monthly or annually)</li>
              <li>Payment is due at the beginning of each billing cycle</li>
              <li>All fees are non-refundable except as required by law</li>
              <li>We reserve the right to change pricing with 30 days notice</li>
            </ul>

            <h3>4.3 Free Trials</h3>
            <p>
              Free trial periods may be offered. At the end of the trial, you will be charged unless you cancel before the trial expires.
            </p>

            <h3>4.4 Cancellation</h3>
            <p>
              You may cancel your subscription at any time. Cancellation takes effect at the end of the current billing period. You will retain access to the Service until that date.
            </p>
          </div>

          <div className="legal-block">
            <h2>5. Acceptable Use Policy</h2>
            <p>You agree not to use the Service to:</p>
            <ul>
              <li>Violate any applicable laws or regulations</li>
              <li>Infringe on intellectual property rights of others</li>
              <li>Transmit malware, viruses, or harmful code</li>
              <li>Attempt to gain unauthorized access to our systems</li>
              <li>Interfere with or disrupt the Service</li>
              <li>Use the Service for competitive analysis against Perceptron</li>
              <li>Resell or redistribute the Service without authorization</li>
              <li>Scrape or extract data using automated means beyond API limits</li>
              <li>Impersonate others or misrepresent your affiliation</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>6. Intellectual Property Rights</h2>
            <h3>6.1 Our Property</h3>
            <p>
              The Service, including all software, algorithms, designs, text, graphics, and other content, is owned by Perceptron and protected by intellectual property laws. You may not copy, modify, or reverse engineer any part of the Service.
            </p>

            <h3>6.2 Your Data</h3>
            <p>
              You retain all rights to the data you input into the Service. By using the Service, you grant us a license to process, analyze, and store your data solely for the purpose of providing the Service.
            </p>

            <h3>6.3 Aggregated Data</h3>
            <p>
              We may use anonymized and aggregated data derived from your use of the Service for analytics, research, and service improvement purposes.
            </p>
          </div>

          <div className="legal-block">
            <h2>7. Data Processing and Sources</h2>
            <h3>7.1 Source Configuration</h3>
            <p>
              You are responsible for ensuring you have the right to access and process data from the sources you configure in Perceptron.
            </p>

            <h3>7.2 Third-Party Data</h3>
            <p>
              The Service aggregates data from third-party sources. We do not guarantee the accuracy, completeness, or reliability of third-party content.
            </p>

            <h3>7.3 NLP Processing</h3>
            <p>
              Our NLP algorithms provide automated analysis. Results should be reviewed and verified before making business decisions.
            </p>
          </div>

          <div className="legal-block">
            <h2>8. Service Level and Availability</h2>
            <h3>8.1 Uptime</h3>
            <p>
              We strive to maintain 99.9% uptime but do not guarantee uninterrupted access. Scheduled maintenance will be announced in advance when possible.
            </p>

            <h3>8.2 Support</h3>
            <p>
              Support is provided according to your subscription plan. Response times and support channels vary by plan tier.
            </p>

            <h3>8.3 Service Modifications</h3>
            <p>
              We reserve the right to modify, suspend, or discontinue any aspect of the Service with reasonable notice.
            </p>
          </div>

          <div className="legal-block">
            <h2>9. API Usage and Limits</h2>
            <p>If you use our API, you agree to:</p>
            <ul>
              <li>Comply with rate limits specified in your subscription plan</li>
              <li>Use API keys securely and not share them</li>
              <li>Not abuse or overload our infrastructure</li>
              <li>Properly attribute data sourced from our API</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>10. Confidentiality</h2>
            <p>
              Both parties agree to keep confidential any non-public information disclosed during the use of the Service. This obligation survives termination of these Terms.
            </p>
          </div>

          <div className="legal-block">
            <h2>11. Disclaimers and Limitations of Liability</h2>
            <h3>11.1 No Warranties</h3>
            <p>
              THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
            </p>

            <h3>11.2 Limitation of Liability</h3>
            <p>
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, PERCEPTRON SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES.
            </p>

            <h3>11.3 Maximum Liability</h3>
            <p>
              Our total liability for any claims arising from these Terms or the Service shall not exceed the amount you paid us in the 12 months preceding the claim.
            </p>
          </div>

          <div className="legal-block">
            <h2>12. Indemnification</h2>
            <p>
              You agree to indemnify and hold harmless Perceptron from any claims, damages, losses, liabilities, and expenses arising from: (a) your use of the Service; (b) your violation of these Terms; or (c) your violation of any rights of another party.
            </p>
          </div>

          <div className="legal-block">
            <h2>13. Termination</h2>
            <h3>13.1 By You</h3>
            <p>
              You may terminate your account at any time through your account settings or by contacting support.
            </p>

            <h3>13.2 By Us</h3>
            <p>
              We may suspend or terminate your access to the Service if you violate these Terms, fail to pay fees, or for any other reason with or without notice.
            </p>

            <h3>13.3 Effect of Termination</h3>
            <p>
              Upon termination, your right to use the Service ceases immediately. We may delete your data according to our data retention policy. Provisions that should survive termination will remain in effect.
            </p>
          </div>

          <div className="legal-block">
            <h2>14. Dispute Resolution</h2>
            <h3>14.1 Informal Resolution</h3>
            <p>
              Before filing a claim, you agree to contact us to attempt to resolve the dispute informally.
            </p>

            <h3>14.2 Arbitration</h3>
            <p>
              Any dispute arising from these Terms shall be resolved through binding arbitration rather than in court, except you may assert claims in small claims court if they qualify.
            </p>

            <h3>14.3 Class Action Waiver</h3>
            <p>
              You agree that disputes will be resolved on an individual basis and waive the right to participate in class actions or class arbitrations.
            </p>
          </div>

          <div className="legal-block">
            <h2>15. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of the jurisdiction where Perceptron is headquartered, without regard to conflict of law provisions.
            </p>
          </div>

          <div className="legal-block">
            <h2>16. Changes to Terms</h2>
            <p>
              We may modify these Terms at any time. Material changes will be notified via email or through the Service. Continued use of the Service after changes constitutes acceptance of the modified Terms.
            </p>
          </div>

          <div className="legal-block">
            <h2>17. General Provisions</h2>
            <h3>17.1 Entire Agreement</h3>
            <p>
              These Terms constitute the entire agreement between you and Perceptron regarding the Service.
            </p>

            <h3>17.2 Severability</h3>
            <p>
              If any provision is found to be unenforceable, the remaining provisions will remain in full effect.
            </p>

            <h3>17.3 Waiver</h3>
            <p>
              Our failure to enforce any right or provision shall not constitute a waiver of such right or provision.
            </p>

            <h3>17.4 Assignment</h3>
            <p>
              You may not assign these Terms without our written consent. We may assign these Terms without restriction.
            </p>
          </div>

          <div className="legal-block">
            <h2>18. Contact Information</h2>
            <p>For questions about these Terms of Service, please contact us:</p>
            <ul>
              <li>Email: legal@perceptron.io</li>
              <li>Address: Perceptron Legal Team</li>
            </ul>
          </div>

          <div className="legal-block legal-acknowledgment">
            <p>
              <strong>By using Perceptron, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.</strong>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Terms;
