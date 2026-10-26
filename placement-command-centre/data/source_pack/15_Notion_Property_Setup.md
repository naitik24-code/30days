# Notion property setup notes

After importing CSVs, Notion may import every column as Text. Change types where useful:

- `Master Question Tracker`: `No.` → Number; `Confidence (1–5)` → Number; `Revisit?` → Checkbox; `Status` → Status or Select.
- `Project Upgrade Board`: `Priority` and `Status` → Select; add a Date property if you assign deadlines.
- `Job Application Tracker`: `Date applied` and `Follow-up date` → Date; `Job URL` → URL; `Status` → Status or Select.
- `Daily Scorecard`: numeric counts/percentages/hours/energy → Number; day stays Number.
- `Spaced Revision Tracker`: review columns and `Next review date` → Date; recall/explain fields → Checkbox or Select.
- `Interview Question Bank`: confidence → Number; practice status → Status.

Recommended select options:
- Status: Not Started, In Progress, Blocked, Done, Review
- Priority: P0, P1, P2
- Application status: To Apply, Applied, Referral Requested, Assessment, Interview, Rejected, Offer, Follow-up

Notion's CSV import does not automatically recreate Excel formulas, dropdown validation, or relationships. Configure those after import if needed.
