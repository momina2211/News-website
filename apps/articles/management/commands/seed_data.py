"""Management command: seed example data for local dev."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.articles.models import Article
from apps.comments.models import Comment


CATEGORIES = [
    {"name": "Technology", "icon": "💻", "color": "#3B82F6",
     "description": "The latest in tech, software, AI, and gadgets."},
    {"name": "World News", "icon": "🌍", "color": "#10B981",
     "description": "Breaking news and analysis from around the globe."},
    {"name": "Science", "icon": "🔬", "color": "#8B5CF6",
     "description": "Discoveries, research, and scientific breakthroughs."},
    {"name": "Business", "icon": "📈", "color": "#F59E0B",
     "description": "Markets, economy, startups, and corporate news."},
    {"name": "Health", "icon": "❤️", "color": "#EF4444",
     "description": "Health tips, medical research, and wellness."},
    {"name": "Sports", "icon": "⚽", "color": "#06B6D4",
     "description": "Latest scores, analysis, and sports stories."},
    {"name": "Culture", "icon": "🎭", "color": "#EC4899",
     "description": "Arts, entertainment, film, music, and books."},
    {"name": "Politics", "icon": "🏛️", "color": "#6366F1",
     "description": "Domestic and international political coverage."},
]

TAGS = ["AI", "Python", "Climate", "NASA", "Startup", "Economy", "Football",
        "Research", "Innovation", "Django", "OpenSource", "Space", "Bitcoin"]

SAMPLE_ARTICLES = [
    {
        "title": "The Rise of Artificial Intelligence in Modern Newsrooms",
        "summary": "AI tools are transforming how journalists research, write, and distribute news content worldwide.",
        "content": """Artificial intelligence is rapidly changing the media landscape.
From automated reporting to advanced content personalization, AI tools are becoming indispensable in modern newsrooms.

## How AI is Being Used

Major publishers are now using AI to:

- **Automate routine reports** such as earnings summaries and sports scores
- **Personalize content feeds** based on reader behavior and preferences
- **Detect misinformation** before it spreads

## The Human Element

Despite these advances, the human journalist remains central. AI handles the volume; humans handle the nuance.

> "Technology is a tool. The story is always about people." — Editor, The Daily Brief

## Looking Ahead

As large language models become more capable, newsrooms that adapt will thrive. Those that resist may find themselves left behind in an increasingly competitive information economy.""",
        "category": "Technology",
        "tags": ["AI", "Innovation"],
        "is_featured": True,
    },
    {
        "title": "Global Climate Summit Reaches Historic Carbon Agreement",
        "summary": "World leaders signed an unprecedented climate deal pledging net-zero emissions by 2045.",
        "content": """Representatives from 192 nations convened in Geneva this week to sign what analysts are calling the most significant climate agreement since the Paris Accord.

## Key Commitments

The agreement includes:

1. Net-zero carbon emissions by 2045
2. A $500 billion Green Transition Fund
3. Mandatory annual emissions reporting for all signatories

## Reactions

Environmental groups welcomed the deal while cautioning that implementation will be the true test.

"Words on paper don't stop floods," said one climate activist. "We need action within months, not decades."

## What Comes Next

Each nation must submit a detailed implementation roadmap by Q1 next year. A new international oversight body will monitor progress annually.""",
        "category": "World News",
        "tags": ["Climate"],
    },
    {
        "title": "Django 5.0: What Every Python Developer Needs to Know",
        "summary": "Django 5 ships with facet filters, simplified templates, and major ORM improvements.",
        "content": """Django 5.0 marks a milestone for the framework that powers millions of websites globally.

## Top New Features

### Facet Filters in Admin
The Django admin now shows counts alongside filter options, making data exploration far more intuitive.

### Field Groups in Forms
New `FieldGroup` support enables cleaner form layouts without writing custom widgets.

### Simplified URL Routing
Route converters have been streamlined, reducing boilerplate significantly.

## Upgrading

Most Django 4.2 projects will upgrade smoothly. Run:

```
python manage.py check --deploy
```

to identify any compatibility issues before migrating.

## Performance Improvements

Benchmark tests show a 15% improvement in ORM query generation for complex lookups.""",
        "category": "Technology",
        "tags": ["Django", "Python", "OpenSource"],
    },
    {
        "title": "NASA's Artemis Mission Discovers Water Ice Deposits on Moon",
        "summary": "Lunar probes confirm large subsurface water ice reserves near the Moon's south pole.",
        "content": """NASA scientists have confirmed the presence of significant water ice deposits beneath the surface near the Moon's south pole.

## The Discovery

Using ground-penetrating radar aboard the Artemis reconnaissance orbiter, researchers mapped ice concentrations extending several meters below the regolith.

## Why It Matters

Water ice is critical for future crewed missions. It can be:

- Converted into drinking water
- Electrolyzed into hydrogen and oxygen for rocket fuel
- Used for radiation shielding

## Next Steps

NASA plans a robotic extraction test in 2026, with crewed operations targeting 2028 under the Artemis IV mission profile.""",
        "category": "Science",
        "tags": ["NASA", "Space", "Research"],
    },
    {
        "title": "Tech Startup Raises $200M Series B to Revolutionize Healthcare AI",
        "summary": "MedVision AI secures landmark funding round to deploy diagnostic models across 50 hospital networks.",
        "content": """MedVision AI, a three-year-old startup based in San Francisco, announced today it has closed a $200 million Series B funding round led by Sequoia Capital.

## What MedVision Does

The company's flagship product uses computer vision and large language models to assist radiologists in reading CT scans and MRIs, reducing diagnostic errors by up to 40% in clinical trials.

## The Market Opportunity

Healthcare AI is projected to reach $45 billion by 2030. MedVision is positioning itself at the intersection of imaging, clinical decision support, and patient records.

## Expansion Plans

The company plans to:

- Deploy to 50 hospital networks in 12 months
- Expand to the European market in 2027
- File for FDA breakthrough device designation

CEO Dr. Ananya Patel said: "We're not replacing doctors — we're giving them a superpower." """,
        "category": "Business",
        "tags": ["AI", "Startup", "Innovation"],
    },
]


class Command(BaseCommand):
    help = "Seed example data: users, categories, tags, and articles"

    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding example data...")

        # Create users
        admin, _ = User.objects.get_or_create(username="admin", defaults={
            "email": "admin@newshub.com",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
            "first_name": "Admin",
            "last_name": "User",
            "bio": "Site administrator and head editor.",
        })
        admin.set_password("admin123")
        admin.save()
        self.stdout.write(f"  ✓ Admin user: admin / admin123")

        editor, _ = User.objects.get_or_create(username="editor", defaults={
            "email": "editor@newshub.com",
            "role": "editor",
            "first_name": "Sarah",
            "last_name": "Connor",
            "bio": "Senior editor with 10 years in digital journalism.",
        })
        editor.set_password("editor123")
        editor.save()
        self.stdout.write(f"  ✓ Editor user: editor / editor123")

        author, _ = User.objects.get_or_create(username="author", defaults={
            "email": "author@newshub.com",
            "role": "author",
            "first_name": "James",
            "last_name": "Wright",
            "bio": "Journalist and tech writer covering AI, science, and global news.",
            "twitter": "jameswright",
        })
        author.set_password("author123")
        author.save()
        self.stdout.write(f"  ✓ Author user: author / author123")

        # Create categories
        categories = {}
        for cat_data in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=cat_data["name"], defaults=cat_data)
            categories[cat.name] = cat
        self.stdout.write(f"  ✓ {len(categories)} categories created")

        # Create tags
        tags = {}
        for tag_name in TAGS:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags[tag_name] = tag
        self.stdout.write(f"  ✓ {len(tags)} tags created")

        # Create articles
        created_count = 0
        for article_data in SAMPLE_ARTICLES:
            cat_name = article_data.pop("category")
            tag_names = article_data.pop("tags", [])
            if not Article.objects.filter(title=article_data["title"]).exists():
                article = Article.objects.create(
                    **article_data,
                    author=author,
                    category=categories.get(cat_name),
                    status="published",
                    published_at=timezone.now(),
                )
                for tag_name in tag_names:
                    if tag_name in tags:
                        article.tags.add(tags[tag_name])
                created_count += 1

                # Add a sample comment
                Comment.objects.create(
                    article=article,
                    user=admin,
                    content="Great article! Very informative and well-written.",
                    is_approved=True,
                )

        self.stdout.write(f"  ✓ {created_count} articles created (with comments)")
        self.stdout.write(self.style.SUCCESS("\n✅ Example data seeded successfully!"))
        self.stdout.write("\n📋 Login credentials:")
        self.stdout.write("   Admin:  admin / admin123  → http://localhost:8000/admin/")
        self.stdout.write("   Editor: editor / editor123")
        self.stdout.write("   Author: author / author123")

