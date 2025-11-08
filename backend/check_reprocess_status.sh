#!/bin/bash
# Check the status of the reprocessing job

echo "=== Reprocessing Status ===="
echo ""

# Check if process is running
if pgrep -f "reprocess_by_published_date.py" > /dev/null; then
    echo "✓ Reprocessing is RUNNING"
    echo "  PID: $(pgrep -f 'reprocess_by_published_date.py')"
else
    echo "✗ Reprocessing is NOT running"
fi

echo ""
echo "=== Latest Log Output ==="
tail -20 /Users/samanb/dev/perceptron/backend/reprocess_bg.log

echo ""
echo "=== Database Status ==="
cd /Users/samanb/dev/perceptron/backend && ./venv/bin/python3 -c "
from keywords.importance_repository import ImportanceRepository
from datetime import datetime, timedelta

repo = ImportanceRepository()
today = datetime.now().date()

teams = ['regulator', 'investor', 'competitor', 'researcher']
print('\nKeywords by team for last 7 days:')
for team in teams:
    total = 0
    for i in range(7):
        check_date = today - timedelta(days=i)
        keywords = repo.get_top_keywords(team, check_date, limit=10000, min_importance=0)
        total += len(keywords)
    print(f'  {team}: {total} keywords')
" 2>/dev/null

echo ""
echo "To monitor live: tail -f /Users/samanb/dev/perceptron/backend/reprocess_bg.log"
