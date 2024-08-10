import ffmpeg
from typing import Dict
from requests import get
from lxml import etree


def remove_geoblock(m3u8: str) -> str:
    if "geoblock" in m3u8:
        return m3u8[:-13]
    return m3u8


def get_iframe_src(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    }

    response = get(url, headers=headers)

    if not response.ok:
        raise Exception("Something wrong with the url")

    parser = etree.HTMLParser()

    tree = etree.fromstring(response.content, parser)

    search_element = tree.xpath('//iframe[contains(@src, "ashdi")]')

    assert isinstance(search_element, list)

    try:
        iframe = search_element[0]
    except:
        raise Exception("iframe not found")

    assert isinstance(iframe, etree._Element)

    source = str(iframe.get("src"))

    return source


def get_m3u8(url: str) -> str:
    src: str = remove_geoblock(get_iframe_src(url))

    js_response: str = get(src).text

    start: int = js_response.find('file:"') + 6
    end: int = js_response.find("m3u8") + 4

    return js_response[start:end]


# def get_segments(raw_list_of_segments: str) -> list[str]:
#     lst = get(raw_list_of_segments).text
#     start = lst.find("http")
#     los = lst[start:].splitlines()

#     return los[::2]


def download(raw_list_of_segments: str, file_name: str) -> None:
    stream = ffmpeg.input(raw_list_of_segments)

    stream = stream.output(file_name, codec="copy", format="mp4")

    ffmpeg.run(stream)

    print("Приємного перегляду!")


def get_quality(m3u8_qualities: str) -> Dict[str, str]:
    response = get(m3u8_qualities).text
    lines: Dict[str, str] = {
        line.split("hls/", 1)[1].split("/")[0]: line
        for line in response.splitlines()
        if line.startswith("http")
    }

    return lines


def test() -> None:
    l = get_iframe_src(
        "https://uakino.me/filmy/genre-action/22552-kryminalne-misto-2.html"
    )
    print(get(l).text)


def main() -> None:
    url: str = input("Посилання: ").lstrip()
    if not url or not url.startswith("https"):
        main()

    m3u8: str = get_m3u8(url)

    qls: Dict[str, str] = get_quality(m3u8)
    for q in qls.keys():
        print(f"[+] {q}")
    q: str = input("Виберіть якість: ")

    url_for_segments = qls.get(q)
    if not url_for_segments:
        main()

    file_name: str = input("Введіть назву файлу: ")
    if not file_name:
        file_name = "movie.mp4"

    download(str(url_for_segments), file_name)


if __name__ == "__main__":
    main()
    # test()
