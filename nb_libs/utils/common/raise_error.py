from utils.except_class import DGTaskError
from utils.message import display, message

def raise_dg_task_error_from_unexpected(reason:str):
    err_format = message.get('DEFAULT', 'unexpected_errors_format')
    display.display_err(err_format.format(reason))
    raise DGTaskError()

def not_exec_pre_cell_raise():
    msg = message.get('nb_exec', 'not_exec_pre_cell')
    display.display_err(msg)
    raise DGTaskError('The immediately preceding cell may not have been executed')