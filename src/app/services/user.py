from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select

# --- Models ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    balance: float
    monthly_budget: float
    credit_cards: str  # Comma separated for simplicity in hackathon

# --- Database ---
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- Service ---
class UserService:
    def __init__(self):
        # Initialize DB on start
        create_db_and_tables()
        self._seed_data()
    
    def _seed_data(self):
        """Seed mock data if empty"""
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == "demo_user")).first()
            if not user:
                print("🌱 Seeding demo_user...")
                demo_user = User(
                    username="demo_user",
                    balance=1500.00,
                    monthly_budget=500.00,
                    credit_cards="Amex_Gold,Visa_Signature"
                )
                session.add(demo_user)
                session.commit()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with Session(engine) as session:
            return session.get(User, user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        with Session(engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first()

# Singleton instance
user_service = UserService()
