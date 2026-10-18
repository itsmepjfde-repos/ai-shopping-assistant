"""Select the active mock dataset for all ecommerce API routes."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATASET_NAME = os.getenv("ECOMM_MOCK_DATA", "default").strip().lower()

if DATASET_NAME == "default":
    from app import mock_data as selected_data
elif DATASET_NAME == "edge":
    from app import mock_data_edge as selected_data
else:
    raise ValueError(
        f"Unsupported ECOMM_MOCK_DATA value {DATASET_NAME!r}; choose 'default' or 'edge'."
    )

AVAILABILITY = selected_data.AVAILABILITY
PRICES = selected_data.PRICES
PRODUCTS = selected_data.PRODUCTS
REVIEWS = selected_data.REVIEWS
get_valid_product = selected_data.get_valid_product
