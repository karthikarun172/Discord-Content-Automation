import os
import requests
from utils.logger import logger
from config.settings import (
    PEXELS_API_KEY,
    GIPHY_API_KEY
)

def search_images(
    query,
    limit=5,
):
    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers={
            "Authorization": PEXELS_API_KEY
        },
        params={
            "query": query,
            "per_page": limit,
        }
    )

    response.raise_for_status()

    data = response.json()

    return [
        photo["src"]["large"]
        for photo in data["photos"]
    ]

def download_file(
    url,
    output_path,
):
    response = requests.get(
        url,
        stream=True,
        timeout=30,
    )

    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(
            chunk_size=8192
        ):
            f.write(chunk)

    return output_path

def download_images(
    query,
    output_dir,
    limit=5,
):
    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    image_urls = search_images(
        query,
        limit,
    )

    downloaded_files = []

    for index, image_url in enumerate(
        image_urls,
        start=1,
    ):
        file_path = os.path.join(
            output_dir,
            f"image_{index}.jpg",
        )

        download_file(
            image_url,
            file_path,
        )

        downloaded_files.append(
            file_path
        )

    return downloaded_files

def build_scene_assets(
    project_name,
    scene,
):
    """
    Downloads all assets required for a scene.

    Returns:
        {
            "scene": 2,
            "images": [...],
            "gifs": [...]
        }
    """

    scene_number = str(
        scene["scene"]
    ).zfill(3)

    scene_dir = os.path.join(
        "generated",
        project_name,
        f"scene_{scene_number}",
    )

    image_dir = os.path.join(
        scene_dir,
        "images",
    )

    gif_dir = os.path.join(
        scene_dir,
        "gifs",
    )

    os.makedirs(
        image_dir,
        exist_ok=True,
    )

    os.makedirs(
        gif_dir,
        exist_ok=True,
    )

    logger.info(
        f"Building assets for scene "
        f"{scene['scene']}"
    )

    images = download_images(
        query=scene["image_query"],
        output_dir=image_dir,
        limit=5,
    )

    gifs = download_gifs(
        query=scene["gif_query"],
        output_dir=gif_dir,
        limit=5,
    )

    return {
        "scene": scene["scene"],
        "images": images,
        "gifs": gifs,
    }

def build_project_assets(
    project_name,
    storyboard,
):
    """
    Build assets for all b-roll scenes.

    Returns summary of generated assets.
    """

    results = []

    scenes = storyboard.get(
        "scenes",
        []
    )

    logger.info(
        f"Building assets for "
        f"{len(scenes)} scenes"
    )

    for scene in scenes:

        if scene["type"] == "avatar":
            logger.info(
                f"Skipping avatar scene "
                f"{scene['scene']}"
            )
            continue

        scene_result = build_scene_assets(
            project_name,
            scene,
        )

        results.append(
            scene_result
        )

    return {
        "project": project_name,
        "total_scenes": len(scenes),
        "processed_scenes": len(results),
        "results": results,
    }

def search_gifs(
    query,
    limit=5,
):
    response = requests.get(
        "https://api.giphy.com/v1/gifs/search",
        params={
            "api_key": GIPHY_API_KEY,
            "q": query,
            "limit": limit,
            "rating": "g",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return [
        gif["images"]["original"]["url"]
        for gif in data["data"]
    ]

def download_gifs(
    query,
    output_dir,
    limit=5,
):
    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    gif_urls = search_gifs(
        query,
        limit,
    )

    downloaded_files = []

    for index, gif_url in enumerate(
        gif_urls,
        start=1,
    ):
        file_path = os.path.join(
            output_dir,
            f"gif_{index}.gif",
        )

        download_file(
            gif_url,
            file_path,
        )

        downloaded_files.append(
            file_path
        )

    return downloaded_files