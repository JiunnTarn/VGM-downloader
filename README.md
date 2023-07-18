# VGM-downloader

VGM-downloader is a tiled image downloader designed to fetch full-size images of artworks from the [Van Gogh Museum website](https://www.vangoghmuseum.nl/en)

## Usage

1. Add the URLs of the artworks you want to download to `urls.yaml` 

   > Please ensure that it follows the YAML file format

2. Run `python main.py`
3. Wait for the download to complete. Full-sized images can be found in the `/output` directory

## Notes

1. Since duplicate artwork titles are common, the downloaded files will have prefixes to avoid repetition. You can use regex renaming to remove them
2. If you want to keep the tiled images, set `save_slices` to `True` in `main.py`
3. Illegal characters in the artwork titles will be replaced with `_`
