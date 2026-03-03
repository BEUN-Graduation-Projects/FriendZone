# backend/models/__init__.py

from backend.models.user_model import User
from backend.models.community_model import Community, CommunityMember
from backend.models.chat_room_model import ChatRoom, ChatUserStatus
from backend.models.chat_model import ChatMessage
from backend.models.similarity_model import UserSimilarity

# Test modelleri (eğer varsa)
try:
    from backend.models.test_model import PersonalityTestResult, HobbyResult
except ImportError:
    PersonalityTestResult = None
    HobbyResult = None

__all__ = [
    'User',
    'Community',
    'CommunityMember',
    'ChatRoom',
    'ChatUserStatus',
    'ChatMessage',
    'UserSimilarity',
]

if PersonalityTestResult:
    __all__.extend(['PersonalityTestResult', 'HobbyResult'])