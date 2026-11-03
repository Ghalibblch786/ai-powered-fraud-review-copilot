# Card-Not-Present Fraud

## What it is
Card-not-present (CNP) fraud happens when stolen card details are used without the physical card — most commonly online — making it harder to verify that the person transacting is actually the account holder. Because the fraudster is working from stolen numbers rather than familiarity with the account, their purchases often don't match the size or shape of the real owner's normal spending.

## How it typically shows up
A fraudster using stolen card details usually isn't shopping the way the real cardholder would. Unconstrained by the account owner's actual habits or budget, they tend to make purchases that are noticeably larger than what that customer typically spends — either testing how much the card will allow before it's declined, or simply trying to extract as much value as possible before the compromise is detected. This commonly surfaces as a transaction amount well outside the customer's established spending range, sometimes as a single outsized purchase with nothing building up to it.

## Evidence signals
- Transaction amount significantly above the customer's typical spending range
- A one-off large purchase with no smaller, related purchases around it suggesting a genuine gradual buildup
- A purchase size inconsistent with the account's established spending habits, even if the merchant itself looks ordinary
- The amount alone being the primary anomaly, without other context (like travel) that would otherwise explain it

## Innocent explanations
- Most people make an occasional large planned purchase, such as electronics, a travel booking, or a medical bill.
- A customer's typical spending range is an estimate, so an amount a little above it is a gray area, not a strong signal.
- A large amount in a category where big purchases are normal (travel, electronics) is easier to explain than one in a category where they are not (groceries, dining).

## What to check
- How far above the customer's typical maximum the amount is. As a rough guide: up to about twice the maximum is a gray area; several times the maximum is strongly unusual.
- Whether the merchant category fits a large purchase.
- The merchant's risk tier.
- The location compared with the customer's home location.
- The account's age.
- Any other purchases close in time.

## How to decide
- Lean **escalate** when the amount is several times the customer's typical maximum. **A low-risk merchant does not cancel out a very large amount.**
- Lean **escalate** when the amount is moderately above the range and comes with another warning sign: a different location, a high-risk merchant, a burst of purchases, or a very new account.
- Lean **clear** when the amount is only moderately above the range, in a category that fits, at the home location, on an established account, at a low- or medium-risk merchant.
- Describe evidence as "consistent with" a pattern. Never state that fraud happened; the analyst makes the final decision.
