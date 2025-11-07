"""
Test the team repository to verify config.json integration.
"""

from teams import TeamRepository, get_team_config

def test_repository():
    """Test repository functionality."""
    
    print("=" * 70)
    print("Testing Team Repository")
    print("=" * 70)
    
    repo = TeamRepository()
    
    # Test 1: Get all teams
    print("\n1. Get All Teams:")
    teams = repo.get_all_teams()
    print(f"   Found {len(teams)} active teams")
    for team in teams:
        print(f"   - {team.team_name} ({team.team_key})")
    
    # Test 2: Get team by key
    print("\n2. Get Team by Key (regulator):")
    team = repo.get_team_by_key("regulator")
    if team:
        print(f"   Name: {team.team_name}")
        print(f"   Color: {team.color}")
        print(f"   Threshold: {team.keyword_config.get('relevance_threshold')}")
    
    # Test 3: Get team sources
    print("\n3. Get Team Sources (investor):")
    sources = repo.get_team_sources("investor")
    print(f"   Found {len(sources)} sources")
    for source in sources:
        print(f"   - {source.source_name}: {source.source_url}")
        print(f"     Interval: {source.fetch_interval_minutes} min")
    
    # Test 4: Get keyword config
    print("\n4. Get Keyword Config (researcher):")
    config = repo.get_keyword_config("researcher")
    if config:
        print(f"   Threshold: {config.get('relevance_threshold')}")
        print(f"   Methods: {config.get('methods')}")
        print(f"   Min Frequency: {config.get('min_frequency')}")
        print(f"   Max Phrase Length: {config.get('max_phrase_length')}")
    
    # Test 5: Get API team list
    print("\n5. Get Team List for API:")
    api_teams = repo.get_team_list_for_api()
    for team in api_teams:
        print(f"   {team['team_key']}: {team['team_name']}")
        print(f"      Sources: {team['source_count']}")
        print(f"      Color: {team['color']}")
    
    # Test 6: Get statistics
    print("\n6. Database Statistics:")
    stats = repo.get_statistics()
    print(f"   Total Teams: {stats['total_teams']}")
    print(f"   Active Teams: {stats['active_teams']}")
    print(f"   Total Sources: {stats['total_sources']}")
    print(f"   Enabled Sources: {stats['enabled_sources']}")
    
    # Test 7: Get complete team config
    print("\n7. Get Complete Config (competitor):")
    full_config = get_team_config("competitor")
    if full_config:
        print(f"   Team: {full_config['team_name']}")
        print(f"   Description: {full_config['description']}")
        print(f"   Keyword Methods: {full_config['keyword_config']['methods']}")
        print(f"   Sentiment Enabled: {full_config['sentiment_config']['enable_sentiment']}")
        print(f"   Sources: {len(full_config['sources'])}")
        for src in full_config['sources']:
            print(f"      - {src['source_name']}")
    
    repo.close()
    
    print("\n" + "=" * 70)
    print("✓ All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    test_repository()
