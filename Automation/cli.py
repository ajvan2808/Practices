import argparse
import pathlib
import asyncio
import sys


def read_user_cli():
    parser = argparse.ArgumentParser(prog='Automation', description='Scraping data from websites',
                                     epilog='Application will start soon!')
    parser.add_argument(
        '-u',
        '--urls',
        metavar='URLs',
        nargs='+',
        type=str,
        default="",
        help='Enter one or more website urls'
    )
    parser.add_argument(
        '-f',
        '--input-file',
        metavar='FILE',
        type=str,
        default="",
        help='Read urls from file.'
    )
    # parser.add_argument(
    #     '-a',
    #     '--asynchronous',
    #     action='store_true',
    #     help='Scraping asynchronously'
    # )
    return parser.parse_args()


def read_urls_from_files(file):
    file_path = pathlib.Path(file)
    if file_path is file:
        with file_path.open() as urls_file:
            urls = [url.strip() for url in urls_file]
            if urls:
                return urls
            print(f'Error: Empty input files, {file}', file=sys.stderr)
    else:
        print(f'Error: Input file not found, {file}', file=sys.stderr)
    return []


def _get_website_urls(user_args):
    urls = user_args.urls
    if user_args.input_file:
        urls += read_urls_from_files(user_urls.input_file)
    return urls
