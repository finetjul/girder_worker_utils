import os

import girder_client
import mock
import pytest

from girder_worker_utils.transforms import girder_io

DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fake_dir')
FILE_PATH = os.path.join(DIR_PATH, 'file1.txt')


@pytest.fixture
def mock_gc():
    return mock.MagicMock(spec=girder_client.GirderClient)


@pytest.fixture
def mock_rm():
    with mock.patch('os.remove') as rm:
        yield rm


@pytest.fixture
def mock_rmtree():
    with mock.patch('shutil.rmtree') as rmtree:
        yield rmtree


def test_GirderUploadToItem_with_kwargs(mock_gc):
    uti = girder_io.GirderUploadToItem('the_id', gc=mock_gc, upload_kwargs={'reference': 'foo'})
    assert uti.transform(FILE_PATH) == 'the_id'
    mock_gc.uploadFileToItem.assert_called_once_with('the_id', FILE_PATH, reference='foo')


def test_GirderUploadToItem_upload_directory(mock_gc):
    uti = girder_io.GirderUploadToItem('the_id', gc=mock_gc, upload_kwargs={'reference': 'foo'})
    assert uti.transform(DIR_PATH) == 'the_id'

    files = {'file1.txt', 'file2.txt'}
    calls = [mock.call('the_id', os.path.join(DIR_PATH, f), reference='foo') for f in files]
    mock_gc.uploadFileToItem.assert_has_calls(calls, any_order=True)


@pytest.mark.parametrize('should_delete', (True, False))
def test_GirderUploadToItem_cleanup_file(mock_gc, mock_rm, mock_rmtree, should_delete):
    uti = girder_io.GirderUploadToItem('the_id', delete_file=should_delete, gc=mock_gc)
    uti.transform(FILE_PATH)
    uti.cleanup()
    if should_delete:
        mock_rm.assert_called_once_with(FILE_PATH)
    else:
        mock_rm.assert_not_called()
    mock_rmtree.assert_not_called()


@pytest.mark.parametrize('should_delete', (True, False))
def test_GirderUploadToItem_cleanup_dir(mock_gc, mock_rm, mock_rmtree, should_delete):
    uti = girder_io.GirderUploadToItem('the_id', delete_file=should_delete, gc=mock_gc)
    uti.transform(DIR_PATH)
    uti.cleanup()
    if should_delete:
        mock_rmtree.assert_called_once_with(DIR_PATH)
    else:
        mock_rmtree.assert_not_called()
    mock_rm.assert_not_called()