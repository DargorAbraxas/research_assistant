from pymupdf4llm.helpers import utils

def compute_reading_order(boxes, joined_boxes, vectors, vertical_gap=36):
    """
    Patched version of pymupdf4llm.helpers.utils.compute_reading_order.

    This reorders horizontal stripes before column clustering
    and reorder them to follow a two-column way, ideal for scientific
    papers.
    """
    stripes = utils.cluster_stripes(
        boxes,
        joined_boxes,
        vectors,
        vertical_gap=vertical_gap,
    )

    # Flatten horizontal boxes
    stripe = [box for horizontal_stripe in stripes for box in horizontal_stripe]
    stripe.sort(key=lambda b: (int(b[0]), int(b[1])))
    stripes = [stripe]

    ordered = []
    for stripe in stripes:
        columns = utils.cluster_columns_in_stripe(stripe)
        for col in columns:
            ordered.extend(col)

    if len(stripes) > 1:
        ordered.sort(key=lambda b: (round(b[0]), round(b[1])))
    return ordered

# Replace the library function with this version
utils.compute_reading_order = compute_reading_order
