# -*- coding: utf-8 -*-
# @Time    : 2025/1/2 15:31
# @Author  : Galleons
# @File    : initialdb.py

"""
这里是文件说明
"""

import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "docbase"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

# Sample meals data
dummy_meals = [
    {
        "title": "Juicy Cheese Burger",
        "slug": "juicy-cheese-burger",
        "image": "/images/burger.jpg",
        "summary": "A mouth-watering burger with a juicy beef patty and melted cheese, served in a soft bun.",
        "instructions": """
            1. Prepare the patty:
               Mix 200g of ground beef with salt and pepper. Form into a patty.

            2. Cook the patty:
               Heat a pan with a bit of oil. Cook the patty for 2-3 minutes each side, until browned.

            3. Assemble the burger:
               Toast the burger bun halves. Place lettuce and tomato on the bottom half. Add the cooked patty and top with a slice of cheese.

            4. Serve:
               Complete the assembly with the top bun and serve hot.
        """,
        "creator": "John Doe",
        "creator_email": "johndoe@example.com"
    },
    {
        "title": "Spicy Curry",
        "slug": "spicy-curry",
        "image": "/images/curry.jpg",
        "summary": "A rich and spicy curry, infused with exotic spices and creamy coconut milk.",
        "instructions": """
            1. Chop vegetables:
               Cut your choice of vegetables into bite-sized pieces.

            2. Sauté vegetables:
               In a pan with oil, sauté the vegetables until they start to soften.

            3. Add curry paste:
               Stir in 2 tablespoons of curry paste and cook for another minute.

            4. Simmer with coconut milk:
               Pour in 500ml of coconut milk and bring to a simmer. Let it cook for about 15 minutes.

            5. Serve:
               Enjoy this creamy curry with rice or bread.
        """,
        "creator": "Max Schwarz",
        "creator_email": "max@example.com"
    }
]  # ... Add other meals similarly


class MealsDatabase:
    def __init__(self, db_config: Dict[str, str]):
        """Initialize database connection."""
        self.db_config = db_config
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor(cursor_factory=DictCursor)
            print("Successfully connected to the database")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise

    def create_table(self):
        """Create meals table if it doesn't exist."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id SERIAL PRIMARY KEY,
                    slug VARCHAR(255) NOT NULL UNIQUE,
                    title VARCHAR(255) NOT NULL,
                    image VARCHAR(255) NOT NULL,
                    summary TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    creator VARCHAR(255) NOT NULL,
                    creator_email VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
            print("Successfully created meals table")
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating table: {e}")
            raise

    def insert_meals(self, meals: List[Dict]):
        """Insert meals data into the database."""
        try:
            insert_query = """
                INSERT INTO meals (
                    slug, title, image, summary, instructions, creator, creator_email
                ) VALUES (
                    %(slug)s, %(title)s, %(image)s, %(summary)s, 
                    %(instructions)s, %(creator)s, %(creator_email)s
                )
                ON CONFLICT (slug) DO NOTHING
            """

            for meal in meals:
                self.cursor.execute(insert_query, meal)

            self.conn.commit()
            print(f"Successfully inserted {len(meals)} meals")
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting meals: {e}")
            raise

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed")


def init_database():
    """Initialize database and insert sample data."""
    db = MealsDatabase(DB_CONFIG)

    try:
        db.connect()
        db.create_table()
        db.insert_meals(dummy_meals)
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()