import os
from ..utils.params import ex_pkg_info as epi
from ..utils.path import path, display as pd
from ..utils.message import message
from IPython.display import HTML, display

def trans_top():
    """Display a link button to the Study or Execution Flow Top Page.

    1. In the research execution environment, it is displayed as a link button on the research flow top page.
    2. In the experiment execution environment, it is displayed as a link button on the top page of the experiment flow.
    """

    # Identify whether the function execution environment is research or experimental
    # If the ex_pkg_info.json file is not present, the research execution environment, and if present, the experimental execution environment.

    html_text = ''
    if epi.exist_file():
        # For experiment execution environment
        top_path = os.path.join('./../', path.RESEARCH_DIR ,path.RESEARCH_TOP)
        html_text = pd.button_html(top_path, message.get("menu", "trans_reserch_top"))
    else:
        # For research execution environment
        top_path = os.path.join('./../', path.EXPERIMENT_DIR ,path.EXPERIMENT_TOP)
        html_text = pd.button_html(top_path, message.get("menu", "trans_experiment_top"))

    display(HTML(html_text))
