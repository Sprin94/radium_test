"""
Module for uploading files.

This module downloads multiple text files from a given URL, writes their
content to local files, computes the SHA-256 hash of each downloaded file using
the get_file_hash function, and prints the file path and its hash.
"""
import asyncio
import hashlib
import os
import platform
from pathlib import Path

import aiofiles
import aiohttp

URL_FILE_LIST = 'https://gitea.radium.group/radium/project-configuration/tree-list/branch/master'

URL_FILES = 'https://gitea.radium.group/radium/project-configuration/raw/branch/master/'

CHUNK_SIZE = 4096

CURRENT_PATH = Path('.')

TEMP_PATH = CURRENT_PATH / 'temp'


def create_temp_path(temp_path: str = TEMP_PATH) -> None:
    """
    Create the temporary directory if it does not exist.

    Args:
        temp_path (str): The path to the temporary directory.
            Defaults to `TEMP_PATH`.

    """
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)


def check_and_create_path(filename: str) -> None:
    """
    Check if the directory.

    Check if the directory path for the given filename exists, and creates
    it if it does not.

    Args:
        filename (str): The filename whose directory path needs to be checked
                         and created.
    """
    right_slash = filename.rfind('/')
    if right_slash != -1:
        path = TEMP_PATH / filename[:right_slash + 1]
        if not os.path.exists(path):
            os.makedirs(path)


async def write_file(filename: str, text: str) -> None:
    """
    Asynchronously writes the given data to a file with the given filename.

    Args:
        filename (str): The name of the file to be written.
        text (str): The data to be written to the file.
    """
    check_and_create_path(filename)
    async with aiofiles.open(TEMP_PATH / filename, 'w') as new_file:
        await new_file.write(text)


async def upload(
    session: aiohttp.ClientSession,
    filename: str,
    semaphore: asyncio.Semaphore,
) -> None:
    """
    Download a file from a URL and writes its content to a local file.

    Args:
        session (aiohttp.ClientSession): An instance of `aiohttp.ClientSession`
        filename (str): The name of the file to be downloaded and written.
        semaphore (asyncio.Semaphore): A semaphore used to limit concurrent.
    """
    async with semaphore:
        response = await session.get(URL_FILES + filename)
        text = await response.text()
        await write_file(filename, text)


def file_hash(path: str) -> str:
    """
    Compute the SHA-256 hash of the file at the given path and returns it.

    Args:
        path (str): The path to the file whose hash needs to be computed.

    Returns:
        str: The SHA-256 hash of the file.
    """
    with open(path, 'rb') as current_file:
        hash_sha256 = hashlib.sha256()
        while True:
            chunk = current_file.read(CHUNK_SIZE)
            if not chunk:
                break
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


async def main():
    """Download multiple files from a URL and writes their content to local.

    Computes the SHA-256 hash of each downloaded file using the
    `get_file_hash` function and prints the file path and its hash.
    """
    semaphore = asyncio.Semaphore(3)
    async with aiohttp.ClientSession() as session:
        response = await session.get(URL_FILE_LIST)
        file_list = await response.json()
        await asyncio.gather(
            *[upload(session, txt_file, semaphore) for txt_file in file_list],
        )
        for path in TEMP_PATH.rglob('*'):
            if path.is_file():
                file_hash(path)


if __name__ == '__main__':
    create_temp_path()
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
