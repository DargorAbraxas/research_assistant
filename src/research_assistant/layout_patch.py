from pymupdf4llm.helpers import utils

def compute_reading_order(boxes, joined_boxes, vectors, vertical_gap=12):
    """
    Patched version of pymupdf4llm.helpers.utils.compute_reading_order.

    This version collapses all horizontal stripes before column clustering
    and reorder them in a strictly two-column way, ideal for scientific
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
    stripe.sort(key=lambda b: (b[1], b[0]))
    stripes = [stripe]

    ordered = []
    for stripe in stripes:
        columns = utils.cluster_columns_in_stripe(stripe)
        for col in columns:
            ordered.extend(col)
    return ordered

# Replace the library function with this version
utils.compute_reading_order = compute_reading_order
