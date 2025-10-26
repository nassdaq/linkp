"""Main runner for LinkP daily posts."""

import sys
from pathlib import Path
from datetime import datetime

from linkp.config import Config
from linkp.git_tracker import GitTracker
from linkp.ai_summarizer import AISummarizer
from linkp.visual_generator import VisualGenerator
from linkp.linkedin_poster import LinkedInPoster


def run_daily_post():
    """Run the daily LinkedIn post workflow."""
    print("🚀 Starting LinkP daily post workflow...\n")
    
    # Load configuration
    config = Config()
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    print("✅ Configuration loaded")
    
    # Track Git changes
    print("\n📊 Tracking Git changes...")
    git_tracker = GitTracker(config.project_path)
    
    try:
        changes = git_tracker.get_recent_changes(days=1)
        print(f"✅ Found: {changes['summary']}")
    except ValueError as e:
        print(f"❌ Git error: {e}")
        sys.exit(1)
    
    if not changes.get("commits"):
        print("\n⚠️  No commits found in the last 24 hours")
        response = input("Do you still want to create a post? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)
    
    # Generate AI summary
    print("\n🤖 Generating AI summary...")
    summarizer = AISummarizer(config.openai_api_key)
    
    try:
        summary = summarizer.generate_summary(changes)
        print(f"✅ AI Summary:\n{summary}")
    except Exception as e:
        print(f"❌ AI summarization error: {e}")
        sys.exit(1)
    
    # Generate visual
    print("\n🎨 Generating visual...")
    visual_gen = VisualGenerator(openai_api_key=config.openai_api_key)
    
    # Create output directory
    output_dir = Path.cwd() / ".linkp_output"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = output_dir / f"post_{timestamp}.png"
    
    try:
        # Generate image with summary and git context
        visual_gen.create_summary_image(summary, image_path, git_context=changes)
        print(f"✅ Visual saved to {image_path}")
    except Exception as e:
        print(f"⚠️  Visual generation error: {e}")
        print("Continuing without visual...")
        image_path = None
    
    # Post to LinkedIn
    print("\n📱 Posting to LinkedIn...")
    poster = LinkedInPoster(
        config.linkedin_client_id,
        config.linkedin_client_secret,
        config.linkedin_access_token,
        person_urn=config.linkedin_person_urn
    )
    
    # Add hashtags
    hashtags = "#coding #development #opensource #github #softwareengineering"
    post_text = f"{summary}\n\n{hashtags}"
    
    try:
        if image_path and image_path.exists():
            # Try to post with image first
            try:
                poster.post_with_image(post_text, image_path)
                print("✅ Posted to LinkedIn with visual!")
            except Exception as img_error:
                # Fall back to text-only post if image upload fails
                print(f"⚠️  Image upload failed ({img_error}), posting text only...")
                try:
                    poster.post_text_update(post_text)
                    print("✅ Posted to LinkedIn (text only)!")
                except Exception as text_error:
                    raise text_error
        else:
            poster.post_text_update(post_text)
            print("✅ Posted to LinkedIn!")
    except Exception as e:
        print(f"❌ LinkedIn posting error: {e}")
        print("\nPost details saved below for manual posting:")
        print("-" * 60)
        print(post_text)
        print("-" * 60)
        sys.exit(1)
    
    # Save log
    log_file = output_dir / "post_history.txt"
    with open(log_file, "a") as f:
        f.write(f"\n{datetime.now().isoformat()}\n")
        f.write(f"{post_text}\n")
        f.write("-" * 60 + "\n")
    
    print(f"\n📝 Post logged to {log_file}")
