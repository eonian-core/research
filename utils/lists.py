def split_interval(start, end, N):
    if N <= 2:
        return [start, end]

    step = (end - start) // (N - 1)
    points = [start + i * step for i in range(1, N - 1)]
    points.append(end)

    return [start] + points
