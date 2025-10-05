# ANDIO One – A1111 Extension (UI + Routing)
# Path: stable-diffusion-webui/extensions/andio-one/scripts/andio_one.py
import json, os, base64, io, requests, gradio as gr
from PIL import Image
from modules import script_callbacks

ANDIO_TITLE = "ANDIO One – Wardrobe Inpaint"
A1111_URL = os.environ.get("ANDIO_A1111_URL", "http://127.0.0.1:7860")
PRESETS_PATH = os.path.join(os.path.dirname(__file__), "..", "presets", "outfits.json")

def _load_presets():
    try:
        with open(PRESETS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("outfits", []), data.get("materials", [])
    except Exception:
        return [], []

def _pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def _img_to_mask_b64(mask_img):
    # Falls die Maske als Dictionary (z. B. {'image':...}) kommt, extrahiere sie
    if isinstance(mask_img, dict):
        mask_img = mask_img.get("image", mask_img.get("mask", None))

    # Wenn sie als Bytes/Base64 kommt → dekodiere sie
    if isinstance(mask_img, str):
        if mask_img.startswith("data:image"):
            mask_img = mask_img.split(",")[1]
        mask_img = Image.open(io.BytesIO(base64.b64decode(mask_img)))

    # Prüfe, ob das ein gültiges PIL-Bild ist
    if not isinstance(mask_img, Image.Image):
        raise ValueError("Mask input is not a valid image.")

    # In Graustufen konvertieren
    if mask_img.mode != "L":
        mask_img = mask_img.convert("L")

    # In Base64 umwandeln
    buf = io.BytesIO()
    mask_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")
    
def _system_info():
    try:
        r = requests.get(f"{A1111_URL}/sdapi/v1/system-info", timeout=2)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def _inpaint_via_api(pil_img, pil_mask, prompt, neg_prompt, steps, cfg, denoise, sampler, seed, width, height):
    payload = {
        "init_images": [_pil_to_b64(pil_img)],
        "mask": _img_to_mask_b64(pil_mask) if pil_mask is not None else None,
        "resize_mode": 0,
        "prompt": prompt or "",
        "negative_prompt": neg_prompt or "",
        "steps": int(steps),
        "cfg_scale": float(cfg),
        "denoising_strength": float(denoise),
        "sampler_name": sampler or "Euler a",
        "seed": int(seed) if (isinstance(seed, int) or (isinstance(seed, str) and seed.isdigit())) else -1,
        "width": int(width),
        "height": int(height),
        "inpainting_fill": 1,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 32,
        "mask_blur": 4,
        "restore_faces": False,
        "tiling": False,
        "batch_size": 1,
        "n_iter": 1
    }
    r = requests.post(f"{A1111_URL}/sdapi/v1/img2img", json=payload, timeout=180)
    r.raise_for_status()
    out = r.json()
    images_b64 = out.get("images", [])
    results = []
    for b in images_b64:
        results.append(Image.open(io.BytesIO(base64.b64decode(b.split(",",1)[-1]))))
    return results

def _txt2img(prompt, neg_prompt, steps, cfg, sampler, seed, width, height):
    payload = {
        "prompt": prompt or "",
        "negative_prompt": neg_prompt or "",
        "steps": int(steps),
        "cfg_scale": float(cfg),
        "sampler_name": sampler or "Euler a",
        "seed": int(seed) if (isinstance(seed, int) or (isinstance(seed, str) and seed.isdigit())) else -1,
        "width": int(width),
        "height": int(height),
        "batch_size": 1,
        "n_iter": 1
    }
    r = requests.post(f"{A1111_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
    r.raise_for_status()
    out = r.json()
    images_b64 = out.get("images", [])
    results = []
    for b in images_b64:
        results.append(Image.open(io.BytesIO(base64.b64decode(b.split(",",1)[-1]))))
    return results

def andio_generate(mode, image, mask, p1, p2, p3, p4, p5, negative, steps, cfg, denoise, sampler, seed, width, height, outfit, material):
    fields = [p for p in [p1, p2, p3, p4, p5] if p and p.strip()]
    extra = []
    if outfit and outfit != "-":
        extra.append(outfit)
    if material and material != "-":
        extra.append(material)
    prompt = ", ".join(fields + extra)
    if mode == "Inpaint":
        if image is None:
            return [], "Bitte ein Bild hochladen."
        results = _inpaint_via_api(image, mask, prompt, negative, steps, cfg, denoise, sampler, seed, width, height)
    else:
        results = _txt2img(prompt, negative, steps, cfg, sampler, seed, width, height)
    return results, f"OK – {len(results)} Bild(er)"

def on_ui_tabs():
    outfits, materials = _load_presets()
    info = _system_info()

    with gr.Blocks(elem_id="andio_root", css=".andio-chip{border-radius:999px;padding:6px 10px;border:1px solid #fff3;}") as ui:
        gr.Markdown("## ANDIO One – Wardrobe Editor (A1111 Engine)")

        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("**Prompts (P1–P5)** – links fokusiert")
                p1 = gr.Textbox(label="P1", placeholder="z.B. outfit idea …", elem_id="p1")
                p2 = gr.Textbox(label="P2")
                p3 = gr.Textbox(label="P3")
                p4 = gr.Textbox(label="P4")
                p5 = gr.Textbox(label="P5")
                negative = gr.Textbox(label="Negative Prompt", placeholder="unwanted details …")

                outfit = gr.Dropdown(choices=["-"] + outfits, value="-", label="Outfit Preset")
                material = gr.Dropdown(choices=["-"] + materials, value="-", label="Material Preset")

                with gr.Accordion("Advanced", open=False):
                    steps = gr.Slider(1, 40, value=20, step=1, label="Steps")
                    cfg = gr.Slider(1.0, 15.0, value=7.0, step=0.5, label="CFG")
                    denoise = gr.Slider(0.0, 1.0, value=0.55, step=0.01, label="Denoising (Inpaint)")
                    sampler = gr.Dropdown(choices=["Euler a","Euler","DPM++ 2M Karras","DDIM"], value="Euler a", label="Sampler")
                    seed = gr.Textbox(value="-1", label="Seed")
                    with gr.Row():
                        width = gr.Number(value=768, label="Breite")
                        height = gr.Number(value=1024, label="Höhe")

                with gr.Row():
                    mode = gr.Radio(["Inpaint", "Text2Img"], value="Inpaint", label="Modus")
                    run = gr.Button("Generate", variant="primary")

                status = gr.HTML(f"""
                <div class="andio-status">
                  <b>Status:</b> {('Verbunden ✅' if info else 'Keine Verbindung ❌')} •
                  {('CUDA ' + str(info.get('cuda',{}).get('version'))) if info else ''}
                  • {('VRAM ' + str(info.get('system',{}).get('cuda',{}).get('vram_total_gb','?')) + ' GB') if info else ''}
                </div>
                """)

            with gr.Column(scale=2, min_width=600):
                with gr.Row():
                    image = gr.Image(label="Bild", type="pil", height=530)
                    mask = gr.Image(label="Maske", type="pil", tool="sketch", height=530)
                gallery = gr.Gallery(label="Ergebnis", columns=2, height=520, show_label=True)

        run.click(
            andio_generate,
            inputs=[mode, image, mask, p1, p2, p3, p4, p5, negative, steps, cfg, denoise, sampler, seed, width, height, outfit, material],
            outputs=[gallery, status]
        )

    return [(ui, "ANDIO One", "andio_one_tab")]

def on_app_started(blocks, app):
    def _ok():
        return {"ok": True, "src": "andio-one-ext"}
    app.add_api_route("/sdapi/v1/andio/ok", _ok, methods=["GET"])

script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_app_started(on_app_started)
