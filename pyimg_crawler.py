from bs4 import BeautifulSoup
import requests
import shutil
import os


def _parse_html(url_link):
    '''
    Get and parse a given html page using BeautifulSoup and return a
    soup instance.

    :param
    url_link (string): Url link of the target html page

    :return
    soup (BeautifulSoup instance): Parsed html page instance
    '''

    # Get and parse page
    page = requests.get(url_link)
    soup = BeautifulSoup(page.text, 'html.parser')

    return soup


def get_imgs(url_link, folder):
    '''
    Extract target image urls from a given Html page and download them.

    :param
    url_link (string): Url link of the target html page
    folder (string): Path to folder to save image to.

    :return
    img_urls (list): List containing urls of images found in the
                  target html page. In this context, we target images
                  found in <div class="single-content">
    '''

    soup = _parse_html(url_link)

    sc_div = soup.find('div', class_='single-content')
    p_imgs = sc_div.find_all('img', src=True)

    # Check if there are images found
    if len(p_imgs) == 0:
        return

    # Download all found images
    for u in p_imgs:
        if u.has_attr('data-lazy-src'):
            download_img(u['data-lazy-src'], folder)
    # img_urls = [u['data-lazy-src'] for u in p_imgs if u.has_attr('data-lazy-src')]

    # return img_urls


def get_page_urls(url_link):
    '''
    Extract associated page urls from given starting page.

    :param
    url_link (string): Url link of the target html page

    :return
    page_urls (list): List containing all associated html pages.
    '''

    soup = _parse_html(url_link)

    # Get page urls div
    pl_div = soup.find('div', class_='page-links')
    a_hrefs = pl_div.find_all('a', href=True)
    pg_urls = [u['href'] for u in a_hrefs]

    # Drop first and last pages due to next and prev page buttons.
    pg_urls = pg_urls[1:-1]
    # Add current page to list of page urls
    pg_urls.append(url_link)

    return pg_urls


def download_img(img_url, folder):
    '''
    Download image from a given image url.
    :param
    img_url (string): Url of an image.
    folder (string): Path to folder to save image to.
    '''

    # Get image content and construct output file name
    content = requests.get(img_url, stream=True)
    img_name = img_url.split('/')[-1]
    img_file = os.path.join(folder, img_name)

    # Write to image file
    f = open(img_file, 'wb')
    content.raw.decode_content = True
    shutil.copyfileobj(content.raw, f)
    del content


if __name__ == '__main__':
    # Parse input file with list of sites to crawl
    with open('sites.txt') as f:
        url_list = [line.rstrip() for line in f]

    for url in url_list:
        print('Processing {}'.format(url))
        pages = get_page_urls(url)

        # Generate the relevant output folder(s)
        folder_name = url.split('/')[-1].split('.')[0]
        img_folder = os.path.join('output', folder_name)
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)

        # Parse through each page and download found images
        for p in pages:
            get_imgs(p, img_folder)

    print('Download complete')