import openai
import os
import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class GPTService:
    """GPT servisi - OpenAI entegrasyonu"""

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("OPENAI_API_KEY bulunamadı")

    def get_community_suggestions(self, community_data: Dict, members_data: List[Dict],
                                  suggestion_type: str = "general") -> Optional[str]:
        """Topluluk için öneriler al"""
        try:
            if not self.api_key:
                return self._get_fallback_suggestions(community_data, suggestion_type)

            prompt = self._create_suggestion_prompt(community_data, members_data, suggestion_type)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir üniversite öğrenci topluluğu asistanısın. Yardımcı, yaratıcı ve pratik öneriler sun."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )

            suggestion = response.choices[0].message.content.strip()
            logger.info(f"GPT önerisi oluşturuldu: {community_data['name']} - {suggestion_type}")

            return suggestion

        except Exception as e:
            logger.error(f"GPT öneri hatası: {str(e)}")
            return self._get_fallback_suggestions(community_data, suggestion_type)

    def get_icebreaker_questions(self, community_data: Dict, members_data: List[Dict]) -> List[str]:
        """Buz kırıcı sorular oluştur"""
        try:
            if not self.api_key:
                return self._get_fallback_icebreakers()

            prompt = f"""
            Aşağıdaki üniversite topluluğu için eğlenceli ve etkileşimli buz kırıcı sorular öner:

            Topluluk: {community_data['name']}
            Kategori: {community_data.get('category', 'genel')}
            Üye Sayısı: {len(members_data)}

            Lütfen 5 farklı buz kırıcı soru öner. Sorular:
            - Eğlenceli ve hafif olsun
            - Kişisel olmayan konular içersin
            - Üyelerin birbirini tanımasını sağlasın
            - Topluluk temasına uygun olsun

            Yanıtı sadece soruları numaralandırarak ver.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir buz kırıcı soru uzmanısın. Eğlenceli ve güvenli sorular üret."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.8
            )

            content = response.choices[0].message.content.strip()
            questions = self._parse_icebreaker_response(content)

            return questions

        except Exception as e:
            logger.error(f"Buz kırıcı oluşturma hatası: {str(e)}")
            return self._get_fallback_icebreakers()

    def get_activity_suggestions(self, community_data: Dict, members_data: List[Dict]) -> Dict:
        """Etkinlik önerileri oluştur"""
        try:
            if not self.api_key:
                return self._get_fallback_activities(community_data)

            # Üyelerin hobilerini topla
            all_hobbies = []
            for member in members_data:
                hobbies = member.get('hobbies', [])
                if hobbies:
                    all_hobbies.extend(hobbies)

            prompt = f"""
            Aşağıdaki üniversite topluluğu için etkinlik önerileri yap:

            Topluluk: {community_data['name']}
            Kategori: {community_data.get('category', 'genel')}
            Üye Hobileri: {', '.join(set(all_hobbies))[:200]}
            Üye Sayısı: {len(members_data)}

            Lütfen 3 farklı etkinlik öner. Her etkinlik için:
            - Etkinlik adı
            - Kısa açıklama (1-2 cümle)
            - Gerekli hazırlık/süre
            - Beklenen katılım ve faydalar

            Öneriler üyelerin ortak ilgi alanlarına uygun olsun.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir etkinlik planlama uzmanısın. Yaratıcı, uygulanabilir ve bütçe dostu etkinlikler öner."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600,
                temperature=0.7
            )

            activities_text = response.choices[0].message.content.strip()
            activities = self._parse_activities_response(activities_text)

            return {
                "activities": activities,
                "raw_text": activities_text
            }

        except Exception as e:
            logger.error(f"Etkinlik öneri hatası: {str(e)}")
            return self._get_fallback_activities(community_data)

    def get_conversation_topics(self, community_data: Dict, members_data: List[Dict]) -> List[str]:
        """Sohbet konusu önerileri oluştur"""
        try:
            if not self.api_key:
                return self._get_fallback_topics()

            prompt = f"""
            Aşağıdaki üniversite topluluğu için sohbet konuları öner:

            Topluluk: {community_data['name']}
            Kategori: {community_data.get('category', 'genel')}
            Üye Sayısı: {len(members_data)}

            Lütfen 5 ilgi çekici sohbet konusu öner. Konular:
            - Güncel ve ilgi çekici olsun
            - Tartışmaya açık olsun
            - Topluluk temasına uygun olsun
            - Üyelerin ortak ilgi alanlarına hitap etsin

            Yanıtı sadece konuları numaralandırarak ver.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir sohbet moderatörüsün. İlgi çekici ve düşündürücü konular öner."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=250,
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            topics = self._parse_topics_response(content)

            return topics

        except Exception as e:
            logger.error(f"Sohbet konusu hatası: {str(e)}")
            return self._get_fallback_topics()

    def _create_suggestion_prompt(self, community_data: Dict, members_data: List[Dict],
                                  suggestion_type: str) -> str:
        """GPT için prompt oluştur"""

        base_prompt = f"""
        Topluluk Bilgileri:
        - Adı: {community_data['name']}
        - Kategori: {community_data.get('category', 'genel')}
        - Açıklama: {community_data.get('description', 'Yok')}
        - Üye Sayısı: {len(members_data)}
        """

        # Üye bilgilerini ekle (ilk 5 üye)
        if members_data:
            base_prompt += "\nÜye Özellikleri (örnekler):"
            for i, member in enumerate(members_data[:5], 1):
                base_prompt += f"""
                - Üye {i}: {member.get('personality', 'Belirtilmemiş')} kişilik, 
                  Hobiler: {', '.join(member.get('hobbies', [])[:3]) or 'Belirtilmemiş'}
                """

        if suggestion_type == 'topic':
            base_prompt += """
            \nLütfen bu topluluk için 3 ilgi çekici sohbet konusu öner. 
            Konular üyelerin ortak ilgi alanlarına uygun olsun.
            """
        elif suggestion_type == 'activity':
            base_prompt += """
            \nLütfen bu topluluk için 3 uygulanabilir etkinlik öner.
            Etkinlikler üyelerin hobileri ve kişilik özelliklerine uygun olsun.
            """
        elif suggestion_type == 'icebreaker':
            base_prompt += """
            \nLütfen bu topluluk için 5 eğlenceli buz kırıcı soru öner.
            Sorular üyelerin birbirini daha iyi tanımasını sağlasın.
            """
        else:  # general
            base_prompt += """
            \nLütfen bu topluluk için genel önerilerde bulun. 
            Topluluğun gelişimi için faydalı tavsiyeler ver.
            """

        return base_prompt

    def _parse_icebreaker_response(self, content: str) -> List[str]:
        """Buz kırıcı yanıtını ayrıştır"""
        lines = content.split('\n')
        questions = []

        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Numara, tire veya bullet işaretini temizle
                question = line.split('.', 1)[-1] if '.' in line else line
                question = question.lstrip(' -•')
                if question and len(question) > 10:  # Anlamlı uzunluk kontrolü
                    questions.append(question)

        return questions[:5] if questions else self._get_fallback_icebreakers()

    def _parse_activities_response(self, content: str) -> List[Dict]:
        """Etkinlik yanıtını ayrıştır"""
        # Basit parsing - gerçek uygulamada daha gelişmiş parsing gerekebilir
        activities = []
        lines = content.split('\n')

        current_activity = {}
        for line in lines:
            line = line.strip()
            if line.lower().startswith('etkinlik') or line.lower().startswith('activity'):
                if current_activity:
                    activities.append(current_activity)
                current_activity = {'name': line}
            elif line.lower().startswith('açıklama') or ':' in line:
                if 'açıklama' in current_activity:
                    current_activity['description'] += ' ' + line
                else:
                    current_activity['description'] = line

        if current_activity:
            activities.append(current_activity)

        return activities if activities else self._get_fallback_activities({})

    def _parse_topics_response(self, content: str) -> List[str]:
        """Konu yanıtını ayrıştır"""
        return self._parse_icebreaker_response(content)

    def _get_fallback_suggestions(self, community_data: Dict, suggestion_type: str) -> str:
        """Fallback önerileri"""
        fallbacks = {
            'general': f"{community_data['name']} topluluğu için öneriler: Düzenli buluşmalar yapın, ortak projeler geliştirin, üyeler arası iletişimi güçlendirin.",
            'topic': "Önerilen sohbet konuları: 1) Gelecekteki teknoloji trendleri 2) Üniversite deneyimleri 3) Kariyer planları",
            'activity': "Önerilen etkinlikler: 1) Haftalık buluşma 2) Ortak proje çalışması 3) Konuk konuşmacı daveti",
            'icebreaker': "Buz kırıcı sorular: 1) En sevdiğiniz ders hangisi? 2) Boş zamanlarınızda ne yaparsınız? 3) Hayalinizdeki kariyer nedir?"
        }
        return fallbacks.get(suggestion_type, fallbacks['general'])

    def _get_fallback_icebreakers(self) -> List[str]:
        """Fallback buz kırıcılar"""
        return [
            "En sevdiğiniz ders hangisi ve neden?",
            "Boş zamanlarınızda ne yapmaktan hoşlanırsınız?",
            "Üniversite hayatınızın en unutulmaz anısı nedir?",
            "Hangi alanda kendinizi geliştirmek istiyorsunuz?",
            "Gelecek 5 yıl içinde neler başarmak istiyorsunuz?"
        ]

    def _get_fallback_activities(self, community_data: Dict) -> Dict:
        """Fallback etkinlikler"""
        return {
            "activities": [
                {
                    "name": "Haftalık Toplantı",
                    "description": "Düzenli buluşmalarla topluluk bağlarını güçlendirin"
                },
                {
                    "name": "Ortak Proje",
                    "description": "Birlikte çalışarak deneyim kazanın"
                },
                {
                    "name": "Konuk Konuşmacı",
                    "description": "Alanında uzman kişileri davet edin"
                }
            ],
            "raw_text": "Fallback etkinlik önerileri"
        }

    def _get_fallback_topics(self) -> List[str]:
        """Fallback sohbet konuları"""
        return [
            "Gelecekteki teknoloji trendleri",
            "Üniversite deneyimleri ve zorluklar",
            "Kariyer planları ve hedefler",
            "Yeni öğrenilen beceriler",
            "Topluluk proje fikirleri"
        ]


# Global servis instance'ı
gpt_service = GPTService()