# Stripe Payment Integration - Setup Guide

## Overview
Perceptron now has complete Stripe payment integration for the Pro plan ($49/month). The backend and frontend are fully implemented and ready to use.

## Current Status ✅
- ✅ Backend payment routes created (`backend/payment_routes.py`)
- ✅ Stripe library installed (v13.2.0)
- ✅ Frontend payment flow implemented
- ✅ Payment success/cancel pages created
- ✅ Environment variables configured (placeholders)

## What's Implemented

### Backend Endpoints
```
POST /api/payments/create-checkout-session  - Create Stripe Checkout
POST /api/payments/create-portal-session    - Customer portal access
POST /api/payments/webhook                  - Handle Stripe events
GET  /api/payments/subscription/{id}        - Get subscription details
POST /api/payments/cancel-subscription/{id} - Cancel subscription
GET  /api/payments/config                   - Get publishable key
```

### Frontend Features
- **Pricing Page**: Pro plan button triggers Stripe Checkout
- **Payment Success**: Beautiful success page with order confirmation
- **Payment Cancel**: Cancel page with retry options
- **Loading States**: Button shows "Loading..." during redirect

## Setup Instructions

### Step 1: Get Stripe API Keys
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Sign up or log in
3. Switch to **Test Mode** (toggle in top right)
4. Go to **Developers → API Keys**
5. Copy your keys:
   - **Publishable key**: `pk_test_...`
   - **Secret key**: `sk_test_...` (click "Reveal test key")

### Step 2: Configure Environment Variables
Update `backend/.env` with your actual Stripe keys:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_YOUR_ACTUAL_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_ACTUAL_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
STRIPE_PRO_PRICE_ID=price_1SR36SD6KhY1qnt2DZe7ERlZ
```

### Step 3: Configure Stripe Webhook (For Production)
1. In Stripe Dashboard, go to **Developers → Webhooks**
2. Click **Add endpoint**
3. Set endpoint URL: `https://your-domain.com/api/payments/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the **Signing secret** (starts with `whsec_`)
6. Update `STRIPE_WEBHOOK_SECRET` in `.env`

### Step 4: Verify Price ID
The price ID `price_1SR36SD6KhY1qnt2DZe7ERlZ` is already configured. To verify or create a new price:

1. Go to **Products** in Stripe Dashboard
2. Find your "Perceptron Pro" product or create one
3. Set price: $49/month (recurring)
4. Copy the Price ID (starts with `price_`)
5. Update `STRIPE_PRO_PRICE_ID` in `.env` if needed

## Testing the Payment Flow

### Step 1: Start the Backend
```bash
cd backend
python app.py
```

### Step 2: Start the Frontend
```bash
cd frontend
npm run dev
```

### Step 3: Test with Test Cards
1. Navigate to `http://localhost:5173/pricing`
2. Click **"Get Started"** on the Pro plan
3. Use Stripe test cards:
   - **Success**: `4242 4242 4242 4242`
   - **Decline**: `4000 0000 0000 0002`
   - **Requires authentication**: `4000 0025 0000 3155`
4. Use any future date for expiry, any 3-digit CVC, any ZIP code
5. Verify redirect to success page

## Payment Flow Diagram

```
User clicks "Get Started" (Pro plan)
    ↓
Frontend calls /api/payments/create-checkout-session
    ↓
Backend creates Stripe Checkout session
    ↓
User redirected to Stripe Checkout page
    ↓
User enters payment details
    ↓
[Success] → Redirect to /payment-success
[Cancel]  → Redirect to /pricing
    ↓
Stripe webhook notifies backend (checkout.session.completed)
    ↓
Backend updates user subscription status
```

## Important Notes

### Security
- ✅ Never commit real API keys to Git
- ✅ Use environment variables for all secrets
- ✅ Webhook signatures are verified server-side
- ✅ Price ID is server-side controlled

### Webhook Handling
The webhook endpoint in `payment_routes.py` has TODO comments for database integration:

```python
# TODO: Update user's subscription status in database
# TODO: Activate Pro features for the user
# TODO: Send confirmation email
```

You'll need to implement these to:
1. Store subscription data in your database
2. Update user permissions/features
3. Send email notifications

### Customer Portal
Users can manage their subscription via the customer portal:
- Update payment method
- View invoices
- Cancel subscription
- Update billing information

To enable, call `/api/payments/create-portal-session` from your settings page.

## Production Checklist

Before going live:
- [ ] Replace test keys with **live keys** (remove `_test_` from keys)
- [ ] Configure production webhook endpoint
- [ ] Implement database updates in webhook handler
- [ ] Add email notifications
- [ ] Test all payment scenarios
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure CORS for your production domain
- [ ] Update success/cancel URLs to production domain
- [ ] Review Stripe Dashboard settings (tax, invoicing, etc.)

## Troubleshooting

### Issue: "Invalid API Key"
- Check that you copied the correct key from Stripe Dashboard
- Ensure no extra spaces in `.env` file
- Restart the backend server after updating `.env`

### Issue: Webhook Not Receiving Events
- Verify webhook endpoint URL is correct
- Check that webhook secret matches Stripe Dashboard
- Use Stripe CLI for local testing: `stripe listen --forward-to localhost:8000/api/payments/webhook`

### Issue: Checkout Session Creation Fails
- Check backend logs for Stripe API errors
- Verify price ID exists in Stripe Dashboard
- Ensure backend is running and accessible

## Next Steps

1. **Add to Settings Page**: Implement customer portal link
2. **Database Integration**: Store subscription data
3. **Email Notifications**: Confirm subscriptions, renewals, cancellations
4. **Feature Gating**: Enable/disable features based on subscription status
5. **Analytics**: Track conversion rates, churn, MRR

## Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Testing](https://stripe.com/docs/testing)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)

---

**Ready to accept payments!** 🎉

Replace the placeholder keys with your actual Stripe test keys and you're ready to start testing the payment flow.
