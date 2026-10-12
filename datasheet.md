# Source Dataset Notes

The supplied dataset documentation describes the input as a snapshot of crowdsourced retail price observations. Rows represent a product price observation associated with a recording date and may include product, brand, category, store, city, country, and currency fields.

## Caveats
- Missing product/location metadata exists in the supplied CSV.
- Price values are denominated in their recorded currency; this project does not convert currencies.
- This is a static snapshot, not a live API integration.
- Do not interpret simple price averages across different products or package sizes as a cost-of-living or inflation index.
