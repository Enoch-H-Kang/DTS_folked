from google import genai
from google.genai import types
import google.generativeai as legacy_genai
from PIL import Image
from io import BytesIO
import os
import time
from typing import List, Dict
import json
from dotenv import load_dotenv

# ------------------------------------------------------------
# Brooks Glycerin 22 Ad Image Generator – Dynamic & Modular
# ------------------------------------------------------------
# • No scenario list – Gemini invents each concept.
# • Prompt requirements are now stored as a list so they can be
#   easily tweaked, extended, or randomized without touching the
#   main string. Each call assembles them on‑the‑fly.
# ------------------------------------------------------------


class BrooksAdImageGenerator:
    def __init__(self, api_key: str, output_dir: str = "brooks_glycerin_22_ads"):
        """Init the ad image generator.

        Args:
            api_key:  Google Gemini API key.
            output_dir: Directory where images/logs are saved.
        """
        self.api_key = api_key
        self.output_dir = output_dir

        # Image client (Imagen 3)
        self.client = genai.Client(api_key=api_key)

        # Text client (Gemini‑Pro) for prompt crafting
        legacy_genai.configure(api_key=api_key)
        self.text_model = legacy_genai.GenerativeModel("gemini-2.5-pro")

        os.makedirs(output_dir, exist_ok=True)

        # ————————————————————————————————————————————————
        # CREATIVE BRIEF (static, but easy to edit)
        # ————————————————————————————————————————————————
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

        # ————————————————————————————————————————————————
        # PROMPT REQUIREMENTS (now modular)
        #   • Edit, reorder, or randomise as you like.
        #   • Each entry is a requirement sentence; numbering is added
        #     automatically when building the full prompt.
        # ————————————————————————————————————————————————
        self.prompt_requirements: List[str] = [
            "Generate a **fresh, non-repetitive concept** for this image only (don’t echo earlier prompts).",
            "Depict the product in a visually compelling way — this may include a full-body runner, just the lower leg/foot in motion, or the shoe alone, depending on what best fits the concept.",
            "Reinforce the brand tone: confident, empowering, inclusive, performance-driven.",
            "Place the scene in a **specific time, location, and atmosphere** that amplifies comfort and motion.",
            "Direct the viewer’s eye with strong composition cues.",
            "Specify camera viewpoint and technical look: lens focal length, aperture, motion blur, or—if illustrative—brush style/texture.",
            "Define lighting mood and a colour palette that harmonises with Brooks brand hues.",
            "Integrate **subtle Brooks identifiers** without cluttering the frame.",
            "Overlay the **brand** and the **tagline** in negative space using clean, modern typography.",
            "Choose an atmosphere (e.g. elegant, vibrant, kinetic, tranquil, earthy, viblant, dynamic, chic, modern, urban, moody, or serene) that complements the shoe's identity and enhances visual storytelling."
            "Highlight at least one technical feature (DNA-Tuned midsole cell structure, knit upper texture) in crisp detail.",
            "Include a short **negative prompt** to avoid rival logos, distorted anatomy, low-poly artefacts, or text errors.",
        ]

    # ------------------------------------------------------------------
    # PROMPT GENERATION
    # ------------------------------------------------------------------
    def _assemble_requirements_block(self) -> str:
        """Return the numbered requirements block as a single string."""
        lines = [f"{idx + 1}. {req}" for idx, req in enumerate(self.prompt_requirements)]
        return "\n".join(lines)

    def generate_image_prompt(self, image_number: int) -> str:
        """Ask Gemini to produce a detailed image prompt.

        The requirements block is re‑built each call, so you can modify
        self.prompt_requirements at runtime or subclass for variations.
        """
        prompt_request = f"""
        Based on this creative brief for Brooks Glycerin 22 running shoes:

        {self.creative_brief}

        Create a detailed, specific image generation prompt for ad image #{image_number}.
        Requirements:\n{self._assemble_requirements_block()}

        Return **only** the image generation prompt with no additional explanation.
        """

        try:
            response = self.text_model.generate_content(prompt_request)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating prompt for image {image_number}: {e}")
            return (
                "High‑quality advertising photo of Brooks Glycerin 22 running shoe, "
                "dynamic composition, dramatic lighting, modern aesthetics"
            )

    # ------------------------------------------------------------------
    # IMAGE GENERATION (unchanged)
    # ------------------------------------------------------------------
    def generate_image(self, prompt: str, image_number: int) -> str:
        try:
            print(f"Generating image {image_number} → {prompt[:90]}…")

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
            print("  ⚠️ No images returned")
            return None
        except Exception as e:
            print(f"Error generating image {image_number}: {e}")
            return None

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------
    def generate_all_ads(self, num_images: int = 10) -> List[Dict]:
        generated_images = []
        print("Starting Brooks Glycerin 22 ad image generation…")
        print(f"Output directory: {self.output_dir}")
        print("-" * 60)

        for i in range(1, num_images + 1):
            print(f"\n[{i}/{num_images}] Crafting prompt…")
            image_prompt = self.generate_image_prompt(i)
            print("  → Generating image…")
            image_path = self.generate_image(image_prompt, i)

            generated_images.append(
                {
                    "image_number": i,
                    "prompt": image_prompt,
                    "image_path": image_path,
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            time.sleep(3)  # Respect rate limits
            print(f"  ✓ Completed image {i}")

        self._save_generation_log(generated_images)
        print(f"\n✅ Generated {len(generated_images)} ad images!")
        print(f"📁 Saved in: {self.output_dir}")
        return generated_images

    # ------------------------------------------------------------------
    # LOGGING
    # ------------------------------------------------------------------
    def _save_generation_log(self, images_info: List[Dict]):
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


# ------------------------------------------------------------
# CLI ENTRY POINT
# ------------------------------------------------------------

def main():
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        print("❌ GOOGLE_API_KEY missing (set in .env)")
        return

    NUM_IMAGES = int(os.getenv("NUM_AD_IMAGES", "100"))

    gen = BrooksAdImageGenerator(api_key=API_KEY, output_dir="brooks_glycerin_22_campaign")



    try:
        gen.generate_all_ads(num_images=NUM_IMAGES)
    except Exception as e:
        print(f"Fatal error: {e}\nCheck your API key and internet connection.")


if __name__ == "__main__":
    print("Brooks Glycerin 22 Ad Image Generator – Dynamic & Modular")
    print("=" * 50)
    main()
