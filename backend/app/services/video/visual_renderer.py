import os
import math
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from app.services.video.scene_planner import VideoScene
from app.core.logging import logger


class VisualRenderer:
    """
    Renders high-resolution 1280x720 graphic frames for each video scene.
    Supports LaTeX formulas, code cards, flowchart diagrams, and concept cards.
    """

    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self._load_fonts()

    def _load_fonts(self):
        try:
            # Standard Windows fonts
            self.title_font = ImageFont.truetype("arialbd.ttf", 36)
            self.header_font = ImageFont.truetype("arialbd.ttf", 26)
            self.body_font = ImageFont.truetype("arial.ttf", 22)
            self.code_font = ImageFont.truetype("consola.ttf", 20)
            self.small_font = ImageFont.truetype("arial.ttf", 16)
            self.badge_font = ImageFont.truetype("arialbd.ttf", 16)
        except Exception:
            self.title_font = ImageFont.load_default()
            self.header_font = ImageFont.load_default()
            self.body_font = ImageFont.load_default()
            self.code_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
            self.badge_font = ImageFont.load_default()

    def render_scene_frame(
        self,
        scene: VideoScene,
        time_sec: float,
        total_scene_sec: float
    ) -> Image.Image:
        """
        Renders a single video frame for the given scene at timestamp time_sec.
        """
        # Create base canvas with rich dark background (#0f172a to #1e293b gradient)
        img = Image.new("RGB", (self.width, self.height), color="#0f172a")
        draw = ImageDraw.Draw(img)

        # Draw background ambient grid lines
        for x in range(0, self.width, 60):
            draw.line([(x, 0), (x, self.height)], fill="#1e293b", width=1)
        for y in range(0, self.height, 60):
            draw.line([(0, y), (self.width, y)], fill="#1e293b", width=1)

        # Top Header Bar
        self._draw_header(draw, scene)

        # Main Stage Area (Left / Center Stage: x: 40 to 860, y: 100 to 600)
        v_type = (scene.visual_type or "text_card").lower()
        v_data = scene.visual_data or {}

        if v_type == "math":
            self._draw_math_board(draw, scene, v_data, time_sec)
        elif v_type == "code":
            self._draw_code_board(draw, scene, v_data, time_sec)
        elif v_type == "diagram":
            self._draw_diagram_board(draw, scene, v_data, time_sec)
        else:
            self._draw_concept_card(draw, scene, v_data, time_sec)

        # Bottom Subtitle & Narration Bar
        self._draw_subtitle_bar(draw, scene, time_sec, total_scene_sec)

        return img

    def _draw_header(self, draw: ImageDraw.ImageDraw, scene: VideoScene):
        # Header banner container
        draw.rectangle([(30, 20), (self.width - 30, 80)], fill="#1e293b", outline="#334155", width=2)
        
        # Subject / Scene Type Badge
        badge_text = f"SCENE {scene.scene_number} • {scene.scene_type.upper()}"
        draw.rounded_rectangle([(45, 32), (260, 68)], radius=6, fill="#3b82f6")
        draw.text((60, 42), badge_text, font=self.badge_font, fill="#ffffff")

        # Concept Title
        title = scene.title[:65]
        draw.text((280, 36), title, font=self.header_font, fill="#f8fafc")

    def _draw_concept_card(self, draw: ImageDraw.ImageDraw, scene: VideoScene, data: Dict[str, Any], t: float):
        # Main content card
        card_rect = [(40, 100), (860, 580)]
        draw.rounded_rectangle(card_rect, radius=12, fill="#1e293b", outline="#475569", width=2)

        # Concept headline
        draw.text((70, 130), scene.concept, font=self.title_font, fill="#38bdf8")
        draw.line([(70, 180), (830, 180)], fill="#334155", width=2)

        # Key points / items
        items = data.get("items", [])
        if items:
            y_offset = 205
            for idx, item in enumerate(items[:4]):
                draw.ellipse([(70, y_offset + 6), (82, y_offset + 18)], fill="#10b981")
                draw.text((95, y_offset), f"{item}", font=self.body_font, fill="#e2e8f0")
                y_offset += 50
        else:
            # Multiline text wrap
            lines = self._wrap_text(scene.on_screen_text, 50)
            y_offset = 205
            for line in lines[:8]:
                draw.text((70, y_offset), line, font=self.body_font, fill="#cbd5e1")
                y_offset += 36

        # Analogy or example callout box
        if data.get("analogy") or data.get("example"):
            callout = data.get("analogy") or data.get("example") or ""
            draw.rounded_rectangle([(65, 450), (835, 550)], radius=8, fill="#0f172a", outline="#f59e0b", width=1)
            draw.text((85, 465), "💡 Key Intuition:", font=self.header_font, fill="#f59e0b")
            callout_lines = self._wrap_text(str(callout), 55)
            for i, cl in enumerate(callout_lines[:2]):
                draw.text((85, 498 + i * 24), cl, font=self.body_font, fill="#fef3c7")

    def _draw_math_board(self, draw: ImageDraw.ImageDraw, scene: VideoScene, data: Dict[str, Any], t: float):
        card_rect = [(40, 100), (860, 580)]
        draw.rounded_rectangle(card_rect, radius=12, fill="#1e293b", outline="#8b5cf6", width=2)

        draw.text((70, 125), "Mathematical Derivation & Formula", font=self.header_font, fill="#a78bfa")
        draw.line([(70, 165), (830, 165)], fill="#334155", width=2)

        # Main Equation Highlight Box
        eq = data.get("equation") or data.get("formula") or scene.concept
        draw.rounded_rectangle([(70, 185), (830, 275)], radius=8, fill="#0f172a", outline="#c084fc", width=2)
        draw.text((100, 210), f"$$ {eq} $$", font=self.title_font, fill="#f3e8ff")

        # Step-by-step derivations
        steps = data.get("steps", [])
        y_offset = 300
        for i, st in enumerate(steps[:5]):
            draw.text((75, y_offset), f"• {st}", font=self.body_font, fill="#e2e8f0")
            y_offset += 40

    def _draw_code_board(self, draw: ImageDraw.ImageDraw, scene: VideoScene, data: Dict[str, Any], t: float):
        card_rect = [(40, 100), (860, 580)]
        draw.rounded_rectangle(card_rect, radius=12, fill="#020617", outline="#0284c7", width=2)

        # Editor header
        draw.rectangle([(40, 100), (860, 140)], fill="#0f172a")
        draw.ellipse([(60, 115), (72, 127)], fill="#ef4444")
        draw.ellipse([(80, 115), (92, 127)], fill="#f59e0b")
        draw.ellipse([(100, 115), (112, 127)], fill="#10b981")
        draw.text((140, 110), f"solution.{data.get('language', 'py')}", font=self.small_font, fill="#94a3b8")

        # Code lines
        raw_code = data.get("code") or scene.on_screen_text
        lines = raw_code.split("\n")
        y_offset = 155
        for i, line in enumerate(lines[:10]):
            # Line number
            draw.text((55, y_offset), f"{i+1:2d}", font=self.code_font, fill="#475569")
            draw.text((95, y_offset), line, font=self.code_font, fill="#38bdf8")
            y_offset += 28

        # Output terminal preview
        if data.get("output"):
            draw.rounded_rectangle([(60, 480), (840, 555)], radius=6, fill="#1e293b", outline="#334155", width=1)
            draw.text((75, 490), "❯ Execution Output:", font=self.badge_font, fill="#10b981")
            draw.text((75, 518), str(data.get("output")), font=self.code_font, fill="#a7f3d0")

    def _draw_diagram_board(self, draw: ImageDraw.ImageDraw, scene: VideoScene, data: Dict[str, Any], t: float):
        card_rect = [(40, 100), (860, 580)]
        draw.rounded_rectangle(card_rect, radius=12, fill="#1e293b", outline="#06b6d4", width=2)

        draw.text((70, 125), "Conceptual Flow & Interaction Diagram", font=self.header_font, fill="#22d3ee")
        draw.line([(70, 165), (830, 165)], fill="#334155", width=2)

        # Dynamic 3-stage visual flow nodes
        nodes = [
            ("1. Input / State", "Initial System Conditions"),
            ("2. Core Transformation", scene.concept[:30]),
            ("3. Result / Equilibrium", "Final Observable State")
        ]
        
        y_center = 300
        x_positions = [180, 450, 720]

        for i, (node_title, node_sub) in enumerate(nodes):
            cx = x_positions[i]
            # Pulsing active node based on time
            is_active = int(t * 1.5) % 3 == i
            outline_color = "#38bdf8" if is_active else "#64748b"
            bg_color = "#0369a1" if is_active else "#0f172a"

            draw.rounded_rectangle([(cx - 100, y_center - 60), (cx + 100, y_center + 60)], radius=10, fill=bg_color, outline=outline_color, width=2)
            draw.text((cx - 85, y_center - 35), node_title, font=self.badge_font, fill="#f8fafc")
            draw.text((cx - 85, y_center), node_sub[:24], font=self.small_font, fill="#bae6fd")

            # Connector arrow to next node
            if i < len(nodes) - 1:
                next_x = x_positions[i + 1]
                draw.line([(cx + 100, y_center), (next_x - 100, y_center)], fill="#38bdf8", width=3)
                draw.polygon([(next_x - 100, y_center), (next_x - 110, y_center - 6), (next_x - 110, y_center + 6)], fill="#38bdf8")

        # Bottom analogy / rule
        if data.get("analogy") or scene.concept:
            rule_text = data.get("analogy") or f"Key physical law governing {scene.concept}"
            draw.rounded_rectangle([(65, 470), (835, 550)], radius=8, fill="#0f172a", outline="#0284c7", width=1)
            draw.text((85, 485), f"💡 Takeaway: {rule_text[:75]}", font=self.body_font, fill="#e0f2fe")

    def _draw_subtitle_bar(self, draw: ImageDraw.ImageDraw, scene: VideoScene, t: float, total_t: float):
        # Subtitle Container at bottom
        draw.rounded_rectangle([(30, 600), (self.width - 30, 700)], radius=8, fill="#020617", outline="#1e293b", width=2)
        
        # Audio speaker icon indicator
        draw.text((50, 615), "🔊 AI Teacher Narration:", font=self.badge_font, fill="#38bdf8")

        # Animated typed narration words
        words = scene.narration.split()
        if total_t > 0:
            fraction = min(1.0, max(0.0, t / total_t))
            word_count = max(1, int(fraction * len(words)))
            visible_text = " ".join(words[:word_count])
        else:
            visible_text = scene.narration

        lines = self._wrap_text(visible_text, 90)
        y = 640
        for line in lines[:2]:
            draw.text((50, y), line, font=self.body_font, fill="#f8fafc")
            y += 26

        # Progress bar at very bottom
        pct = min(1.0, max(0.0, t / total_t)) if total_t > 0 else 1.0
        bar_w = int((self.width - 60) * pct)
        draw.rectangle([(30, 696), (30 + bar_w, 700)], fill="#3b82f6")

    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        words = text.split()
        lines = []
        cur = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 <= max_chars:
                cur.append(w)
                cur_len += len(w) + 1
            else:
                lines.append(" ".join(cur))
                cur = [w]
                cur_len = len(w)
        if cur:
            lines.append(" ".join(cur))
        return lines
