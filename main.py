import os
import re
from datetime import datetime
from pathlib import Path

def define_env(env):
    @env.macro
    def recent_posts(count=3):
        posts = []
        
        # Adjust this path to match your blog structure
        # Common paths: "docs/blog/posts", "docs/posts", "blog/posts"
        blog_paths = [
            "docs/blog/posts",
            "docs/posts", 
            "blog/posts",
            "posts"
        ]
        
        blog_dir = None
        for path in blog_paths:
            if os.path.exists(path):
                blog_dir = path
                break
        
        if not blog_dir:
            print(f"Blog directory not found. Checked: {blog_paths}")
            return []
        
        print(f"Found blog directory: {blog_dir}")
        
        # Process all markdown files
        for filename in os.listdir(blog_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(blog_dir, filename)
                post_data = parse_post(filepath, filename)
                if post_data:
                    posts.append(post_data)
        
        # Sort by date (newest first) and return requested count
        posts.sort(key=lambda x: x['date'], reverse=True)
        return posts[:count]

def parse_post(filepath, filename):
    """Parse a blog post markdown file and extract metadata"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                post_content = parts[2].strip()
            else:
                frontmatter = ""
                post_content = content
        else:
            frontmatter = ""
            post_content = content
        
        # Parse frontmatter
        metadata = {}
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        
        # Extract title
        title = metadata.get('title', '')
        if not title:
            # Try to get title from first heading in content
            title_match = re.search(r'^#\s+(.+)$', post_content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            else:
                title = filename.replace('.md', '').replace('-', ' ').title()
        
        # Extract date - prioritize 'created' field
        date_str = metadata.get('created', '') or metadata.get('date', '')
        post_date = None
        
        if date_str:
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',           # 2024-01-15
                '%Y/%m/%d',           # 2024/01/15
                '%d-%m-%Y',           # 15-01-2024
                '%m/%d/%Y',           # 01/15/2024
                '%Y-%m-%d %H:%M:%S',  # 2024-01-15 14:30:00
                '%Y-%m-%dT%H:%M:%S',  # 2024-01-15T14:30:00 (ISO format)
                '%Y-%m-%dT%H:%M:%SZ', # 2024-01-15T14:30:00Z (ISO with Z)
                '%B %d, %Y',          # January 15, 2024
                '%d %B %Y'            # 15 January 2024
            ]
            for fmt in date_formats:
                try:
                    post_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
        
        # If no date in frontmatter, try to extract from filename
        if not post_date:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            if date_match:
                try:
                    post_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                except ValueError:
                    pass
        
        # Use file modification time as fallback
        if not post_date:
            post_date = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        # Create URL - adjust this based on your blog URL structure
        url_slug = filename.replace('.md', '')
        if post_date:
            # Format: /blog/YYYY/MM/DD/slug/
            url = f"/blog/{post_date.year}/{post_date.month:02d}/{post_date.day:02d}/{url_slug}/"
        else:
            url = f"/blog/{url_slug}/"
        
        # Extract description/excerpt
        description = metadata.get('description', '')
        if not description:
            # Get first paragraph as description
            paragraphs = [p.strip() for p in post_content.split('\n\n') if p.strip()]
            if paragraphs:
                description = paragraphs[0][:150] + ('...' if len(paragraphs[0]) > 150 else '')
        
        return {
            'title': title,
            'url': url,
            'date': post_date,
            'date_str': post_date.strftime('%B %d, %Y') if post_date else 'Unknown date',
            'description': description
        }
        
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None