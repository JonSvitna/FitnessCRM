"""
Stripe payment processing utilities
Phase 6: Mobile & Integrations - M6.3: Payment Integration
"""

import os
import stripe
from flask import current_app
from utils.logger import logger

# Initialize Stripe (lazy loading to handle missing key gracefully)
_stripe_client = None

def get_stripe_client():
    """Get or initialize Stripe client"""
    global _stripe_client
    
    if _stripe_client is None:
        stripe_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe_key:
            logger.warning("Stripe secret key not configured. Payment processing will be disabled.")
            return None
        
        try:
            stripe.api_key = stripe_key
            _stripe_client = stripe
            logger.info("Stripe client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Stripe client: {str(e)}")
            return None
    
    return _stripe_client

def create_payment_intent(amount, currency='usd', metadata=None, customer_id=None):
    """
    Create a Stripe PaymentIntent
    
    Args:
        amount: Amount in cents (e.g., 1000 for $10.00)
        currency: Currency code (default: 'usd')
        metadata: Additional metadata to attach
        customer_id: Stripe customer ID (optional)
    
    Returns:
        PaymentIntent object or None if Stripe is not configured
    """
    stripe_client = get_stripe_client()
    if not stripe_client:
        return None
    
    try:
        intent_params = {
            'amount': int(amount * 100),  # Convert to cents
            'currency': currency,
            'automatic_payment_methods': {
                'enabled': True,
            },
        }
        
        if customer_id:
            intent_params['customer'] = customer_id
        
        if metadata:
            intent_params['metadata'] = metadata
        
        intent = stripe_client.PaymentIntent.create(**intent_params)
        logger.info(f"PaymentIntent created: {intent.id}")
        return intent
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating PaymentIntent: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating PaymentIntent: {str(e)}")
        raise

def create_customer(email, name=None, phone=None, metadata=None):
    """
    Create a Stripe customer
    
    Args:
        email: Customer email
        name: Customer name (optional)
        phone: Customer phone (optional)
        metadata: Additional metadata (optional)
    
    Returns:
        Customer object or None if Stripe is not configured
    """
    stripe_client = get_stripe_client()
    if not stripe_client:
        return None
    
    try:
        customer_params = {
            'email': email,
        }
        
        if name:
            customer_params['name'] = name
        
        if phone:
            customer_params['phone'] = phone
        
        if metadata:
            customer_params['metadata'] = metadata
        
        customer = stripe_client.Customer.create(**customer_params)
        logger.info(f"Stripe customer created: {customer.id}")
        return customer
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating customer: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating customer: {str(e)}")
        raise

def create_subscription(customer_id, price_id, metadata=None):
    """
    Create a Stripe subscription
    
    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID
        metadata: Additional metadata (optional)
    
    Returns:
        Subscription object or None if Stripe is not configured
    """
    stripe_client = get_stripe_client()
    if not stripe_client:
        return None
    
    try:
        subscription_params = {
            'customer': customer_id,
            'items': [{'price': price_id}],
        }
        
        if metadata:
            subscription_params['metadata'] = metadata
        
        subscription = stripe_client.Subscription.create(**subscription_params)
        logger.info(f"Stripe subscription created: {subscription.id}")
        return subscription
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating subscription: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating subscription: {str(e)}")
        raise

def cancel_subscription(subscription_id, cancel_immediately=False):
    """
    Cancel a Stripe subscription
    
    Args:
        subscription_id: Stripe subscription ID
        cancel_immediately: If True, cancel immediately; if False, cancel at period end
    
    Returns:
        Subscription object or None if Stripe is not configured
    """
    stripe_client = get_stripe_client()
    if not stripe_client:
        return None
    
    try:
        if cancel_immediately:
            subscription = stripe_client.Subscription.delete(subscription_id)
        else:
            subscription = stripe_client.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        logger.info(f"Stripe subscription cancelled: {subscription_id}")
        return subscription
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error cancelling subscription: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error cancelling subscription: {str(e)}")
        raise

def create_refund(charge_id, amount=None, reason=None):
    """
    Create a Stripe refund
    
    Args:
        charge_id: Stripe charge ID
        amount: Amount to refund in dollars (if None, full refund)
        reason: Refund reason (duplicate, fraudulent, requested_by_customer)
    
    Returns:
        Refund object or None if Stripe is not configured
    """
    stripe_client = get_stripe_client()
    if not stripe_client:
        return None
    
    try:
        refund_params = {
            'charge': charge_id,
        }
        
        if amount:
            refund_params['amount'] = int(amount * 100)  # Convert to cents
        
        if reason:
            refund_params['reason'] = reason
        
        refund = stripe_client.Refund.create(**refund_params)
        logger.info(f"Stripe refund created: {refund.id}")
        return refund
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating refund: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating refund: {str(e)}")
        raise

def get_payment_methods(customer_id):
    """
    Get saved payment methods for a customer
    
    Args:
        customer_id: Stripe customer ID
    
    Returns:
        List of payment methods or None if Stripe is not configured
    """
    stripe_client = get_stripe_client()
    if not stripe_client:
        return None
    
    try:
        payment_methods = stripe_client.PaymentMethod.list(
            customer=customer_id,
            type='card'
        )
        return payment_methods.data
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting payment methods: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting payment methods: {str(e)}")
        raise

def verify_webhook_signature(payload, signature, webhook_secret):
    """
    Verify Stripe webhook signature
    
    Args:
        payload: Raw request body
        signature: Stripe signature header
        webhook_secret: Webhook signing secret
    
    Returns:
        Event object if valid, None otherwise
    """
    stripe_client = get_stripe_client()
    if not stripe_client:
        return None
    
    try:
        event = stripe_client.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        return event
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return None
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying webhook: {str(e)}")
        return None

def is_stripe_configured():
    """Check if Stripe is properly configured"""
    return get_stripe_client() is not None

