import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import stripe
from .models import User,Product,CartItem,Cart
from . import db
from .forms import ProductForm
from flask_mail import Message
from . import mail
from werkzeug.utils import secure_filename



auth = Blueprint('auth', __name__)

@auth.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/sign_up.html', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        new_user = User(email=request.form['email'], first_name=request.form['firstName'], password=generate_password_hash(request.form['password1'],  method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        send_registration_email(new_user.email, new_user.first_name)

        flash('Account created!', category='success')
        return redirect(url_for('views.created'))
    return render_template('sign_up.html', user=current_user)


@auth.route('/send_email')
def send_registration_email(email, first_name):
    msg = Message(
        'Welcome to Our eShop!',
        recipients=[email])
    
    msg.body = f'Hi {first_name},\n\nThank you for registering at our eShop!'
    
    # # Optional: You can use an HTML template for better-looking emails
    # msg.html = render_template('email_welcome.html', username=username)



    try:
        mail.send(msg)
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


@auth.route('/addproduct.html', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        description = form.description.data
        photo = form.photo.data
        
        
        if photo:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join('https://www.pythonanywhere.com/user/jacobsalib/files/home/jacobsalib/eshop/website/static/images',  filename)
            photo.save(photo_path)

        product = Product(name=name, price=price, description=description, photo=photo_path)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('auth.add_product'))

    products = Product.query.all()
    return render_template('addproduct.html', products=products, form=form)


@auth.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    user_cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not user_cart:
        user_cart = Cart(user_id=current_user.id)
        db.session.add(user_cart)
        db.session.commit()

    # Check if the item is already in the cart
    cart_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=product.id).first()

    if cart_item:
        cart_item.quantity += 1  
    else:
        new_cart_item = CartItem(cart_id=user_cart.id, product_id=product.id, quantity=1)
        db.session.add(new_cart_item)

    db.session.commit()

    flash('Item added to cart', 'success')
    return redirect(url_for('auth.view_cart'))


@auth.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=current_user.id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'success')
    else:
        flash('Item not found or does not belong to your cart.', 'danger')

    return redirect(url_for('auth.view_cart'))


@auth.route('/increase_quantity/<int:item_id>', methods=['POST'])
@login_required
def increase_quantity(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=current_user.id).first()

    if cart_item:
        cart_item.quantity += 1  
        db.session.commit()
        flash(f'Added one more {cart_item.product.name} to your cart.', 'success')
    else:
        flash('Item not found in your cart.', 'danger')

    return redirect(url_for('auth.view_cart'))


@auth.route('/decrease_quantity/<int:item_id>', methods=['POST'])
@login_required
def decrease_quantity(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=current_user.id).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  
        else:
            db.session.delete(cart_item)

        db.session.commit()
        flash('Removed item from your cart.', 'success')
    else:
        flash('Item not found in your cart.', 'danger')

    return redirect(url_for('auth.view_cart'))


@auth.route('/cart')
@login_required
def view_cart():
    user_cart = Cart.query.filter_by(user_id=current_user.id).first()

    total_price = 0
    total_discount = 0
    tax =  24
    shipping_fee = 5.00  
    discount_amount = 0

    if user_cart:
        items = CartItem.query.filter_by(cart_id=user_cart.id).all()
        
        # item discount from shop(if exist for a product)
        for item in items:
            discount_amount = item.product.price * (item.product.discount / 100)
            discounted_price = item.product.price - discount_amount
            total_price += discounted_price * item.quantity  
            total_discount += discount_amount * item.quantity

        # user input code discount
        user_code_discount_percentage = session.get('discount', 0)
        user_code_discount_amount = total_price * (user_code_discount_percentage / 100)
        user_price_after_discount_code = total_price - user_code_discount_amount

        tax_included = round(total_price * (tax / 100))

        if discount_amount or user_code_discount_amount:
            if total_price >= 100 :
                shipping_fee_after = 0.00  
                grand_total = total_price - discount_amount - user_code_discount_amount
            else:
                shipping_fee_after = 5.00  
                grand_total = round(total_price + shipping_fee, 2) - discount_amount - user_code_discount_amount
        else:
            if total_price >= 100 :
                shipping_fee_after = 0.00  
                grand_total = total_price
            else:
                shipping_fee_after = 5.00  
                grand_total = round(total_price + shipping_fee, 2)

        return render_template('cart.html', items=items, total_price=total_price, tax=tax, shipping_fee=shipping_fee,
                               grand_total=grand_total, total_discount=total_discount,
                               user_code_discount_percentage=user_code_discount_percentage,
                               user_code_discount_amount=user_code_discount_amount,
                               user_price_after_discount_code=user_price_after_discount_code,
                               tax_included=tax_included,
                               shipping_fee_after=shipping_fee_after)
    else:
        flash('Your cart is empty.', 'info')
        return render_template('cart.html', items=[], total_price=0, total_discount=0)
    


@auth.route('/apply_discount', methods=['POST'])
@login_required
def apply_discount():
   
    user_discount_code = request.form.get('discount_code')
    user_code = User.query.filter_by(user_discount=current_user.user_discount).first()
    db.session.add(user_code)
    db.session.commit()

    if  user_discount_code  == "NEW10":
        user_code_discount_percentage = 10
        session['discount'] = user_code_discount_percentage
        flash(f"Discount code applied: {user_code_discount_percentage}% off", 'success')
    else:
        flash('Invalid discount code', 'danger')

    return redirect(url_for('auth.view_cart'))


@auth.route('/checkout')
@login_required
def checkout():
    user_code = User.query.filter_by(user_discount=current_user.user_discount).first()
    cart_items = CartItem.query.filter_by(cart_id=current_user.id).all()
    grand_total= sum(item.product.price * item.quantity for item in cart_items)
    
    if user_code == 10 :
        discount_amount = grand_total * (10 / 100)
        grand_total = grand_total - discount_amount


    if grand_total < 100:
        grand_total = grand_total + 5.00
    
    return render_template('checkout.html',
                            grand_total=grand_total,
                            stripe_public_key='pk_test_51PyIz6GCnsDUo2I6pa9gwkEqpk7KGOAiLT4frLH4ODssM1xWwGh2hiD97WUwS43qpta5GErUQpPKRjLZAb6Ovx1C00l88oWPWb')



@auth.route('/process_payment', methods=['POST', 'GET'])
@login_required
def process_payment():
    token = request.form.get('stripeToken')  
    amount = request.form.get('amount')  

    if not token or not amount :
        flash('Error processing payment. Please try again.', 'danger')
        return redirect(url_for('auth.checkout'))

    try:
        amount_in_cents = int(float(amount) * 100)

        charge = stripe.Charge.create(
            amount=amount_in_cents, 
            currency='eur',
            description=f'Charge for {current_user.first_name}',
            source=token, 
            )

        print(f"Charge successful: {charge['id']}")
        print(f"Charge amount: {charge['amount']} cents")
        print(f"Customer: {current_user.first_name}")

        flash('Payment successful!', 'success')
        return redirect(url_for('auth.order_confirmation'))
    

    except stripe.error.CardError as e:
        flash(f'Payment error: {e.user_message}', 'danger')
        return redirect(url_for('auth.checkout'))

    except stripe.error.StripeError as e:
        flash(f'Something went wrong with the payment: {e.user_message}', 'danger')
        return redirect(url_for('auth.checkout'))


@auth.route('/order_confirmation')
@login_required
def order_confirmation():
    return render_template('order_confirmation.html')
