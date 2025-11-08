from flask import Flask, request, redirect, url_for, session, render_template, flash
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-it-make-it-random-12345'

# База користувачів (логін: {пароль, аватарка, стартовий баланс})
USERS = {
    'admin': {
        'password': 'password123',
        'avatar': 'https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg',
        'balance': 10000
    },
    'user1': {
        'password': '123456',
        'avatar': 'https://avatars.steamstatic.com/b5bd56c1aa4644a474a2e4972be27534804bf7fa_full.jpg',
        'balance': 5000
    },
    'gamer': {
        'password': 'qwerty',
        'avatar': 'https://avatars.steamstatic.com/c5d56249ee5d28a07db4ac9f7f60924714d2cade_full.jpg',
        'balance': 15000
    }
}

# Дані про ігри
GAMES = [
    {
        'id': 1,
        'title': 'Cyberpunk 2077',
        'description': 'Футуристична RPG з відкритим світом у Night City. Створіть свого персонажа та досліджуйте величезний мегаполіс майбутнього.',
        'image': 'cyberpunk.jpg',
        'tags': ['RPG', 'Відкритий світ', 'Sci-Fi'],
        'original_price': 1499,
        'discount': 40,
        'current_price': 899
    },
    {
        'id': 2,
        'title': 'Elden Ring',
        'description': 'Епічна action-RPG від FromSoftware. Досліджуйте величезний фантастичний світ та долайте складних босів.',
        'image': 'eldenring.jpg',
        'tags': ['RPG', 'Екшн', 'Фентезі'],
        'original_price': 1699,
        'discount': 25,
        'current_price': 1274
    },
    {
        'id': 3,
        'title': 'Counter-Strike 2',
        'description': 'Легендарний тактичний шутер нового покоління. Працюйте в команді та перемагайте противників.',
        'image': 'cs2.jpg',
        'tags': ['Шутер', 'Мультиплеєр', 'Конкурентний'],
        'original_price': 0,
        'discount': 0,
        'current_price': 0
    },
    {
        'id': 4,
        'title': 'Baldurs Gate 3',
        'description': 'Епічна RPG за мотивами Dungeons & Dragons. Створюйте свою історію у світі магії та пригод.',
        'image': 'bg3.jpg',
        'tags': ['RPG', 'Пригоди', 'Покрокова'],
        'original_price': 1799,
        'discount': 15,
        'current_price': 1529
    }
]

def get_current_user():
    """Отримати дані поточного користувача"""
    username = session.get('username')
    if username and username in USERS:
        return {
            'username': username,
            'avatar': USERS[username]['avatar']
        }
    return None

def check_auth():
    """Перевірка авторизації"""
    if 'username' not in session:
        return False
    return True

def init_user_data():
    """Ініціалізація даних користувача"""
    if not check_auth():
        return False
    
    username = session['username']
    
    # Ініціалізація балансу користувача
    if f'balance_{username}' not in session:
        session[f'balance_{username}'] = USERS[username]['balance']
    
    # Ініціалізація кошика
    if f'cart_{username}' not in session:
        session[f'cart_{username}'] = []
    
    # Ініціалізація куплених ігор
    if f'purchased_{username}' not in session:
        session[f'purchased_{username}'] = []
    
    return True

def get_user_balance():
    """Отримати баланс користувача"""
    username = session.get('username')
    return session.get(f'balance_{username}', 0)

def get_user_cart():
    """Отримати кошик користувача"""
    username = session.get('username')
    return session.get(f'cart_{username}', [])

def get_user_purchased():
    """Отримати куплені ігри користувача"""
    username = session.get('username')
    return session.get(f'purchased_{username}', [])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Сторінка входу"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')
        
        print(f"🔐 Login attempt: {username}")
        
        # Перевірка логіну та пароля
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            
            # Запам'ятати (постійна сесія)
            if remember:
                session.permanent = True
            
            print(f"✅ Login successful: {username}")
            flash(f'Вітаємо, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            print(f"❌ Login failed: {username}")
            flash('❌ Невірний логін або пароль!', 'error')
            return redirect(url_for('login'))
    
    # Якщо вже залогінений - перенаправити
    if check_auth():
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Вихід з акаунту"""
    username = session.get('username')
    session.clear()
    print(f"👋 Logout: {username}")
    flash('Ви вийшли з акаунту', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    """Головна сторінка магазину"""
    if not check_auth():
        return redirect(url_for('login'))
    
    init_user_data()
    
    print("=" * 50)
    print("📍 INDEX PAGE - Loading...")
    
    balance = get_user_balance()
    cart_count = len(get_user_cart())
    purchased_ids = get_user_purchased()
    current_user = get_current_user()
    
    print(f"   User: {session.get('username')}")
    print(f"   Balance: {balance} ₴")
    print(f"   Games: {len(GAMES)}")
    print(f"   Cart items: {cart_count}")
    
    try:
        html = render_template('index.html', 
                             games=GAMES, 
                             cart_count=cart_count,
                             balance=balance,
                             purchased_ids=purchased_ids,
                             current_user=current_user)
        print(f"   ✅ Rendered successfully")
        print("=" * 50)
        return html
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        print("=" * 50)
        return f"<h1>Error loading page</h1><pre>{e}</pre>"

@app.route('/add-to-cart/<int:game_id>', methods=['POST'])
def add_to_cart(game_id):
    """Додати гру в кошик"""
    if not check_auth():
        return redirect(url_for('login'))
    
    init_user_data()
    username = session['username']
    
    print(f"➕ Adding game {game_id} to cart for {username}...")
    
    # Перевірка чи гра вже куплена
    if game_id in get_user_purchased():
        flash('Ви вже купили цю гру!', 'info')
        return redirect(url_for('index'))
    
    cart = get_user_cart()
    if game_id not in cart:
        cart.append(game_id)
        session[f'cart_{username}'] = cart
        session.modified = True
        print(f"   ✅ Game {game_id} added!")
        flash('Гру додано до кошика!', 'success')
    else:
        flash('Ця гра вже в кошику!', 'info')
    
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    """Сторінка кошика"""
    if not check_auth():
        return redirect(url_for('login'))
    
    init_user_data()
    
    cart_ids = get_user_cart()
    cart_games = [game for game in GAMES if game['id'] in cart_ids]
    
    total = sum(game['current_price'] for game in cart_games)
    cart_count = len(cart_games)
    balance = get_user_balance()
    current_user = get_current_user()
    
    try:
        html = render_template('cart.html', 
                             games=cart_games, 
                             total=total, 
                             cart_count=cart_count,
                             balance=balance,
                             current_user=current_user)
        return html
    except Exception as e:
        return f"<h1>Error loading cart</h1><pre>{e}</pre>"

@app.route('/checkout', methods=['POST'])
def checkout():
    """Оформлення замовлення (покупка)"""
    if not check_auth():
        return redirect(url_for('login'))
    
    init_user_data()
    username = session['username']
    
    cart_ids = get_user_cart()
    cart_games = [game for game in GAMES if game['id'] in cart_ids]
    total = sum(game['current_price'] for game in cart_games)
    balance = get_user_balance()
    
    if not cart_games:
        flash('Ваш кошик порожній!', 'warning')
        return redirect(url_for('cart'))
    
    if balance >= total:
        # Оплата успішна
        session[f'balance_{username}'] = balance - total
        
        purchased = get_user_purchased()
        purchased.extend(cart_ids)
        session[f'purchased_{username}'] = purchased
        
        session[f'cart_{username}'] = []
        session.modified = True
        
        print(f"✅ Payment successful for {username}!")
        flash(f'✅ Оплата успішна! Списано {total} ₴. Ігри додано до вашої бібліотеки!', 'success')
        return redirect(url_for('library'))
    else:
        shortage = total - balance
        flash(f'❌ Оплата відхилена! Недостатньо коштів. Бракує {shortage} ₴', 'error')
        return redirect(url_for('cart'))

@app.route('/library')
def library():
    """Бібліотека куплених ігор"""
    if not check_auth():
        return redirect(url_for('login'))
    
    init_user_data()
    
    purchased_ids = get_user_purchased()
    purchased_games = [game for game in GAMES if game['id'] in purchased_ids]
    balance = get_user_balance()
    cart_count = len(get_user_cart())
    current_user = get_current_user()
    
    try:
        html = render_template('library.html',
                             games=purchased_games,
                             balance=balance,
                             cart_count=cart_count,
                             current_user=current_user)
        return html
    except Exception as e:
        return f"<h1>Error loading library</h1><pre>{e}</pre>"

@app.route('/add-balance', methods=['POST'])
def add_balance():
    """Поповнити баланс"""
    if not check_auth():
        return redirect(url_for('login'))
    
    init_user_data()
    username = session['username']
    
    try:
        amount = int(request.form.get('amount', 0))
        if amount > 0 and amount <= 10000:
            current_balance = get_user_balance()
            session[f'balance_{username}'] = current_balance + amount
            session.modified = True
            flash(f'✅ Баланс поповнено на {amount} ₴', 'success')
            print(f"💰 Balance added for {username}: +{amount} ₴")
        else:
            flash('❌ Невірна сума! (від 1 до 10000 ₴)', 'error')
    except:
        flash('❌ Помилка поповнення балансу!', 'error')
    
    return redirect(url_for('index'))

@app.route('/remove-from-cart/<int:game_id>', methods=['POST'])
def remove_from_cart(game_id):
    """Видалити гру з кошика"""
    if not check_auth():
        return redirect(url_for('login'))
    
    init_user_data()
    username = session['username']
    
    cart = get_user_cart()
    if game_id in cart:
        cart.remove(game_id)
        session[f'cart_{username}'] = cart
        session.modified = True
        flash('Гру видалено з кошика', 'info')
    
    return redirect(url_for('cart'))

@app.route('/clear-cart', methods=['POST'])
def clear_cart():
    """Очистити весь кошик"""
    if not check_auth():
        return redirect(url_for('login'))
    
    init_user_data()
    username = session['username']
    
    session[f'cart_{username}'] = []
    session.modified = True
    flash('Кошик очищено', 'info')
    
    return redirect(url_for('cart'))

@app.route('/reset', methods=['POST'])
def reset():
    """Скинути всі дані (для тестування)"""
    if not check_auth():
        return redirect(url_for('login'))
    
    username = session.get('username')
    
    # Скидаємо тільки дані користувача, але не логаут
    session[f'balance_{username}'] = USERS[username]['balance']
    session[f'cart_{username}'] = []
    session[f'purchased_{username}'] = []
    session.modified = True
    
    flash(f'🔄 Дані скинуто! Баланс: {USERS[username]["balance"]} ₴', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🎮 STEAM STORE - Starting server...")
    print("=" * 70)
    
    print("\n👤 Test Accounts:")
    for username, data in USERS.items():
        print(f"   {username} / {data['password']} (Balance: {data['balance']} ₴)")
    
    print("\n📍 Open in browser: http://127.0.0.1:5000/")
    print("\n💡 Features:")
    print("   ✅ Login system with 3 accounts")
    print("   ✅ Individual balance per user")
    print("   ✅ Individual cart per user")
    print("   ✅ Individual library per user")
    print("   ✅ User avatar in navbar")
    print("   ✅ Logout button")
    print("   ✅ Session persistence")
    print("\n" + "=" * 70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)