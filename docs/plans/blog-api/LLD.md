# Low-Level Design: aiworkshop

**Created:** 2026-02-02T16:06:57Z
**Status:** Draft

## 1. Implementation Overview

<!-- AI: Brief summary of implementation approach -->

The blog API will be implemented as a RESTful API using **FastAPI** (Python 3.11+) framework, leveraging the existing `src/api/` structure. The implementation follows a layered architecture:

- **API Layer** (`src/api/`): FastAPI routers for authentication, users, posts, and comments
- **Service Layer** (`src/services/`): Business logic for user, post, and comment operations
- **Repository Layer** (`src/repositories/`): Data access layer with SQLAlchemy ORM
- **Model Layer** (`src/models/`): SQLAlchemy models and Pydantic schemas
- **Middleware Layer** (`src/middleware/`): Authentication, validation, and error handling
- **Database Layer**: PostgreSQL with Alembic for migrations

The implementation will extend the existing `src/api/main.py` file to include all required endpoints, with dependency injection for authentication and database sessions. All code will include comprehensive type hints, docstrings, and will follow PEP 8 style guidelines.

---

## 2. File Structure

<!-- AI: List all new and modified files with descriptions -->

### New Files

```
src/
  api/
    routes/
      __init__.py                          # Router initialization and registration
      auth.py                              # Authentication endpoints (login)
      users.py                             # User CRUD endpoints
      posts.py                             # Post CRUD endpoints
      comments.py                          # Comment CRUD endpoints
      health.py                            # Health check endpoints
  
  models/
    database.py                            # Database connection and session management
    user.py                                # User SQLAlchemy model
    post.py                                # Post SQLAlchemy model
    comment.py                             # Comment SQLAlchemy model
    __init__.py                            # Model exports
  
  schemas/
    __init__.py                            # Schema exports
    user.py                                # User Pydantic schemas (request/response)
    post.py                                # Post Pydantic schemas
    comment.py                             # Comment Pydantic schemas
    auth.py                                # Authentication schemas
    common.py                              # Common schemas (pagination, errors)
  
  services/
    __init__.py                            # Service exports
    user_service.py                        # User business logic
    post_service.py                        # Post business logic
    comment_service.py                     # Comment business logic
    auth_service.py                        # Authentication logic
  
  repositories/
    __init__.py                            # Repository exports
    user_repository.py                     # User data access
    post_repository.py                     # Post data access
    comment_repository.py                  # Comment data access
  
  middleware/
    __init__.py                            # Middleware exports
    auth_middleware.py                     # JWT authentication dependency
    error_handler.py                       # Global exception handlers
  
  utils/
    __init__.py                            # Utility exports
    password.py                            # Password hashing utilities
    jwt.py                                 # JWT token utilities
    pagination.py                          # Pagination helper functions
  
  config/
    __init__.py                            # Config exports
    settings.py                            # Application configuration (env variables)

migrations/
  env.py                                   # Alembic environment configuration
  script.py.mako                           # Alembic migration template
  versions/
    001_create_users_table.py              # Initial user table migration
    002_create_posts_table.py              # Post table migration
    003_create_comments_table.py           # Comment table migration

tests/
  conftest.py                              # Pytest fixtures and configuration
  test_auth.py                             # Authentication endpoint tests
  test_users.py                            # User endpoint tests
  test_posts.py                            # Post endpoint tests
  test_comments.py                         # Comment endpoint tests
  unit/
    test_user_service.py                   # User service unit tests
    test_post_service.py                   # Post service unit tests
    test_comment_service.py                # Comment service unit tests
    test_auth_service.py                   # Auth service unit tests
    test_password_utils.py                 # Password utility tests
    test_jwt_utils.py                      # JWT utility tests
  integration/
    test_user_flow.py                      # End-to-end user flows
    test_post_flow.py                      # End-to-end post flows
    test_comment_flow.py                   # End-to-end comment flows

alembic.ini                                # Alembic configuration file
.env.example                               # Example environment variables
docker-compose.yml                         # Docker services (app + PostgreSQL)
Dockerfile                                 # Application container definition
```

### Modified Files

```
src/api/main.py                            # Updated to register all routers and middleware
requirements.txt                           # Add FastAPI, SQLAlchemy, Alembic, etc.
README.md                                  # Add blog API documentation
.gitignore                                 # Add .env, __pycache__, alembic versions
```

---

## 3. Detailed Component Designs

<!-- AI: For each major component from HLD, provide detailed design -->

### 3.1 Authentication Module

**File:** `src/utils/jwt.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from src.config.settings import settings

class JWTManager:
    """Handles JWT token generation and validation."""
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generate JWT access token.
        
        Args:
            data: Payload data (must include 'sub' for user ID)
            expires_delta: Token expiration time (default: 24 hours)
        
        Returns:
            Encoded JWT token string
        """
        
    def decode_token(self, token: str) -> dict:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload dictionary
        
        Raises:
            JWTError: If token is invalid or expired
        """
```

**File:** `src/utils/password.py`

```python
from passlib.context import CryptContext

class PasswordManager:
    """Handles password hashing and verification."""
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a plaintext password using bcrypt.
        
        Args:
            password: Plaintext password
        
        Returns:
            Hashed password string
        """
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a hash.
        
        Args:
            plain_password: Plaintext password to verify
            hashed_password: Stored password hash
        
        Returns:
            True if password matches, False otherwise
        """
```

**File:** `src/middleware/auth_middleware.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.user import User
from src.utils.jwt import JWTManager

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to extract and validate current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
    
    Returns:
        Authenticated User model instance
    
    Raises:
        HTTPException: 401 if token invalid or user not found
    """
```

### 3.2 User Service

**File:** `src/services/user_service.py`

```python
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate
from src.utils.password import PasswordManager

class UserService:
    """Business logic for user operations."""
    
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with validation.
        
        Args:
            user_data: User creation schema
        
        Returns:
            Created User model
        
        Raises:
            HTTPException: 400 if username/email already exists
        """
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
    
    def update_user(self, user_id: int, user_data: UserUpdate, current_user: User) -> User:
        """
        Update user profile with authorization check.
        
        Args:
            user_id: User ID to update
            user_data: Update data
            current_user: Currently authenticated user
        
        Returns:
            Updated User model
        
        Raises:
            HTTPException: 403 if not authorized, 404 if user not found
        """
    
    def validate_unique_fields(self, username: str, email: str, exclude_user_id: Optional[int] = None) -> None:
        """
        Validate username and email uniqueness.
        
        Raises:
            HTTPException: 400 if username or email already exists
        """
```

### 3.3 Post Service

**File:** `src/services/post_service.py`

```python
from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.models.post import Post
from src.models.user import User
from src.repositories.post_repository import PostRepository
from src.schemas.post import PostCreate, PostUpdate

class PostService:
    """Business logic for post operations."""
    
    def __init__(self, db: Session):
        self.repository = PostRepository(db)
        self.db = db
    
    def create_post(self, post_data: PostCreate, author: User) -> Post:
        """
        Create a new blog post.
        
        Args:
            post_data: Post creation schema
            author: Author User model
        
        Returns:
            Created Post model
        """
    
    def get_posts(self, page: int = 1, limit: int = 20) -> Tuple[List[Post], int]:
        """
        Get paginated list of posts.
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page (max 100)
        
        Returns:
            Tuple of (posts list, total count)
        """
    
    def get_post_by_id(self, post_id: int) -> Post:
        """
        Get single post by ID.
        
        Raises:
            HTTPException: 404 if post not found
        """
    
    def update_post(self, post_id: int, post_data: PostUpdate, current_user: User) -> Post:
        """
        Update post with ownership authorization.
        
        Args:
            post_id: Post ID to update
            post_data: Update data
            current_user: Currently authenticated user
        
        Returns:
            Updated Post model
        
        Raises:
            HTTPException: 403 if not author, 404 if not found
        """
    
    def delete_post(self, post_id: int, current_user: User) -> None:
        """
        Delete post with ownership authorization.
        
        Raises:
            HTTPException: 403 if not author, 404 if not found
        """
    
    def check_ownership(self, post: Post, user: User) -> None:
        """
        Verify user owns the post.
        
        Raises:
            HTTPException: 403 if user is not the post author
        """
```

### 3.4 Comment Service

**File:** `src/services/comment_service.py`

```python
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.models.comment import Comment
from src.models.user import User
from src.repositories.comment_repository import CommentRepository
from src.repositories.post_repository import PostRepository
from src.schemas.comment import CommentCreate, CommentUpdate

class CommentService:
    """Business logic for comment operations."""
    
    def __init__(self, db: Session):
        self.repository = CommentRepository(db)
        self.post_repository = PostRepository(db)
        self.db = db
    
    def create_comment(self, post_id: int, comment_data: CommentCreate, author: User) -> Comment:
        """
        Create comment on a post.
        
        Args:
            post_id: Target post ID
            comment_data: Comment creation schema
            author: Author User model
        
        Returns:
            Created Comment model
        
        Raises:
            HTTPException: 404 if post not found
        """
    
    def get_comments_by_post(self, post_id: int) -> List[Comment]:
        """
        Get all comments for a post.
        
        Args:
            post_id: Post ID
        
        Returns:
            List of Comment models ordered by createdAt
        
        Raises:
            HTTPException: 404 if post not found
        """
    
    def update_comment(self, comment_id: int, comment_data: CommentUpdate, current_user: User) -> Comment:
        """
        Update comment with ownership authorization.
        
        Raises:
            HTTPException: 403 if not author, 404 if not found
        """
    
    def delete_comment(self, comment_id: int, current_user: User) -> None:
        """
        Delete comment with ownership authorization.
        
        Raises:
            HTTPException: 403 if not author, 404 if not found
        """
```

### 3.5 Repository Layer

**File:** `src/repositories/user_repository.py`

```python
from typing import Optional
from sqlalchemy.orm import Session
from src.models.user import User

class UserRepository:
    """Data access layer for User model."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        """Insert user into database."""
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
    
    def update(self, user: User) -> User:
        """Update existing user."""
    
    def exists_by_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email exists."""
    
    def exists_by_username(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """Check if username exists."""
```

**File:** `src/repositories/post_repository.py`

```python
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.post import Post

class PostRepository:
    """Data access layer for Post model."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, post: Post) -> Post:
        """Insert post into database."""
    
    def get_by_id(self, post_id: int) -> Optional[Post]:
        """Find post by ID with author relationship loaded."""
    
    def get_all_paginated(self, skip: int, limit: int) -> Tuple[List[Post], int]:
        """
        Get paginated posts ordered by createdAt DESC.
        
        Returns:
            Tuple of (posts list, total count)
        """
    
    def update(self, post: Post) -> Post:
        """Update existing post."""
    
    def delete(self, post: Post) -> None:
        """Delete post from database."""
```

**File:** `src/repositories/comment_repository.py`

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.comment import Comment

class CommentRepository:
    """Data access layer for Comment model."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, comment: Comment) -> Comment:
        """Insert comment into database."""
    
    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """Find comment by ID with relationships loaded."""
    
    def get_by_post_id(self, post_id: int) -> List[Comment]:
        """Get all comments for a post ordered by createdAt ASC."""
    
    def update(self, comment: Comment) -> Comment:
        """Update existing comment."""
    
    def delete(self, comment: Comment) -> None:
        """Delete comment from database."""
```

---

## 4. Database Schema Changes

<!-- AI: SQL/migration scripts for schema changes -->

### Migration 001: Create Users Table

**File:** `migrations/versions/001_create_users_table.py`

```python
"""create users table

Revision ID: 001
Revises: 
Create Date: 2026-02-02 16:06:57
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create indexes
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
```

### Migration 002: Create Posts Table

**File:** `migrations/versions/002_create_posts_table.py`

```python
"""create posts table

Revision ID: 002
Revises: 001
Create Date: 2026-02-02 16:06:57
"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create indexes
    op.create_index('ix_posts_author_id', 'posts', ['author_id'])
    op.create_index('ix_posts_created_at', 'posts', ['created_at'])
    op.create_index('ix_posts_title', 'posts', ['title'])

def downgrade() -> None:
    op.drop_index('ix_posts_title', table_name='posts')
    op.drop_index('ix_posts_created_at', table_name='posts')
    op.drop_index('ix_posts_author_id', table_name='posts')
    op.drop_table('posts')
```

### Migration 003: Create Comments Table

**File:** `migrations/versions/003_create_comments_table.py`

```python
"""create comments table

Revision ID: 003
Revises: 002
Create Date: 2026-02-02 16:06:57
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create indexes
    op.create_index('ix_comments_post_id', 'comments', ['post_id'])
    op.create_index('ix_comments_author_id', 'comments', ['author_id'])
    op.create_index('ix_comments_post_id_created_at', 'comments', ['post_id', 'created_at'])

def downgrade() -> None:
    op.drop_index('ix_comments_post_id_created_at', table_name='comments')
    op.drop_index('ix_comments_author_id', table_name='comments')
    op.drop_index('ix_comments_post_id', table_name='comments')
    op.drop_table('comments')
```

### SQLAlchemy Models

**File:** `src/models/user.py`

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
```

**File:** `src/models/post.py`

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.database import Base

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
```

**File:** `src/models/comment.py`

```python
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.database import Base

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    
    __table_args__ = (
        Index('ix_comments_post_id_created_at', 'post_id', 'created_at'),
    )
```

**File:** `src/models/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from src.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    """
    Dependency for database session.
    Yields session and ensures cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 5. API Implementation Details

<!-- AI: For each API endpoint, specify handler logic, validation, error handling -->

### Authentication Endpoints

**File:** `src/api/routes/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.schemas.auth import LoginRequest, LoginResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns:
        - **token**: JWT access token
        - **user**: User profile (without password)
    
    Raises:
        - 401: Invalid credentials
    """
    service = AuthService(db)
    return service.authenticate_user(credentials.email, credentials.password)
```

**File:** `src/services/auth_service.py`

```python
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.repositories.user_repository import UserRepository
from src.utils.password import PasswordManager
from src.utils.jwt import JWTManager
from src.schemas.auth import LoginResponse
from src.schemas.user import UserResponse

class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.jwt_manager = JWTManager()
    
    def authenticate_user(self, email: str, password: str) -> LoginResponse:
        """
        Authenticate user credentials and generate JWT token.
        
        Steps:
        1. Find user by email
        2. Verify password against hash
        3. Generate JWT token with user ID
        4. Return token and user profile
        
        Raises:
            HTTPException: 401 if credentials invalid
        """
        user = self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not PasswordManager.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        token = self.jwt_manager.create_access_token({"sub": str(user.id)})
        
        return LoginResponse(
            token=token,
            user=UserResponse.from_orm(user)
        )
```

### User Endpoints

**File:** `src/api/routes/users.py`

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.user import User
from src.middleware.auth_middleware import get_current_user
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Validation:
    - Username: 3-50 characters, alphanumeric + underscore
    - Email: Valid email format
    - Password: Minimum 8 characters
    - Username and email must be unique
    
    Steps:
    1. Validate input schema (Pydantic)
    2. Check username/email uniqueness
    3. Hash password with bcrypt
    4. Create user record
    5. Return user profile (without password)
    
    Raises:
        - 400: Validation error or duplicate username/email
    """
    service = UserService(db)
    return service.create_user(user_data)

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user profile by ID.
    
    Public endpoint - no authentication required.
    
    Raises:
        - 404: User not found
    """
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    
    Authorization: User can only update their own profile.
    
    Steps:
    1. Verify authenticated user ID matches user_id
    2. Validate new username/email uniqueness (if changed)
    3. Update user record
    4. Return updated profile
    
    Raises:
        - 401: Not authenticated
        - 403: Not authorized (trying to update another user)
        - 404: User not found
        - 400: Validation error or duplicate username/email
    """
    service = UserService(db)
    return service.update_user(user_id, user_data, current_user)
```

### Post Endpoints

**File:** `src/api/routes/posts.py`

```python
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.user import User
from src.middleware.auth_middleware import get_current_user
from src.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from src.services.post_service import PostService

router = APIRouter(prefix="/api/posts", tags=["posts"])

@router.get("", response_model=PostListResponse, status_code=status.HTTP_200_OK)
async def list_posts(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all posts with pagination.
    
    Public endpoint - no authentication required.
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    
    Returns:
    - data: List of posts with author information
    - pagination: Page metadata (page, limit, total, totalPages)
    
    Posts ordered by created_at DESC (newest first).
    """
    service = PostService(db)
    posts, total = service.get_posts(page, limit)
    
    return PostListResponse(
        data=[PostResponse.from_orm(post) for post in posts],
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": (total + limit - 1) // limit
        }
    )

@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single post by ID.
    
    Public endpoint - includes author information.
    
    Raises:
        - 404: Post not found
    """
    service = PostService(db)
    return service.get_post_by_id(post_id)

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new blog post.
    
    Authentication required.
    
    Validation:
    - title: 1-255 characters, required
    - content: Non-empty text, required
    
    Steps:
    1. Validate input (Pydantic)
    2. Set author_id to authenticated user
    3. Create post record
    4. Return post with author info
    
    Raises:
        - 401: Not authenticated
        - 400: Validation error
    """
    service = PostService(db)
    return service.create_post(post_data, current_user)

@router.put("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update existing post.
    
    Authorization: Only post author can update.
    
    Steps:
    1. Fetch post by ID
    2. Verify current_user.id == post.author_id
    3. Update title and/or content
    4. Return updated post
    
    Raises:
        - 401: Not authenticated
        - 403: Not authorized (not the author)
        - 404: Post not found
        - 400: Validation error
    """
    service = PostService(db)
    return service.update_post(post_id, post_data, current_user)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete post.
    
    Authorization: Only post author can delete.
    Cascade deletion: All comments on the post are also deleted.
    
    Raises:
        - 401: Not authenticated
        - 403: Not authorized (not the author)
        - 404: Post not found
    """
    service = PostService(db)
    service.delete_post(post_id, current_user)
```

### Comment Endpoints

**File:** `src/api/routes/comments.py`

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from src.models.database import get_db
from src.models.user import User
from src.middleware.auth_middleware import get_current_user
from src.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from src.services.comment_service import CommentService

router = APIRouter(tags=["comments"])

@router.get("/api/posts/{post_id}/comments", response_model=List[CommentResponse], status_code=status.HTTP_200_OK)
async def list_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    List all comments for a post.
    
    Public endpoint.
    Comments ordered by created_at ASC (oldest first).
    
    Raises:
        - 404: Post not found
    """
    service = CommentService(db)
    comments = service.get_comments_by_post(post_id)
    return [CommentResponse.from_orm(comment) for comment in comments]

@router.post("/api/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create comment on a post.
    
    Authentication required.
    
    Validation:
    - content: Non-empty text, required
    - post_id: Post must exist
    
    Steps:
    1. Verify post exists
    2. Set author_id to authenticated user
    3. Create comment record
    4. Return comment with author info
    
    Raises:
        - 401: Not authenticated
        - 404: Post not found
        - 400: Validation error
    """
    service = CommentService(db)
    return service.create_comment(post_id, comment_data, current_user)

@router.put("/api/comments/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update comment.
    
    Authorization: Only comment author can update.
    
    Steps:
    1. Fetch comment by ID
    2. Verify current_user.id == comment.author_id
    3. Update content
    4. Return updated comment
    
    Raises:
        - 401: Not authenticated
        - 403: Not authorized (not the author)
        - 404: Comment not found
        - 400: Validation error
    """
    service = CommentService(db)
    return service.update_comment(comment_id, comment_data, current_user)

@router.delete("/api/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete comment.
    
    Authorization: Only comment author can delete.
    
    Raises:
        - 401: Not authenticated
        - 403: Not authorized (not the author)
        - 404: Comment not found
    """
    service = CommentService(db)
    service.delete_comment(comment_id, current_user)
```

### Health Check Endpoints

**File:** `src/api/routes/health.py`

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.models.database import get_db
from datetime import datetime

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic liveness probe.
    
    Returns:
        - status: "healthy"
        - timestamp: Current UTC timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe with database connectivity check.
    
    Returns:
        - status: "ready"
        - database: "connected"
        - timestamp: Current UTC timestamp
    
    Raises:
        - 503: Database connection failed
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
```

---

## 6. Function Signatures

<!-- AI: Key function/method signatures with parameters and return types -->

### Pydantic Schemas

**File:** `src/schemas/user.py`

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """Schema for user registration request."""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)

class UserUpdate(BaseModel):
    """Schema for user profile update request."""
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    username: str
    email: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserPublicResponse(BaseModel):
    """Schema for public user info (in post/comment responses)."""
    id: int
    username: str
    
    model_config = ConfigDict(from_attributes=True)
```

**File:** `src/schemas/post.py`

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from src.schemas.user import UserPublicResponse

class PostCreate(BaseModel):
    """Schema for post creation request."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)

class PostUpdate(BaseModel):
    """Schema for post update request."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)

class PostResponse(BaseModel):
    """Schema for post response with author info."""
    id: int
    title: str
    content: str
    author: UserPublicResponse
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PostListResponse(BaseModel):
    """Schema for paginated post list response."""
    data: list[PostResponse]
    pagination: dict
```

**File:** `src/schemas/comment.py`

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from src.schemas.user import UserPublicResponse

class CommentCreate(BaseModel):
    """Schema for comment creation request."""
    content: str = Field(..., min_length=1)

class CommentUpdate(BaseModel):
    """Schema for comment update request."""
    content: str = Field(..., min_length=1)

class CommentResponse(BaseModel):
    """Schema for comment response with author info."""
    id: int
    content: str
    author: UserPublicResponse
    post_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

**File:** `src/schemas/auth.py`

```python
from pydantic import BaseModel, EmailStr
from src.schemas.user import UserResponse

class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """Schema for login response."""
    token: str
    user: UserResponse
```

**File:** `src/schemas/common.py`

```python
from pydantic import BaseModel
from typing import List, Optional

class ErrorDetail(BaseModel):
    """Schema for validation error detail."""
    field: str
    message: str

class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: dict
    
    @classmethod
    def create(cls, code: str, message: str, details: Optional[List[ErrorDetail]] = None):
        return cls(error={
            "code": code,
            "message": message,
            "details": details or []
        })
```

### Configuration

**File:** `src/config/settings.py`

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/blogapi"
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Security
    BCRYPT_ROUNDS: int = 10
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 7. State Management

<!-- AI: How application state is managed (Redux, Context, database) -->

### Application State Management

The blog API follows a **stateless architecture** with no server-side session management:

1. **Authentication State:**
   - **Client-Side:** JWT tokens stored in client (localStorage/cookies)
   - **Server-Side:** Stateless validation via JWT signature verification
   - No session store (Redis/database) required
   - Token contains user ID payload, decoded on each request

2. **Database State:**
   - **Primary State Store:** PostgreSQL database
   - **Connection Pooling:** SQLAlchemy connection pool (10 base connections, 20 max overflow)
   - **Session Management:** Request-scoped database sessions via `get_db()` dependency
   - **Transaction Scope:** Each request creates a new session, committed/rolled back at end

3. **Request State:**
   - **Dependency Injection:** FastAPI dependencies provide request-scoped state
   - `get_db()`: Database session for the request
   - `get_current_user()`: Authenticated user for the request
   - State cleanup via try/finally in dependencies

4. **Application State:**
   - **Configuration:** Loaded from environment variables at startup via Pydantic Settings
   - **Immutable:** Settings object is read-only after initialization
   - **No In-Memory Cache:** MVP does not include Redis or in-memory caching

5. **Concurrency Model:**
   - **Async Handlers:** FastAPI async endpoints for I/O-bound operations
   - **Thread Safety:** SQLAlchemy sessions are not shared between requests
   - **No Global Mutable State:** All state is request-scoped or database-backed

### State Flow Diagram

```
Client Request → FastAPI Router → Dependencies (DB Session, Current User)
                                      ↓
                              Service Layer (Business Logic)
                                      ↓
                              Repository Layer (Data Access)
                                      ↓
                              PostgreSQL Database
                                      ↓
                              Response (JSON)
```

### Horizontal Scaling Implications

Since the application is stateless:
- Any instance can handle any request (no sticky sessions)
- Load balancer can use round-robin or least-connections
- Scaling involves adding/removing application containers
- Shared state is entirely in PostgreSQL (single source of truth)

---

## 8. Error Handling Strategy

<!-- AI: Error codes, exception handling, user-facing messages -->

### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "fieldName",
        "message": "Field-specific error message"
      }
    ]
  }
}
```

### Error Codes and HTTP Status Mapping

**File:** `src/middleware/error_handler.py`

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from jose import JWTError
from typing import Union

class ErrorCode:
    """Standard error codes."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"

def register_error_handlers(app: FastAPI):
    """Register global exception handlers."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors (400)."""
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"][1:])
            details.append({
                "field": field,
                "message": error["msg"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": ErrorCode.VALIDATION_ERROR,
                    "message": "Invalid request data",
                    "details": details
                }
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors (400/409)."""
        error_message = str(exc.orig)
        
        # Detect unique constraint violations
        if "duplicate key" in error_message.lower() or "unique constraint" in error_message.lower():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": {
                        "code": ErrorCode.DUPLICATE_RESOURCE,
                        "message": "A resource with this value already exists",
                        "details": []
                    }
                }
            )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": ErrorCode.DATABASE_ERROR,
                    "message": "Database constraint violation",
                    "details": []
                }
            }
        )
    
    @app.exception_handler(JWTError)
    async def jwt_error_handler(request: Request, exc: JWTError):
        """Handle JWT token errors (401)."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "code": ErrorCode.AUTHENTICATION_FAILED,
                    "message": "Invalid or expired authentication token",
                    "details": []
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors (500)."""
        # Log the full exception for debugging
        import logging
        logging.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR,
                    "message": "An internal error occurred",
                    "details": []
                }
            }
        )
```

### Custom HTTPException Usage

Services raise HTTPException with appropriate status codes:

```python
from fastapi import HTTPException, status

# 400 Bad Request - Validation error
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Username already exists"
)

# 401 Unauthorized - Authentication failure
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid email or password"
)

# 403 Forbidden - Authorization failure
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have permission to modify this resource"
)

# 404 Not Found - Resource not found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Post not found"
)
```

### Error Handling in Layers

**Repository Layer:**
- Raises SQLAlchemy exceptions (IntegrityError, etc.)
- Does NOT catch exceptions - let them bubble up

**Service Layer:**
- Catches repository exceptions and converts to HTTPException
- Validates business logic and raises HTTPException with appropriate codes
- Example: Check ownership before update/delete

**API Layer:**
- FastAPI automatically handles HTTPException
- Global exception handlers format error responses
- No try/catch needed in route handlers (handled by middleware)

### Logging Strategy

**File:** `src/config/logging.py`

```python
import logging
import sys
from src.config.settings import settings

def setup_logging():
    """Configure application logging."""
    
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress verbose SQLAlchemy logs in production
    if not settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

**What to Log:**
- INFO: Request/response (endpoint, status, user ID, duration)
- WARNING: Authorization failures, validation errors
- ERROR: Unhandled exceptions, database errors
- DEBUG: SQL queries, detailed request data (development only)

**What NOT to Log:**
- Passwords (plain or hashed)
- JWT tokens
- Full request bodies with sensitive data

---

## 9. Test Plan

### Unit Tests

**File:** `tests/unit/test_password_utils.py`

```python
import pytest
from src.utils.password import PasswordManager

def test_hash_password():
    """Test password hashing generates different hashes for same password."""
    password = "testPassword123"
    hash1 = PasswordManager.hash_password(password)
    hash2 = PasswordManager.hash_password(password)
    
    assert hash1 != hash2  # Different salts
    assert hash1.startswith("$2b$")  # bcrypt format

def test_verify_password_correct():
    """Test password verification succeeds with correct password."""
    password = "testPassword123"
    hashed = PasswordManager.hash_password(password)
    
    assert PasswordManager.verify_password(password, hashed) is True

def test_verify_password_incorrect():
    """Test password verification fails with incorrect password."""
    password = "testPassword123"
    hashed = PasswordManager.hash_password(password)
    
    assert PasswordManager.verify_password("wrongPassword", hashed) is False
```

**File:** `tests/unit/test_jwt_utils.py`

```python
import pytest
from datetime import timedelta
from jose import JWTError
from src.utils.jwt import JWTManager

def test_create_access_token():
    """Test JWT token creation."""
    jwt_manager = JWTManager()
    token = jwt_manager.create_access_token({"sub": "123"})
    
    assert isinstance(token, str)
    assert len(token) > 0

def test_decode_valid_token():
    """Test decoding valid JWT token."""
    jwt_manager = JWTManager()
    data = {"sub": "123", "username": "testuser"}
    token = jwt_manager.create_access_token(data)
    
    decoded = jwt_manager.decode_token(token)
    
    assert decoded["sub"] == "123"
    assert decoded["username"] == "testuser"

def test_decode_expired_token():
    """Test decoding expired token raises JWTError."""
    jwt_manager = JWTManager()
    token = jwt_manager.create_access_token(
        {"sub": "123"},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )
    
    with pytest.raises(JWTError):
        jwt_manager.decode_token(token)

def test_decode_invalid_token():
    """Test decoding invalid token raises JWTError."""
    jwt_manager = JWTManager()
    
    with pytest.raises(JWTError):
        jwt_manager.decode_token("invalid.token.here")
```

**File:** `tests/unit/test_user_service.py`

```python
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserUpdate
from src.models.user import User

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def user_service(mock_db):
    return UserService(mock_db)

def test_create_user_success(user_service):
    """Test successful user creation."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    user_service.repository.exists_by_email = Mock(return_value=False)
    user_service.repository.exists_by_username = Mock(return_value=False)
    user_service.repository.create = Mock(return_value=User(
        id=1,
        username="testuser",
        email="test@example.com"
    ))
    
    result = user_service.create_user(user_data)
    
    assert result.username == "testuser"
    assert result.email == "test@example.com"

def test_create_user_duplicate_email(user_service):
    """Test user creation fails with duplicate email."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    user_service.repository.exists_by_email = Mock(return_value=True)
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.create_user(user_data)
    
    assert exc_info.value.status_code == 400
    assert "email" in str(exc_info.value.detail).lower()

def test_update_user_unauthorized(user_service):
    """Test user update fails when not authorized."""
    user_data = UserUpdate(username="newusername")
    current_user = User(id=1, username="user1")
    target_user_id = 2
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.update_user(target_user_id, user_data, current_user)
    
    assert exc_info.value.status_code == 403
```

**File:** `tests/unit/test_post_service.py`

```python
import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from src.services.post_service import PostService
from src.schemas.post import PostCreate, PostUpdate
from src.models.post import Post
from src.models.user import User

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def post_service(mock_db):
    return PostService(mock_db)

def test_create_post_success(post_service):
    """Test successful post creation."""
    post_data = PostCreate(title="Test Post", content="Test content")
    author = User(id=1, username="author")
    
    post_service.repository.create = Mock(return_value=Post(
        id=1,
        title="Test Post",
        content="Test content",
        author_id=1
    ))
    
    result = post_service.create_post(post_data, author)
    
    assert result.title == "Test Post"
    assert result.author_id == 1

def test_update_post_not_author(post_service):
    """Test post update fails when user is not author."""
    post = Post(id=1, title="Test", content="Content", author_id=1)
    current_user = User(id=2, username="otheruser")
    
    post_service.repository.get_by_id = Mock(return_value=post)
    
    with pytest.raises(HTTPException) as exc_info:
        post_service.update_post(1, PostUpdate(title="New Title"), current_user)
    
    assert exc_info.value.status_code == 403

def test_delete_post_not_found(post_service):
    """Test post deletion fails when post not found."""
    current_user = User(id=1, username="user")
    
    post_service.repository.get_by_id = Mock(return_value=None)
    
    with pytest.raises(HTTPException) as exc_info:
        post_service.delete_post(999, current_user)
    
    assert exc_info.value.status_code == 404
```

### Integration Tests

**File:** `tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.main import app
from src.models.database import Base, get_db
from src.config.settings import settings

# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Create user and return authentication headers."""
    # Register user
    client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
```

**File:** `tests/test_auth.py`

```python
import pytest
from fastapi import status

def test_login_success(client):
    """Test successful login returns token."""
    # Register user
    client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.json()
    assert "user" in response.json()
    assert response.json()["user"]["email"] == "test@example.com"

def test_login_invalid_email(client):
    """Test login with non-existent email fails."""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_invalid_password(client):
    """Test login with wrong password fails."""
    client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

**File:** `tests/test_users.py`

```python
import pytest
from fastapi import status

def test_register_user_success(client):
    """Test user registration creates user."""
    response = client.post("/api/users", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    })
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"
    assert "password" not in response.json()

def test_register_duplicate_email(client):
    """Test registration with duplicate email fails."""
    client.post("/api/users", json={
        "username": "user1",
        "email": "test@example.com",
        "password": "password123"
    })
    
    response = client.post("/api/users", json={
        "username": "user2",
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_user_profile(client, auth_headers):
    """Test getting user profile."""
    # Get current user ID from auth_headers (parse token or make request)
    response = client.get("/api/users/1")
    
    assert response.status_code == status.HTTP_200_OK
    assert "username" in response.json()

def test_update_user_profile_success(client, auth_headers):
    """Test updating own profile."""
    response = client.put("/api/users/1", json={
        "username": "updateduser"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "updateduser"

def test_update_other_user_profile_forbidden(client, auth_headers):
    """Test updating another user's profile fails."""
    # Create second user
    client.post("/api/users", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "password123"
    })
    
    response = client.put("/api/users/2", json={
        "username": "hacked"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
```

**File:** `tests/test_posts.py`

```python
import pytest
from fastapi import status

def test_create_post_success(client, auth_headers):
    """Test authenticated user can create post."""
    response = client.post("/api/posts", json={
        "title": "My First Post",
        "content": "This is the content of my first post."
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == "My First Post"
    assert "author" in response.json()

def test_create_post_unauthenticated(client):
    """Test unauthenticated user cannot create post."""
    response = client.post("/api/posts", json={
        "title": "Test Post",
        "content": "Content"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_list_posts(client, auth_headers):
    """Test listing posts with pagination."""
    # Create some posts
    for i in range(3):
        client.post("/api/posts", json={
            "title": f"Post {i}",
            "content": f"Content {i}"
        }, headers=auth_headers)
    
    response = client.get("/api/posts")
    
    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.json()
    assert "pagination" in response.json()
    assert len(response.json()["data"]) == 3

def test_get_post_by_id(client, auth_headers):
    """Test getting single post."""
    create_response = client.post("/api/posts", json={
        "title": "Test Post",
        "content": "Content"
    }, headers=auth_headers)
    
    post_id = create_response.json()["id"]
    
    response = client.get(f"/api/posts/{post_id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == post_id

def test_update_own_post(client, auth_headers):
    """Test updating own post."""
    create_response = client.post("/api/posts", json={
        "title": "Original Title",
        "content": "Original content"
    }, headers=auth_headers)
    
    post_id = create_response.json()["id"]
    
    response = client.put(f"/api/posts/{post_id}", json={
        "title": "Updated Title"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Title"

def test_delete_own_post(client, auth_headers):
    """Test deleting own post."""
    create_response = client.post("/api/posts", json={
        "title": "Post to Delete",
        "content": "Content"
    }, headers=auth_headers)
    
    post_id = create_response.json()["id"]
    
    response = client.delete(f"/api/posts/{post_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify post is deleted
    get_response = client.get(f"/api/posts/{post_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
```

**File:** `tests/test_comments.py`

```python
import pytest
from fastapi import status

def test_create_comment_success(client, auth_headers):
    """Test creating comment on post."""
    # Create post first
    post_response = client.post("/api/posts", json={
        "title": "Post",
        "content": "Content"
    }, headers=auth_headers)
    post_id = post_response.json()["id"]
    
    # Create comment
    response = client.post(f"/api/posts/{post_id}/comments", json={
        "content": "Great post!"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["content"] == "Great post!"
    assert response.json()["post_id"] == post_id

def test_create_comment_nonexistent_post(client, auth_headers):
    """Test creating comment on non-existent post fails."""
    response = client.post("/api/posts/9999/comments", json={
        "content": "Comment"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_comments_for_post(client, auth_headers):
    """Test listing comments for a post."""
    # Create post
    post_response = client.post("/api/posts", json={
        "title": "Post",
        "content": "Content"
    }, headers=auth_headers)
    post_id = post_response.json()["id"]
    
    # Create comments
    for i in range(3):
        client.post(f"/api/posts/{post_id}/comments", json={
            "content": f"Comment {i}"
        }, headers=auth_headers)
    
    # List comments
    response = client.get(f"/api/posts/{post_id}/comments")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3

def test_update_own_comment(client, auth_headers):
    """Test updating own comment."""
    # Create post and comment
    post_response = client.post("/api/posts", json={
        "title": "Post",
        "content": "Content"
    }, headers=auth_headers)
    post_id = post_response.json()["id"]
    
    comment_response = client.post(f"/api/posts/{post_id}/comments", json={
        "content": "Original comment"
    }, headers=auth_headers)
    comment_id = comment_response.json()["id"]
    
    # Update comment
    response = client.put(f"/api/comments/{comment_id}", json={
        "content": "Updated comment"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "Updated comment"

def test_delete_own_comment(client, auth_headers):
    """Test deleting own comment."""
    # Create post and comment
    post_response = client.post("/api/posts", json={
        "title": "Post",
        "content": "Content"
    }, headers=auth_headers)
    post_id = post_response.json()["id"]
    
    comment_response = client.post(f"/api/posts/{post_id}/comments", json={
        "content": "Comment to delete"
    }, headers=auth_headers)
    comment_id = comment_response.json()["id"]
    
    # Delete comment
    response = client.delete(f"/api/comments/{comment_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
```

### E2E Tests

**File:** `tests/integration/test_user_flow.py`

```python
import pytest
from fastapi import status

def test_complete_user_flow(client):
    """Test complete user registration and profile management flow."""
    # 1. Register user
    register_response = client.post("/api/users", json={
        "username": "e2euser",
        "email": "e2e@example.com",
        "password": "password123"
    })
    assert register_response.status_code == status.HTTP_201_CREATED
    user_id = register_response.json()["id"]
    
    # 2. Login
    login_response = client.post("/api/auth/login", json={
        "email": "e2e@example.com",
        "password": "password123"
    })
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Get profile
    profile_response = client.get(f"/api/users/{user_id}")
    assert profile_response.status_code == status.HTTP_200_OK
    assert profile_response.json()["username"] == "e2euser"
    
    # 4. Update profile
    update_response = client.put(f"/api/users/{user_id}", json={
        "username": "updated_e2euser"
    }, headers=headers)
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["username"] == "updated_e2euser"
```

**File:** `tests/integration/test_post_flow.py`

```python
import pytest
from fastapi import status

def test_complete_post_lifecycle(client, auth_headers):
    """Test complete post creation, update, and deletion flow."""
    # 1. Create post
    create_response = client.post("/api/posts", json={
        "title": "E2E Post",
        "content": "This is an end-to-end test post."
    }, headers=auth_headers)
    assert create_response.status_code == status.HTTP_201_CREATED
    post_id = create_response.json()["id"]
    
    # 2. List posts (verify it appears)
    list_response = client.get("/api/posts")
    assert any(post["id"] == post_id for post in list_response.json()["data"])
    
    # 3. Get single post
    get_response = client.get(f"/api/posts/{post_id}")
    assert get_response.status_code == status.HTTP_200_OK
    
    # 4. Update post
    update_response = client.put(f"/api/posts/{post_id}", json={
        "title": "Updated E2E Post",
        "content": "Updated content"
    }, headers=auth_headers)
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["title"] == "Updated E2E Post"
    
    # 5. Delete post
    delete_response = client.delete(f"/api/posts/{post_id}", headers=auth_headers)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # 6. Verify deleted
    get_deleted_response = client.get(f"/api/posts/{post_id}")
    assert get_deleted_response.status_code == status.HTTP_404_NOT_FOUND
```

**File:** `tests/integration/test_comment_flow.py`

```python
import pytest
from fastapi import status

def test_complete_comment_flow(client, auth_headers):
    """Test complete comment creation, update, and deletion flow."""
    # 1. Create post
    post_response = client.post("/api/posts", json={
        "title": "Post for Comments",
        "content": "Content"
    }, headers=auth_headers)
    post_id = post_response.json()["id"]
    
    # 2. Create comment
    comment_response = client.post(f"/api/posts/{post_id}/comments", json={
        "content": "First comment"
    }, headers=auth_headers)
    assert comment_response.status_code == status.HTTP_201_CREATED
    comment_id = comment_response.json()["id"]
    
    # 3. List comments (verify it appears)
    list_response = client.get(f"/api/posts/{post_id}/comments")
    assert len(list_response.json()) == 1
    
    # 4. Update comment
    update_response = client.put(f"/api/comments/{comment_id}", json={
        "content": "Updated comment"
    }, headers=auth_headers)
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["content"] == "Updated comment"
    
    # 5. Delete comment
    delete_response = client.delete(f"/api/comments/{comment_id}", headers=auth_headers)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # 6. Verify deleted (list should be empty)
    final_list_response = client.get(f"/api/posts/{post_id}/comments")
    assert len(final_list_response.json()) == 0
```

---

## 10. Migration Strategy

<!-- AI: How to migrate from current state to new implementation -->

### Phase 1: Setup and Configuration (Days 1-2)

1. **Environment Setup:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file
   cp .env.example .env
   # Edit .env with actual values (DATABASE_URL, JWT_SECRET, etc.)
   ```

2. **Database Setup:**
   ```bash
   # Start PostgreSQL (Docker Compose)
   docker-compose up -d postgres
   
   # Initialize Alembic
   alembic init migrations
   
   # Run migrations
   alembic upgrade head
   ```

3. **Verify Setup:**
   ```bash
   # Start application
   uvicorn src.api.main:app --reload
   
   # Test health endpoint
   curl http://localhost:8000/api/health
   ```

### Phase 2: Core Implementation (Days 3-8)

1. **Implement Models and Database Layer (Day 3):**
   - Create SQLAlchemy models (User, Post, Comment)
   - Create Alembic migrations
   - Test database connectivity

2. **Implement Authentication (Day 4):**
   - JWT utilities
   - Password hashing utilities
   - Auth middleware
   - Login endpoint

3. **Implement User Module (Day 5):**
   - User repository
   - User service
   - User endpoints (register, get, update)
   - Unit tests

4. **Implement Post Module (Day 6):**
   - Post repository
   - Post service
   - Post endpoints (CRUD)
   - Unit tests

5. **Implement Comment Module (Day 7):**
   - Comment repository
   - Comment service
   - Comment endpoints (CRUD)
   - Unit tests

6. **Error Handling and Validation (Day 8):**
   - Global exception handlers
   - Pydantic schemas validation
   - Error response formatting

### Phase 3: Testing (Days 9-10)

1. **Integration Tests (Day 9):**
   - Write and run integration tests
   - Fix bugs found during testing
   - Test all API endpoints with test client

2. **E2E Tests (Day 10):**
   - Write and run end-to-end flow tests
   - Performance testing (response time < 200ms)
   - Load testing (100 concurrent users)

### Phase 4: Deployment (Days 11-12)

1. **Containerization (Day 11):**
   - Create Dockerfile
   - Create docker-compose.yml
   - Test Docker build and run locally

2. **Production Deployment (Day 12):**
   - Deploy to PaaS (Heroku/Render/Railway) or Cloud VMs
   - Configure production environment variables
   - Run database migrations in production
   - Configure Nginx reverse proxy (if needed)
   - Setup SSL certificates (Let's Encrypt)

3. **Monitoring Setup (Day 12):**
   - Configure logging output
   - Setup health check monitoring (UptimeRobot)
   - Configure alerting (Slack/email)

### Phase 5: Documentation and Handoff (Day 13)

1. **API Documentation:**
   - Generate OpenAPI/Swagger docs
   - Write README with setup instructions
   - Document environment variables

2. **Operational Runbook:**
   - Deployment procedures
   - Rollback procedures
   - Common troubleshooting steps

### Data Migration Considerations

Since this is a new project with no existing data:
- No data migration scripts required
- Initial database setup via Alembic migrations
- Optionally seed test data for development/staging

---

## 11. Rollback Plan

<!-- AI: How to rollback if deployment fails -->

### Rollback Triggers

Rollback should be initiated if:
- Application fails to start (health check fails)
- Critical bug in production (data corruption, security vulnerability)
- Error rate > 10% for 5 minutes
- Database migration failure

### Rollback Procedures

#### Application Rollback (Docker Deployment)

**Step 1: Stop Current Version**
```bash
# Stop running containers
docker-compose down
```

**Step 2: Revert to Previous Image**
```bash
# Pull previous stable image
docker pull <registry>/blog-api:<previous-tag>

# Update docker-compose.yml to use previous tag
# image: <registry>/blog-api:<previous-tag>

# Start previous version
docker-compose up -d
```

**Step 3: Verify Rollback**
```bash
# Check health endpoint
curl https://api.example.com/api/health

# Monitor logs
docker-compose logs -f app

# Check error rates in monitoring dashboard
```

#### Database Rollback (Alembic)

**Option 1: Rollback Migration (If Schema Changed)**
```bash
# Downgrade to previous migration
alembic downgrade -1

# Verify database state
alembic current
```

**Option 2: Restore from Backup (If Data Corrupted)**
```bash
# Stop application
docker-compose stop app

# Restore PostgreSQL from latest backup
pg_restore -d blogapi -C backup_file.sql

# Restart application with previous version
docker-compose up -d
```

#### PaaS Rollback (Heroku/Render/Railway)

**Heroku:**
```bash
# List recent releases
heroku releases

# Rollback to previous release
heroku rollback v123
```

**Render/Railway:**
- Use web dashboard to redeploy previous commit
- Or manually trigger deployment from previous git commit

### Rollback Decision Matrix

| Severity | Error Rate | Action | Approval Required |
|----------|-----------|--------|-------------------|
| Critical | >10% | Immediate rollback | No (automatic) |
| High | 5-10% | Rollback within 15 min | Team lead approval |
| Medium | 1-5% | Investigate, rollback if not fixed in 30 min | Team lead approval |
| Low | <1% | Monitor, fix forward | No rollback |

### Post-Rollback Actions

1. **Incident Report:**
   - Document what went wrong
   - Root cause analysis
   - Steps to prevent recurrence

2. **Hot Fix:**
   - Fix bug in development
   - Test thoroughly
   - Deploy fix as new version

3. **Communication:**
   - Notify stakeholders of rollback
   - Provide ETA for fix deployment
   - Update status page (if applicable)

### Testing Rollback Procedure

Rollback should be tested in staging:
```bash
# Deploy new version to staging
# Intentionally break something
# Execute rollback procedure
# Verify staging returns to working state
```

---

## 12. Performance Considerations

<!-- AI: Performance optimizations, caching, indexing -->

### Database Performance Optimizations

**1. Indexes (Already in Schema):**
```sql
-- Users table
CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_email ON users(email);

-- Posts table
CREATE INDEX ix_posts_author_id ON posts(author_id);
CREATE INDEX ix_posts_created_at ON posts(created_at);
CREATE INDEX ix_posts_title ON posts(title);  -- For search (future)

-- Comments table
CREATE INDEX ix_comments_post_id ON comments(post_id);
CREATE INDEX ix_comments_author_id ON comments(author_id);
CREATE INDEX ix_comments_post_id_created_at ON comments(post_id, created_at);  -- Composite
```

**2. Query Optimization:**

**Use `joinedload` for Eager Loading:**
```python
# In repositories - avoid N+1 queries
from sqlalchemy.orm import joinedload

def get_by_id(self, post_id: int) -> Optional[Post]:
    return self.db.query(Post)\
        .options(joinedload(Post.author))\
        .filter(Post.id == post_id)\
        .first()

def get_all_paginated(self, skip: int, limit: int) -> Tuple[List[Post], int]:
    posts = self.db.query(Post)\
        .options(joinedload(Post.author))\
        .order_by(Post.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    total = self.db.query(func.count(Post.id)).scalar()
    return posts, total
```

**3. Connection Pooling:**
```python
# src/models/database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,        # Verify connections before use
    pool_size=10,              # Base connection pool size
    max_overflow=20,           # Max additional connections
    pool_recycle=3600          # Recycle connections after 1 hour
)
```

**4. Database Query Monitoring:**
```python
# Enable SQL logging in development
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Use EXPLAIN ANALYZE for slow queries
# Example: EXPLAIN ANALYZE SELECT * FROM posts WHERE author_id = 1;
```

### API Performance Optimizations

**1. Response Time Targets:**
- GET endpoints: < 100ms (p95)
- POST/PUT endpoints: < 200ms (p95)
- Database queries: < 50ms (p95)

**2. Pagination:**
```python
# Limit maximum page size to prevent large queries
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

def get_posts(page: int = 1, limit: int = DEFAULT_PAGE_SIZE):
    limit = min(limit, MAX_PAGE_SIZE)  # Cap at 100
    skip = (page - 1) * limit
    # Query with LIMIT and OFFSET
```

**3. Async Handlers:**
```python
# Use async/await for I/O-bound operations
@router.get("/posts")
async def list_posts(db: Session = Depends(get_db)):
    # Database queries are still synchronous (SQLAlchemy)
    # But FastAPI can handle other requests concurrently
    pass
```

**4. Response Compression:**
```python
# Enable gzip compression in FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Caching Strategy (Future Enhancement)

**Not implemented in MVP, but planned for future:**

**1. Redis Cache Layer:**
```python
# Cache frequently accessed posts
@lru_cache(maxsize=128)
def get_popular_posts():
    # Cache top 20 posts for 5 minutes
    pass

# Cache user profiles
def get_user_profile(user_id: int):
    cache_key = f"user:{user_id}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    user = db.query(User).filter(User.id == user_id).first()
    redis.setex(cache_key, 3600, json.dumps(user.dict()))  # 1 hour TTL
    return user
```

**2. Cache Invalidation:**
```python
# Invalidate cache on updates
def update_user(user_id: int, data: UserUpdate):
    user = # ... update user
    redis.delete(f"user:{user_id}")  # Invalidate cache
    return user
```

### Load Testing

**Use Locust or Apache Bench for load testing:**

**File:** `locustfile.py`
```python
from locust import HttpUser, task, between

class BlogAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def list_posts(self):
        self.client.get("/api/posts")
    
    @task(2)
    def get_post(self):
        self.client.get("/api/posts/1")
    
    @task(1)
    def create_post(self):
        self.client.post("/api/posts", json={
            "title": "Load Test Post",
            "content": "Content"
        }, headers=self.headers)
```

**Run load test:**
```bash
# Test with 100 concurrent users
locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10
```

### Monitoring Performance Metrics

**Key Metrics to Track:**
- Response time percentiles (p50, p95, p99)
- Requests per second
- Error rate (4xx, 5xx)
- Database query time
- Connection pool utilization
- CPU and memory usage

**FastAPI Built-in Metrics:**
```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Database Query Performance Tips

1. **Use `select_related` equivalent (joinedload) to avoid N+1 queries**
2. **Add indexes on foreign keys and frequently queried fields**
3. **Use `EXPLAIN ANALYZE` to identify slow queries**
4. **Limit result sets with pagination**
5. **Avoid `SELECT *` - only fetch needed columns (future optimization)**
6. **Use database connection pooling**
7. **Monitor slow query log (queries > 100ms)**

---

## Appendix: Existing Repository Structure

## Repository File Structure

```
.claude-output.json
.claude-plan.json
.claude-resolution.json
.conflict-info.json
.git
.gitignore
.pr-number
CONTRIBUTING.md
LICENSE
README.md
docs/
  getting_started.md
  plans/
    blog-api/
      HLD.md
    health-check/
      HLD.md
      LLD.md
      PRD.md
notebooks/
  README.md
random_colors.py
random_words.py
requirements.txt
src/
  analysis/
    README.md
  api/
    README.md
    __init__.py
    main.py
  models/
    README.md
  random_words.py
  visualization/
    README.md
test_api.py
test_random_colors.py
test_random_words.py
```
