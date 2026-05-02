#!/usr/bin/env python3
"""
RLM explainer animation — v3.
Nemotron Nano Omni feedback-driven improvements:
  - Cohesive 4-color palette (blue/green/yellow/dim)
  - Frame 1: doc as scroll feeding into window (size mismatch)
  - "RLM: Recursive Language Model" defined early
  - Frame 2: visually useful, not just title card
  - Frame 4: clear downward arrows, Sub-LLM labels
  - Frame 5: aggregation arrows from sub-LLMs into ROOT LLM
  - Bigger fonts, bold key terms
  - Standardized document iconography
Covers: problem -> define -> chunk -> delegate -> aggregate -> answer
"""

import cairo
import math
import os
import subprocess

# ── Config ──────────────────────────────────
W, H = 854, 480
FPS = 24
DURATION = 5.0
TOTAL_FRAMES = int(FPS * DURATION)

# ── Cohesive 4-color palette ────────────────
BG = (0.11, 0.11, 0.11)       # #1C1C1C
BLUE = (0.345, 0.769, 0.867)  # #58C4DD — ROOT LLM, key elements
GREEN = (0.514, 0.757, 0.404) # #83C167 — sub-LLMs, processing
YELLOW = (1.0, 0.839, 0.0)    # #FFD600 — final answer, highlights
DIM = (0.40, 0.40, 0.40)      # #666666 — document, context
WHITE = (0.92, 0.92, 0.92)    # #EAEAEA
RED = (1.0, 0.42, 0.42)       # #FF6B6B — overflow warning

# Chunk colors — shades of blue (cohesive)
CHUNK_COLORS = [
    (0.345, 0.769, 0.867),  # bright blue
    (0.25, 0.60, 0.75),     # medium blue
    (0.20, 0.50, 0.65),     # deeper blue
    (0.40, 0.65, 0.80),     # light slate
    (0.30, 0.55, 0.70),     # steel blue
]

OUT_DIR = "/tmp/rlm_v3_frames"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Drawing helpers ────────────────────────

def rounded_rect(ctx, x, y, w, h, r=8):
    ctx.move_to(x + r, y)
    ctx.line_to(x + w - r, y)
    ctx.arc(x + w - r, y + r, r, -math.pi/2, 0)
    ctx.line_to(x + w, y + h - r)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi/2)
    ctx.line_to(x + r, y + h)
    ctx.arc(x + r, y + h - r, r, math.pi/2, math.pi)
    ctx.line_to(x, y + r)
    ctx.arc(x + r, y + r, r, math.pi, 3*math.pi/2)
    ctx.close_path()

def draw_text(ctx, text, x, y, color=WHITE, size=22, center=True, mono=False, bold=True):
    ctx.set_source_rgb(*color)
    face = "monospace" if mono else "sans-serif"
    weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    ext = ctx.text_extents(text)
    tw, th = ext[2], ext[3]
    tx = x - tw/2 if center else x
    ty = y + th/3
    ctx.move_to(tx, ty)
    ctx.show_text(text)
    return ext

def draw_arrow(ctx, x1, y1, x2, y2, color, width=2.5, head_size=10):
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    ctx.set_line_width(width)
    ctx.set_source_rgb(*color)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()
    # Arrowhead
    ctx.move_to(x2, y2)
    ctx.line_to(x2 - head_size * math.cos(angle - 0.4),
                y2 - head_size * math.sin(angle - 0.4))
    ctx.move_to(x2, y2)
    ctx.line_to(x2 - head_size * math.cos(angle + 0.4),
                y2 - head_size * math.sin(angle + 0.4))
    ctx.stroke()

def fill_rounded(ctx, x, y, w, h, color, r=8):
    ctx.set_source_rgb(*color)
    rounded_rect(ctx, x, y, w, h, r)
    ctx.fill()

def stroke_rounded(ctx, x, y, w, h, color, r=8, width=2):
    ctx.set_line_width(width)
    ctx.set_source_rgb(*color)
    rounded_rect(ctx, x, y, w, h, r)
    ctx.stroke()

def fill_circle(ctx, cx, cy, r, color):
    ctx.set_source_rgb(*color)
    ctx.arc(cx, cy, r, 0, 2*math.pi)
    ctx.fill()

def stroke_circle(ctx, cx, cy, r, color, width=2):
    ctx.set_line_width(width)
    ctx.set_source_rgb(*color)
    ctx.arc(cx, cy, r, 0, 2*math.pi)
    ctx.stroke()

def lerp(a, b, t):
    return a + (b - a) * max(0, min(1, t))

def ease(t):
    return t * t * (3 - 2 * t)


# ── Scene rendering ────────────────────────

def render_frame(frame_num):
    t = frame_num / FPS
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    cx, cy = W / 2, H / 2

    # Clear background
    ctx.set_source_rgb(*BG)
    ctx.paint()

    # ════════════════════════════════════════════
    # Phase 1: Problem (0.0s - 1.0s)
    # Show massive doc scroll feeding THROUGH tiny context window
    # ════════════════════════════════════════════
    if t < 1.0:
        p = t / 1.0
        p_eased = ease(p)

        # Title
        draw_text(ctx, "Context Too Big?", cx, 40, WHITE, 34, bold=True)

        # The tiny context window — placed in center as a "viewport"
        win_w, win_h = 220, 48
        win_x = cx - win_w / 2
        win_y = 85
        fill_rounded(ctx, win_x, win_y, win_w, win_h, (0.08, 0.08, 0.12), r=6)
        stroke_rounded(ctx, win_x, win_y, win_w, win_h, BLUE, r=6, width=2.5)
        draw_text(ctx, "Context Window (128K)", cx, win_y + win_h / 2, BLUE, 14, bold=True)

        # The massive document scroll — grows downward THROUGH the window
        total_scroll_h = 360
        scroll_h = int(lerp(0, total_scroll_h, p_eased))
        scroll_w = 140
        scroll_x = cx - scroll_w / 2
        scroll_top = win_y + win_h / 2 - int(lerp(0, 180, p_eased))

        # Draw the entire scroll body
        fill_rounded(ctx, scroll_x, scroll_top, scroll_w, scroll_h, (0.18, 0.18, 0.18), r=4)
        stroke_rounded(ctx, scroll_x, scroll_top, scroll_w, scroll_h, DIM, r=4, width=1.5)

        # Simulated text lines inside scroll
        line_count = min(scroll_h // 14, 24)
        for row in range(line_count):
            line_w = lerp(70, 110, (row * 17) % 100 / 100)
            lx = scroll_x + (scroll_w - line_w) / 2
            ly = scroll_top + 18 + row * 14
            ctx.set_source_rgb(*DIM)
            ctx.set_line_width(3)
            ctx.move_to(lx, ly)
            ctx.line_to(lx + line_w, ly)
            ctx.stroke()

        # Highlight the part of the scroll VISIBLE through the window
        # Overlay a semi-transparent blue rectangle between scroll_top and window bottom
        if scroll_h > win_y - scroll_top + win_h:
            clip_y = max(scroll_top, win_y)
            clip_bottom = min(scroll_top + scroll_h, win_y + win_h)
            clip_h = clip_bottom - clip_y
            if clip_h > 0:
                ctx.rectangle(win_x + 3, clip_y + 3, win_w - 6, clip_h - 6)
                ctx.clip()
                fill_rounded(ctx, scroll_x, scroll_top, scroll_w, scroll_h, (0.25, 0.25, 0.35), r=0)
                ctx.reset_clip()

        # Label below scroll
        scroll_bottom = scroll_top + scroll_h
        draw_text(ctx, "MILLION-TOKEN DOCUMENT", cx, scroll_bottom + 25, DIM, 15, bold=True)

        # Overflow indicators — doc extends past window on both sides
        if p_eased > 0.4:
            op = (p_eased - 0.4) / 0.6
            # Left overflow (doc scroll visible to left of window)
            left_extra = 50 * op
            fill_rounded(ctx, scroll_x - left_extra, scroll_top, left_extra, scroll_h, (0.14, 0.14, 0.14), r=0)
            # Right overflow
            fill_rounded(ctx, scroll_x + scroll_w, scroll_top, 50 * op, scroll_h, (0.14, 0.14, 0.14), r=0)
            # RED overflow arrows
            ctx.set_source_rgb(*RED)
            ctx.set_line_width(3)
            ox = scroll_x - left_extra - 5
            ctx.move_to(ox, scroll_top + scroll_h / 2)
            ctx.line_to(ox + 30, scroll_top + scroll_h / 2)
            ctx.stroke()
            ctx.move_to(ox + 10, scroll_top + scroll_h / 2 - 5)
            ctx.line_to(ox + 25, scroll_top + scroll_h / 2)
            ctx.line_to(ox + 10, scroll_top + scroll_h / 2 + 5)
            ctx.set_source_rgb(*RED)
            ctx.fill()

            ox2 = scroll_x + scroll_w + 50 * op + 5
            ctx.set_source_rgb(*RED)
            ctx.set_line_width(3)
            ctx.move_to(ox2, scroll_top + scroll_h / 2)
            ctx.line_to(ox2 - 30, scroll_top + scroll_h / 2)
            ctx.stroke()
            ctx.move_to(ox2 - 10, scroll_top + scroll_h / 2 - 5)
            ctx.line_to(ox2 - 25, scroll_top + scroll_h / 2)
            ctx.line_to(ox2 - 10, scroll_top + scroll_h / 2 + 5)
            ctx.set_source_rgb(*RED)
            ctx.fill()

            # OVERFLOW text
            ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(13)
            ctx.set_source_rgb(*RED)
            ctx.move_to(scroll_x - left_extra - 78, scroll_top + scroll_h / 2 - 12)
            ctx.show_text("OVERFLOW")
            ctx.move_to(scroll_x + scroll_w + 50 * op + 12, scroll_top + scroll_h / 2 - 12)
            ctx.show_text("OVERFLOW")

    # ════════════════════════════════════════════
    # Phase 2: Define RLM + Chunk Overview (1.0s - 2.0s)
    # Animate the document splitting into chunks
    # ════════════════════════════════════════════
    elif t < 2.0:
        p = (t - 1.0) / 1.0
        p_eased = ease(p)

        # Title with RLM definition
        draw_text(ctx, "RLM : Recursive Language Model", cx, 40, BLUE, 28, bold=True)
        draw_text(ctx, "break huge contexts into manageable pieces", cx, 72, DIM, 15, bold=False)

        # Stage 1: Show the monolithic document bar (0.0-0.3)
        bar_y = 110
        bar_h = 50
        bar_x = 50
        bar_w = W - 100

        if p_eased < 0.3:
            bar_p = p_eased / 0.3
            bar_appear_w = int(lerp(0, bar_w, bar_p))
            fill_rounded(ctx, bar_x + (bar_w - bar_appear_w) / 2, bar_y,
                         bar_appear_w, bar_h, (0.15, 0.15, 0.15), r=6)
            stroke_rounded(ctx, bar_x + (bar_w - bar_appear_w) / 2, bar_y,
                           bar_appear_w, bar_h, DIM, r=6, width=1.5)
            if bar_p > 0.5:
                draw_text(ctx, "Million-Token Document (monolithic)",
                          cx, bar_y + bar_h / 2, DIM, 14, bold=True)

        # Stage 2: Document splits into 5 chunks (0.3-0.7)
        elif p_eased < 0.7:
            split_p = (p_eased - 0.3) / 0.4

            # Draw the full bar first
            fill_rounded(ctx, bar_x, bar_y, bar_w, bar_h, (0.15, 0.15, 0.15), r=6)

            # Divide bar into chunks with gaps expanding
            gap = int(lerp(0, 8, split_p))
            chunk_count = 5
            chunk_total_w = bar_w - 10 * 2
            chunk_w = (chunk_total_w - (chunk_count - 1) * gap) / chunk_count
            chunk_x_start = bar_x + 10

            for ci in range(chunk_count):
                cx_pos = chunk_x_start + ci * (chunk_w + gap)
                fill_rounded(ctx, cx_pos, bar_y + 6, chunk_w, bar_h - 12,
                             CHUNK_COLORS[ci], r=4)
                draw_text(ctx, f"C{ci+1}", cx_pos + chunk_w / 2,
                          bar_y + bar_h / 2, WHITE, 13, bold=True)

            # Label under the bar
            draw_text(ctx, "document split into 5 chunks",
                      cx, bar_y + bar_h + 25, GREEN, 16, bold=True)

        # Stage 3: Show the delegation concept (0.7-1.0)
        else:
            delegate_p = (p_eased - 0.7) / 0.3

            # Chunks still shown
            gap = 8
            chunk_count = 5
            chunk_total_w = bar_w - 20
            chunk_w = (chunk_total_w - (chunk_count - 1) * gap) / chunk_count
            chunk_x_start = bar_x + 10
            for ci in range(chunk_count):
                cx_pos = chunk_x_start + ci * (chunk_w + gap)
                fill_rounded(ctx, cx_pos, bar_y + 6, chunk_w, bar_h - 12,
                             CHUNK_COLORS[ci], r=4)
                draw_text(ctx, f"C{ci+1}", cx_pos + chunk_w / 2,
                          bar_y + bar_h / 2, WHITE, 13, bold=True)

            # Arrows going down to LLM icons
            llm_y = bar_y + bar_h + 50
            for ci in range(chunk_count):
                cx_pos = chunk_x_start + ci * (chunk_w + gap) + chunk_w / 2
                ap = max(0, min(1, (delegate_p * chunk_count - ci) * 1.5))
                if ap > 0:
                    arrow_end = lerp(bar_y + bar_h, llm_y - 16, ap)
                    draw_arrow(ctx, cx_pos, bar_y + bar_h + 5,
                               cx_pos, arrow_end, GREEN, width=2, head_size=7)
                    if ap > 0.7:
                        fill_circle(ctx, cx_pos, llm_y, 14, GREEN)
                        stroke_circle(ctx, cx_pos, llm_y, 14, WHITE, width=1.5)
                        draw_text(ctx, f"LLM{ci+1}", cx_pos, llm_y, WHITE, 9, bold=True)

            draw_text(ctx, "each chunk  →  sub-LLM  →  summary",
                      cx, llm_y + 30, GREEN, 16, bold=True)

    # ════════════════════════════════════════════
    # Phase 3: Chunk → Delegate (2.0s - 3.3s)
    # Chunks at top, arrows down to Sub-LLM circles
    # ════════════════════════════════════════════
    elif t < 3.3:
        p = (t - 2.0) / 1.3
        p_eased = ease(p)

        # Title
        draw_text(ctx, "RLM : Chunk & Delegate", cx, 50, BLUE, 28, bold=True)

        # 5 chunk boxes across the top
        chunk_count = 5
        chunk_w = 120
        chunk_h = 42
        total_w = chunk_count * chunk_w + (chunk_count - 1) * 8
        start_x = cx - total_w / 2
        chunk_y = 95

        for ci in range(chunk_count):
            cx_pos = start_x + ci * (chunk_w + 8)
            fill_rounded(ctx, cx_pos, chunk_y, chunk_w, chunk_h,
                         CHUNK_COLORS[ci], r=6)
            draw_text(ctx, f"Chunk {ci+1}", cx_pos + chunk_w / 2,
                      chunk_y + chunk_h / 2, WHITE, 15, bold=True)
            # Small size indicator
            draw_text(ctx, "~200K tokens", cx_pos + chunk_w / 2,
                      chunk_y + chunk_h + 14, DIM, 10, bold=False)

        # Sub-LLM circles below — appear one by one
        circle_y = chunk_y + chunk_h + 55
        circle_r = 26

        for ci in range(chunk_count):
            cx_pos = start_x + ci * (chunk_w + 8) + chunk_w / 2
            appear = max(0, min(1, (p_eased * chunk_count - ci) * 1.3))
            if appear > 0:
                # Arrow from chunk down to circle
                arrow_progress = min(1, appear * 2)
                arrow_end_y = lerp(chunk_y + chunk_h, circle_y - circle_r - 5, arrow_progress)
                draw_arrow(ctx, cx_pos, chunk_y + chunk_h + 5,
                           cx_pos, arrow_end_y, DIM, width=2, head_size=7)

                # Circle (sub-LLM)
                sr = circle_r * appear
                fill_circle(ctx, cx_pos, circle_y, sr, GREEN)
                stroke_circle(ctx, cx_pos, circle_y, sr, WHITE, width=1.5)
                if appear > 0.7:
                    draw_text(ctx, f"LLM{ci+1}", cx_pos, circle_y,
                              WHITE, 12, bold=True)

        # Sub-LLM label
        draw_text(ctx, "Sub-LLMs process each chunk in parallel",
                  cx, circle_y + circle_r + 25, GREEN, 16, bold=True)

        # Code snippet appearing at bottom
        if p_eased > 0.6:
            code_p = (p_eased - 0.6) / 0.4
            code_y = circle_y + circle_r + 50
            code_w, code_h = 380, 65
            code_x = cx - code_w / 2

            # Code box background
            fill_rounded(ctx, code_x, code_y, code_w, code_h * code_p,
                         (0.08, 0.08, 0.10), r=6)
            stroke_rounded(ctx, code_x, code_y, code_w, code_h * code_p,
                           DIM, r=6, width=1.5)
            if code_p > 0.3:
                draw_text(ctx, ">>> result = llm_query(f\"Summarize: {chunk}\")",
                          cx, code_y + 22, YELLOW, 13, mono=True, bold=False)
            if code_p > 0.6:
                draw_text(ctx, ">>> summary = aggregate(all_results)",
                          cx, code_y + 44, YELLOW, 13, mono=True, bold=False)

    # ════════════════════════════════════════════
    # Phase 4: Aggregate (3.3s - 4.2s)
    # Sub-LLM circles → arrows up → ROOT LLM → final answer
    # ════════════════════════════════════════════
    elif t < 4.2:
        p = (t - 3.3) / 0.9
        p_eased = ease(p)

        # Title
        draw_text(ctx, "RLM : Aggregate Results", cx, 45, BLUE, 28, bold=True)

        # Sub-LLM circles at the bottom
        chunk_count = 5
        circle_r = 24
        spacing = 110
        start_x = cx - (chunk_count - 1) * spacing / 2
        circle_y = H - 80

        for ci in range(chunk_count):
            cx_pos = start_x + ci * spacing
            fill_circle(ctx, cx_pos, circle_y, circle_r, GREEN)
            stroke_circle(ctx, cx_pos, circle_y, circle_r, WHITE, width=1.5)
            draw_text(ctx, f"LLM{ci+1}", cx_pos, circle_y, WHITE, 11, bold=True)

        # ROOT LLM circle in center
        root_cx, root_cy = cx, 170
        root_r = 38
        fill_circle(ctx, root_cx, root_cy, root_r, BLUE)
        stroke_circle(ctx, root_cx, root_cy, root_r, WHITE, width=2.5)
        draw_text(ctx, "ROOT", root_cx, root_cy - 8, WHITE, 14, bold=True)
        draw_text(ctx, "LLM", root_cx, root_cy + 12, WHITE, 14, bold=True)

        # Arrows from sub-LLMs up to ROOT LLM
        for ci in range(chunk_count):
            cx_pos = start_x + ci * spacing
            arrow_delay = ci * 0.12
            ap = max(0, min(1, (p_eased - arrow_delay) / 0.4))
            if ap > 0:
                ay2 = lerp(circle_y - circle_r - 5, root_cy + root_r + 5, ap)
                draw_arrow(ctx, cx_pos, circle_y - circle_r - 5,
                           cx_pos, ay2, YELLOW, width=2.5, head_size=9)
                # Summary label on arrow
                if ap > 0.8:
                    ctx.set_source_rgb(0.7, 0.7, 0.7)
                    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(9)
                    ctx.move_to(cx_pos + 12, (circle_y - circle_r - 5 + ay2) / 2)
                    ctx.show_text("summary")

        # Label
        if p_eased > 0.5:
            draw_text(ctx, "All summaries flow back to the ROOT LLM for synthesis",
                      cx, 115, DIM, 14, bold=False)

    # ════════════════════════════════════════════
    # Phase 5: Final Answer + CTA (4.2s - 5.0s)
    # ════════════════════════════════════════════
    else:
        p = (t - 4.2) / 0.8
        p_eased = ease(p)

        # Title
        draw_text(ctx, "RLM : Final Answer", cx, 45, BLUE, 28, bold=True)

        # ROOT LLM circle
        root_cx, root_cy = cx, 150
        root_r = 38
        fill_circle(ctx, root_cx, root_cy, root_r, BLUE)
        stroke_circle(ctx, root_cx, root_cy, root_r, WHITE, width=2.5)
        draw_text(ctx, "ROOT", root_cx, root_cy - 8, WHITE, 14, bold=True)
        draw_text(ctx, "LLM", root_cx, root_cy + 12, WHITE, 14, bold=True)

        # Sub-LLM circles (smaller, fading)
        chunk_count = 5
        circle_r = 20
        spacing = 95
        start_x = cx - (chunk_count - 1) * spacing / 2
        circle_y = H - 120

        for ci in range(chunk_count):
            cx_pos = start_x + ci * spacing
            fill_circle(ctx, cx_pos, circle_y, circle_r, GREEN)
            stroke_circle(ctx, cx_pos, circle_y, circle_r, DIM, width=1)
            draw_text(ctx, f"LLM{ci+1}", cx_pos, circle_y, WHITE, 10, bold=True)

        # Arrows from sub-LLMs up to ROOT LLM
        for ci in range(chunk_count):
            cx_pos = start_x + ci * spacing
            ap = max(0, min(1, (p_eased - ci * 0.1) / 0.3))
            if ap > 0:
                ay2 = lerp(circle_y - circle_r - 5, root_cy + root_r + 5, min(1, ap * 1.5))
                draw_arrow(ctx, cx_pos, circle_y - circle_r - 5,
                           cx_pos, ay2, YELLOW, width=2, head_size=8)

        # Final answer box appearing below
        answer_p = max(0, (p_eased - 0.4) / 0.6)
        if answer_p > 0:
            box_y = 210
            box_w = int(lerp(100, 400, answer_p))
            box_h = 50
            box_x = cx - box_w / 2
            fill_rounded(ctx, box_x, box_y, box_w, box_h, YELLOW, r=8)
            draw_text(ctx, "FINAL ANSWER", cx, box_y + box_h / 2,
                      BG, 20, bold=True)

            # Arrow from ROOT LLM to final answer
            draw_arrow(ctx, root_cx, root_cy + root_r + 5,
                       root_cx, box_y - 5, YELLOW, width=3, head_size=10)

        # CTA at bottom
        cta_p = max(0, (p_eased - 0.7) / 0.3)
        if cta_p > 0:
            draw_text(ctx, "Try it yourself:", cx, H - 75, DIM, 14, bold=False)
            draw_text(ctx, "pip install mini-rlm", cx, H - 45, GREEN, 20, mono=True, bold=True)
            # Pulsing circle indicator
            pulse = abs(math.sin(t * 6)) * 0.5 + 0.3
            fill_circle(ctx, cx - 175, H - 45, 5, (pulse, pulse, pulse))

    # Save frame
    path = os.path.join(OUT_DIR, f"frame_{frame_num:04d}.png")
    surface.write_to_png(path)
    surface.finish()
    return path


# ── Main ────────────────────────────────────

def main():
    print(f"Rendering {TOTAL_FRAMES} frames ({DURATION}s at {FPS}fps)...")
    for i in range(TOTAL_FRAMES):
        render_frame(i)
        if (i + 1) % 12 == 0:
            print(f"  Progress: {i+1}/{TOTAL_FRAMES} frames")
    print("Done rendering!")

    # Encode to video
    output_path = "/home/stormbird/Documents/mini-rlm/rlm-animation/rlm_explainer_v3.mp4"
    cmd = [
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", f"{OUT_DIR}/frame_%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "18",
        output_path
    ]
    print(f"Encoding video...")
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Video saved to {output_path}")

    # Cleanup
    import shutil
    shutil.rmtree(OUT_DIR)
    print("Temporary frames cleaned up.")

if __name__ == "__main__":
    main()
