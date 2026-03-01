# backend/routes/admin_routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from backend.models.user_model import User
from backend.models.community_model import Community, CommunityMember
from backend.models.test_model import PersonalityTestResult, HobbyResult
from backend.models.chat_model import ChatMessage
from backend.models.chat_room_model import ChatRoom, ChatUserStatus
from backend.app import db
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ==================================================
# Admin Decorator - Yetkilendirme
# ==================================================

def admin_required(f):
    """Admin yetkisi kontrolü decorator'ı"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Session'da admin kontrolü
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)

    return decorated_function


# ==================================================
# Admin Giriş Sayfaları
# ==================================================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin giriş sayfası"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Basit admin kontrolü (production'da daha güvenli yap!)
        if username == 'admin' and password == 'FriendZone2024':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['login_time'] = datetime.now().isoformat()
            logger.info(f"Admin girişi: {username}")
            return redirect(url_for('admin.index'))
        else:
            return render_template('admin/login.html', error='Geçersiz kullanıcı adı veya şifre')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """Admin çıkış"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin.login'))


# ==================================================
# Ana Dashboard
# ==================================================

@admin_bp.route('/')
@admin_required
def index():
    """Admin ana dashboard"""
    return render_template('admin/index.html')


@admin_bp.route('/api/dashboard/stats')
@admin_required
def dashboard_stats():
    """Dashboard istatistikleri (API)"""
    try:
        # Temel istatistikler
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        completed_tests = User.query.filter_by(is_test_completed=True).count()

        total_communities = Community.query.count()
        active_communities = Community.query.filter_by(is_active=True).count()

        total_messages = ChatMessage.query.count()
        messages_today = ChatMessage.query.filter(
            ChatMessage.timestamp >= datetime.now().date()
        ).count()

        online_users = ChatUserStatus.query.filter_by(is_online=True).count()

        # Son 7 günlük kayıt istatistikleri
        last_7_days = []
        for i in range(6, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            count = User.query.filter(
                db.func.date(User.created_at) == date
            ).count()
            last_7_days.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })

        # Topluluk kategorileri dağılımı
        categories = db.session.query(
            Community.category,
            db.func.count(Community.id)
        ).group_by(Community.category).all()

        category_distribution = [
            {'category': cat or 'Diğer', 'count': count}
            for cat, count in categories
        ]

        # Kişilik tipleri dağılımı
        personality_types = db.session.query(
            User.personality_type,
            db.func.count(User.id)
        ).filter(User.personality_type.isnot(None)).group_by(User.personality_type).all()

        personality_distribution = [
            {'type': ptype or 'Belirtilmemiş', 'count': count}
            for ptype, count in personality_types
        ]

        return jsonify({
            'success': True,
            'stats': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'completed_tests': completed_tests,
                    'online_now': online_users,
                    'completion_rate': round((completed_tests / total_users * 100) if total_users > 0 else 0, 1)
                },
                'communities': {
                    'total': total_communities,
                    'active': active_communities,
                    'avg_members': round(total_users / total_communities if total_communities > 0 else 0, 1)
                },
                'messages': {
                    'total': total_messages,
                    'today': messages_today,
                    'avg_per_day': round(total_messages / 30 if total_messages > 0 else 0, 1)  # Son 30 gün
                },
                'charts': {
                    'registrations': last_7_days,
                    'categories': category_distribution,
                    'personality': personality_distribution
                }
            }
        })

    except Exception as e:
        logger.error(f"Dashboard istatistik hatası: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================================================
# Kullanıcı Yönetimi
# ==================================================

@admin_bp.route('/users')
@admin_required
def users_page():
    """Kullanıcı yönetim sayfası"""
    return render_template('admin/users.html')


@admin_bp.route('/api/users')
@admin_required
def get_users():
    """Tüm kullanıcıları getir (API)"""
    try:
        # Sayfalama
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        query = User.query

        # Arama
        if search:
            query = query.filter(
                db.or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.university.ilike(f'%{search}%'),
                    User.department.ilike(f'%{search}%')
                )
            )

        # Sıralama
        if order == 'desc':
            query = query.order_by(getattr(User, sort).desc())
        else:
            query = query.order_by(getattr(User, sort).asc())

        # Sayfala
        paginated = query.paginate(page=page, per_page=per_page)

        users = []
        for user in paginated.items:
            user_dict = user.to_dict(include_sensitive=True)

            # Ek bilgiler
            user_dict['communities_count'] = len([m for m in user.communities if m.is_active])
            user_dict['messages_count'] = user.messages.count()
            user_dict['online_status'] = user.is_online()

            # Hobiler
            user_dict['hobbies_list'] = user.get_hobbies_list()

            users.append(user_dict)

        return jsonify({
            'success': True,
            'users': users,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        })

    except Exception as e:
        logger.error(f"Kullanıcı listesi hatası: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def manage_user(user_id):
    """Kullanıcı detayları, güncelleme ve silme"""
    user = User.query.get_or_404(user_id)

    if request.method == 'GET':
        # Detayları getir
        try:
            user_dict = user.to_dict(include_sensitive=True)

            # Topluluk üyelikleri
            user_dict['communities'] = []
            for membership in user.communities:
                if membership.is_active:
                    user_dict['communities'].append({
                        'id': membership.community.id,
                        'name': membership.community.name,
                        'role': membership.role,
                        'joined_at': membership.joined_at.isoformat()
                    })

            # Test sonuçları
            user_dict['test_results'] = {
                'personality_type': user.personality_type,
                'personality_scores': user.personality_scores,
                'hobbies': user.get_hobbies_list()
            }

            # İstatistikler
            user_dict['statistics'] = {
                'total_messages': user.messages.count(),
                'messages_last_week': user.messages.filter(
                    ChatMessage.timestamp >= datetime.now() - timedelta(days=7)
                ).count(),
                'communities_count': len([m for m in user.communities if m.is_active]),
                'last_active': max([m.timestamp for m in user.messages.all()] or [user.created_at]).isoformat()
            }

            return jsonify({'success': True, 'user': user_dict})

        except Exception as e:
            logger.error(f"Kullanıcı detay hatası: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    elif request.method == 'PUT':
        # Kullanıcı güncelle
        try:
            data = request.get_json()

            if 'name' in data:
                user.name = data['name']
            if 'university' in data:
                user.university = data['university']
            if 'department' in data:
                user.department = data['department']
            if 'year' in data:
                user.year = data['year']
            if 'is_active' in data:
                user.is_active = data['is_active']

            user.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"Kullanıcı güncellendi (Admin): {user.email}")
            return jsonify({'success': True, 'message': 'Kullanıcı güncellendi'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Kullanıcı güncelleme hatası: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    elif request.method == 'DELETE':
        # Kullanıcı sil
        try:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"Kullanıcı silindi (Admin): ID {user_id}")
            return jsonify({'success': True, 'message': 'Kullanıcı silindi'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Kullanıcı silme hatası: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500


# ==================================================
# Topluluk Yönetimi
# ==================================================

@admin_bp.route('/communities')
@admin_required
def communities_page():
    """Topluluk yönetim sayfası"""
    return render_template('admin/communities.html')


@admin_bp.route('/api/communities')
@admin_required
def get_communities():
    """Tüm toplulukları getir (API)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')

        query = Community.query.filter_by(is_active=True)

        if search:
            query = query.filter(
                db.or_(
                    Community.name.ilike(f'%{search}%'),
                    Community.description.ilike(f'%{search}%'),
                    Community.category.ilike(f'%{search}%')
                )
            )

        paginated = query.paginate(page=page, per_page=per_page)

        communities = []
        for community in paginated.items:
            comm_dict = community.to_dict(include_stats=True)

            # Ek bilgiler
            comm_dict['creator_name'] = community.creator.name if community.creator else 'Bilinmiyor'
            comm_dict['total_messages'] = community.messages.count()
            comm_dict['online_members'] = len(community.get_online_members())

            # Son aktivite
            last_msg = community.messages.order_by(ChatMessage.timestamp.desc()).first()
            comm_dict['last_activity'] = last_msg.timestamp.isoformat() if last_msg else None

            communities.append(comm_dict)

        return jsonify({
            'success': True,
            'communities': communities,
            'total': paginated.total,
            'pages': paginated.pages
        })

    except Exception as e:
        logger.error(f"Topluluk listesi hatası: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================================================
# Test Sonuçları
# ==================================================

@admin_bp.route('/tests')
@admin_required
def tests_page():
    """Test sonuçları sayfası"""
    return render_template('admin/tests.html')


@admin_bp.route('/api/tests/results')
@admin_required
def get_test_results():
    """Test sonuçlarını getir (API)"""
    try:
        # Kişilik testi sonuçları
        personality_stats = db.session.query(
            User.personality_type,
            db.func.count(User.id)
        ).filter(
            User.personality_type.isnot(None)
        ).group_by(User.personality_type).all()

        # En yaygın hobiler
        all_hobbies = []
        users = User.query.filter(User.hobbies.isnot(None)).all()
        for user in users:
            hobbies = user.get_hobbies_list()
            all_hobbies.extend(hobbies)

        from collections import Counter
        hobby_counts = Counter(all_hobbies).most_common(20)

        # Kategori bazlı hobi dağılımı
        hobby_categories = {
            'Teknoloji': ['programlama', 'yazılım', 'ai', 'robotik', 'teknoloji', 'bilgisayar'],
            'Spor': ['futbol', 'basketbol', 'yüzme', 'koşu', 'yoga', 'fitness', 'spor'],
            'Sanat': ['resim', 'müzik', 'fotoğraf', 'dans', 'tiyatro', 'sanat'],
            'Doğa': ['doğa', 'kamp', 'yürüyüş', 'bisiklet', 'açık hava'],
            'Eğitim': ['kitap', 'okuma', 'dil', 'kurs', 'eğitim', 'araştırma']
        }

        category_counts = {cat: 0 for cat in hobby_categories}
        for hobby, count in hobby_counts:
            for cat, keywords in hobby_categories.items():
                if any(keyword in hobby.lower() for keyword in keywords):
                    category_counts[cat] += count
                    break

        return jsonify({
            'success': True,
            'results': {
                'personality_distribution': [
                    {'type': ptype or 'Belirtilmemiş', 'count': count}
                    for ptype, count in personality_stats
                ],
                'top_hobbies': [
                    {'hobby': hobby, 'count': count}
                    for hobby, count in hobby_counts
                ],
                'hobby_categories': [
                    {'category': cat, 'count': count}
                    for cat, count in category_counts.items()
                ],
                'total_tests_completed': User.query.filter_by(is_test_completed=True).count(),
                'completion_rate': round(
                    User.query.filter_by(is_test_completed=True).count() /
                    User.query.count() * 100 if User.query.count() > 0 else 0,
                    1
                )
            }
        })

    except Exception as e:
        logger.error(f"Test sonuçları hatası: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================================================
# Detaylı Analitikler
# ==================================================

@admin_bp.route('/analytics')
@admin_required
def analytics_page():
    """Analitik sayfası"""
    return render_template('admin/analytics.html')


@admin_bp.route('/api/analytics/detailed')
@admin_required
def detailed_analytics():
    """Detaylı analitik verileri"""
    try:
        # Zaman aralığı
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)

        # Günlük aktif kullanıcılar
        daily_active = db.session.query(
            db.func.date(ChatMessage.timestamp).label('date'),
            db.func.count(db.distinct(ChatMessage.user_id)).label('users')
        ).filter(
            ChatMessage.timestamp >= start_date
        ).group_by(
            db.func.date(ChatMessage.timestamp)
        ).all()

        # Günlük mesaj sayıları
        daily_messages = db.session.query(
            db.func.date(ChatMessage.timestamp).label('date'),
            db.func.count(ChatMessage.id).label('count')
        ).filter(
            ChatMessage.timestamp >= start_date
        ).group_by(
            db.func.date(ChatMessage.timestamp)
        ).all()

        # En aktif topluluklar
        active_communities = db.session.query(
            Community.name,
            db.func.count(ChatMessage.id).label('message_count')
        ).join(ChatMessage).filter(
            ChatMessage.timestamp >= start_date
        ).group_by(Community.id).order_by(
            db.func.count(ChatMessage.id).desc()
        ).limit(10).all()

        # En aktif kullanıcılar
        active_users = db.session.query(
            User.name,
            User.email,
            db.func.count(ChatMessage.id).label('message_count')
        ).join(ChatMessage).filter(
            ChatMessage.timestamp >= start_date
        ).group_by(User.id).order_by(
            db.func.count(ChatMessage.id).desc()
        ).limit(10).all()

        return jsonify({
            'success': True,
            'analytics': {
                'daily_active': [
                    {'date': str(d.date), 'users': d.users}
                    for d in daily_active
                ],
                'daily_messages': [
                    {'date': str(m.date), 'count': m.count}
                    for m in daily_messages
                ],
                'active_communities': [
                    {'name': c.name, 'message_count': c.message_count}
                    for c in active_communities
                ],
                'active_users': [
                    {'name': u.name, 'email': u.email, 'message_count': u.message_count}
                    for u in active_users
                ],
                'period_days': days
            }
        })

    except Exception as e:
        logger.error(f"Detaylı analitik hatası: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================================================
# Veritabanı Yönetimi
# ==================================================

@admin_bp.route('/api/db/backup', methods=['POST'])
@admin_required
def backup_database():
    """Veritabanı yedeği al"""
    try:
        import os
        import shutil
        from datetime import datetime

        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/friendzone_backup_{timestamp}.db'

        # SQLite için
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            shutil.copy2(db_path, backup_file)

        logger.info(f"Veritabanı yedeği alındı: {backup_file}")

        return jsonify({
            'success': True,
            'message': 'Veritabanı yedeği alındı',
            'file': backup_file
        })

    except Exception as e:
        logger.error(f"Veritabanı yedekleme hatası: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500