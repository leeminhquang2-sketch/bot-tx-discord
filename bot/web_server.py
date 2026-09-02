# bot/web_server.py
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_session import Session
import secrets
from datetime import datetime, timedelta
from database import get_user, update_user, add_transaction, get_all_users, get_transactions, load_db, save_db
from config_manager import config_manager
from secrets_manager import secrets_manager

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Cấu hình session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = './data/sessions'
Session(app)

# CORS cho phép truy cập từ bên ngoài
CORS(app, origins='*')

ADMIN_PASSWORD = secrets_manager.get_admin_password()
WEB_ACCESS_KEY = secrets_manager.get_web_key()

# Middleware kiểm tra key truy cập
def require_web_key(f):
    def decorated_function(*args, **kwargs):
        # Kiểm tra session đã xác thực chưa
        if not session.get('authenticated'):
            # Nếu chưa, redirect đến trang nhập key
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Middleware kiểm tra admin
def require_admin(f):
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Trang chủ - redirect đến login"""
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Trang đăng nhập với key truy cập"""
    if request.method == 'POST':
        key = request.form.get('key', '').strip()
        password = request.form.get('password', '').strip()
        
        # Kiểm tra key truy cập
        if key != WEB_ACCESS_KEY:
            return render_template('login.html', error='❌ Key truy cập không đúng!')
        
        # Kiểm tra mật khẩu admin
        if password != ADMIN_PASSWORD:
            return render_template('login.html', error='❌ Mật khẩu không đúng!')
        
        # Đăng nhập thành công
        session['authenticated'] = True
        session['login_time'] = datetime.now().isoformat()
        return redirect(url_for('dashboard'))
    
    # GET request - hiển thị trang login
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Đăng xuất"""
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/dashboard')
@require_web_key
def dashboard():
    """Dashboard Admin"""
    return render_template('dashboard.html')

# ===== API ENDPOINTS =====

@app.route('/api/stats')
@require_web_key
def get_stats():
    db = load_db()
    users = db.get('users', {})
    transactions = db.get('transactions', [])
    
    return jsonify({
        'totalUsers': len(users),
        'totalBalance': sum(u.get('balance', 0) for u in users.values()),
        'totalGames': sum(u.get('games_played', 0) for u in users.values()),
        'totalTransactions': len(transactions),
        'dailyReward': config_manager.get('daily_reward', 5000),
        'betMultiplier': config_manager.get('bet_multiplier', 194),
        'currencyName': config_manager.get('currency_name', 'MQ')
    })

@app.route('/api/players')
@require_web_key
def get_players():
    users = get_all_users()
    players = []
    for user_id, data in users.items():
        players.append({
            'userId': user_id,
            'username': data.get('username', f'User {user_id[:6]}'),
            'balance': data.get('balance', 0),
            'gamesPlayed': data.get('games_played', 0),
            'totalWon': data.get('total_won', 0),
            'totalLost': data.get('total_lost', 0),
            'lastDaily': data.get('last_daily')
        })
    
    players.sort(key=lambda x: x['balance'], reverse=True)
    return jsonify(players)

@app.route('/api/add-money', methods=['POST'])
@require_web_key
def add_money():
    data = request.json
    user_id = str(data.get('userId'))
    amount = int(data.get('amount', 0))
    reason = data.get('reason', 'Admin cấp tiền qua web')
    
    if not user_id or amount <= 0:
        return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
    
    user_data = get_user(user_id)
    new_balance = user_data['balance'] + amount
    update_user(user_id, {'balance': new_balance})
    add_transaction(user_id, 'admin_add_web', amount, reason)
    
    return jsonify({
        'success': True,
        'userId': user_id,
        'amount': amount,
        'newBalance': new_balance
    })

@app.route('/api/transactions')
@require_web_key
def get_transactions_list():
    limit = request.args.get('limit', 100, type=int)
    transactions = get_transactions(limit)
    return jsonify(transactions)

@app.route('/api/settings', methods=['GET', 'PUT'])
@require_web_key
def handle_settings():
    if request.method == 'GET':
        return jsonify({
            'dailyReward': config_manager.get('daily_reward', 5000),
            'betMultiplier': config_manager.get('bet_multiplier', 194),
            'minBet': config_manager.get('min_bet', 1000),
            'maxBet': config_manager.get('max_bet', 10000000),
            'currencyName': config_manager.get('currency_name', 'MQ')
        })
    else:
        data = request.json
        config_manager.update(data)
        return jsonify({'success': True})

def run_web_server():
    """Chạy Web Server"""
    host = config_manager.get('api_host', '0.0.0.0')
    port = config_manager.get('api_port', 5000)
    
    print("\n" + "="*50)
    print("🌐 WEB ADMIN SERVER")
    print("="*50)
    print(f"📌 Truy cập: http://{host}:{port}")
    print(f"🔑 Key truy cập: {WEB_ACCESS_KEY}")
    print("="*50 + "\n")
    
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_web_server()
