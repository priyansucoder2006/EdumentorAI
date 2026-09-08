import math
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont


class AvatarRenderer:
    """
    Renders an animated, emotionally expressive AI Teacher avatar in Picture-in-Picture mode.
    Includes natural blinking, lip-sync mouth movement during speech, and mood styling.
    """

    def __init__(self):
        try:
            self.badge_font = ImageFont.truetype("arialbd.ttf", 15)
            self.name_font = ImageFont.truetype("arialbd.ttf", 18)
            self.sub_font = ImageFont.truetype("arial.ttf", 13)
        except Exception:
            self.badge_font = ImageFont.load_default()
            self.name_font = ImageFont.load_default()
            self.sub_font = ImageFont.load_default()

    def draw_avatar_overlay(
        self,
        base_img: Image.Image,
        time_sec: float,
        mood: str = "explaining",
        is_speaking: bool = True
    ) -> Image.Image:
        """
        Composites the animated AI Teacher Avatar into the right panel (x: 880 to 1250, y: 100 to 580).
        """
        draw = ImageDraw.Draw(base_img)

        # Panel frame
        panel_rect = [(880, 100), (1240, 580)]
        draw.rounded_rectangle(panel_rect, radius=12, fill="#0f172a", outline="#3b82f6", width=2)

        # Avatar window top bar
        draw.rectangle([(880, 100), (1240, 140)], fill="#1e293b")
        draw.text((895, 112), "👨‍🏫 AI Master Teacher", font=self.name_font, fill="#f8fafc")

        # Mood badge
        mood_colors = {
            "explaining": ("#3b82f6", "Explaining"),
            "questioning": ("#f59e0b", "Questioning"),
            "praising": ("#10b981", "Praising"),
            "remedial": ("#ec4899", "Remedial Coaching")
        }
        badge_color, badge_label = mood_colors.get(mood.lower(), ("#3b82f6", "Teaching"))
        draw.rounded_rectangle([(1100, 110), (1225, 134)], radius=4, fill=badge_color)
        draw.text((1110, 114), badge_label, font=self.badge_font, fill="#ffffff")

        # Avatar Center coordinates
        cx = 1060
        cy = 310

        # Background spotlight glow behind avatar
        glow_radius = 110
        draw.ellipse([(cx - glow_radius, cy - 70 - glow_radius), (cx + glow_radius, cy - 70 + glow_radius)], fill="#1e3a8a")

        # 1. Torso / Shoulders (Professional navy blazer + crisp white shirt)
        draw.rounded_rectangle([(cx - 85, cy + 80), (cx + 85, cy + 240)], radius=25, fill="#1e293b", outline="#334155", width=2)
        # Shirt V-neck & Collar
        draw.polygon([(cx - 30, cy + 80), (cx + 30, cy + 80), (cx, cy + 140)], fill="#f8fafc")
        draw.polygon([(cx - 10, cy + 120), (cx + 10, cy + 120), (cx, cy + 180)], fill="#3b82f6")  # Tie

        # 2. Neck
        draw.rectangle([(cx - 20, cy + 40), (cx + 20, cy + 85)], fill="#fcd34d")

        # 3. Head (Warm skin tone oval)
        head_w = 60
        head_h = 75
        draw.ellipse([(cx - head_w, cy - head_h), (cx + head_w, cy + head_h)], fill="#fcd34d", outline="#d97706", width=2)

        # 4. Hair (Neat modern styling)
        draw.ellipse([(cx - head_w - 5, cy - head_h - 15), (cx + head_w + 5, cy - 10)], fill="#1c1917")
        draw.chord([(cx - head_w, cy - head_h - 10), (cx + head_w, cy + 5)], 180, 360, fill="#1c1917")

        # 5. Eyebrows
        eyebrow_y = cy - 25
        if mood == "questioning":
            # Raised right eyebrow
            draw.line([(cx - 35, eyebrow_y + 2), (cx - 15, eyebrow_y - 2)], fill="#1c1917", width=3)
            draw.line([(cx + 15, eyebrow_y - 6), (cx + 35, eyebrow_y - 12)], fill="#1c1917", width=3)
        else:
            draw.line([(cx - 35, eyebrow_y), (cx - 15, eyebrow_y - 2)], fill="#1c1917", width=3)
            draw.line([(cx + 15, eyebrow_y - 2), (cx + 35, eyebrow_y)], fill="#1c1917", width=3)

        # 6. Eyes & Natural Blinking (blink every 3.5 seconds for 0.15 sec)
        blink_cycle = time_sec % 3.5
        is_blinking = blink_cycle < 0.18

        eye_y = cy - 10
        if is_blinking:
            draw.line([(cx - 35, eye_y), (cx - 15, eye_y)], fill="#1c1917", width=3)
            draw.line([(cx + 15, eye_y), (cx + 35, eye_y)], fill="#1c1917", width=3)
        else:
            # Left Eye
            draw.ellipse([(cx - 36, eye_y - 8), (cx - 14, eye_y + 8)], fill="#ffffff")
            draw.ellipse([(cx - 28, eye_y - 5), (cx - 20, eye_y + 5)], fill="#0284c7")
            draw.ellipse([(cx - 26, eye_y - 3), (cx - 22, eye_y + 3)], fill="#0f172a")
            # Right Eye
            draw.ellipse([(cx + 14, eye_y - 8), (cx + 36, eye_y + 8)], fill="#ffffff")
            draw.ellipse([(cx + 20, eye_y - 5), (cx + 28, eye_y + 5)], fill="#0284c7")
            draw.ellipse([(cx + 22, eye_y - 3), (cx + 26, eye_y + 3)], fill="#0f172a")

        # 7. Modern Smart Glasses
        draw.rounded_rectangle([(cx - 42, eye_y - 14), (cx - 8, eye_y + 14)], radius=4, outline="#38bdf8", width=2)
        draw.rounded_rectangle([(cx + 8, eye_y - 14), (cx + 42, eye_y + 14)], radius=4, outline="#38bdf8", width=2)
        draw.line([(cx - 8, eye_y), (cx + 8, eye_y)], fill="#38bdf8", width=2)

        # 8. Nose
        draw.polygon([(cx, cy), (cx - 4, cy + 18), (cx + 4, cy + 18)], fill="#d97706")

        # 9. Mouth Lip-Sync Animation
        mouth_y = cy + 40
        if is_speaking:
            # Fast phonetic lip oscillation (5 Hz frequency)
            mouth_phase = (math.sin(time_sec * 12.0) + 1.0) / 2.0  # 0.0 to 1.0
            open_h = int(4 + mouth_phase * 14)
            mouth_w = int(16 + mouth_phase * 4)
            # Open mouth with teeth / tongue hint
            draw.ellipse([(cx - mouth_w, mouth_y - open_h // 2), (cx + mouth_w, mouth_y + open_h // 2)], fill="#881337", outline="#4c0519", width=2)
            if open_h > 8:
                draw.rectangle([(cx - 10, mouth_y - open_h // 2 + 2), (cx + 10, mouth_y - open_h // 2 + 5)], fill="#ffffff")  # Teeth
        else:
            # Friendly gentle smile
            draw.arc([(cx - 20, mouth_y - 10), (cx + 20, mouth_y + 10)], 0, 180, fill="#881337", width=3)

        # 10. Live Audio Waveform Indicator at bottom of panel
        draw.rounded_rectangle([(895, 520), (1225, 565)], radius=6, fill="#1e293b", outline="#334155", width=1)
        draw.text((910, 532), "Voice Synthesizer: Active", font=self.sub_font, fill="#10b981")

        # Animated Audio Bars
        for b_idx in range(8):
            bx = 1130 + b_idx * 11
            b_height = int(6 + 14 * abs(math.sin(time_sec * 8.0 + b_idx * 0.8))) if is_speaking else 4
            draw.line([(bx, 552), (bx, 552 - b_height)], fill="#38bdf8", width=4)

        return base_img
