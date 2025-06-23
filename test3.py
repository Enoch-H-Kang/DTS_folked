"""
Brooks Glycerin 22 Ad Image Generator – Dynamic, Modular & Multimodal
--------------------------------------------------------------------
This script auto-generates ad-ready prompts for Imagen 3 via Gemini Pro/Flash.
It now
• uses a richer, production-grade prompt requirements list,
• lets Gemini "see" reference mock-ups so it can mimic branding/typography,
• keeps the original CLI + logging workflow intact.

Usage (TL;DR)
--------------
1. Put two small reference PNGs/JPEGs (≤1024×1024 px) that show your
   preferred overlay style in the same folder or anywhere you like.
   In this example we name them `beach_mock.png` and `bench_mock.png`.
2. Create a `.env` file next to this script containing your GOOGLE_API_KEY and
   optional NUM_AD_IMAGES, e.g.:

     GOOGLE_API_KEY="YOUR-KEY-HERE"
     NUM_AD_IMAGES=5

3. Run:  `python brooks_ad_image_generator.py`

Gemini will craft a fresh prompt for each image while respecting your visual
guidelines; Imagen 3 then turns each prompt into a 1×1 image and saves them in
`brooks_glycerin_22_campaign/` alongside a JSON generation log.
"""

from __future__ import annotations

import os
import time
import json
from io import BytesIO
from typing import List, Dict

from dotenv import load_dotenv
from PIL import Image

# Gemini SDKs
from google import genai  # Imagen 3 & Files API
from google.genai import types  # Helper for Imagen config
import google.generativeai as legacy_genai  # Gemini-Pro/Flash text model


class BrooksAdImageGenerator:
    """Generate Brooks Glycerin 22 ad images using Gemini + Imagen 3."""

    def __init__(
        self,
        api_key: str,
        output_dir: str = "brooks_glycerin_22_ads",
        reference_image_paths: List[str] | None = None,
        use_flash: bool = False,
    ) -> None:
        self.api_key = api_key
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.reference_images: List[Image.Image] = []
        if reference_image_paths:
            for path in reference_image_paths:
                try:
                    self.reference_images.append(Image.open(path))
                except Exception as e:
                    print(f"⚠️  Could not load reference image '{path}': {e}")
        if not self.reference_images:
            print("ℹ️  No reference images loaded – prompts will be text-only.")

        self.client = genai.Client(api_key=api_key)
        legacy_genai.configure(api_key=api_key)
        model_name = "gemini-2.5-flash" if use_flash else "gemini-2.5-pro"
        self.text_model = legacy_genai.GenerativeModel(model_name)

        self.creative_brief = (
            """
            Brooks Glycerin 22 Creative Brief:\n\n"
            "Product: Brooks Glycerin 22 flagship high-cushion running shoe\n\n"
            "Key Features:\n"
            "– DNA Tuned Cushioning: nitrogen-infused, dual-size cell foam\n"
            "– Engineered Double Jacquard Knit Upper: breathable & flexible\n"
            "– Broad Platform: stabilises foot for smooth transitions\n"
            "– Modern Design: fresh colourways & sculpted midsole\n\n"
            "Target Audience: neutral runners, daily trainers, fitness enthusiasts (25-55)\n"
            "USP: \"Supreme comfort meets responsive performance—every step, every mile.\"\n"
            "Tone: confident, inviting, empowering, performance-driven, inclusive\n"
            "Tagline: \"THE ALL-NEW GLYCERIN 22\"\n"
            "Mandatories:\n"
            "– Show Glycerin 22 in action\n"
            "– Feature close-ups of DNA Tuned midsole & knit upper\n"
            "– Include Brooks branding elements\n"
            "– Modern, dynamic composition\n"
            "– Clean typography for brand name (BROOKS) & tagline\n"
            """
        )

        self.prompt_requirements: List[str] = [
            "Generate a **fresh, non-repetitive concept** for this image only (don’t echo earlier prompts).",
            "Show a **close-up of the Brooks Glycerin 22** as the unmistakable hero subject – zoom in on the midsole, knit texture, or side profile.",
            "Reinforce the brand tone: confident, empowering, inclusive, performance-driven.",
            "Place the scene in a **specific time, location, and atmosphere** that amplifies comfort and motion.",
            "If people appear, cast a **diverse, relatable runner** whose expression and body language convey joy and determination.",
            "Direct the viewer’s eye with strong composition cues (rule-of-thirds, leading lines, dynamic diagonals, shallow depth of field).",
            "Specify camera viewpoint and technical look: lens focal length, aperture, motion blur, or—if illustrative—brush style/texture.",
            "Define lighting mood (cinematic rim light, soft diffused dawn, neon street glow) and a colour palette that harmonises with Brooks brand hues.",
            "Integrate **subtle Brooks identifiers** (logo on tongue, chevron pattern, ‘Run Happy’ motif) without cluttering the frame.",
            "Overlay the **brand** and the **tagline** in negative space using clean, modern typography.",
            "Show **kinetic cues** that dramatise cushion and responsiveness.",
            "Highlight at least one technical feature (DNA-Tuned midsole cell structure, knit upper texture) in crisp detail.",
            "Include a short **negative prompt** to avoid rival logos, distorted anatomy, low-poly artefacts, or text errors.",
        ]

    def _assemble_requirements_block(self) -> str:
        return "\n".join(f"{i + 1}. {req}" for i, req in enumerate(self.prompt_requirements))

    def generate_image_prompt(self, image_number: int) -> str:
        visual_instruction = """
The reference images shown above are **only** for layout style. 
Use them to understand:
– The exact font style of the \"BROOKS\" brand name
– The exact way “THE ALL-NEW GLYCERIN 22” overlay is styled and positioned
– The use of bold fonts, gradients, shadows, or boxed color backgrounds
⛔ Do NOT copy or describe the exact shoe in these images. 
⛔ Do NOT refer to the background, clothing, socks, legs, or any specific scene. 
Only apply the same **typographic overlay approach** when composing the visual prompt.
Make sure you position the brand name and tagline, but in a way that fits the new scene you create.
"""

        prompt_request = f"""
Based on this creative brief for Brooks Glycerin 22 running shoes:
{self.creative_brief}

{visual_instruction}

Now create a detailed, specific image-generation prompt for ad image #{image_number}.

Requirements:
{self._assemble_requirements_block()}

Return **only** the image prompt — no extra commentary.
"""

        contents = self.reference_images + [prompt_request]

        try:
            response = self.text_model.generate_content(contents=contents)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️  Error generating prompt for image {image_number}: {e}")
            return (
                "High-quality ad photo of Brooks Glycerin 22 shoe with modern brand overlay, bold tagline, and energetic atmosphere."
            )

    def generate_image(self, prompt: str, image_number: int) -> str | None:
        try:
            print(f"  ↳  Generating image {image_number} → {prompt[:80]}…")

            response = self.client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="1:1"),
            )

            if response and getattr(response, "generated_images", None):
                filename = f"brooks_glycerin_22_ad_{image_number:02d}.png"
                filepath = os.path.join(self.output_dir, filename)

                img_bytes = response.generated_images[0].image.image_bytes
                Image.open(BytesIO(img_bytes)).save(filepath)
                print(f"  ✓ Saved → {filepath}")
                return filepath

            print("  ⚠️  No images returned (empty response)")
            return None
        except Exception as e:
            print(f"⚠️  Error generating image {image_number}: {e}")
            return None

    def generate_all_ads(self, num_images: int = 10) -> List[Dict]:
        generated_images: List[Dict] = []

        print("Starting Brooks Glycerin 22 ad image generation…")
        print(f"Output directory: {self.output_dir}")
        print("-" * 60)

        for i in range(1, num_images + 1):
            print(f"\n[{i}/{num_images}] Crafting prompt…")
            image_prompt = self.generate_image_prompt(i)
            print("  → Calling Imagen 3…")
            image_path = self.generate_image(image_prompt, i)

            generated_images.append(
                {
                    "image_number": i,
                    "prompt": image_prompt,
                    "image_path": image_path,
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

            time.sleep(3)
            print(f"✓ Completed image {i}")

        self._save_generation_log(generated_images)
        print(f"\n✅ Generated {len(generated_images)} ad images!")
        print(f"📁  Saved in: {self.output_dir}")
        return generated_images

    def _save_generation_log(self, images_info: List[Dict]) -> None:
        log_path = os.path.join(self.output_dir, "generation_log.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "campaign": "Brooks Glycerin 22 Ad Campaign",
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_images": len(images_info),
                    "images": images_info,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        print(f"📋 Log saved → {log_path}")


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY missing (set in .env)")
        return

    num_images = int(os.getenv("NUM_AD_IMAGES", "3"))

    reference_paths = [
        os.getenv("REF_IMAGE_1", "beach_mock.png"),
        os.getenv("REF_IMAGE_2", "bench_mock.png"),
    ]

    gen = BrooksAdImageGenerator(
        api_key=api_key,
        output_dir="brooks_glycerin_22_campaign",
        reference_image_paths=reference_paths,
        use_flash=bool(os.getenv("USE_GEMINI_FLASH")),
    )

    try:
        gen.generate_all_ads(num_images=num_images)
    except Exception as e:
        print(f"Fatal error: {e}\nCheck your API key, file paths, and internet connection.")


if __name__ == "__main__":
    print("Brooks Glycerin 22 Ad Image Generator – Dynamic, Modular & Multimodal")
    print("=" * 70)
    main()
