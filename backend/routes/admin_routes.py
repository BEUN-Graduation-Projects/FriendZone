# backend/routes/admin_routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
from backend.app import db
from backend.models.user_model import User
from backend.models.community_model import Community, CommunityMember
from backend.models.chat_model import ChatMessage
from backend.models.chat_room_model import ChatRoom, ChatUserStatus
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ==================================================
# Admin Decorator - Yetkilendirme
# ==================================================

def admin_required(f):
    """Admin yetkisi kontrolü decorator'ı"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
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
    return render_template('admin/index.html', now=datetime.now())


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
                    'avg_per_day': round(total_messages / 30 if total_messages > 0 else 0, 1)
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
    return render_template('admin/users.html', now=datetime.now())


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

        # Test filtresi
        test_filter = request.args.get('test_filter', 'all')
        if test_filter == 'completed':
            query = query.filter_by(is_test_completed=True)
        elif test_filter == 'not_completed':
            query = query.filter_by(is_test_completed=False)

        # Status filtresi
        status_filter = request.args.get('status_filter', 'all')
        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)

        # Sıralama
        if order == 'desc':
            query = query.order_by(getattr(User, sort).desc())
        else:
            query = query.order_by(getattr(User, sort).asc())

        # Sayfala
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        users = []
        for user in paginated.items:
            user_dict = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'university': user.university,
                'department': user.department,
                'year': user.year,
                'personality_type': user.personality_type,
                'hobbies_list': user.get_hobbies_list() if hasattr(user, 'get_hobbies_list') else [],
                'communities_count': len([m for m in user.communities if m.is_active]) if hasattr(user,
                                                                                                  'communities') else 0,
                'messages_count': user.messages.count() if hasattr(user, 'messages') else 0,
                'is_active': user.is_active,
                'is_test_completed': user.is_test_completed,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
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
            user_dict = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'university': user.university,
                'department': user.department,
                'year': user.year,
                'personality_type': user.personality_type,
                'personality_scores': user.personality_scores,
                'hobbies_list': user.get_hobbies_list() if hasattr(user, 'get_hobbies_list') else [],
                'is_active': user.is_active,
                'is_test_completed': user.is_test_completed,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }

            # Topluluk üyelikleri
            user_dict['communities'] = []
            if hasattr(user, 'communities'):
                for membership in user.communities:
                    if membership.is_active and membership.community:
                        user_dict['communities'].append({
                            'id': membership.community.id,
                            'name': membership.community.name,
                            'role': membership.role,
                            'joined_at': membership.joined_at.isoformat() if membership.joined_at else None
                        })

            # İstatistikler
            user_dict['statistics'] = {
                'total_messages': user.messages.count() if hasattr(user, 'messages') else 0,
                'communities_count': len(user_dict['communities'])
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
    return render_template('admin/communities.html', now=datetime.now())


@admin_bp.route('/api/communities')
@admin_required
def get_communities():
    """Tüm toplulukları getir (API)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', 'all')
        status = request.args.get('status', 'all')

        query = Community.query

        if search:
            query = query.filter(
                db.or_(
                    Community.name.ilike(f'%{search}%'),
                    Community.description.ilike(f'%{search}%')
                )
            )

        if category != 'all':
            query = query.filter_by(category=category)

        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        communities = []
        for community in paginated.items:
            # Aktif üye sayısını hesapla
            active_members = len([m for m in community.members if m.is_active]) if hasattr(community, 'members') else 0

            comm_dict = {
                'id': community.id,
                'name': community.name,
                'description': community.description,
                'category': community.category,
                'tags': community.tags or [],
                'compatibility_score': community.compatibility_score or 0,
                'max_members': community.max_members,
                'current_member_count': active_members,
                'is_active': community.is_active,
                'creator_name': community.creator.name if community.creator else 'Bilinmiyor',
                'created_at': community.created_at.isoformat() if community.created_at else None,
                'total_messages': community.messages.count() if hasattr(community, 'messages') else 0,
                'online_members': 0
            }

            # Online üye sayısını hesapla
            try:
                if hasattr(community, 'members'):
                    for member in community.members:
                        if member.is_active and hasattr(member, 'user') and member.user:
                            status = ChatUserStatus.query.filter_by(
                                user_id=member.user_id,
                                is_online=True
                            ).first()
                            if status:
                                comm_dict['online_members'] += 1
            except:
                pass

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


@admin_bp.route('/api/communities/<int:community_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def manage_community(community_id):
    """Topluluk detayları, güncelleme ve silme"""
    community = Community.query.get_or_404(community_id)

    if request.method == 'GET':
        try:
            # Aktif üyeleri getir
            members = []
            if hasattr(community, 'members'):
                for member in community.members:
                    if member.is_active and member.user:
                        members.append({
                            'user_id': member.user_id,
                            'name': member.user.name,
                            'email': member.user.email,
                            'role': member.role,
                            'joined_at': member.joined_at.isoformat() if member.joined_at else None
                        })

            comm_dict = {
                'id': community.id,
                'name': community.name,
                'description': community.description,
                'category': community.category,
                'tags': community.tags or [],
                'compatibility_score': community.compatibility_score or 0,
                'max_members': community.max_members,
                'current_member_count': len(members),
                'is_active': community.is_active,
                'creator_name': community.creator.name if community.creator else 'Bilinmiyor',
                'created_at': community.created_at.isoformat() if community.created_at else None,
                'members': members,
                'total_messages': community.messages.count() if hasattr(community, 'messages') else 0
            }

            return jsonify({'success': True, 'community': comm_dict})

        except Exception as e:
            logger.error(f"Topluluk detay hatası: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()

            if 'name' in data:
                community.name = data['name']
            if 'description' in data:
                community.description = data['description']
            if 'category' in data:
                community.category = data['category']
            if 'tags' in data:
                community.tags = data['tags']
            if 'max_members' in data:
                community.max_members = data['max_members']
            if 'is_active' in data:
                community.is_active = data['is_active']

            community.updated_at = datetime.utcnow()
            db.session.commit()

            return jsonify({'success': True, 'message': 'Topluluk güncellendi'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Topluluk güncelleme hatası: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    elif request.method == 'DELETE':
        try:
            db.session.delete(community)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Topluluk silindi'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Topluluk silme hatası: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500


# ==================================================
# Test Sonuçları
# ==================================================

@admin_bp.route('/tests')
@admin_required
def tests_page():
    """Test sonuçları sayfası"""
    return render_template('admin/tests.html', now=datetime.now())


@admin_bp.route('/api/tests/results')
@admin_required
def get_test_results():
    """Test sonuçlarını getir (API)"""
    try:
        total_users = User.query.count()
        completed_tests = User.query.filter_by(is_test_completed=True).count()

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
            if hasattr(user, 'get_hobbies_list'):
                hobbies = user.get_hobbies_list()
                if isinstance(hobbies, list):
                    all_hobbies.extend(hobbies)

        from collections import Counter
        hobby_counts = Counter(all_hobbies).most_common(20)

        # Kategori bazlı hobi dağılımı
        hobby_categories = {
            'Teknoloji': ['programlama', 'yazılım', 'ai', 'robotik', 'teknoloji', 'bilgisayar', 'kodlama'],
            'Spor': ['futbol', 'basketbol', 'yüzme', 'koşu', 'yoga', 'fitness', 'spor', 'voleybol', 'tenis'],
            'Sanat': ['resim', 'müzik', 'fotoğraf', 'dans', 'tiyatro', 'sanat', 'çizim', 'enstrüman'],
            'Doğa': ['doğa', 'kamp', 'yürüyüş', 'bisiklet', 'açık hava', 'dağcılık'],
            'Eğitim': ['kitap', 'okuma', 'dil', 'kurs', 'eğitim', 'araştırma', 'akademik'],
            'Sosyal': ['gönüllülük', 'organizasyon', 'network', 'mentorluk', 'etkinlik']
        }

        category_counts = {cat: 0 for cat in hobby_categories}
        for hobby, count in hobby_counts[:50]:  # İlk 50 hobiyi al
            hobby_lower = hobby.lower() if isinstance(hobby, str) else ''
            for cat, keywords in hobby_categories.items():
                if any(keyword in hobby_lower for keyword in keywords):
                    category_counts[cat] += count
                    break

        return jsonify({
            'success': True,
            'results': {
                'total_users': total_users,
                'total_tests_completed': completed_tests,
                'completion_rate': round((completed_tests / total_users * 100) if total_users > 0 else 0, 1),
                'personality_distribution': [
                    {'type': ptype or 'Belirtilmemiş', 'count': count}
                    for ptype, count in personality_stats
                ],
                'top_hobbies': [
                    {'hobby': hobby, 'count': count, 'category': 'Diğer'}
                    for hobby, count in hobby_counts[:15]
                ],
                'hobby_categories': [
                    {'category': cat, 'count': count}
                    for cat, count in category_counts.items()
                ]
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
    return render_template('admin/analytics.html', now=datetime.now())


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
        ).join(ChatMessage, ChatMessage.community_id == Community.id).filter(
            ChatMessage.timestamp >= start_date
        ).group_by(Community.id).order_by(
            db.func.count(ChatMessage.id).desc()
        ).limit(10).all()

        # En aktif kullanıcılar
        active_users = db.session.query(
            User.name,
            User.email,
            db.func.count(ChatMessage.id).label('message_count')
        ).join(ChatMessage, ChatMessage.user_id == User.id).filter(
            ChatMessage.timestamp >= start_date
        ).group_by(User.id).order_by(
            db.func.count(ChatMessage.id).desc()
        ).limit(10).all()

        # Saatlik dağılım
        hourly_distribution = [0] * 24
        hourly_data = db.session.query(
            db.func.strftime('%H', ChatMessage.timestamp).label('hour'),
            db.func.count(ChatMessage.id).label('count')
        ).filter(
            ChatMessage.timestamp >= start_date
        ).group_by('hour').all()

        for hour, count in hourly_data:
            if hour and 0 <= int(hour) < 24:
                hourly_distribution[int(hour)] = count

        # Ortalamalar
        total_users = User.query.count()
        total_communities = Community.query.filter_by(is_active=True).count()
        total_msgs = sum([m.count for m in daily_messages])

        averages = {
            'per_user': round(total_msgs / total_users if total_users > 0 else 0, 1),
            'per_community': round(total_msgs / total_communities if total_communities > 0 else 0, 1)
        }

        return jsonify({
            'success': True,
            'analytics': {
                'daily_active': [{'date': str(d.date), 'users': d.users} for d in daily_active],
                'daily_messages': [{'date': str(m.date), 'count': m.count} for m in daily_messages],
                'active_communities': [{'name': c.name, 'message_count': c.message_count} for c in active_communities],
                'active_users': [{'name': u.name, 'email': u.email, 'message_count': u.message_count} for u in
                                 active_users],
                'hourly_distribution': hourly_distribution,
                'averages': averages,
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
        db_path = 'friendzone.db'
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_file)
            logger.info(f"Veritabanı yedeği alındı: {backup_file}")
            return jsonify({
                'success': True,
                'message': 'Veritabanı yedeği alındı',
                'file': backup_file
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Veritabanı dosyası bulunamadı'
            }), 404

    except Exception as e:
        logger.error(f"Veritabanı yedekleme hatası: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================================================
# Export İşlemleri
# ==================================================

@admin_bp.route('/api/users/export')
@admin_required
def export_users():
    """Kullanıcıları CSV olarak dışa aktar"""
    try:
        import csv
        from flask import Response

        users = User.query.all()

        # CSV oluştur
        output = []
        headers = ['ID', 'İsim', 'Email', 'Üniversite', 'Bölüm', 'Sınıf', 'Kişilik Tipi', 'Hobiler', 'Aktif',
                   'Kayıt Tarihi']
        output.append(','.join(headers))

        for user in users:
            hobbies = ', '.join(user.get_hobbies_list()) if hasattr(user, 'get_hobbies_list') else ''
            row = [
                str(user.id),
                user.name,
                user.email,
                user.university or '',
                user.department or '',
                str(user.year) if user.year else '',
                user.personality_type or '',
                hobbies,
                'Evet' if user.is_active else 'Hayır',
                user.created_at.strftime('%Y-%m-%d') if user.created_at else ''
            ]
            # CSV formatına uygun hale getir (tırnak içine al)
            row = [f'"{cell}"' if ',' in cell else cell for cell in row]
            output.append(','.join(row))

        return Response(
            '\n'.join(output),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=kullanicilar.csv'}
        )

    except Exception as e:
        logger.error(f"Kullanıcı export hatası: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500