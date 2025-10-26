"""Visual generation for LinkedIn posts using AI — upgraded for creativity and philosophy."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import os
from openai import OpenAI
import requests


class VisualGenerator:
    """Generate visually appealing, philosophical LinkedIn post images using AI."""
    
    def __init__(self, openai_api_key=None):
        self.width = 1200
        self.height = 630
        self.bg_color = (13, 23, 33)  # Dark blue background
        self.text_color = (255, 255, 255)
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            self.client = None

    def create_summary_image(self, summary, output_path=None, git_context=None):
        """Create an AI-enhanced LinkedIn-style visual summarizing a software update."""
        if self.client:
            try:
                return self._generate_ai_image(summary, git_context, output_path)
            except Exception as e:
                print(f"⚠️ AI image generation failed: {e}. Falling back to code-based image.")
        
        return self._create_code_design_image(summary, output_path, git_context)

    def _generate_ai_image(self, summary, git_context, output_path):
        """Generate a philosophical and aesthetic image using GPT-image-1."""
        prompt = self._build_image_prompt(summary, git_context)
        
        response = self.client.images.generate(
            model="gpt-image-1",  # Upgraded from dall-e-3
            prompt=prompt,
            size="1024x1024",
            n=1,
            quality="high"
        )

        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image = Image.open(io.BytesIO(image_response.content))

        # Resize for LinkedIn format
        image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        if output_path:
            image.save(output_path)
        
        return image

    def _build_image_prompt(self, summary, git_context):
        """Build a poetic, philosophical yet professional AI prompt for visual generation."""
        languages = []
        if git_context:
            for action, filename in git_context.get('files_changed', [])[:10]:
                ext = filename.split('.')[-1] if '.' in filename else ''
                if ext:
                    languages.append(ext.upper())
        language_desc = ', '.join(set(languages)) if languages else 'software'

        # --- ✨ Philosophical + Developer-oriented prompt generation ✨ ---
        prompt = f"""
        Create a cinematic, visually stunning artwork for a LinkedIn post.

        Theme: The journey of creation and progress in software development.
        Context: "{summary}"
        Technologies involved: {language_desc}

        Artistic direction:
        - Style: Minimalist, futuristic, elegant, and deeply symbolic.
        - Mood: Philosophical, inspiring, and thought-provoking.
        - Visual elements: abstract representations of coding, logic, growth, or digital light.
        - Use metaphors like light emerging from darkness, code as energy, mind as architecture.
        - Color palette: dark blue, cyan, soft gold, or aurora tones — emphasizing focus and intelligence.
        - Should feel like a visual poem about progress, creation, and purpose.
        - No text or logos on the image.
        - Perfect for a professional audience on LinkedIn.
        """

        return prompt.strip()

    def _create_code_design_image(self, summary, output_path, git_context):
        """Fallback static image generation (text-based)."""
        image = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(image)
        
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            code_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 20)
        except:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            code_font = ImageFont.load_default()

        # Draw content
        draw.text((50, 60), "// Daily Dev Update", fill=(100, 150, 200), font=code_font)
        draw.text((50, 110), "Daily Progress", fill=self.text_color, font=title_font)

        text_y = 220
        max_width = self.width - 140
        words = summary.split()
        line = []

        for word in words:
            test_line = ' '.join(line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=body_font)
            text_width = bbox[2] - bbox[0]
            if text_width > max_width and line:
                draw.text((70, text_y), ' '.join(line), fill=self.text_color, font=body_font)
                text_y += 45
                line = [word]
            else:
                line.append(word)

        if line:
            draw.text((70, text_y), ' '.join(line), fill=self.text_color, font=body_font)

        if git_context:
            commits = git_context.get('commits', [])
            files = git_context.get('files_changed', [])
            if commits and files:
                stats = f"// {len(commits)} commits, {len(files)} files"
                draw.text((50, self.height - 50), stats, fill=(200, 200, 200), font=code_font)

        if output_path:
            image.save(output_path)
        
        return image
