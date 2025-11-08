"""
Stripe payment integration for Perceptron.

Handles subscription creation, checkout sessions, and webhooks.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import stripe
import os
from typing import Optional

# Load Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "price_1SR36SD6KhY1qnt2DZe7ERlZ")

router = APIRouter(prefix="/api/payments", tags=["payments"])


class CheckoutSessionRequest(BaseModel):
    """Request model for creating a checkout session."""
    price_id: str
    success_url: str
    cancel_url: str
    customer_email: Optional[str] = None
    user_id: Optional[str] = None


class CheckoutSessionResponse(BaseModel):
    """Response model for checkout session."""
    session_id: str
    url: str


class PortalSessionRequest(BaseModel):
    """Request model for creating a customer portal session."""
    customer_id: str
    return_url: str


class PortalSessionResponse(BaseModel):
    """Response model for customer portal session."""
    url: str


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(request: CheckoutSessionRequest):
    """
    Create a Stripe Checkout session for subscription payment.
    
    This endpoint creates a checkout session that redirects the user
    to Stripe's hosted payment page.
    """
    try:
        # Create checkout session parameters
        params = {
            "mode": "subscription",
            "line_items": [
                {
                    "price": request.price_id,
                    "quantity": 1,
                }
            ],
            "success_url": request.success_url,
            "cancel_url": request.cancel_url,
            "billing_address_collection": "auto",
            "allow_promotion_codes": True,
        }
        
        # Add customer email if provided
        if request.customer_email:
            params["customer_email"] = request.customer_email
        
        # Add metadata for tracking
        if request.user_id:
            params["metadata"] = {
                "user_id": request.user_id
            }
        
        # Create the session
        session = stripe.checkout.Session.create(**params)
        
        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/create-portal-session", response_model=PortalSessionResponse)
async def create_portal_session(request: PortalSessionRequest):
    """
    Create a Stripe Customer Portal session.
    
    This allows customers to manage their subscription, update payment methods,
    view invoices, and cancel their subscription.
    """
    try:
        session = stripe.billing_portal.Session.create(
            customer=request.customer_id,
            return_url=request.return_url,
        )
        
        return PortalSessionResponse(url=session.url)
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create portal session: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    
    This endpoint receives events from Stripe about subscription changes,
    payments, cancellations, etc.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]
    
    print(f"Received Stripe webhook: {event_type}")
    
    if event_type == "checkout.session.completed":
        # Payment successful
        session = data
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        user_id = session.get("metadata", {}).get("user_id")
        
        print(f"Checkout completed for customer {customer_id}")
        print(f"Subscription ID: {subscription_id}")
        print(f"User ID: {user_id}")
        
        # TODO: Update user's subscription status in your database
        # await update_user_subscription(user_id, subscription_id, customer_id, "active")
        
    elif event_type == "customer.subscription.updated":
        # Subscription updated
        subscription = data
        customer_id = subscription.get("customer")
        status = subscription.get("status")
        
        print(f"Subscription updated for customer {customer_id}: {status}")
        
        # TODO: Update subscription status in database
        # await update_subscription_status(customer_id, status)
        
    elif event_type == "customer.subscription.deleted":
        # Subscription cancelled
        subscription = data
        customer_id = subscription.get("customer")
        
        print(f"Subscription cancelled for customer {customer_id}")
        
        # TODO: Update user's subscription status to cancelled
        # await update_user_subscription_status(customer_id, "cancelled")
        
    elif event_type == "invoice.payment_failed":
        # Payment failed
        invoice = data
        customer_id = invoice.get("customer")
        
        print(f"Payment failed for customer {customer_id}")
        
        # TODO: Handle failed payment (send email, update status, etc.)
        # await handle_failed_payment(customer_id)
        
    elif event_type == "invoice.payment_succeeded":
        # Payment succeeded
        invoice = data
        customer_id = invoice.get("customer")
        
        print(f"Payment succeeded for customer {customer_id}")
        
        # TODO: Extend subscription, send receipt email
        # await handle_successful_payment(customer_id, invoice)
    
    return {"status": "success"}


@router.get("/subscription/{subscription_id}")
async def get_subscription(subscription_id: str):
    """
    Get subscription details from Stripe.
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        return {
            "id": subscription.id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "plan": {
                "amount": subscription.plan.amount / 100,  # Convert cents to dollars
                "currency": subscription.plan.currency,
                "interval": subscription.plan.interval,
            }
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription not found: {str(e)}"
        )


@router.post("/cancel-subscription/{subscription_id}")
async def cancel_subscription(subscription_id: str):
    """
    Cancel a subscription at the end of the current billing period.
    """
    try:
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        
        return {
            "status": "success",
            "message": "Subscription will be cancelled at the end of the billing period",
            "cancel_at": subscription.current_period_end
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/config")
async def get_stripe_config():
    """
    Get Stripe publishable key for frontend.
    """
    publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
    
    if not publishable_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe publishable key not configured"
        )
    
    return {
        "publishable_key": publishable_key,
        "pro_price_id": STRIPE_PRO_PRICE_ID
    }
