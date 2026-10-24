# Test Output

All output below was captured from a real run in the build environment; nothing was edited or typed by hand.

## Environment

```
Python 3.13.17
Django 5.2.18
2026-10-24 08:30 UTC
```

(Times are UTC. Run by the AI assistant in its sandbox, **not** on your machine: please re-run the tests yourself and replace this section with your own output before submitting.)

## Command

```bash
python manage.py test -v 2
```

## Result: 112 tests, all passed (exit code 0)

> History note: the first run of the suite during this build had **4 failures**, all fixed before the run below:
> 1. `test_product_does_not_fit_in_one_dimension`: the test data was wrong (the item *could* rotate to fit); the engine was correct. Test fixed.
> 2. `test_blank_extra_rows_are_ignored`: showed a real UX flaw (the quantity input rendered `min="0"` and a cleared quantity on a blank row counted as a change). Fixed with an explicit `min_value=1` quantity field; the test now mimics a browser.
> 3. and 4. Two duplicate-product tests (form and view): showed that Django's generic "Please correct the duplicate data for product." fired before the friendlier message. Fixed by running the custom check first.
>
> The output below is the final run.

```
Found 112 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, sessions, warehouse
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
  Applying warehouse.0001_initial... OK
System check identified no issues (0 silenced).
test_duplicate_name_rejected (warehouse.tests.test_forms.BoxFormTests.test_duplicate_name_rejected) ... ok
test_negative_cost_is_invalid (warehouse.tests.test_forms.BoxFormTests.test_negative_cost_is_invalid) ... ok
test_non_positive_dimensions_and_capacity (warehouse.tests.test_forms.BoxFormTests.test_non_positive_dimensions_and_capacity) ... ok
test_valid_form (warehouse.tests.test_forms.BoxFormTests.test_valid_form) ... ok
test_zero_cost_is_valid (warehouse.tests.test_forms.BoxFormTests.test_zero_cost_is_valid) ... ok
test_at_least_one_item_is_required (warehouse.tests.test_forms.OrderItemFormSetTests.test_at_least_one_item_is_required) ... ok
test_duplicate_products_are_rejected_with_clear_message (warehouse.tests.test_forms.OrderItemFormSetTests.test_duplicate_products_are_rejected_with_clear_message) ... ok
test_invalid_quantities_are_rejected (warehouse.tests.test_forms.OrderItemFormSetTests.test_invalid_quantities_are_rejected) ... ok
test_quantity_input_has_min_1_in_html (warehouse.tests.test_forms.OrderItemFormSetTests.test_quantity_input_has_min_1_in_html) ... ok
test_unknown_product_is_rejected (warehouse.tests.test_forms.OrderItemFormSetTests.test_unknown_product_is_rejected) ... ok
test_untouched_extra_rows_are_ignored (warehouse.tests.test_forms.OrderItemFormSetTests.test_untouched_extra_rows_are_ignored) ... ok
test_valid_formset (warehouse.tests.test_forms.OrderItemFormSetTests.test_valid_formset) ... ok
test_non_numeric_and_missing_values (warehouse.tests.test_forms.ProductFormTests.test_non_numeric_and_missing_values) ... ok
test_non_positive_values_give_helpful_errors (warehouse.tests.test_forms.ProductFormTests.test_non_positive_values_give_helpful_errors) ... ok
test_required_fields (warehouse.tests.test_forms.ProductFormTests.test_required_fields) ... ok
test_sku_uniqueness_is_case_insensitive_via_normalisation (warehouse.tests.test_forms.ProductFormTests.test_sku_uniqueness_is_case_insensitive_via_normalisation) ... ok
test_valid_form_and_sku_normalisation (warehouse.tests.test_forms.ProductFormTests.test_valid_form_and_sku_normalisation) ... ok
test_box_name_must_be_unique (warehouse.tests.test_models.BoxModelTests.test_box_name_must_be_unique) ... ok
test_cost_uses_decimal_not_float (warehouse.tests.test_models.BoxModelTests.test_cost_uses_decimal_not_float) ... ok
test_database_rejects_negative_cost (warehouse.tests.test_models.BoxModelTests.test_database_rejects_negative_cost) ... ok
test_negative_cost_is_rejected (warehouse.tests.test_models.BoxModelTests.test_negative_cost_is_rejected) ... ok
test_non_positive_dimensions_and_capacity_are_rejected (warehouse.tests.test_models.BoxModelTests.test_non_positive_dimensions_and_capacity_are_rejected) ... ok
test_valid_box_passes_full_clean (warehouse.tests.test_models.BoxModelTests.test_valid_box_passes_full_clean) ... ok
test_zero_cost_is_allowed (warehouse.tests.test_models.BoxModelTests.test_zero_cost_is_allowed) ... ok
test_deleting_an_order_removes_its_items (warehouse.tests.test_models.OrderModelTests.test_deleting_an_order_removes_its_items) ... ok
test_order_item_line_weight (warehouse.tests.test_models.OrderModelTests.test_order_item_line_weight) ... ok
test_product_on_an_order_cannot_be_deleted (warehouse.tests.test_models.OrderModelTests.test_product_on_an_order_cannot_be_deleted) ... ok
test_quantity_changes_total_weight (warehouse.tests.test_models.OrderModelTests.test_quantity_changes_total_weight) ... ok
test_quantity_must_be_at_least_one (warehouse.tests.test_models.OrderModelTests.test_quantity_must_be_at_least_one) ... ok
test_recommend_box_for_empty_order_raises (warehouse.tests.test_models.OrderModelTests.test_recommend_box_for_empty_order_raises) ... ok
test_recommend_box_uses_database_boxes_cheapest_first (warehouse.tests.test_models.OrderModelTests.test_recommend_box_uses_database_boxes_cheapest_first) ... ok
test_recommend_box_with_no_boxes_configured (warehouse.tests.test_models.OrderModelTests.test_recommend_box_with_no_boxes_configured) ... ok
test_same_product_cannot_appear_twice_in_one_order (warehouse.tests.test_models.OrderModelTests.test_same_product_cannot_appear_twice_in_one_order) ... ok
test_str_includes_reference (warehouse.tests.test_models.OrderModelTests.test_str_includes_reference) ... ok
test_total_weight_and_units_across_multiple_products (warehouse.tests.test_models.OrderModelTests.test_total_weight_and_units_across_multiple_products) ... ok
test_database_rejects_invalid_row_even_without_full_clean (warehouse.tests.test_models.ProductModelTests.test_database_rejects_invalid_row_even_without_full_clean) ... ok
test_non_positive_dimensions_and_weight_fail_validation (warehouse.tests.test_models.ProductModelTests.test_non_positive_dimensions_and_weight_fail_validation) ... ok
test_sku_must_be_unique (warehouse.tests.test_models.ProductModelTests.test_sku_must_be_unique) ... ok
test_str_and_absolute_url (warehouse.tests.test_models.ProductModelTests.test_str_and_absolute_url) ... ok
test_to_spec_carries_quantity (warehouse.tests.test_models.ProductModelTests.test_to_spec_carries_quantity) ... ok
test_valid_product_passes_full_clean (warehouse.tests.test_models.ProductModelTests.test_valid_product_passes_full_clean) ... ok
test_create_valid_and_invalid (warehouse.tests.test_views.BoxViewTests.test_create_valid_and_invalid) ... ok
test_detail_update_delete (warehouse.tests.test_views.BoxViewTests.test_detail_update_delete) ... ok
test_list_empty_state (warehouse.tests.test_views.BoxViewTests.test_list_empty_state) ... ok
test_missing_box_returns_404 (warehouse.tests.test_views.BoxViewTests.test_missing_box_returns_404) ... ok
test_empty_state (warehouse.tests.test_views.DashboardViewTests.test_empty_state) ... ok
test_navigation_links_present (warehouse.tests.test_views.DashboardViewTests.test_navigation_links_present) ... ok
test_shows_counts_and_recent_orders (warehouse.tests.test_views.DashboardViewTests.test_shows_counts_and_recent_orders) ... ok
test_duplicate_product_is_rejected (warehouse.tests.test_views.OrderCreateViewTests.test_duplicate_product_is_rejected) ... ok
test_empty_order_is_rejected (warehouse.tests.test_views.OrderCreateViewTests.test_empty_order_is_rejected) ... ok
test_get_renders_formset (warehouse.tests.test_views.OrderCreateViewTests.test_get_renders_formset) ... ok
test_get_without_products_shows_empty_state (warehouse.tests.test_views.OrderCreateViewTests.test_get_without_products_shows_empty_state) ... ok
test_invalid_quantity_creates_nothing (warehouse.tests.test_views.OrderCreateViewTests.test_invalid_quantity_creates_nothing) ... ok
test_valid_order_is_created_with_items (warehouse.tests.test_views.OrderCreateViewTests.test_valid_order_is_created_with_items) ... ok
test_delete_order (warehouse.tests.test_views.OrderDetailAndListTests.test_delete_order) ... ok
test_detail_shows_products_quantities_and_total_weight (warehouse.tests.test_views.OrderDetailAndListTests.test_detail_shows_products_quantities_and_total_weight) ... ok
test_list_empty_state (warehouse.tests.test_views.OrderDetailAndListTests.test_list_empty_state) ... ok
test_list_shows_orders (warehouse.tests.test_views.OrderDetailAndListTests.test_list_shows_orders) ... ok
test_missing_order_returns_404 (warehouse.tests.test_views.OrderDetailAndListTests.test_missing_order_returns_404) ... ok
test_create_get_renders_form (warehouse.tests.test_views.ProductViewTests.test_create_get_renders_form) ... ok
test_create_post_invalid_shows_errors_and_saves_nothing (warehouse.tests.test_views.ProductViewTests.test_create_post_invalid_shows_errors_and_saves_nothing) ... ok
test_create_post_valid (warehouse.tests.test_views.ProductViewTests.test_create_post_valid) ... ok
test_detail_update_and_delete (warehouse.tests.test_views.ProductViewTests.test_detail_update_and_delete) ... ok
test_list_empty_state (warehouse.tests.test_views.ProductViewTests.test_list_empty_state) ... ok
test_list_shows_products (warehouse.tests.test_views.ProductViewTests.test_list_shows_products) ... ok
test_missing_product_returns_404 (warehouse.tests.test_views.ProductViewTests.test_missing_product_returns_404) ... ok
test_product_used_by_an_order_is_not_deleted (warehouse.tests.test_views.ProductViewTests.test_product_used_by_an_order_is_not_deleted) ... ok
test_always_shows_the_limitation_disclaimer (warehouse.tests.test_views.RecommendationViewTests.test_always_shows_the_limitation_disclaimer) ... ok
test_empty_order_is_handled_without_error (warehouse.tests.test_views.RecommendationViewTests.test_empty_order_is_handled_without_error) ... ok
test_no_boxes_configured_message (warehouse.tests.test_views.RecommendationViewTests.test_no_boxes_configured_message) ... ok
test_no_eligible_box_shows_clear_explanation (warehouse.tests.test_views.RecommendationViewTests.test_no_eligible_box_shows_clear_explanation) ... ok
test_shows_cheapest_eligible_box_and_all_eligible_boxes (warehouse.tests.test_views.RecommendationViewTests.test_shows_cheapest_eligible_box_and_all_eligible_boxes) ... ok
test_weight_rejection_is_explained (warehouse.tests.test_views.RecommendationViewTests.test_weight_rejection_is_explained) ... ok
test_delete_requires_post (warehouse.tests.test_views.SecurityTests.test_delete_requires_post) ... ok
test_post_without_csrf_token_is_forbidden (warehouse.tests.test_views.SecurityTests.test_post_without_csrf_token_is_forbidden) ... ok
test_all_six_permutations_are_tested (warehouse.tests.test_service.FitsInBoxTests.test_all_six_permutations_are_tested) ... ok
test_every_orientation_of_the_item_fits_a_matching_box (warehouse.tests.test_service.FitsInBoxTests.test_every_orientation_of_the_item_fits_a_matching_box) ... ok
test_item_too_large_in_all_orientations (warehouse.tests.test_service.FitsInBoxTests.test_item_too_large_in_all_orientations) ... ok
test_product_does_not_fit_in_one_dimension (warehouse.tests.test_service.FitsInBoxTests.test_product_does_not_fit_in_one_dimension) ... ok
test_product_fits_in_exact_dimensions (warehouse.tests.test_service.FitsInBoxTests.test_product_fits_in_exact_dimensions) ... ok
test_rotation_allows_a_valid_fit (warehouse.tests.test_service.FitsInBoxTests.test_rotation_allows_a_valid_fit) ... ok
test_empty_order_is_rejected (warehouse.tests.test_service.InvalidInputTests.test_empty_order_is_rejected) ... ok
test_invalid_box_values (warehouse.tests.test_service.InvalidInputTests.test_invalid_box_values) ... ok
test_invalid_product_dimensions_and_weight (warehouse.tests.test_service.InvalidInputTests.test_invalid_product_dimensions_and_weight) ... ok
test_invalid_quantities (warehouse.tests.test_service.InvalidInputTests.test_invalid_quantities) ... ok
test_missing_box_entry_is_rejected (warehouse.tests.test_service.InvalidInputTests.test_missing_box_entry_is_rejected) ... ok
test_missing_order_is_rejected (warehouse.tests.test_service.InvalidInputTests.test_missing_order_is_rejected) ... ok
test_missing_product_entry_is_rejected (warehouse.tests.test_service.InvalidInputTests.test_missing_product_entry_is_rejected) ... ok
test_numeric_strings_and_floats_are_coerced_to_decimal (warehouse.tests.test_service.InvalidInputTests.test_numeric_strings_and_floats_are_coerced_to_decimal) ... ok
test_product_name_is_required (warehouse.tests.test_service.InvalidInputTests.test_product_name_is_required) ... ok
test_zero_cost_box_is_valid (warehouse.tests.test_service.InvalidInputTests.test_zero_cost_box_is_valid) ... ok
test_all_failure_reasons_are_reported (warehouse.tests.test_service.RecommendationTests.test_all_failure_reasons_are_reported) ... ok
test_basic_valid_recommendation (warehouse.tests.test_service.RecommendationTests.test_basic_valid_recommendation) ... ok
test_boxes_are_sorted_by_cost_cheapest_first (warehouse.tests.test_service.RecommendationTests.test_boxes_are_sorted_by_cost_cheapest_first) ... ok
test_cheapest_box_is_skipped_when_it_is_too_small (warehouse.tests.test_service.RecommendationTests.test_cheapest_box_is_skipped_when_it_is_too_small) ... ok
test_cheapest_eligible_box_is_selected (warehouse.tests.test_service.RecommendationTests.test_cheapest_eligible_box_is_selected) ... ok
test_equal_cost_ties_prefer_smaller_volume_then_name (warehouse.tests.test_service.RecommendationTests.test_equal_cost_ties_prefer_smaller_volume_then_name) ... ok
test_every_product_in_a_multi_product_order_is_checked (warehouse.tests.test_service.RecommendationTests.test_every_product_in_a_multi_product_order_is_checked) ... ok
test_exact_decimal_weight_match_is_not_broken_by_float_error (warehouse.tests.test_service.RecommendationTests.test_exact_decimal_weight_match_is_not_broken_by_float_error) ... ok
test_known_limitation_passing_checks_is_not_a_packing_guarantee (warehouse.tests.test_service.RecommendationTests.test_known_limitation_passing_checks_is_not_a_packing_guarantee)
Documents the simplification: two 6-cubes cannot really fit a 10x10x6 box. ... ok
test_multi_product_weights_are_combined_against_capacity (warehouse.tests.test_service.RecommendationTests.test_multi_product_weights_are_combined_against_capacity) ... ok
test_no_boxes_configured (warehouse.tests.test_service.RecommendationTests.test_no_boxes_configured) ... ok
test_no_eligible_box_returns_explanation_not_a_box (warehouse.tests.test_service.RecommendationTests.test_no_eligible_box_returns_explanation_not_a_box) ... ok
test_quantity_can_push_an_order_over_capacity (warehouse.tests.test_service.RecommendationTests.test_quantity_can_push_an_order_over_capacity) ... ok
test_result_always_carries_the_disclaimer (warehouse.tests.test_service.RecommendationTests.test_result_always_carries_the_disclaimer) ... ok
test_volume_check_rejects_boxes_that_can_never_hold_the_order (warehouse.tests.test_service.RecommendationTests.test_volume_check_rejects_boxes_that_can_never_hold_the_order) ... ok
test_weight_exactly_equal_to_capacity_is_allowed (warehouse.tests.test_service.RecommendationTests.test_weight_exactly_equal_to_capacity_is_allowed) ... ok
test_weight_exceeding_capacity_is_rejected (warehouse.tests.test_service.RecommendationTests.test_weight_exceeding_capacity_is_rejected) ... ok
test_decimal_arithmetic_is_exact (warehouse.tests.test_service.TotalWeightTests.test_decimal_arithmetic_is_exact) ... ok
test_empty_list_weighs_zero (warehouse.tests.test_service.TotalWeightTests.test_empty_list_weighs_zero) ... ok
test_multiple_products_are_summed (warehouse.tests.test_service.TotalWeightTests.test_multiple_products_are_summed) ... ok
test_quantity_changes_total_weight (warehouse.tests.test_service.TotalWeightTests.test_quantity_changes_total_weight) ... ok

----------------------------------------------------------------------
Ran 112 tests in 0.278s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

## Additional checks run

```
$ python manage.py check
System check identified no issues (0 silenced).

$ python manage.py makemigrations --check --dry-run
No changes detected
```

A dev-server smoke test (`runserver`, then `curl`) returned HTTP 200 for `/`, `/products/`, `/boxes/`, `/orders/`, `/products/new/`, `/boxes/new/`, `/orders/new/` and the CSS file, and 404 for the non-existent `/products/999/`. `check --deploy` with production-style environment variables reported only the two optional HSTS warnings described in the README.

## How to reproduce on your machine

```bash
source .venv/bin/activate
python manage.py test -v 2 2>&1 | tee my_test_output.txt
```

Then paste the contents of `my_test_output.txt` into the "Result" block above (and update the environment block).
