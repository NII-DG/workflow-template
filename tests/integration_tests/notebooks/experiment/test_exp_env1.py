from playwright.sync_api import sync_playwright

from tests.integration_tests.common.utils import get_browser_context

from .test_experiment import experiment

ENV_KEY = 'exp_env1'


def test_experiment(prepare_exp_env):
    # pytest -v -s tests/integration_tests/notebooks/experiment/test_exp_env1.py::test_experiment

    prepare_exp_env(ENV_KEY)
    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            experiment(ENV_KEY, context)
        finally:
            browser = context.browser
            context.close()
            browser.close()
