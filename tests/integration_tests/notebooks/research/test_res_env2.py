from playwright.sync_api import sync_playwright

from tests.integration_tests.common.utils import get_browser_context

from .test_base_finish_research import base_finish_research

ENV_KEY = 'res_env2'


def test_base_finish_research(prepare_res_env_setup):
    # pytest -v -s tests/integration_tests/notebooks/research/test_res_env2.py::test_base_finish_research

    prepare_res_env_setup(ENV_KEY)
    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            base_finish_research(ENV_KEY, context)
        finally:
            browser = context.browser
            context.close()
            browser.close()
