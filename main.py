import requests
import re
import yaml
import os
import html
from PIL import Image
from io import BytesIO

save_slices = False


def load_urls():
    with open('urls.yaml', 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print("Error while parsing YAML:", exc)
            return []


def filename_filter(filename):
    rule = re.compile(r'[\\/:*?"<>|\r\n]+')
    invalids = rule.findall(filename)
    if invalids:
        for nv in invalids:
            filename = filename.replace(nv, "_")
    return filename


def from_micrio(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/88.0.4324.192 Safari/537.36"
    }

    resp = requests.get(url, headers=headers)
    page_content = resp.text
    resp.close()

    title = html.unescape(re.compile('<h1 class="art-object-page-content-title heading-2">(.*?)</h1>', re.S).findall(
        page_content)[0].strip())
    artwork_id = \
        re.compile('<meta property="og:image" content="https://iiif.micr.io/(.*?)/', re.S).findall(
            page_content)[0]

    info_url = f'https://micrio-cdn.vangoghmuseum.nl/{artwork_id}/info.json'
    resp = requests.get(info_url, headers=headers)
    info = resp.json()
    resp.close()

    width = info['width']
    height = info['height']

    col = int(width / 1024) + 1
    row = int(height / 1024) + 1

    if save_slices:
        os.makedirs(f'./slices/{filename_filter(title)}/{artwork_id}', exist_ok=True)
    full_size_image = Image.new('RGB', (width, height))

    for c in range(col):
        for r in range(row):
            image_url = f'https://micrio-cdn.vangoghmuseum.nl/{artwork_id}/0/{c}-{r}.jpg'
            resp = requests.get(image_url)
            img = Image.open(BytesIO(resp.content))
            resp.close()
            if save_slices:
                img.save(f'./slices/{filename_filter(title)}/{artwork_id}/{c}-{r}.jpg')
            full_size_image.paste(img, (1024 * c, 1024 * r))

    full_size_image.save(f"./output/#{artwork_id}#{filename_filter(title)}.jpg")


def from_googleusercontent(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/88.0.4324.192 Safari/537.36"
    }

    resp = requests.get(url, headers=headers)
    page_content = resp.text
    resp.close()

    title = html.unescape(re.compile('<a name="info" class="text-underline-none" tabindex="0">(.*?)</a>', re.S).findall(
        page_content)[0].strip())
    artwork_id = \
        re.compile('<div data-role="micrio".*data-id="(.*?)".*data-base-path', re.S).findall(
            page_content)[0]

    info_url = f'https://vangoghmuseum-assetserver.appspot.com/tiles?id={artwork_id}'
    resp = requests.get(info_url, headers=headers)
    info = resp.json()['levels'][0]
    resp.close()

    width = info['width']
    height = info['height']

    if save_slices:
        os.makedirs(f'./slices/{filename_filter(title)}/{artwork_id}', exist_ok=True)
    full_size_image = Image.new('RGB', (width, height))

    tiles = info['tiles']

    for tile in tiles:
        c = tile['x']
        r = tile['y']
        image_url = tile['url']
        proxies = {'https': 'https://localhost:2434'}
        resp = requests.get(image_url, proxies=proxies)
        img = Image.open(BytesIO(resp.content))
        resp.close()
        if save_slices:
            img.save(f'./slices/{filename_filter(title)}/{artwork_id}/{c}-{r}.jpg')
        full_size_image.paste(img, (512 * c, 512 * r))

    full_size_image.save(f"./output/#{artwork_id}#{filename_filter(title)}.jpg")


if __name__ == '__main__':
    urls = list(dict.fromkeys(load_urls()))
    os.makedirs(f'./output', exist_ok=True)

    pattern_collection = r'https://www.vangoghmuseum\.nl/.*/collection/.*'
    pattern_prints_collection = r'https://www.vangoghmuseum\.nl/.*/prints/collection/.*'

    for url in urls:
        if re.match(pattern_prints_collection, url):
            from_googleusercontent(url)
            print(f'{url}: Downloaded.')
        elif re.match(pattern_collection, url):
            from_micrio(url)
            print(f'{url}: Downloaded.')
        else:
            print(f'Invalid URL: {url}')
