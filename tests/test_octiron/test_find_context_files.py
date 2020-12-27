import tempfile
from pathlib import Path

from octadocs.octiron import Octiron


def test_file_in_upper_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_directory = Path(temp_dir)

        # Create a file that will not be accessible to the finder
        # because it is above the root_directory in structure
        (temp_directory / 'context.yaml').write_text(data='')

        docs_directory = Path(temp_directory) / 'docs'
        docs_directory.mkdir()

        octiron = Octiron(root_directory=docs_directory)
        assert not list(octiron._find_context_files(docs_directory / 'posts'))


def test_file_in_docs_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_directory = Path(temp_dir)

        docs_directory = Path(temp_directory) / 'docs'
        docs_directory.mkdir()
        (docs_directory / 'context.yaml').write_text(data='')

        octiron = Octiron(root_directory=docs_directory)
        assert list(octiron._find_context_files(docs_directory / 'posts')) == [
            temp_directory / 'docs/context.yaml',
        ]


def test_file_in_sub_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_directory = Path(temp_dir)

        docs_directory = Path(temp_directory) / 'docs'
        docs_directory.mkdir()
        (docs_directory / 'context.yaml').write_text(data='')

        posts_directory = Path(docs_directory) / 'posts'
        posts_directory.mkdir()
        (posts_directory / 'context.json').write_text(data='')

        octiron = Octiron(root_directory=docs_directory)
        assert list(octiron._find_context_files(
            docs_directory / 'posts/daily',
        )) == [
            temp_directory / 'docs/posts/context.json',
            temp_directory / 'docs/context.yaml',
        ]


def test_file_in_current_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_directory = Path(temp_dir)

        docs_directory = Path(temp_directory) / 'docs'
        docs_directory.mkdir()
        (docs_directory / 'context.yaml').write_text(data='')

        posts_directory = Path(docs_directory) / 'posts'
        posts_directory.mkdir()
        (posts_directory / 'context.json').write_text(data='')

        octiron = Octiron(root_directory=docs_directory)
        assert list(octiron._find_context_files(
            docs_directory / 'posts/',
        )) == [
            temp_directory / 'docs/posts/context.json',
            temp_directory / 'docs/context.yaml',
        ]
