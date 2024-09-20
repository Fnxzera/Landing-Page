from flask import Flask, render_template, request, jsonify, redirect, url_for
import stripe
import paypalrestsdk

app = Flask(__name__)

# API do Stripe
stripe.api_key = "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"

# API do PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  
    "client_id": "AYZwcs03RFyMFiZocPNVaBsxXMyB2PgBS-331mbchYvxJrG9AiUZQsU0tDUIsSI0bODXi8Qn9ET7pR_u",
    "client_secret": "EPPvZErL4NxXdBshFlCXj4tkF2WXLjHyLphU14BFhrQGkb0SVmDIFm6BTTrBCx42YYVEutrvWPumKdj6"
})

@app.route('/')
def payment_page():
    return render_template('payment.html')

# Stripe
@app.route('/create-stripe-session', methods=['POST'])
def create_stripe_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Produto Exemplo',
                    },
                    'unit_amount': 5000,  # 50,00 EUR
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

# Paypal 
@app.route('/create-paypal-payment', methods=['POST'])
def create_paypal_payment():
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('success', _external=True),
            "cancel_url": url_for('cancel', _external=True)
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Produto Exemplo",
                    "sku": "001",
                    "price": "50.00",
                    "currency": "EUR",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "50.00",
                "currency": "EUR"
            },
            "description": "Compra do Produto Exemplo"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return jsonify({'approval_url': link.href})
    else:
        return jsonify(error=payment.error), 403

# Páginas de sucesso e cancelamento
@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    app.run(debug=True)
