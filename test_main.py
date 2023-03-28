import os
import shutil
import hashlib
import pytest
import asyncio
from aiohttp import ClientSession
from pathlib import Path
import aiofiles

import main

@pytest.fixture(autouse=True)
def set_temp_path(tmp_path):
    main.TEMP_PATH = tmp_path
    yield

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def file_path(tmp_path):
    file = tmp_path / 'test_file.txt'
    file.write_text('This is a test file.')
    return file


@pytest.fixture
def file_list():
    return ['file1.txt', 'file2.txt', 'file3.txt']

@pytest.fixture
def file_content():
    return "This is a test file."

@pytest.fixture
def file_context():
    return [
    'This is a test file.',
    'This is another test file.',
    'This is a third test file.'
]

@pytest.mark.asyncio
async def test_create_temp_path():
    test_path = Path('.')/ 'test'
    main.create_temp_path(test_path)
    assert os.path.exists(test_path)
    os.rmdir(test_path)

def test_check_and_create_path(tmp_path):
    filename = 'dir1/dir2/file.txt'
    main.check_and_create_path(filename)
    path = tmp_path / 'dir1' / 'dir2'
    assert os.path.exists(path)


@pytest.mark.asyncio
async def test_write_file(tmp_path, file_content):
    filename = 'test_file.txt'
    await main.write_file(filename, file_content)
    assert (tmp_path / filename).read_text() == file_content


def test_file_hash(file_path):
    expected_hash = hashlib.sha256('This is a test file.'.encode('utf-8')).hexdigest()
    assert main.file_hash(str(file_path)) == expected_hash

@pytest.mark.asyncio
async def test_upload(tmp_path):
    filename = 'LICENSE'
    async with ClientSession() as session:
        await main.upload(session, filename, asyncio.Semaphore(1))
        response = await session.get(main.URL_FILES + filename)
        text = await response.text()
    assert os.path.exists(tmp_path / filename)
    async with aiofiles.open(main.TEMP_PATH / filename, 'r') as file:
        file_text = await file.read()
        assert file_text == text


@pytest.mark.asyncio
async def  test_main(tmp_path):
    await main.main()
    upload_file_list = [f for f in tmp_path.rglob('*') if f.is_file()]
    async with ClientSession() as session:
        response = await session.get(main.URL_FILE_LIST)
        file_list = await response.json()
    assert len(upload_file_list) == len(file_list)
