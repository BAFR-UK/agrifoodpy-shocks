# Examples

This folder contains pipeline examples for both hazard application and
resilience-impact registration.

## Updated function paths

- Hazard scenario functions now use `agrifoodpy_shocks.hazards.*`
	(for example, `hazards.environmental.apply_production_hazard`).
- Resilience registration and impact computation now use
	`agrifoodpy_shocks.engine.impact.*`:
	- `register_resilience`
	- `register_hazard`
	- `compute_net_impact`

## Included examples

- `ffc_pipeline_with_shocks.yaml`: full food pipeline with production/import
	hazards.
- `test_shocks_registration.yaml`: channel registration with yearly severity.
- `test_shocks_registration_without_years.yaml`: channel registration without
	yearly dimensions.
