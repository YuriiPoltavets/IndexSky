def evaluate_rating(data):
    score = 0

    # Zacks: +1 бал, якщо 1 або 2 (Strong Buy / Buy)
    try:
        if int(data.get("Zacks", 0)) <= 2:
            score += 1
    except:
        pass

    # PE Ratio: +1 бал, якщо < 25
    try:
        if float(data.get("PE Ratio", 100)) < 25:
            score += 1
    except:
        pass

    # EPS Growth: +1 бал, якщо в полі є "%"
    if "%" in data.get("EPS Growth", ""):
        score += 1

    return f"{score}/3"
