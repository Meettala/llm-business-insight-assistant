## Summary

Describe the change and the user or developer problem it solves.

## Validation

- [ ] `python -m pytest tests/ -q`
- [ ] New or changed behavior is covered by tests
- [ ] Documentation is updated

## Safety review

- [ ] The change preserves `QuerySpec` validation
- [ ] No arbitrary code, SQL, or pandas expression execution was introduced
- [ ] Uploaded data and model output remain untrusted inputs
- [ ] No secrets or private datasets are included

## Screenshots

Add screenshots for user-interface changes, or write “Not applicable.”

## Notes

Describe compatibility considerations, limitations, or follow-up work.
