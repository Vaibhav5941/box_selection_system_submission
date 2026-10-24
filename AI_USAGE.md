# AI Usage Record

## 1. AI tools actually used

| Tool / model | Version or date used | What I used it for |
|---|---|---|
| ChatGPT (OpenAI) | October 2026; exact model version not recorded here | Getting help with the Django box selection assignment, project requirements, README documentation, GitHub commands and reviewing the test results. |

## 2. Actual prompts

The original prompts are available in my ChatGPT conversation. I will preserve the original conversation separately as required by the assignment.

The main prompts I used included:

1. **Project development:** "You are a senior Python/Django engineer acting as my coding mentor. Build a complete, professional, runnable Django project for the following hiring assignment: AI-Assisted Box Selection System..." The full prompt included the required features, validation rules, recommendation algorithm, tests, documentation and submission requirements. The complete original prompt should be retained from the conversation rather than reconstructed from this summary.

2. **README improvement:** "reami acha nhi h tum sahi karo usse" followed by my existing README content. I asked for the documentation to be reorganised and made easier to read.

3. **AI usage documentation:** "ab isko fill karne me help karo matlab todo ki jgha kya likho kha se nikau ye sab btao" followed by my AI usage template.

4. **GitHub troubleshooting:** I shared my PowerShell output showing the successful GitHub push and the `remote origin already exists` message, and asked for further guidance through the conversation.

## 3. Suggestions accepted

The following items are reflected in the project requirements and test coverage. I checked the corresponding test names in the terminal output; I should also compare the implementation with the original code-generation suggestions before treating every item as an accepted AI suggestion.

| Suggestion or requirement | Where in the project | Why it is useful |
|---|---|---|
| Keep the recommendation logic separate from the Django views. | `warehouse/services/box_recommendation.py` | Separating business logic makes it easier to test and maintain. |
| Check product rotation and box weight capacity. | Recommendation service and `warehouse/tests/test_service.py` | These checks are important for rejecting unsuitable boxes. |
| Use automated tests for validation, orders and recommendation results. | `warehouse/tests/` | Tests help catch regressions and verify expected behaviour. |
| Document the limitations of simplified box selection. | `README.md` and recommendation tests | Individual fit and volume checks do not guarantee that all products can be packed together. |
| Improve the README's organisation and setup instructions. | `README.md`, if the revised version has been saved | Clear instructions make the project easier for another developer to run and review. |

## 4. Suggestions rejected or modified

I have not yet documented a specific rejected code suggestion. I need to compare the original AI output with my final implementation before recording a concrete example.

I also revised the README content during the conversation. I will describe any specific changes as rejected or modified suggestions only after checking which changes I actually kept in the final file.

## 5. Mistakes identified

I have not yet confirmed a specific defect in the generated application code.

The automated test run completed successfully, but passing tests do not prove that every possible input or real-world packing arrangement is handled correctly. I will record any additional mistakes only after identifying them in the code or reproducing them during testing.

## 6. How I verified important behaviour

I ran the following command in PowerShell from the project directory:

`python manage.py test -v 2`

The terminal reported that Django found 112 tests, the system check identified no issues, all 112 tests completed successfully, and the final result was `OK`.

| Behaviour | How I verified it | Result |
|---|---|---|
| Cheapest eligible box is recommended | `warehouse.tests.test_service.RecommendationTests.test_cheapest_eligible_box_is_selected` and the other recommendation tests ran as part of the full test suite. | Passed |
| Rotation | Service tests covering all six permutations and rotation-based fitting ran. | Passed |
| Weight capacity boundary | Tests for exact capacity and exceeding capacity ran. | Passed |
| Quantity affects total weight | Service and model tests for quantity-dependent weight ran. | Passed |
| No eligible box produces an explanation | Service and recommendation view tests ran. | Passed |
| Empty order and invalid quantity | Service, form and view tests for these cases ran. | Passed |
| Form and model validation | Product, box, order-item and model validation tests ran. | Passed |
| Multi-product limitation | The test `test_known_limitation_passing_checks_is_not_a_packing_guarantee` ran successfully. I also need to be able to explain the limitation in my own words. | Test passed; limitation documented |

### Test run details

- Command: `python manage.py test -v 2`
- Tests discovered: 112
- Execution time: 0.680 seconds
- Django system check: No issues identified
- Final test result: `OK`

These results reflect the terminal output from my test run. I will update this record if I change the code and run the tests again.