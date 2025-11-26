"""
Pytest configuration and shared fixtures

This module contains pytest fixtures that are available to all test modules.
"""
import os
import pytest
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

# Set test environment before importing app modules
os.environ["ENVIRONMENT"] = "local"

# Import all models to ensure they are registered with SQLModel.metadata
from app.models import user, custom_master, koujyou_master  # noqa: F401

from app.config import Settings
from app.database import get_session
from app.main import app


@pytest.fixture(scope="function")
def test_settings() -> Settings:
    """
    Test settings fixture

    Overrides default settings for testing environment.
    Uses in-memory SQLite database for fast test execution.

    Returns:
        Settings: Test configuration settings
    """
    return Settings(
        environment="local",
        debug=True,
        database_url="sqlite:///:memory:",
        database_echo=False,
        database_pool_pre_ping=False,
        database_pool_size=1,
        database_max_overflow=0,
        log_level="DEBUG",
    )


@pytest.fixture(scope="function")
def test_engine(test_settings: Settings):
    """
    Test database engine fixture

    Creates an in-memory SQLite database engine for testing.
    Uses StaticPool to ensure thread-safe testing.

    Args:
        test_settings: Test settings fixture

    Yields:
        Engine: SQLModel database engine
    """
    engine = create_engine(
        test_settings.database_url,
        echo=test_settings.database_echo,
        poolclass=StaticPool,  # Use StaticPool for in-memory database
        connect_args={"check_same_thread": False},  # Required for SQLite
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup: drop all tables
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_connection(test_engine):
    """
    Database connection fixture

    Creates a single connection that will be reused for all requests in a test.
    This is important for in-memory SQLite databases.

    Args:
        test_engine: Test database engine fixture

    Yields:
        Connection: Database connection
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def test_session(db_connection) -> Generator[Session, None, None]:
    """
    Test database session fixture

    Provides a database session for each test function.
    The session is bound to a connection that persists for the test.

    Args:
        db_connection: Database connection fixture

    Yields:
        Session: SQLModel database session
    """
    session = Session(bind=db_connection)

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_connection) -> TestClient:
    """
    FastAPI test client fixture

    Provides a test client for making HTTP requests to the API.
    Overrides the database session dependency to use the test connection.

    Args:
        db_connection: Database connection fixture

    Returns:
        TestClient: FastAPI test client
    """
    def override_get_session():
        """Override the get_session dependency to create a session from test connection"""
        session = Session(bind=db_connection)
        try:
            yield session
        finally:
            session.close()

    # Override the database dependency
    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Clean up: remove dependency override
        app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def reset_database(db_connection):
    """
    Auto-use fixture to reset database state before each test

    This fixture runs automatically before each test function
    to ensure a clean database state.

    Args:
        db_connection: Database connection fixture
    """
    # Clear all tables before each test
    session = Session(bind=db_connection)
    try:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    finally:
        session.close()

