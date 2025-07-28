"""
Score Management System for Ghost of Space
"""
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from utils.logger import logger
import config


@dataclass
class Score:
    """Represents a player score entry"""
    player_name: str
    score: int
    level_reached: int
    play_time: float  # in seconds
    date_achieved: str
    
    def __post_init__(self):
        """Validate score data after initialization"""
        if self.score < 0:
            raise ValueError("Score cannot be negative")
        if self.level_reached < 1:
            raise ValueError("Level must be at least 1")
        if self.play_time < 0:
            raise ValueError("Play time cannot be negative")


class ScoreManager:
    """Manages high scores using SQLite database"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize score manager
        
        Args:
            db_path: Path to the database file (defaults to data/scores.db)
        """
        if db_path is None:
            db_path = config.DATA_DIR / "scores.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(exist_ok=True)
        self._initialize_database()
        
        logger.info(f"Score manager initialized with database: {db_path}")
    
    def _initialize_database(self):
        """Initialize the database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,
                        score INTEGER NOT NULL,
                        level_reached INTEGER NOT NULL,
                        play_time REAL NOT NULL,
                        date_achieved TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_score_desc 
                    ON scores (score DESC)
                ''')
                
                conn.commit()
                logger.info("Database schema initialized")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            # Fallback to JSON if database fails
            self._use_json_fallback = True
    
    def add_score(self, score: Score) -> bool:
        """
        Add a new score to the database
        
        Args:
            score: Score object to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scores 
                    (player_name, score, level_reached, play_time, date_achieved)
                    VALUES (?, ?, ?, ?, ?)
                ''', (score.player_name, score.score, score.level_reached, 
                     score.play_time, score.date_achieved))
                
                conn.commit()
                logger.info(f"Added score: {score.player_name} - {score.score}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error adding score: {e}")
            return False
    
    def get_high_scores(self, limit: int = 10) -> List[Score]:
        """
        Get the highest scores
        
        Args:
            limit: Maximum number of scores to return
            
        Returns:
            List of Score objects sorted by score (descending)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT player_name, score, level_reached, play_time, date_achieved
                    FROM scores
                    ORDER BY score DESC, level_reached DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                scores = []
                
                for row in rows:
                    score = Score(
                        player_name=row[0],
                        score=row[1],
                        level_reached=row[2],
                        play_time=row[3],
                        date_achieved=row[4]
                    )
                    scores.append(score)
                
                logger.debug(f"Retrieved {len(scores)} high scores")
                return scores
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving high scores: {e}")
            return []
    
    def get_player_scores(self, player_name: str, limit: int = 5) -> List[Score]:
        """
        Get scores for a specific player
        
        Args:
            player_name: Name of the player
            limit: Maximum number of scores to return
            
        Returns:
            List of Score objects for the player
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT player_name, score, level_reached, play_time, date_achieved
                    FROM scores
                    WHERE player_name = ?
                    ORDER BY score DESC
                    LIMIT ?
                ''', (player_name, limit))
                
                rows = cursor.fetchall()
                scores = []
                
                for row in rows:
                    score = Score(
                        player_name=row[0],
                        score=row[1],
                        level_reached=row[2],
                        play_time=row[3],
                        date_achieved=row[4]
                    )
                    scores.append(score)
                
                logger.debug(f"Retrieved {len(scores)} scores for player {player_name}")
                return scores
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving player scores: {e}")
            return []
    
    def get_player_best_score(self, player_name: str) -> Optional[Score]:
        """
        Get the best score for a specific player
        
        Args:
            player_name: Name of the player
            
        Returns:
            Best Score object for the player, or None if no scores found
        """
        scores = self.get_player_scores(player_name, limit=1)
        return scores[0] if scores else None
    
    def is_high_score(self, score: int, limit: int = 10) -> bool:
        """
        Check if a score qualifies as a high score
        
        Args:
            score: Score to check
            limit: Number of high scores to consider
            
        Returns:
            True if the score qualifies as a high score
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM scores WHERE score > ?
                ''', (score,))
                
                count = cursor.fetchone()[0]
                return count < limit
                
        except sqlite3.Error as e:
            logger.error(f"Error checking high score: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get various statistics about scores
        
        Returns:
            Dictionary containing statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total games played
                cursor.execute('SELECT COUNT(*) FROM scores')
                total_games = cursor.fetchone()[0]
                
                # Highest score
                cursor.execute('SELECT MAX(score) FROM scores')
                highest_score = cursor.fetchone()[0] or 0
                
                # Average score
                cursor.execute('SELECT AVG(score) FROM scores')
                average_score = cursor.fetchone()[0] or 0
                
                # Highest level reached
                cursor.execute('SELECT MAX(level_reached) FROM scores')
                highest_level = cursor.fetchone()[0] or 0
                
                # Most active player
                cursor.execute('''
                    SELECT player_name, COUNT(*) as game_count
                    FROM scores
                    GROUP BY player_name
                    ORDER BY game_count DESC
                    LIMIT 1
                ''')
                most_active_result = cursor.fetchone()
                most_active_player = most_active_result[0] if most_active_result else "N/A"
                
                stats = {
                    'total_games': total_games,
                    'highest_score': highest_score,
                    'average_score': round(average_score, 1),
                    'highest_level': highest_level,
                    'most_active_player': most_active_player
                }
                
                logger.debug(f"Retrieved statistics: {stats}")
                return stats
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving statistics: {e}")
            return {
                'total_games': 0,
                'highest_score': 0,
                'average_score': 0,
                'highest_level': 0,
                'most_active_player': 'N/A'
            }
    
    def clear_scores(self) -> bool:
        """
        Clear all scores from the database
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM scores')
                conn.commit()
                
                logger.info("All scores cleared")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error clearing scores: {e}")
            return False
    
    def export_scores(self, export_path: Optional[Path] = None) -> bool:
        """
        Export scores to JSON file
        
        Args:
            export_path: Path to export file (defaults to data/scores_export.json)
            
        Returns:
            True if successful, False otherwise
        """
        if export_path is None:
            export_path = config.DATA_DIR / "scores_export.json"
        
        try:
            scores = self.get_high_scores(limit=100)  # Export top 100 scores
            scores_data = [asdict(score) for score in scores]
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(scores_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Scores exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting scores: {e}")
            return False
    
    def import_scores(self, import_path: Path) -> bool:
        """
        Import scores from JSON file
        
        Args:
            import_path: Path to import file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                scores_data = json.load(f)
            
            imported_count = 0
            for score_dict in scores_data:
                try:
                    score = Score(**score_dict)
                    if self.add_score(score):
                        imported_count += 1
                except (TypeError, ValueError) as e:
                    logger.warning(f"Skipping invalid score entry: {e}")
            
            logger.info(f"Imported {imported_count} scores from {import_path}")
            return imported_count > 0
            
        except Exception as e:
            logger.error(f"Error importing scores: {e}")
            return False


# Global score manager instance
score_manager = ScoreManager()


def create_score(player_name: str, score: int, level_reached: int, 
                play_time: float) -> Score:
    """
    Create a new Score object with current timestamp
    
    Args:
        player_name: Name of the player
        score: Final score
        level_reached: Highest level reached
        play_time: Total play time in seconds
        
    Returns:
        New Score object
    """
    return Score(
        player_name=player_name,
        score=score,
        level_reached=level_reached,
        play_time=play_time,
        date_achieved=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


def format_play_time(seconds: float) -> str:
    """
    Format play time as a human-readable string
    
    Args:
        seconds: Play time in seconds
        
    Returns:
        Formatted time string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_score(score: int) -> str:
    """
    Format score with thousands separators
    
    Args:
        score: Score value
        
    Returns:
        Formatted score string
    """
    return f"{score:,}"