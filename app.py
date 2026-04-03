import os
import re
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_mail import Mail, Message
import mysql.connector
from werkzeug.utils import secure_filename

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key-for-local-dev-only')

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Email config from environment variables
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_USERNAME'))

mail = Mail(app)

# Database config from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),     
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx', 'txt'}

CATEGORY_TO_DEPARTMENT = {
    'Billing Issue': 'Finance Department',
    'Technical Issue': 'IT Support',
    'Service Complaint': 'Customer Care',
    'Delivery Issue': 'Logistics Department',
    'Account Problem': 'Customer Support'
}

TRAINING_DATA = [
    ('payment deducted twice from my card and invoice is wrong', 'Billing Issue'),
    ('refund is not processed and extra charges on my bill', 'Billing Issue'),
    ('billing amount is incorrect and payment failed', 'Billing Issue'),
    ('i was charged again despite successful transaction', 'Billing Issue'),
    ('double charged for same order and no response from support', 'Billing Issue'),
    ('subscription renewed automatically without my permission', 'Billing Issue'),
    ('overcharged tax amount and discount not applied', 'Billing Issue'),
    ('partial payment accepted but full amount billed', 'Billing Issue'),
    ('credit card charged after cancellation request', 'Billing Issue'),
    ('invoice shows wrong product quantity and pricing', 'Billing Issue'),
    ('late fee added incorrectly to my account', 'Billing Issue'),
    ('promo code applied but still charged full price', 'Billing Issue'),
    ('bank rejected payment but i was still billed', 'Billing Issue'),
    ('charged for canceled order that never shipped', 'Billing Issue'),
    ('multiple small charges instead of one payment', 'Billing Issue'),
    ('billing date changed without notification', 'Billing Issue'),
    ('refund shows as credit but not in my account', 'Billing Issue'),
    ('service charged monthly but only used once', 'Billing Issue'),
    ('wrong currency charged on international order', 'Billing Issue'),
    ('setup fee charged after free trial ended', 'Billing Issue'),
    ('disputed charge removed but reappeared next bill', 'Billing Issue'),
    ('pay later option selected but immediate charge', 'Billing Issue'),
    ('bundle discount promised but not given', 'Billing Issue'),
    ('shipping charged separately after free shipping offer', 'Billing Issue'),


    ('app is crashing and website login page is not loading', 'Technical Issue'),
    ('server error and unable to connect to system', 'Technical Issue'),
    ('my application freezes whenever i submit form', 'Technical Issue'),
    ('bug in portal and otp verification is not working', 'Technical Issue'),
    ('page loads forever and buttons dont respond', 'Technical Issue'),
    ('search function broken and shows no results', 'Technical Issue'),
    ('profile picture upload fails every time', 'Technical Issue'),
    ('checkout process stuck at payment gateway', 'Technical Issue'),
    ('mobile app force closes when opening cart', 'Technical Issue'),
    ('filter options not working on product page', 'Technical Issue'),
    ('password reset email never received', 'Technical Issue'),
    ('live chat widget not loading properly', 'Technical Issue'),
    ('order confirmation page shows error 500', 'Technical Issue'),
    ('pdf download link broken on invoice page', 'Technical Issue'),
    ('zoom function not working on product images', 'Technical Issue'),
    ('notification bell shows wrong unread count', 'Technical Issue'),
    ('sort by price feature completely broken', 'Technical Issue'),
    ('address autocomplete not working in forms', 'Technical Issue'),
    ('tracking page shows invalid order number', 'Technical Issue'),
    ('captcha verification keeps failing', 'Technical Issue'),
    ('video tutorials wont play in help section', 'Technical Issue'),
    ('desktop site redirects to wrong subdomain', 'Technical Issue'),
    ('wishlist items disappearing randomly', 'Technical Issue'),
    ('currency converter not updating rates', 'Technical Issue'),
    ('print invoice button creates blank page', 'Technical Issue'),
    ('dark mode toggle broken on mobile', 'Technical Issue'),
    ('infinite scroll stops working halfway', 'Technical Issue'),

    ('staff was rude and support service is very poor', 'Service Complaint'),
    ('customer service did not help and behavior was disappointing', 'Service Complaint'),
    ('bad service quality and no one responded properly', 'Service Complaint'),
    ('support executive was unprofessional and slow', 'Service Complaint'),
    ('waited 45 minutes on hold then call dropped', 'Service Complaint'),
    ('agent gave wrong information about policy', 'Service Complaint'),
    ('promised callback never happened after 3 days', 'Service Complaint'),
    ('chat support disconnected mid conversation', 'Service Complaint'),
    ('representative argued instead of helping', 'Service Complaint'),
    ('transferred 4 times to wrong departments', 'Service Complaint'),
    ('support only available during business hours', 'Service Complaint'),
    ('agent demanded personal details unnecessarily', 'Service Complaint'),
    ('solution offered doesnt actually work', 'Service Complaint'),
    ('blamed me instead of fixing the problem', 'Service Complaint'),
    ('script reading instead of real help', 'Service Complaint'),
    ('ignored my follow up emails completely', 'Service Complaint'),
    ('promised resolution within 24hrs but no update', 'Service Complaint'),
    ('chat agent typing visible but no response', 'Service Complaint'),
    ('support hours listed wrong on website', 'Service Complaint'),
    ('asked same questions multiple times', 'Service Complaint'),
    ('solution requires paying extra fees', 'Service Complaint'),
    ('agent hung up when i asked for supervisor', 'Service Complaint'),
    ('email support takes 5 days to respond', 'Service Complaint'),
    ('live chat unavailable during peak hours', 'Service Complaint'),
    ('callback promised but phone never rang', 'Service Complaint'),
    ('support script sounds robotic and unhelpful', 'Service Complaint'),

    ('delivery is late and parcel has not arrived', 'Delivery Issue'),
    ('order shipment delayed and package not delivered', 'Delivery Issue'),
    ('courier status is wrong and item missing in transit', 'Delivery Issue'),
    ('my product has not reached even after expected date', 'Delivery Issue'),
    ('delivered to wrong address in neighborhood', 'Delivery Issue'),
    ('package marked delivered but not received', 'Delivery Issue'),
    ('driver left at gate and no one home', 'Delivery Issue'),
    ('delivery attempt failed 3 times no reschedule', 'Delivery Issue'),
    ('item damaged during transit packaging poor', 'Delivery Issue'),
    ('tracking shows out for delivery all day', 'Delivery Issue'),
    ('delivered to neighbor who denies receiving', 'Delivery Issue'),
    ('courier demanded extra cash on delivery', 'Delivery Issue'),
    ('package stolen from doorstep after delivery', 'Delivery Issue'),
    ('wrong item delivered completely different order', 'Delivery Issue'),
    ('delivery slot promised but arrived 2 days late', 'Delivery Issue'),
    ('partial delivery missing half the order', 'Delivery Issue'),
    ('returned to sender without notification', 'Delivery Issue'),
    ('tracking stuck at same location 4 days', 'Delivery Issue'),
    ('delivered to completely wrong city', 'Delivery Issue'),
    ('driver called once and never showed up', 'Delivery Issue'),
    ('package opened and resealed by courier', 'Delivery Issue'),
    ('delivery radius exceeded but charged extra', 'Delivery Issue'),
    ('no delivery attempt made as promised', 'Delivery Issue'),
    ('item held at warehouse needs pickup', 'Delivery Issue'),
    ('courier contact number not working', 'Delivery Issue'),
    ('delivery status says failed unknown reason', 'Delivery Issue'),
    ('promised same day delivery took 5 days', 'Delivery Issue'),
    ('multiple packages but only one delivered', 'Delivery Issue'),

    ('unable to access my account and password reset fails', 'Account Problem'),
    ('account is locked and login credentials not accepted', 'Account Problem'),
    ('profile access denied and account suspended unexpectedly', 'Account Problem'),
    ('cannot update account details and email verification failed', 'Account Problem'),
    ('two factor authentication code not arriving', 'Account Problem'),
    ('account created but cannot verify email', 'Account Problem'),
    ('phone number already registered error', 'Account Problem'),
    ('forgot password link expired immediately', 'Account Problem'),
    ('account shows as new user after login', 'Account Problem'),
    ('payment method not saving in profile', 'Account Problem'),
    ('address book empty after adding details', 'Account Problem'),
    ('account balance shows incorrect amount', 'Account Problem'),
    ('cannot change registered mobile number', 'Account Problem'),
    ('profile picture upload rejected wrong format', 'Account Problem'),
    ('account merged with someone elses data', 'Account Problem'),
    ('login works but profile page blank', 'Account Problem'),
    ('verification email sent to wrong address', 'Account Problem'),
    ('account deactivated without warning', 'Account Problem'),
    ('cannot remove old payment method', 'Account Problem'),
    ('name change rejected by verification', 'Account Problem'),
    ('session expires immediately after login', 'Account Problem'),
    ('account shows wrong subscription status', 'Account Problem'),
    ('duplicate account created accidentally', 'Account Problem'),
    ('cannot access order history section', 'Account Problem'),
    ('profile shows wrong registered date', 'Account Problem'),
    ('sms verification failing network issue', 'Account Problem'),
    ('account recovery requires old password', 'Account Problem')
]

# Admin credentials from environment variables
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@complaintiq.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
try:
    nltk.download('punkt_tab', quiet=True)
except Exception:
    pass

STOP_WORDS = set(stopwords.words('english'))
vectorizer = TfidfVectorizer()
model = LogisticRegression(max_iter=1000)

def train_model():
    texts = [preprocess_text(item[0]) for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]
    x_train = vectorizer.fit_transform(texts)
    model.fit(x_train, labels)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    tokens = word_tokenize(text)
    filtered = [word for word in tokens if word not in STOP_WORDS and len(word) > 2]
    return ' '.join(filtered)

def predict_category(text):
    cleaned = preprocess_text(text)
    vector = vectorizer.transform([cleaned])
    return model.predict(vector)[0]

def detect_priority(text):
    text_l = text.lower()

    high_keywords = [
        'urgent', 'immediately', 'asap', 'deducted twice',
        'fraud', 'failed payment', 'critical', 'locked',
        'cannot access', 'security'
    ]

    medium_keywords = [
        'late', 'delay', 'not working', 'issue',
        'problem', 'slow', 'pending'
    ]

    if any(keyword in text_l for keyword in high_keywords):
        return 'High'
    if any(keyword in text_l for keyword in medium_keywords):
        return 'Medium'
    return 'Low'

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return 'Positive'
    if polarity < -0.1:
        return 'Negative'
    return 'Neutral'

def generate_complaint_id():
    return 'CMP-' + datetime.now().strftime('%Y%m%d') + '-' + uuid.uuid4().hex[:6].upper()

def send_email_safe(subject, recipients, body):
    try:
        msg = Message(subject=subject, recipients=recipients)
        msg.body = body
        mail.send(msg)
        return True
    except Exception:
        return False

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def fetch_one(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def fetch_all(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute_query(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return last_id

@app.route('/')
def index():
    return redirect(url_for('submit_complaint'))

@app.route('/submit', methods=['GET', 'POST'])
def submit_complaint():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        complaint_text = request.form.get('complaint_text', '').strip()
        file = request.files.get('attachment')

        if not name or not email or not complaint_text:
            flash('All required fields must be filled.')
            return redirect(url_for('submit_complaint'))

        complaint_id = generate_complaint_id()
        category = predict_category(complaint_text)
        priority = detect_priority(complaint_text)
        sentiment = analyze_sentiment(complaint_text)
        department = CATEGORY_TO_DEPARTMENT.get(category, 'General Support')
        attachment_name = None

        if file and file.filename:
            if allowed_file(file.filename):
                filename = secure_filename(f"{complaint_id}_{file.filename}")
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                attachment_name = filename
            else:
                flash('Invalid file type uploaded.')
                return redirect(url_for('submit_complaint'))

        execute_query("""
            INSERT INTO complaints
            (complaint_id, name, email, complaint_text, attachment, category, priority, sentiment, department, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            complaint_id, name, email, complaint_text, attachment_name,
            category, priority, sentiment, department, 'Pending', datetime.now()
        ))

        send_email_safe(
            'Complaint Received',
            [email],
            f'''Your complaint ID {complaint_id} has been registered.

Category: {category}
Priority: {priority}
Status: Pending
Department: {department}
'''
        )

        return render_template(
            'submission_success.html',
            complaint_id=complaint_id,
            category=category,
            priority=priority,
            sentiment=sentiment,
            department=department
        )

    return render_template('submit_complaint.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))

        flash('Invalid admin credentials.')

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('submit_complaint'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    total_row = fetch_one("SELECT COUNT(*) AS total FROM complaints")
    pending_row = fetch_one("SELECT COUNT(*) AS total FROM complaints WHERE status = 'Pending'")
    resolved_row = fetch_one("SELECT COUNT(*) AS total FROM complaints WHERE status = 'Resolved'")
    in_progress_row = fetch_one("SELECT COUNT(*) AS total FROM complaints WHERE status = 'In Progress'")

    total = total_row['total'] if total_row else 0
    pending = pending_row['total'] if pending_row else 0
    resolved = resolved_row['total'] if resolved_row else 0
    in_progress = in_progress_row['total'] if in_progress_row else 0

    category_rows = fetch_all("""
        SELECT category, COUNT(*) AS total
        FROM complaints
        GROUP BY category
        ORDER BY total DESC
    """)

    priority_rows = fetch_all("""
        SELECT priority, COUNT(*) AS total
        FROM complaints
        GROUP BY priority
        ORDER BY CASE
            WHEN priority = 'High' THEN 1
            WHEN priority = 'Medium' THEN 2
            WHEN priority = 'Low' THEN 3
            ELSE 4
        END
    """)

    return render_template(
        'admin_dashboard.html',
        active_page='dashboard',
        total=total,
        pending=pending,
        resolved=resolved,
        in_progress=in_progress,
        category_rows=category_rows,
        priority_rows=priority_rows
    )

@app.route('/api/dashboard-live')
@login_required
def dashboard_live():
    total_row = fetch_one("SELECT COUNT(*) AS total FROM complaints")
    pending_row = fetch_one("SELECT COUNT(*) AS total FROM complaints WHERE status = 'Pending'")
    resolved_row = fetch_one("SELECT COUNT(*) AS total FROM complaints WHERE status = 'Resolved'")
    in_progress_row = fetch_one("SELECT COUNT(*) AS total FROM complaints WHERE status = 'In Progress'")

    category_rows = fetch_all("""
        SELECT category, COUNT(*) AS total
        FROM complaints
        GROUP BY category
        ORDER BY total DESC
    """)

    priority_rows = fetch_all("""
        SELECT priority, COUNT(*) AS total
        FROM complaints
        GROUP BY priority
        ORDER BY CASE
            WHEN priority = 'High' THEN 1
            WHEN priority = 'Medium' THEN 2
            WHEN priority = 'Low' THEN 3
            ELSE 4
        END
    """)

    return jsonify({
        "stats": {
            "total": total_row["total"] if total_row else 0,
            "pending": pending_row["total"] if pending_row else 0,
            "resolved": resolved_row["total"] if resolved_row else 0,
            "in_progress": in_progress_row["total"] if in_progress_row else 0
        },
        "categories": category_rows,
        "priorities": priority_rows
    })

@app.route('/admin/manage', methods=['GET'])
@login_required
def manage_complaints():
    category = request.args.get('category', '')
    priority = request.args.get('priority', '')
    status = request.args.get('status', '')
    date_filter = request.args.get('date', '')

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if category:
        query += " AND category = %s"
        params.append(category)

    if priority:
        query += " AND priority = %s"
        params.append(priority)

    if status:
        query += " AND status = %s"
        params.append(status)

    if date_filter == '7':
        query += " AND created_at >= %s"
        params.append(datetime.now() - timedelta(days=7))
    elif date_filter == '30':
        query += " AND created_at >= %s"
        params.append(datetime.now() - timedelta(days=30))

    query += " ORDER BY created_at DESC"
    complaints = fetch_all(query, params)

    return render_template(
        'manage_complaints.html',
        active_page='manage',
        complaints=complaints
    )

@app.route('/admin/complaint/<int:complaint_db_id>', methods=['GET', 'POST'])
@login_required
def complaint_detail(complaint_db_id):
    if request.method == 'POST':
        status = request.form.get('status')
        admin_response = request.form.get('admin_response')

        execute_query("""
            UPDATE complaints
            SET status = %s, admin_response = %s, updated_at = %s
            WHERE id = %s
        """, (status, admin_response, datetime.now(), complaint_db_id))

        complaint = fetch_one("SELECT * FROM complaints WHERE id = %s", (complaint_db_id,))

        if complaint and status == 'Resolved':
            send_email_safe(
                'Complaint Resolved',
                [complaint['email']],
                f'''Your complaint {complaint['complaint_id']} has been resolved.

Response: {admin_response}

Please submit your feedback.
'''
            )

        flash('Complaint updated successfully.')
        return redirect(url_for('complaint_detail', complaint_db_id=complaint_db_id))

    complaint = fetch_one("SELECT * FROM complaints WHERE id = %s", (complaint_db_id,))
    return render_template(
        'complaint_detail.html',
        active_page='manage',
        complaint=complaint
    )

@app.route('/api/dashboard-data')
@login_required
def dashboard_data():
    category_rows = fetch_all("""
        SELECT category, COUNT(*) AS total
        FROM complaints
        GROUP BY category
        ORDER BY total DESC
    """)

    priority_rows = fetch_all("""
        SELECT priority, COUNT(*) AS total
        FROM complaints
        GROUP BY priority
        ORDER BY CASE
            WHEN priority = 'High' THEN 1
            WHEN priority = 'Medium' THEN 2
            WHEN priority = 'Low' THEN 3
            ELSE 4
        END
    """)

    return jsonify({
        'categories': category_rows,
        'priorities': priority_rows
    })

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    train_model()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
