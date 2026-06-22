from __future__ import annotations


def ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    multiplier = 2 / (period + 1)
    output = [values[0]]
    for value in values[1:]:
        output.append((value - output[-1]) * multiplier + output[-1])
    return output


def atr(high: list[float], low: list[float], close: list[float], period: int = 10) -> list[float | None]:
    true_ranges: list[float] = []
    for index, high_value in enumerate(high):
        if index == 0:
            true_ranges.append(high_value - low[index])
        else:
            true_ranges.append(max(high_value - low[index], abs(high_value - close[index - 1]), abs(low[index] - close[index - 1])))
    output: list[float | None] = []
    for index in range(len(true_ranges)):
        if index + 1 < period:
            output.append(None)
        else:
            output.append(sum(true_ranges[index + 1 - period : index + 1]) / period)
    return output


def ott_like(close: list[float], period: int = 14, percent: float = 1.4) -> tuple[list[float], list[float], list[int]]:
    basis = ema(close, period)
    long_stop = [value - (value * percent / 100.0) for value in basis]
    short_stop = [value + (value * percent / 100.0) for value in basis]
    direction = [1]
    line = [long_stop[0]]
    for index in range(1, len(close)):
        if close[index] > short_stop[index - 1]:
            direction.append(1)
        elif close[index] < long_stop[index - 1]:
            direction.append(-1)
        else:
            direction.append(direction[-1])
        line.append(long_stop[index] if direction[-1] == 1 else short_stop[index])
    return basis, line, direction


def supertrend(high: list[float], low: list[float], close: list[float], period: int = 10, multiplier: float = 3.0) -> tuple[list[float | None], list[int]]:
    atr_values = atr(high, low, close, period)
    upper: list[float | None] = []
    lower: list[float | None] = []
    for h_value, l_value, atr_value in zip(high, low, atr_values):
        if atr_value is None:
            upper.append(None)
            lower.append(None)
            continue
        midpoint = (h_value + l_value) / 2.0
        upper.append(midpoint + multiplier * atr_value)
        lower.append(midpoint - multiplier * atr_value)

    trend = [1]
    line: list[float | None] = [lower[0]]
    for index in range(1, len(close)):
        if upper[index - 1] is None or lower[index - 1] is None:
            trend.append(trend[-1])
            line.append(lower[index])
            continue
        if close[index] > upper[index - 1]:
            trend.append(1)
        elif close[index] < lower[index - 1]:
            trend.append(-1)
        else:
            trend.append(trend[-1])
            if trend[-1] == 1 and lower[index] is not None and lower[index - 1] is not None:
                lower[index] = max(lower[index], lower[index - 1])
            elif trend[-1] == -1 and upper[index] is not None and upper[index - 1] is not None:
                upper[index] = min(upper[index], upper[index - 1])
        line.append(lower[index] if trend[-1] == 1 else upper[index])
    return line, trend
