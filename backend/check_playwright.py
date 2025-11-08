"""Check if Playwright flag is set for SEC Blog."""
from storage.repository import SourceConfigRepository
from storage.models import SourceConfigModel

repo = SourceConfigRepository()
source = repo.session.query(SourceConfigModel).filter(
    SourceConfigModel.source_name == 'SEC Blog'
).first()

if source:
    print(f"SEC Blog found (ID: {source.id})")
    print(f"Config: {source.config}")
    print(f"Use Playwright: {source.config.get('use_playwright') if source.config else 'No config'}")
else:
    print("SEC Blog not found")
