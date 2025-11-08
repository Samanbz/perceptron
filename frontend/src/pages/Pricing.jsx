import React from 'react';
import { Link } from 'react-router-dom';

function Pricing() {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for getting started with basic filtering',
      features: [
        'Automatic filtering options',
        'Rule-based content filtering',
        'Basic keyword matching',
        'Standard data sources',
        'Community support',
        '7-day data retention',
        'Standard processing speed',
      ],
      cta: 'Get Started Free',
      ctaLink: '/signup',
      highlighted: false,
    },
    {
      name: 'Pro',
      price: '$49',
      period: 'per month',
      description: 'Advanced AI-powered intelligence for professionals',
      features: [
        'Everything in Free, plus:',
        'AI-powered content filtering',
        'Intelligent pattern recognition',
        'Context-aware analysis',
        'Custom AI training',
        'Advanced analytics & insights',
        'Priority support',
        '30-day data retention',
        'Faster processing speed',
        'Team collaboration tools',
        '30-day money-back guarantee',
      ],
      cta: 'Get Started',
      ctaLink: '/signup',
      highlighted: true,
    },
  ];

  const faqs = [
    {
      question: 'What is the difference between automatic and AI filtering?',
      answer: 'Automatic filtering uses predefined rules and keyword matching, while AI filtering uses machine learning to understand context, sentiment, and patterns in your data for more intelligent results.',
    },
    {
      question: 'Can I upgrade from Free to Pro at any time?',
      answer: 'Yes! You can upgrade instantly. Your Pro features activate immediately, and billing is prorated.',
    },
    {
      question: 'Is there a free trial for the Pro plan?',
      answer: 'We offer a 30-day money-back guarantee. Try Pro risk-free and get a full refund if you are not satisfied.',
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards (Visa, MasterCard, American Express) and PayPal.',
    },
    {
      question: 'Can I cancel my subscription?',
      answer: 'Yes, you can cancel anytime. Your subscription remains active until the end of your billing period.',
    },
  ];

  return (
    <div className="page">
      {/* Hero Section */}
      <section className="pricing-hero">
        <div className="container">
          <h1>Simple, Transparent Pricing</h1>
          <p className="pricing-subtitle">
            Choose the perfect plan for your needs. Start free and scale as you grow.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pricing-section">
        <div className="container">
          <div className="pricing-grid">
            {plans.map((plan, index) => (
              <div
                key={index}
                className={`pricing-card ${plan.highlighted ? 'pricing-card-highlighted' : ''}`}
              >
                {plan.highlighted && <div className="pricing-badge">Most Popular</div>}
                
                <div className="pricing-header">
                  <h3>{plan.name}</h3>
                  <div className="pricing-price">
                    <span className="price-amount">{plan.price}</span>
                    <span className="price-period">/{plan.period}</span>
                  </div>
                  <p className="pricing-description">{plan.description}</p>
                </div>

                <ul className="pricing-features">
                  {plan.features.map((feature, idx) => (
                    <li key={idx}>
                      <svg className="check-icon" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>

                <Link
                  to={plan.ctaLink}
                  className={`btn-full ${plan.highlighted ? 'btn-primary' : 'btn-secondary'}`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Comparison */}
      <section className="comparison-section">
        <div className="container">
          <h2>Compare Plans</h2>
          <div className="comparison-table-wrapper">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Feature</th>
                  <th>Free</th>
                  <th>Pro</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Filtering Type</td>
                  <td>Automatic (rule-based)</td>
                  <td>AI-powered</td>
                </tr>
                <tr>
                  <td>Keyword Matching</td>
                  <td>✓</td>
                  <td>✓</td>
                </tr>
                <tr>
                  <td>Pattern Recognition</td>
                  <td>—</td>
                  <td>✓</td>
                </tr>
                <tr>
                  <td>Context Analysis</td>
                  <td>—</td>
                  <td>✓</td>
                </tr>
                <tr>
                  <td>Custom AI Training</td>
                  <td>—</td>
                  <td>✓</td>
                </tr>
                <tr>
                  <td>Data Retention</td>
                  <td>7 days</td>
                  <td>30 days</td>
                </tr>
                <tr>
                  <td>Processing Speed</td>
                  <td>Standard</td>
                  <td>Fast</td>
                </tr>
                <tr>
                  <td>Support</td>
                  <td>Community</td>
                  <td>Priority</td>
                </tr>
                <tr>
                  <td>Team Collaboration</td>
                  <td>—</td>
                  <td>✓</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="faq-section">
        <div className="container">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-grid">
            {faqs.map((faq, index) => (
              <div key={index} className="faq-item">
                <h4>{faq.question}</h4>
                <p>{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="pricing-cta">
        <div className="container">
          <h2>Ready to get started?</h2>
          <p>Start with the Free plan and upgrade when you need AI-powered intelligence.</p>
          <div className="cta-buttons">
            <Link to="/signup" className="btn-primary btn-large">
              Get Started Free
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Pricing;
