from playwright.sync_api import sync_playwright

from tests.integration_tests.common.utils import get_browser_context

from .test_base_FLOW import base_flow
from .test_base_required_every_time import base_required_every_time

ENV_KEY = 'res_env1'


def test_base_flow(prepare_res_env):
    # pytest -v -s tests/integration_tests/notebooks/research/test_res_env1.py::test_base_flow

    prepare_res_env(ENV_KEY)
    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            base_flow(ENV_KEY, context)
        finally:
            browser = context.browser
            context.close()
            browser.close()


def test_base_required_every_time(prepare_res_env):
    # pytest -v -s tests/integration_tests/notebooks/research/test_res_env1.py::test_base_required_every_time

    prepare_res_env(ENV_KEY)
    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            base_required_every_time(ENV_KEY, context)
        finally:
            browser = context.browser
            context.close()
            browser.close()
