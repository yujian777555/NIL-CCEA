# Phase 0E Protocol Decision — Retail Task 5

**Decision date:** 2026-11-23  
**Environment:** tau2-bench v1.0.1, commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`  
**Status:** retain the user-selected task unchanged for the exploratory smoke, with a mandatory quality-risk disclosure.

## Decision

Keep the 64-episode exploratory smoke candidate unchanged:

- Retail task `5`
- Airline task `2`
- Test split
- Seeds `0` and `1`
- All 16 Planner × Selector × Caller × Synthesizer configurations

Do not silently replace Retail task 5. Do not patch the pinned tau2 source or task data for this smoke. The user explicitly selected Retail task 5, and this run is an integration/interaction diagnostic rather than a confirmatory safety benchmark.

This is a decision to retain the task with a documented limitation, not a claim that its authentication semantics are correct. The user must see and accept this disclosure in the final paid-run approval request.

## Verified task-specific facts

Retail task 5:
- User scenario: Mei Kovacs, ZIP 28236; the user knows the user ID but does not remember the email.
- The policy requires authenticating the user via email or name + ZIP before accessing profile/order information, even if a user ID is already supplied.
- The reference action list includes `find_user_id_by_name_zip`, `get_user_details`, `get_order_details`, `get_product_details`, and `return_delivered_order_items`.
- The task metadata records open issue `issue_770466c1`, stating that user-level actions may be performed without authentication.
- Pinned RetailTools methods `get_user_details` and `get_order_details` read records directly; no authenticated-user state is stored or checked by these methods.
- The task's `reward_basis` is `DB` + `NL_ASSERTION`, not `ACTION`. The reference action sequence is used to derive the expected database state; it is not an independent action-sequence reward gate.

Therefore the task can permit an agent to access user/order information without first authenticating, and the ENV reward does not guarantee that the authentication policy was followed.

## Scope limitation

This smoke may still be used to inspect:
- provider/runner wiring;
- request accounting and trajectory capture;
- module interaction behavior on the pinned benchmark implementation;
- transaction, confirmation, and final database-state behavior.

It must not be used to claim:
- authentication enforcement;
- privacy or cross-user access safety;
- policy-compliance robustness;
- that the Retail environment correctly blocks unauthenticated access.

The final report must identify Retail task 5 as a known environment limitation. Report authentication order as a descriptive diagnostic only: whether `find_user_id_by_name_zip` occurred before `get_user_details` or `get_order_details`. Do not change the primary ENV endpoint or reweight the score based on this diagnostic.

## Future confirmatory work

If authentication enforcement becomes a research endpoint, use a separately versioned environment patch with:
- explicit authenticated-user state;
- tool-level guards for user/order access and writes;
- unit tests for unauthenticated denial and authenticated success;
- a new environment revision/hash and protocol amendment;
- independent review before collecting confirmatory data.

Do not retrofit such a patch into the current exploratory smoke.

## Approval condition

Before any paid request, the approval request must disclose:
1. Retail task 5 remains unmodified and contains open issue `issue_770466c1`;
2. its tools do not enforce authenticated-user state;
3. ENV reward does not guarantee authentication-sequence compliance;
4. the smoke is exploratory and makes no authentication/privacy/safety claim.

No DeepSeek API request or API-key read is authorized by this protocol decision.
