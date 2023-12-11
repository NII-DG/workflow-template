import pytest

from nb_libs.utils.except_class.common_err import DGTaskError
from nb_libs.utils.common.raise_error import raise_dg_task_error_from_unexpected, not_exec_pre_cell_raise


def test_raise_dg_task_error_from_unexpected():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_raise_error.py::test_raise_dg_task_error_from_unexpected

    with pytest.raises(DGTaskError) as e:
        raise_dg_task_error_from_unexpected('test')

    assert str(e.value) == ''


def test_not_exec_pre_cell_raise():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_raise_error.py::test_not_exec_pre_cell_raise

    with pytest.raises(DGTaskError) as e:
        not_exec_pre_cell_raise()

    assert str(e.value) == 'The immediately preceding cell may not have been executed'
