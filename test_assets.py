from services.assets_service import (
    download_images,
    build_scene_assets,
    build_project_assets,
    search_gifs
)
import json

files = download_images(
    query="1970s Kodak laboratory",
    output_dir="generated/test",
)

scene = {
    "scene": 1,
    "type": "broll",
    "image_query": "1970s Kodak laboratory",
    "gif_query": "camera",
}

result = build_scene_assets(
    "kodak_story",
    scene,
)
with open(
    "kodak_storyboard.json",
    "r",
    encoding="utf-8"
) as f:
    storyboard = json.load(f)

result = build_project_assets(
    project_name="kodak_story",
    storyboard=storyboard,
)


print(result)
# gifs = search_gifs(
#     "camera"
# )

# for gif in gifs:
#     print(gif)

