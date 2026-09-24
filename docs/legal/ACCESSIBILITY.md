# Accessibility statement

**Target:** WCAG 2.2 Level AA. **Current status:** partially assessed. No formal conformance claim is made.

## What has been implemented and tested

Automated and scripted browser checks exercised:

- Keyboard navigation with a visible focus indicator and a skip link.
- The search dialog: Escape closes it and focus returns to the trigger.
- A responsive navigation menu that works at 390 px and 320 px widths.
- Reduced-motion preference: the hero shows a still illustration and the film is not requested.
- A pause/resume control for motion.
- A readable fallback when media fails to load.
- Hidden duplicate image links removed from the tab order.
- Long URLs wrap instead of being clipped on narrow screens.
- Clear feedback when browser storage is blocked.

These are engineering checks (11 motion/accessibility states and 13 interaction scenarios), **not** a full WCAG audit.

## Known limitations

- No manual screen-reader testing (NVDA, JAWS, VoiceOver, TalkBack) has been recorded.
- No testing on physical mobile devices or non-Chromium browsers has been recorded.
- Imported demonstration articles may contain images without meaningful alternative text.
- Colour contrast of every imported content block has not been audited.

## Roadmap

1. Automated audit (axe-core or equivalent) of all 63 routes, with issues logged.
2. Manual keyboard and screen-reader pass on key journeys: home, library search, article, tools, reading list.
3. Contrast audit of the design tokens and imported content.
4. Alternative-text review during editorial verification.
5. Publish the results and a remediation timeline.

## Feedback

`[OPERATOR ACCESSIBILITY CONTACT — required before commercial launch]`. For the demonstration, open an issue using the repository's issue tracker.

Legal context: the ADA (per DOJ web guidance), and the European Accessibility Act for covered services. See [COMPLIANCE-REGISTER.md](COMPLIANCE-REGISTER.md).
