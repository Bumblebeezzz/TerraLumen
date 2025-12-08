"""
Stripe payment handling
"""

import stripe
from flask import Blueprint, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, MembershipTransaction, MembershipType, MembershipStatus, PaymentStatus

stripe_bp = Blueprint('stripe', __name__)

def init_stripe():
    """Initialize Stripe with API key"""
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')

@stripe_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    init_stripe()
    
    membership_type = request.form.get('membership_type', 'annual')
    price_id = request.form.get('price_id')  # Stripe Price ID
    
    if not price_id:
        flash('Please select a valid membership option.', 'error')
        return redirect(url_for('main.membership'))
    
    try:
        # Create or retrieve Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.name,
                metadata={'user_id': str(current_user.id)}
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()
        
        # Determine if it's a subscription or one-time payment
        is_subscription = membership_type in ['annual']
        is_lifetime = membership_type == 'lifetime'
        
        if is_subscription:
            # Create subscription checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=current_user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=url_for('stripe.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('main.membership', _external=True),
                metadata={
                    'user_id': str(current_user.id),
                    'membership_type': membership_type
                }
            )
        elif is_lifetime:
            # Create one-time payment checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=current_user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=url_for('stripe.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('main.membership', _external=True),
                metadata={
                    'user_id': str(current_user.id),
                    'membership_type': membership_type
                }
            )
        else:
            # Supporter member (donation)
            checkout_session = stripe.checkout.Session.create(
                customer=current_user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=url_for('stripe.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('main.membership', _external=True),
                metadata={
                    'user_id': str(current_user.id),
                    'membership_type': membership_type
                }
            )
        
        return redirect(checkout_session.url, code=303)
    
    except stripe.error.StripeError as e:
        flash(f'Stripe error: {str(e)}', 'error')
        return redirect(url_for('main.membership'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('main.membership'))

@stripe_bp.route('/success')
@login_required
def success():
    """Handle successful payment"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid session.', 'error')
        return redirect(url_for('main.membership'))
    
    try:
        init_stripe()
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.customer != current_user.stripe_customer_id:
            flash('Invalid session for your account.', 'error')
            return redirect(url_for('main.membership'))
        
        # Update user membership status
        if session.payment_status == 'paid':
            current_user.membership_status = MembershipStatus.ACTIVE
            
            # Store subscription ID if it's a subscription
            if session.mode == 'subscription':
                current_user.stripe_subscription_id = session.subscription
            
            # Create transaction record
            transaction = MembershipTransaction(
                user_id=current_user.id,
                stripe_payment_intent_id=session.payment_intent,
                amount=session.amount_total / 100,  # Convert from cents
                currency=session.currency.upper(),
                status=PaymentStatus.COMPLETED,
                membership_type=MembershipType[session.metadata.get('membership_type', 'annual').upper()]
            )
            db.session.add(transaction)
            db.session.commit()
            
            flash('Payment successful! Your membership is now active.', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Payment is still processing. Please check back later.', 'info')
            return redirect(url_for('auth.dashboard'))
    
    except Exception as e:
        flash(f'Error processing payment: {str(e)}', 'error')
        return redirect(url_for('main.membership'))

@stripe_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        init_stripe()
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    
    return jsonify({'status': 'success'}), 200

def handle_checkout_completed(session):
    """Handle completed checkout"""
    user_id = session.get('metadata', {}).get('user_id')
    if user_id:
        user = User.query.get(int(user_id))
        if user:
            user.membership_status = MembershipStatus.ACTIVE
            if session.get('subscription'):
                user.stripe_subscription_id = session['subscription']
            db.session.commit()

def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    customer_id = subscription.get('customer')
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        if subscription['status'] == 'active':
            user.membership_status = MembershipStatus.ACTIVE
        elif subscription['status'] in ['past_due', 'unpaid']:
            user.membership_status = MembershipStatus.EXPIRED
        db.session.commit()

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    customer_id = subscription.get('customer')
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        user.membership_status = MembershipStatus.INACTIVE
        user.stripe_subscription_id = None
        db.session.commit()

def handle_payment_failed(invoice):
    """Handle failed payment"""
    customer_id = invoice.get('customer')
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        user.membership_status = MembershipStatus.EXPIRED
        db.session.commit()

