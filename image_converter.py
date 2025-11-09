import os
from pathlib import Path
from PIL import Image
from concurrent.futures import ProcessPoolExecutor

kindle_res = (1860, 2480)

def process_image(task):
    page, chapter, low_quality = task

    if low_quality:
        out = chapter / f"{page.stem}.jpg"
    else:
        out = chapter / f"{page.stem}.png"

    if out.exists():
        return

    with Image.open(page) as img:
        w, h = img.size
        aspect = w / h

        # Rotate double pages
        if aspect > 1.4:
            img = img.transpose(Image.ROTATE_90)
        
        img = img.resize(kindle_res, Image.LANCZOS)
        
        if low_quality:
            img = img.convert("L")
            img.save(out, format="JPEG", quality=100, optimize=True)
        else:
            img.save(out, format="PNG")

def prepare_images_parallel(manga, low_quality):
    base = Path(manga)
    if low_quality:
        new_base = Path(f"{manga}_lo_processed")
    else:
        new_base = Path(f"{manga}_hi_processed")
    new_base.mkdir(exist_ok=True)

    chapters = base.iterdir()
    tasks = []

    for chapter in chapters:
        if chapter.is_dir():
            new_chapter = new_base / chapter.name
            new_chapter.mkdir(exist_ok=True)

            pages = chapter.iterdir()
            for page in pages:
                if page.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                    tasks.append((page, new_chapter, low_quality))

    with ProcessPoolExecutor() as exe:
        exe.map(process_image, tasks)

if __name__ == "__main__":
    manga = input("Enter manga: ")
    low_quality = input("Low quality (y/n):") == 'y'
    prepare_images_parallel(manga, low_quality)
    print("✅ Finished")