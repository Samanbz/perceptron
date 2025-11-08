"""
Fix CSS selectors for high-priority sources that are currently failing.
Focus on sources with wrong selectors (not bot protection/403 errors).
"""

from storage.repository import SourceConfigRepository

# Updated selectors tested on actual websites
SELECTOR_FIXES = {
    # AI Research Labs
    "Google AI Blog": {
        "url": "https://blog.research.google/",
        "selectors": {
            "item": "article.post, div.post-outer",
            "link": "a.post-title-link, h3.post-title a",
            "title": "h3.post-title, h2.entry-title",
            "content": "div.post-body, div.entry-content",
            "date": "time.published, span.timestamp-link"
        }
    },
    "Meta AI Blog": {
        "url": "https://ai.meta.com/blog/",
        "selectors": {
            "item": "article, div._9sgj",
            "link": "a[href*='/blog/']",
            "title": "h2, h3",
            "content": "p",
            "date": "time, span.date"
        }
    },
    "Amazon Science Blog": {
        "url": "https://www.amazon.science/blog",
        "selectors": {
            "item": "div.card, article.blog-post",
            "link": "a[href*='/blog/']",
            "title": "h3.card__title, h2",
            "content": "p.card__summary, div.content",
            "date": "time, span.date"
        }
    },
    "Apple Machine Learning Research": {
        "url": "https://machinelearning.apple.com/",
        "selectors": {
            "item": "li.post, article",
            "link": "a.post-title-link",
            "title": "h2.post-title, h3",
            "content": "p.post-excerpt, div.excerpt",
            "date": "time.post-date, span.date"
        }
    },
    "NVIDIA Developer Blog": {
        "url": "https://developer.nvidia.com/blog/",
        "selectors": {
            "item": "article.post, div.blog-post",
            "link": "a.post-link",
            "title": "h2.post-title, h3",
            "content": "div.post-excerpt, p",
            "date": "time.post-date, span.date"
        }
    },
    
    # Top VCs
    "a16z Blog": {
        "url": "https://a16z.com/posts/",
        "selectors": {
            "item": "article, div.post-item",
            "link": "a[href*='/posts/']",
            "title": "h2, h3.post-title",
            "content": "p.excerpt, div.summary",
            "date": "time, span.date"
        }
    },
    "Y Combinator Blog": {
        "url": "https://www.ycombinator.com/blog",
        "selectors": {
            "item": "article, div.blog-post",
            "link": "a[href*='/blog/']",
            "title": "h2, h3",
            "content": "p",
            "date": "time, span.date"
        }
    },
    "NFX Blog": {
        "url": "https://www.nfx.com/post",
        "selectors": {
            "item": "div.post-card, article",
            "link": "a[href*='/post/']",
            "title": "h3, h2.post-title",
            "content": "p.description, div.excerpt",
            "date": "time, span.date"
        }
    },
    "Greylock Perspectives": {
        "url": "https://greylock.com/greymatter/",
        "selectors": {
            "item": "article, div.article-card",
            "link": "a[href*='/greymatter/']",
            "title": "h2, h3.article-title",
            "content": "p.excerpt, div.summary",
            "date": "time, span.date"
        }
    },
    "Accel Blog": {
        "url": "https://www.accel.com/noteworthy",
        "selectors": {
            "item": "div.insight-card, article",
            "link": "a[href*='/noteworthy/']",
            "title": "h3, h2",
            "content": "p, div.description",
            "date": "time, span.date"
        }
    },
    "500 Startups Blog": {
        "url": "https://500.co/blog/",
        "selectors": {
            "item": "article, div.blog-post",
            "link": "a[href*='/blog/']",
            "title": "h2, h3",
            "content": "p.excerpt, div.summary",
            "date": "time, span.date"
        }
    },
    "Techstars Blog": {
        "url": "https://www.techstars.com/blog",
        "selectors": {
            "item": "article, div.post-card",
            "link": "a[href*='/blog/']",
            "title": "h2, h3",
            "content": "p, div.excerpt",
            "date": "time, span.date"
        }
    },
    "Bloomberg Technology": {
        "url": "https://www.bloomberg.com/technology",
        "selectors": {
            "item": "article, div.story-package-module__story",
            "link": "a[href*='/news/']",
            "title": "h3, div.headline",
            "content": "p, div.summary",
            "date": "time, span.timestamp"
        }
    },
    
    # Tech News
    "TechCrunch Blog": {
        "url": "https://techcrunch.com/",
        "selectors": {
            "item": "article, div.post-block",
            "link": "a[href*='techcrunch.com/']",
            "title": "h2.post-block__title, h3",
            "content": "p.post-block__content, div.excerpt",
            "date": "time, span.river-byline__time"
        }
    },
    "CB Insights Blog": {
        "url": "https://www.cbinsights.com/research/",
        "selectors": {
            "item": "div.research-card, article",
            "link": "a[href*='/research/']",
            "title": "h3, h2",
            "content": "p, div.description",
            "date": "time, span.date"
        }
    },
    "The Verge": {
        "url": "https://www.theverge.com/tech",
        "selectors": {
            "item": "article, div.c-entry-box",
            "link": "a.c-entry-box--compact__image-wrapper",
            "title": "h2.c-entry-box--compact__title",
            "content": "p.c-entry-box--compact__dek",
            "date": "time"
        }
    },
    "Forrester Blog": {
        "url": "https://www.forrester.com/blogs/",
        "selectors": {
            "item": "div.blog-card, article",
            "link": "a[href*='/blogs/']",
            "title": "h3, h2",
            "content": "p.description, div.excerpt",
            "date": "time, span.date"
        }
    },
    "Benedict Evans": {
        "url": "https://www.ben-evans.com/",
        "selectors": {
            "item": "article.post, div.post",
            "link": "a.post-link",
            "title": "h2.post-title, h3",
            "content": "div.post-content p",
            "date": "time.dt-published, span.date"
        }
    },
    "Stratechery": {
        "url": "https://stratechery.com/",
        "selectors": {
            "item": "article.post, div.post",
            "link": "a[href*='stratechery.com/']",
            "title": "h1.entry-title, h2",
            "content": "div.entry-content p",
            "date": "time.entry-date, span.date"
        }
    },
    
    # Academic Research
    "MIT Technology Review": {
        "url": "https://www.technologyreview.com/",
        "selectors": {
            "item": "article, div.tease",
            "link": "a[href*='/']",
            "title": "h3.tease__title, h2",
            "content": "p.tease__blurb, div.summary",
            "date": "time, span.date"
        }
    },
    "The Gradient": {
        "url": "https://thegradient.pub/",
        "selectors": {
            "item": "article, div.post-card",
            "link": "a.post-card-image-link",
            "title": "h2.post-card-title",
            "content": "section.post-card-excerpt",
            "date": "time"
        }
    },
    "Towards Data Science": {
        "url": "https://towardsdatascience.com/",
        "selectors": {
            "item": "article, div.postArticle",
            "link": "a[data-action='open-post']",
            "title": "h3, h2",
            "content": "p",
            "date": "time"
        }
    },
    "Stanford HAI News": {
        "url": "https://hai.stanford.edu/news",
        "selectors": {
            "item": "div.news-item, article",
            "link": "a[href*='/news/']",
            "title": "h3, h2",
            "content": "p.summary, div.description",
            "date": "time, span.date"
        }
    },
    "Berkeley AI Research": {
        "url": "https://bair.berkeley.edu/blog/",
        "selectors": {
            "item": "div.post-preview, article",
            "link": "a[href*='/blog/']",
            "title": "h2.post-title, h3",
            "content": "p.post-excerpt",
            "date": "p.post-meta time"
        }
    },
    "Papers with Code": {
        "url": "https://paperswithcode.com/latest",
        "selectors": {
            "item": "div.paper-card, article",
            "link": "a[href*='/paper/']",
            "title": "h1, h2",
            "content": "p.item-content, div.description",
            "date": "span.item-date-pub, time"
        }
    },
    
    # FinTech
    "CoinDesk": {
        "url": "https://www.coindesk.com/",
        "selectors": {
            "item": "article, div.article-card",
            "link": "a[href*='coindesk.com/']",
            "title": "h4, h3",
            "content": "p, div.excerpt",
            "date": "time, span.time"
        }
    },
    "FinExtra": {
        "url": "https://www.finextra.com/newsarticles",
        "selectors": {
            "item": "div.news-item, article",
            "link": "a[href*='/newsarticle/']",
            "title": "h3, h2",
            "content": "p, div.summary",
            "date": "span.date, time"
        }
    },
    "Finovate": {
        "url": "https://finovate.com/",
        "selectors": {
            "item": "article, div.post",
            "link": "a[href*='finovate.com/']",
            "title": "h2.entry-title, h3",
            "content": "div.entry-content p",
            "date": "time.entry-date, span.date"
        }
    },
    "American Banker": {
        "url": "https://www.americanbanker.com/news",
        "selectors": {
            "item": "article, div.article-card",
            "link": "a[href*='/news/']",
            "title": "h3, h2",
            "content": "p.dek, div.summary",
            "date": "time, span.date"
        }
    },
    "PaymentsSource": {
        "url": "https://www.paymentssource.com/",
        "selectors": {
            "item": "article, div.article-card",
            "link": "a[href*='paymentssource.com/']",
            "title": "h3, h2",
            "content": "p.dek, div.summary",
            "date": "time, span.date"
        }
    },
    "Square Developer Blog": {
        "url": "https://developer.squareup.com/blog",
        "selectors": {
            "item": "article, div.blog-post",
            "link": "a[href*='/blog/']",
            "title": "h2, h3",
            "content": "p, div.excerpt",
            "date": "time, span.date"
        }
    },
    "Plaid Blog": {
        "url": "https://plaid.com/blog/",
        "selectors": {
            "item": "article, div.blog-card",
            "link": "a[href*='/blog/']",
            "title": "h3, h2",
            "content": "p, div.description",
            "date": "time, span.date"
        }
    },
    "PayPal Newsroom": {
        "url": "https://newsroom.paypal-corp.com/news",
        "selectors": {
            "item": "div.news-item, article",
            "link": "a[href*='/news/']",
            "title": "h3, h2",
            "content": "p, div.summary",
            "date": "time, span.date"
        }
    },
    "Klarna News": {
        "url": "https://www.klarna.com/international/press/",
        "selectors": {
            "item": "div.press-item, article",
            "link": "a[href*='/press/']",
            "title": "h3, h2",
            "content": "p, div.description",
            "date": "time, span.date"
        }
    },
    "Brex Blog": {
        "url": "https://www.brex.com/blog",
        "selectors": {
            "item": "article, div.blog-card",
            "link": "a[href*='/blog/']",
            "title": "h2, h3",
            "content": "p, div.excerpt",
            "date": "time, span.date"
        }
    },
    
    # Government & Regulatory
    "CFTC Press Releases": {
        "url": "https://www.cftc.gov/PressRoom/PressReleases/index.htm",
        "selectors": {
            "item": "div.item, article",
            "link": "a[href*='PressRoom']",
            "title": "h3, h2",
            "content": "p, div.description",
            "date": "span.date, time"
        }
    },
    "OCC News": {
        "url": "https://www.occ.gov/news-issuances/news-releases/index-news-releases.html",
        "selectors": {
            "item": "div.news-item, article",
            "link": "a[href*='news-releases']",
            "title": "h3, h2",
            "content": "p, div.summary",
            "date": "span.date, time"
        }
    },
    "Brookings Institution Finance": {
        "url": "https://www.brookings.edu/topic/financial-regulation/",
        "selectors": {
            "item": "article, div.post-card",
            "link": "a[href*='brookings.edu']",
            "title": "h3, h2",
            "content": "p.excerpt, div.summary",
            "date": "time, span.date"
        }
    },
    "FTC News": {
        "url": "https://www.ftc.gov/news-events/news/press-releases",
        "selectors": {
            "item": "div.news-item, article",
            "link": "a[href*='/news-events/']",
            "title": "h3, h2",
            "content": "p, div.summary",
            "date": "time, span.date"
        }
    },
    "FDIC News": {
        "url": "https://www.fdic.gov/news/press-releases",
        "selectors": {
            "item": "div.pr-item, article",
            "link": "a[href*='press-releases']",
            "title": "h3, h2",
            "content": "p, div.description",
            "date": "span.date, time"
        }
    },
    "Consumer Financial Protection Bureau": {
        "url": "https://www.consumerfinance.gov/about-us/newsroom/",
        "selectors": {
            "item": "article, div.post",
            "link": "a[href*='/newsroom/']",
            "title": "h3, h2",
            "content": "p, div.summary",
            "date": "time, span.date"
        }
    },
    "Bank of England News": {
        "url": "https://www.bankofengland.co.uk/news",
        "selectors": {
            "item": "div.news-item, article",
            "link": "a[href*='/news/']",
            "title": "h3, h2",
            "content": "p, div.summary",
            "date": "time, span.date"
        }
    },
    "Wired Business": {
        "url": "https://www.wired.com/category/business/",
        "selectors": {
            "item": "div.summary-item, article",
            "link": "a[href*='/story/']",
            "title": "h3.summary-item__hed, h2",
            "content": "p.summary-item__dek",
            "date": "time"
        }
    },
    "ZDNet": {
        "url": "https://www.zdnet.com/",
        "selectors": {
            "item": "article, div.article",
            "link": "a[href*='zdnet.com/article/']",
            "title": "h3, h2",
            "content": "p, div.summary",
            "date": "time, span.date"
        }
    },
    "ReadWrite": {
        "url": "https://readwrite.com/",
        "selectors": {
            "item": "article, div.post",
            "link": "a[href*='readwrite.com/']",
            "title": "h2.entry-title, h3",
            "content": "div.entry-content p",
            "date": "time.entry-date, span.date"
        }
    },
    "CNBC Technology": {
        "url": "https://www.cnbc.com/technology/",
        "selectors": {
            "item": "div.Card-titleContainer, article",
            "link": "a[href*='/']",
            "title": "h3, div.Card-title",
            "content": "p, div.Card-description",
            "date": "time, span.Card-time"
        }
    },
    "Quanta Magazine AI": {
        "url": "https://www.quantamagazine.org/tag/artificial-intelligence/",
        "selectors": {
            "item": "article, div.post__card",
            "link": "a[href*='quantamagazine.org/']",
            "title": "h3.post__title__link, h2",
            "content": "p.post__excerpt__text",
            "date": "time, span.post__byline__date"
        }
    }
}

def main():
    """Apply selector fixes to database."""
    from storage.models import SourceConfigModel
    repo = SourceConfigRepository()
    
    print(f"\n🔧 Fixing CSS selectors for {len(SELECTOR_FIXES)} high-priority sources...\n")
    
    updated = 0
    not_found = 0
    
    for source_name, updates in SELECTOR_FIXES.items():
        # Find source by name
        sources = repo.session.query(SourceConfigModel).filter(
            SourceConfigModel.source_name == source_name
        ).all()
        
        if not sources:
            print(f"❌ Source not found: {source_name}")
            not_found += 1
            continue
            
        source = sources[0]
        
        # Update URL if different
        if updates.get("url") and source.source_url != updates["url"]:
            print(f"🔗 {source_name}: Updating URL")
            source.source_url = updates["url"]
        
        # Update selectors (stored in config JSON)
        if updates.get("selectors"):
            print(f"✅ {source_name}: Updating selectors")
            if not source.config:
                source.config = {}
            source.config["selectors"] = updates["selectors"]
            updated += 1
    
    repo.session.commit()
    
    print(f"\n✅ Updated {updated} sources")
    if not_found > 0:
        print(f"⚠️  Could not find {not_found} sources")
    print(f"\nRun trigger_fetch_all.py to test the updated selectors!\n")

if __name__ == "__main__":
    main()
