import React from 'react';

function Cookies() {
  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Cookie Policy</h1>
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
              This Cookie Policy explains how Perceptron uses cookies and similar tracking technologies when you visit our website and use our intelligence platform. This policy should be read together with our Privacy Policy and Terms of Service.
            </p>
          </div>

          <div className="legal-block">
            <h2>2. What Are Cookies?</h2>
            <p>
              Cookies are small text files that are stored on your device (computer, tablet, or mobile) when you visit a website. They are widely used to make websites work more efficiently and provide information to website owners.
            </p>
            <p>Cookies can be:</p>
            <ul>
              <li><strong>Session cookies:</strong> Temporary cookies that expire when you close your browser</li>
              <li><strong>Persistent cookies:</strong> Cookies that remain on your device for a set period or until you delete them</li>
              <li><strong>First-party cookies:</strong> Set by the website you are visiting</li>
              <li><strong>Third-party cookies:</strong> Set by a different domain than the one you are visiting</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>3. How We Use Cookies</h2>
            <p>Perceptron uses cookies for the following purposes:</p>
            
            <h3>3.1 Essential Cookies</h3>
            <p>These cookies are necessary for the website to function properly and cannot be disabled.</p>
            <ul>
              <li>Authentication and security</li>
              <li>Session management</li>
              <li>Load balancing</li>
              <li>User preferences and settings</li>
            </ul>

            <h3>3.2 Performance and Analytics Cookies</h3>
            <p>These cookies help us understand how visitors interact with our platform.</p>
            <ul>
              <li>Page view tracking</li>
              <li>User behavior analysis</li>
              <li>Error tracking and debugging</li>
              <li>Performance monitoring</li>
              <li>A/B testing and optimization</li>
            </ul>

            <h3>3.3 Functionality Cookies</h3>
            <p>These cookies enable enhanced functionality and personalization.</p>
            <ul>
              <li>Language preferences</li>
              <li>Regional settings</li>
              <li>Dashboard customization</li>
              <li>Saved searches and filters</li>
              <li>Theme preferences</li>
            </ul>

            <h3>3.4 Targeting and Advertising Cookies</h3>
            <p>These cookies may be used to show you relevant advertisements.</p>
            <ul>
              <li>Interest-based advertising</li>
              <li>Remarketing campaigns</li>
              <li>Conversion tracking</li>
              <li>Social media integration</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>4. Specific Cookies We Use</h2>
            <p>Below is a list of the main cookies used by Perceptron:</p>
            
            <h3>Essential Cookies</h3>
            <ul>
              <li><strong>session_id:</strong> Maintains your login session (Session cookie)</li>
              <li><strong>csrf_token:</strong> Prevents cross-site request forgery attacks (Session cookie)</li>
              <li><strong>auth_token:</strong> Authenticates API requests (Persistent, 30 days)</li>
            </ul>

            <h3>Analytics Cookies</h3>
            <ul>
              <li><strong>_ga:</strong> Google Analytics - distinguishes users (Persistent, 2 years)</li>
              <li><strong>_gid:</strong> Google Analytics - distinguishes users (Persistent, 24 hours)</li>
              <li><strong>_gat:</strong> Google Analytics - throttles request rate (Persistent, 1 minute)</li>
            </ul>

            <h3>Functionality Cookies</h3>
            <ul>
              <li><strong>user_prefs:</strong> Stores user preferences (Persistent, 1 year)</li>
              <li><strong>dashboard_layout:</strong> Saves dashboard configuration (Persistent, 6 months)</li>
              <li><strong>theme:</strong> Remembers theme selection (Persistent, 1 year)</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>5. Third-Party Cookies</h2>
            <p>
              We may use third-party services that set their own cookies. These services include:
            </p>
            <ul>
              <li><strong>Google Analytics:</strong> Web analytics and reporting</li>
              <li><strong>Content Delivery Networks (CDN):</strong> Faster content delivery</li>
              <li><strong>Social Media Platforms:</strong> Social sharing and authentication</li>
              <li><strong>Payment Processors:</strong> Secure payment processing</li>
            </ul>
            <p>
              These third parties have their own privacy and cookie policies, which we encourage you to review.
            </p>
          </div>

          <div className="legal-block">
            <h2>6. Other Tracking Technologies</h2>
            <p>In addition to cookies, we may use other tracking technologies:</p>
            
            <h3>6.1 Web Beacons (Pixels)</h3>
            <p>
              Small electronic images embedded in web pages or emails to track user behavior and measure campaign effectiveness.
            </p>

            <h3>6.2 Local Storage</h3>
            <p>
              Browser storage mechanisms (localStorage, sessionStorage) used to store data locally on your device for improved performance.
            </p>

            <h3>6.3 Server Logs</h3>
            <p>
              Our servers automatically record information such as IP addresses, browser types, referring pages, and timestamps.
            </p>

            <h3>6.4 Fingerprinting</h3>
            <p>
              We may collect device and browser configuration data to identify unique users for security and fraud prevention purposes.
            </p>
          </div>

          <div className="legal-block">
            <h2>7. Managing Your Cookie Preferences</h2>
            <p>You have several options to control and manage cookies:</p>

            <h3>7.1 Browser Settings</h3>
            <p>
              Most web browsers allow you to control cookies through their settings. You can:
            </p>
            <ul>
              <li>Block all cookies</li>
              <li>Block third-party cookies only</li>
              <li>Clear cookies when you close your browser</li>
              <li>Delete existing cookies</li>
            </ul>

            <h3>7.2 Opt-Out Tools</h3>
            <p>You can opt out of specific tracking services:</p>
            <ul>
              <li><strong>Google Analytics:</strong> <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener noreferrer">Google Analytics Opt-out Browser Add-on</a></li>
              <li><strong>Network Advertising Initiative:</strong> <a href="https://optout.networkadvertising.org/" target="_blank" rel="noopener noreferrer">NAI Opt-out Tool</a></li>
              <li><strong>Digital Advertising Alliance:</strong> <a href="https://optout.aboutads.info/" target="_blank" rel="noopener noreferrer">DAA WebChoices Tool</a></li>
            </ul>

            <h3>7.3 Our Cookie Preference Center</h3>
            <p>
              You can manage your cookie preferences directly on our platform through the Cookie Settings in your account dashboard.
            </p>
          </div>

          <div className="legal-block">
            <h2>8. Impact of Disabling Cookies</h2>
            <p>
              If you choose to disable cookies, some features of our platform may not function properly:
            </p>
            <ul>
              <li>You may not be able to log in or stay logged in</li>
              <li>Your preferences and settings may not be saved</li>
              <li>Some features may be unavailable or work incorrectly</li>
              <li>Page loading times may increase</li>
              <li>You may see less relevant content and advertisements</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>9. Do Not Track Signals</h2>
            <p>
              Some browsers have a Do Not Track (DNT) feature that signals to websites that you do not want your online activity tracked. Currently, there is no industry standard for responding to DNT signals, and our website does not respond to DNT signals at this time.
            </p>
          </div>

          <div className="legal-block">
            <h2>10. Cookies and Mobile Devices</h2>
            <p>
              When you access our platform through a mobile device or app, we may collect similar information through mobile SDKs and device identifiers. You can control mobile tracking through your device settings:
            </p>
            <ul>
              <li><strong>iOS:</strong> Settings → Privacy → Tracking</li>
              <li><strong>Android:</strong> Settings → Google → Ads</li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>11. International Data Transfers</h2>
            <p>
              Cookies may result in data being transferred to servers located outside your country of residence. We ensure appropriate safeguards are in place to protect your information in accordance with applicable data protection laws.
            </p>
          </div>

          <div className="legal-block">
            <h2>12. Children&apos;s Privacy</h2>
            <p>
              Our services are not intended for individuals under the age of 18, and we do not knowingly collect cookies or tracking data from children.
            </p>
          </div>

          <div className="legal-block">
            <h2>13. Changes to This Cookie Policy</h2>
            <p>
              We may update this Cookie Policy from time to time to reflect changes in technology, legislation, or our business practices. We will notify you of material changes by:
            </p>
            <ul>
              <li>Posting the updated policy on our website</li>
              <li>Updating the last modified date</li>
              <li>Sending you an email notification (for significant changes)</li>
            </ul>
            <p>
              Continued use of our platform after changes constitutes acceptance of the updated Cookie Policy.
            </p>
          </div>

          <div className="legal-block">
            <h2>14. More Information</h2>
            <p>For more information about cookies and online privacy, visit:</p>
            <ul>
              <li><a href="https://www.allaboutcookies.org" target="_blank" rel="noopener noreferrer">All About Cookies</a></li>
              <li><a href="https://www.youronlinechoices.com" target="_blank" rel="noopener noreferrer">Your Online Choices</a></li>
              <li><a href="https://ico.org.uk/for-the-public/online/cookies/" target="_blank" rel="noopener noreferrer">ICO - Cookies</a></li>
            </ul>
          </div>

          <div className="legal-block">
            <h2>15. Contact Us</h2>
            <p>If you have questions about our use of cookies or this Cookie Policy, please contact us:</p>
            <ul>
              <li>Email: privacy@perceptron.io</li>
              <li>Subject: Cookie Policy Inquiry</li>
            </ul>
          </div>

          <div className="legal-block legal-acknowledgment">
            <p>
              <strong>By continuing to use our platform, you consent to our use of cookies as described in this Cookie Policy.</strong>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Cookies;
