def fig(fig, include_plotlyjs="cdn", full_html: bool = False) -> str:
    """Returns html for a plotly figure. By default the plotly javascript is not
    included but imported from the plotly cdn, and the full html wrapper is not included.

    Args:
        include_plotlyjs (bool, str): how to import the necessary javascript for the plotly
            fig. Defaults to 'cdn', which means the figure just links to javascript file
            hosted by plotly. If set to True then a 3MB javascript snippet is included.
            For other options check https://plotly.com/python-api-reference/generated/plotly.io.to_html.html
        full_html (bool): include <html>, <head> and <body> tags. Defaults to False.
    """
    return fig.to_html(include_plotlyjs=include_plotlyjs, full_html=full_html)