"""
Template for creating new sourcers.

Copy this file and implement the required methods.
"""

from typing import List, Optional
from .base import BaseSourcer, SourcedContent


class TemplateSourcer(BaseSourcer):
    """
    Template for creating a new sourcer.
    
    Replace this class with your actual sourcer implementation.
    """

    def __init__(self, config_param: str, name: Optional[str] = None):
        """
        Initialize the sourcer.

        Args:
            config_param: Required configuration parameter
            name: Optional name for this sourcer
        """
        super().__init__(name)
        self.config_param = config_param
        
        # Validate configuration on initialization
        self.validate_config(config_param=config_param)

    def validate_config(self, **kwargs) -> bool:
        """
        Validate the sourcer configuration.

        Args:
            **kwargs: Configuration parameters to validate

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        config_param = kwargs.get("config_param")
        
        # Add your validation logic here
        if not config_param:
            raise ValueError("config_param is required")
        
        # Add more validation as needed
        # Example:
        # if not isinstance(config_param, str):
        #     raise ValueError("config_param must be a string")
        
        return True

    async def fetch(self, **kwargs) -> List[SourcedContent]:
        """
        Fetch content from the source.

        Args:
            **kwargs: Optional parameters to override defaults

        Returns:
            List of SourcedContent objects

        Raises:
            Exception: If fetching fails
        """
        # Get configuration (allow override via kwargs)
        config_param = kwargs.get("config_param", self.config_param)
        
        # TODO: Implement your fetching logic here
        # This is where you would:
        # 1. Make API calls, scrape websites, read files, etc.
        # 2. Parse the response
        # 3. Create SourcedContent objects
        
        contents = []
        
        # Example structure:
        # for item in fetched_items:
        #     content = SourcedContent(
        #         title=item.get("title"),
        #         content=item.get("content"),
        #         url=item.get("url"),
        #         published_date=parse_date(item.get("date")),
        #         author=item.get("author"),
        #         metadata={
        #             "source_type": "your_source_type",
        #             # Add other source-specific metadata
        #         }
        #     )
        #     contents.append(content)
        
        return contents

    def __repr__(self) -> str:
        """String representation of the sourcer."""
        return f"<TemplateSourcer: {self.name}>"


# Example usage:
if __name__ == "__main__":
    import asyncio
    
    async def test():
        sourcer = TemplateSourcer(
            config_param="test_value",
            name="Test Sourcer"
        )
        
        contents = await sourcer.fetch()
        
        for content in contents:
            print(f"Title: {content.title}")
            print(f"Content: {content.content[:100]}...")
            print(f"URL: {content.url}")
            print("-" * 50)
    
    asyncio.run(test())
