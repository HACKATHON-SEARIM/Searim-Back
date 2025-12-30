from passlib.context import CryptContext

# 비밀번호 해싱 컨텍스트
# bcrypt_sha256: bcrypt의 72바이트 제한을 우회하기 위해 SHA256 사전 해싱 사용
# Python 3.12 + passlib 1.7.4 + bcrypt 3.2.2 호환성 보장
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)
