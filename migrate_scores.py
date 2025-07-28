#!/usr/bin/env python3
"""
Migration script for Ghost of Space scores
Converts old JSON scores to new SQLite database format
"""
import json
import sys
from pathlib import Path
from score_manager import score_manager, create_score
from utils.logger import logger


def migrate_old_scores():
    """Migrate scores from old Scored.json to new database"""
    old_scores_file = Path("Scored.json")
    
    if not old_scores_file.exists():
        print("No old scores file (Scored.json) found.")
        print("Nothing to migrate.")
        return True
    
    try:
        print("Loading old scores from Scored.json...")
        with open(old_scores_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        if not old_data:
            print("No scores found in old file.")
            return True
        
        print(f"Found {len(old_data)} old score entries.")
        
        migrated_count = 0
        for score_value, player_data in old_data.items():
            try:
                score_int = int(score_value)
                
                # Extract player name
                if isinstance(player_data, dict):
                    player_name = list(player_data.keys())[0]
                else:
                    player_name = str(player_data)
                
                # Create new score object with estimated values
                new_score = create_score(
                    player_name=player_name,
                    score=score_int,
                    level_reached=max(1, score_int // 50),  # Estimate level
                    play_time=score_int * 2.0  # Estimate play time
                )
                
                if score_manager.add_score(new_score):
                    migrated_count += 1
                    print(f"Migrated: {player_name} - {score_int}")
                
            except (ValueError, KeyError, IndexError) as e:
                print(f"Skipping invalid entry: {e}")
                continue
        
        print(f"\nMigration complete!")
        print(f"Successfully migrated {migrated_count} scores.")
        
        # Backup old file
        backup_file = old_scores_file.with_suffix('.json.backup')
        old_scores_file.rename(backup_file)
        print(f"Old scores backed up to: {backup_file}")
        
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        logger.error(f"Score migration failed: {e}")
        return False


def verify_migration():
    """Verify the migration was successful"""
    try:
        scores = score_manager.get_high_scores(limit=10)
        stats = score_manager.get_statistics()
        
        print("\n=== Migration Verification ===")
        print(f"Total games in new database: {stats['total_games']}")
        print(f"Highest score: {stats['highest_score']}")
        print(f"Most active player: {stats['most_active_player']}")
        
        if scores:
            print("\nTop 5 scores:")
            for i, score in enumerate(scores[:5], 1):
                print(f"{i}. {score.player_name}: {score.score}")
        
        return True
        
    except Exception as e:
        print(f"Error during verification: {e}")
        return False


def main():
    """Main migration function"""
    print("Ghost of Space - Score Migration Tool")
    print("=" * 40)
    
    # Check if new database already has scores
    stats = score_manager.get_statistics()
    if stats['total_games'] > 0:
        response = input(f"Database already contains {stats['total_games']} scores. Continue? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Migration cancelled.")
            return
    
    # Perform migration
    if migrate_old_scores():
        verify_migration()
        print("\nMigration completed successfully!")
        print("You can now run the enhanced version of Ghost of Space.")
    else:
        print("\nMigration failed. Please check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()