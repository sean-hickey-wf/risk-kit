from enum import Enum

from risk_kit.expert_scorecard.models import ExpertScorecard

try:
    import plotly.graph_objects as go
    from plotly.graph_objects import Figure
except ImportError:
    raise ImportError(  # noqa: B904
        "The visualisation module requires aditional optionaldependencies. Install with: pip install risk-kit[viz]"
    )


class ScorecardColours(Enum):
    HEADER = "lightblue"
    LINE = "#cccccc"
    LOW_SCORE = "rgba(255, 99, 132, 0.3)"
    MEDIUM_SCORE = "rgba(255, 159, 64, 0.3)"
    HIGH_SCORE = "rgba(75, 192, 192, 0.3)"


class ScorecardVisualizer:
    """
    Table-based visualiser for Expert Scorecards.
    """

    def __init__(self, scorecard: ExpertScorecard):
        self.scorecard = scorecard
        self.min_score, self.max_score = self.scorecard.get_score_range()

    def _score_to_color(self, score: float) -> str:
        """Convert a score to a color with transparency."""
        if self.max_score == self.min_score:
            normalized = 0.5
        else:
            normalized = (score - self.min_score) / (self.max_score - self.min_score)

        if normalized <= 0.33:
            return ScorecardColours.LOW_SCORE.value
        elif normalized <= 0.66:
            return ScorecardColours.MEDIUM_SCORE.value
        else:
            return ScorecardColours.HIGH_SCORE.value

    def create_scorecard_table(self) -> Figure:
        headers, all_rows = self.scorecard.get_table_data()

        display_headers = [h.replace("_", " ").title() for h in headers]

        values = [
            ["" if getattr(row, header) is None else str(getattr(row, header)) for row in all_rows]
            for header in headers
        ]
        colors = [
            [self._score_to_color(row.score) for row in all_rows] if header == "score" else ["white"] * len(all_rows)
            for header in headers
        ]

        fig = go.Figure(
            data=[
                go.Table(
                    header={
                        "values": display_headers,
                        "fill_color": ScorecardColours.HEADER.value,
                        "align": "left",
                        "font": {"size": 12, "color": "black"},
                        "height": 40,
                        "line": {"color": "white", "width": 2},
                    },
                    cells={
                        "values": values,
                        "fill_color": colors,
                        "align": "left",
                        "font": {"size": 11},
                        "height": 30,
                        "line": {"color": ScorecardColours.LINE.value, "width": 2},
                    },
                )
            ]
        )

        num_rows = len(all_rows)
        fig.update_layout(
            title={
                "text": "<b>Visualisation of Expert Scorecard</b>",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16},
            },
            height=max(400, num_rows * 35 + 150),
            margin={"l": 20, "r": 20, "t": 80, "b": 20},
        )

        return fig

    def to_html(self) -> str:

        fig = self.create_scorecard_table()
        return fig.to_html(include_plotlyjs="cdn")

    def save_html(self, filename: str) -> None:
        fig = self.create_scorecard_table()
        fig.write_html(filename)
