from flask import Blueprint, request, jsonify
import openai
import os
import logging
from backend.models.community_model import Community
from backend.models.user_model import User

logger = logging.getLogger(__name__)

# Blueprint oluştur
assistant_bp = Blueprint('assistant', __name__)

# OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')


@assistant_bp.route('/suggestions', methods=['POST'])
def get_community_suggestions():
    """GPT ile topluluk önerileri al"""
    try:
        data = request.get_json()
        community_id = data.get('community_id')
        suggestion_type = data.get('type', 'general')  # general, topic, activity, icebreaker

        if not community_id:
            return jsonify({
                "success": False,
                "message": "Topluluk ID gereklidir"
            }), 400

        # Topluluğu ve üyelerini getir
        community = Community.query.get(community_id)
        if not community:
            return jsonify({
                "success": False,
                "message": "Topluluk bulunamadı"
            }), 404

        # Üyelerin bilgilerini topla
        members_info = []
        for member in community.members:
            user = member.user
            members_info.append({
                'name': user.name,
                'personality': user.personality_type,
                'hobbies': user.get_hobbies_list(),
                'department': user.department
            })

        # GPT'ye prompt hazırla
        prompt = create_suggestion_prompt(community, members_info, suggestion_type)

        # GPT'den yanıt al
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Sen bir üniversite öğrenci topluluğu asistanısın. Yardımcı ve yaratıcı öneriler sun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        suggestion = response.choices[0].message.content.strip()

        logger.info(f"GPT önerisi oluşturuldu: {community.name} - {suggestion_type}")

        return jsonify({
            "success": True,
            "suggestion": suggestion,
            "type": suggestion_type,
            "community_name": community.name
        })

    except Exception as e:
        logger.error(f"GPT öneri hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Öneri oluşturulamadı"
        }), 500


@assistant_bp.route('/icebreaker', methods=['POST'])
def get_icebreaker():
    """Buz kırıcı soru önerisi al"""
    try:
        data = request.get_json()
        community_id = data.get('community_id')

        if not community_id:
            return jsonify({
                "success": False,
                "message": "Topluluk ID gereklidir"
            }), 400

        community = Community.query.get(community_id)
        if not community:
            return jsonify({
                "success": False,
                "message": "Topluluk bulunamadı"
            }), 404

        # GPT'ye özel buz kırıcı prompt'u
        prompt = f"""
        Aşağıdaki üniversite öğrenci topluluğu için eğlenceli ve etkileşimli buz kırıcı sorular öner:

        Topluluk: {community.name}
        Kategori: {community.category}
        Açıklama: {community.description or 'Yok'}

        Lütfen 3 farklı buz kırıcı soru öner. Sorular topluluk üyelerinin birbirini daha iyi tanımasını sağlasın.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Sen bir buz kırıcı soru uzmanısın. Eğlenceli ve etkileşimli sorular üret."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.8
        )

        icebreakers = response.choices[0].message.content.strip()

        return jsonify({
            "success": True,
            "icebreakers": icebreakers,
            "community_name": community.name
        })

    except Exception as e:
        logger.error(f"Buz kırıcı oluşturma hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Buz kırıcı oluşturulamadı"
        }), 500


@assistant_bp.route('/activity-suggestions', methods=['POST'])
def get_activity_suggestions():
    """Topluluk etkinlik önerileri al"""
    try:
        data = request.get_json()
        community_id = data.get('community_id')

        if not community_id:
            return jsonify({
                "success": False,
                "message": "Topluluk ID gereklidir"
            }), 400

        community = Community.query.get(community_id)
        if not community:
            return jsonify({
                "success": False,
                "message": "Topluluk bulunamadı"
            }), 404

        # Üyelerin hobilerini topla
        all_hobbies = []
        for member in community.members:
            hobbies = member.user.get_hobbies_list()
            all_hobbies.extend(hobbies)

        # GPT'ye etkinlik öneri prompt'u
        prompt = f"""
        Aşağıdaki üniversite topluluğu için etkinlik önerileri yap:

        Topluluk: {community.name}
        Kategori: {community.category}
        Üye Hobileri: {', '.join(set(all_hobbies))}
        Üye Sayısı: {len(community.members)}

        Lütfen 5 farklı etkinlik öner. Her etkinlik için:
        - Etkinlik adı
        - Kısa açıklama
        - Gerekli malzemeler/zaman
        - Beklenen faydalar

        Öneriler üyelerin hobileri ve topluluk kategorisiyle uyumlu olsun.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Sen bir etkinlik planlama uzmanısın. Yaratıcı ve uygulanabilir etkinlikler öner."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )

        activities = response.choices[0].message.content.strip()

        return jsonify({
            "success": True,
            "activities": activities,
            "community_name": community.name
        })

    except Exception as e:
        logger.error(f"Etkinlik öneri hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Etkinlik önerileri oluşturulamadı"
        }), 500


def create_suggestion_prompt(community, members_info, suggestion_type):
    """GPT için prompt oluştur"""

    base_prompt = f"""
    Topluluk Bilgileri:
    - Adı: {community.name}
    - Kategori: {community.category}
    - Açıklama: {community.description or 'Yok'}
    - Üye Sayısı: {len(members_info)}

    Üye Bilgileri:
    """

    for i, member in enumerate(members_info, 1):
        base_prompt += f"""
        Üye {i}:
        - İsim: {member['name']}
        - Kişilik: {member['personality'] or 'Belirtilmemiş'}
        - Hobiler: {', '.join(member['hobbies']) if member['hobbies'] else 'Belirtilmemiş'}
        - Bölüm: {member['department'] or 'Belirtilmemiş'}
        """

    if suggestion_type == 'topic':
        base_prompt += """
        Lütfen bu topluluk için 3 ilgi çekici sohbet konusu öner. 
        Konular üyelerin ortak ilgi alanlarına uygun olsun.
        """
    elif suggestion_type == 'activity':
        base_prompt += """
        Lütfen bu topluluk için 3 uygulanabilir etkinlik öner.
        Etkinlikler üyelerin hobileri ve kişilik özelliklerine uygun olsun.
        """
    elif suggestion_type == 'icebreaker':
        base_prompt += """
        Lütfen bu topluluk için 5 eğlenceli buz kırıcı soru öner.
        Sorular üyelerin birbirini daha iyi tanımasını sağlasın.
        """
    else:  # general
        base_prompt += """
        Lütfen bu topluluk için genel önerilerde bulun. 
        Topluluğun gelişimi için faydalı tavsiyeler ver.
        """

    return base_prompt