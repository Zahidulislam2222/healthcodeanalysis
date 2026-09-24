# Revision brief — Neural Frontier

The previous Evidence Atlas implementation was rejected by the owner. Functional tests did not establish visual acceptance. Its principal defects were a generic journal composition, a weak metaphor, minimal motion, and insufficient use of the supplied creative references.

## Directions compared

1. Refine the ivory editorial page: rejected because it preserves the composition the owner disliked.
2. Full-screen speculative diagnostic dashboard: rejected because HealthCode is a publication and toolbox, not a working clinical AI product.
3. Cinematic medical-technology publication: selected. A neural sculpture and a short camera sequence introduce the medicine/technology relationship, then give way to actual articles, technology reviews, and tools.

## Observable revision criteria

- Replace the existing hero composition and metaphor, rather than recolor it.
- Build a cinematic opening with expressive sans-serif typography and substantial original imagery.
- Give scroll progress a visible role: camera/frame progress, staged section handoff, and layered review cards.
- Keep the real collection, search, reading list, and six working tools directly reachable.
- Compose mobile separately; keep motion optional and core content readable when media fails.
- Inspect actual opening, intermediate, and ending frames and the full rendered page before visual acceptance.
- Clearly distinguish a rough local composition prototype from finished generated media.
- Keep all work local; no deployment.

## Reference application

The supplied playbook's sections 2, 4B, 5A–5C, and 9 describe early motion prototyping, a shot plan, reviewed generated assets, and a metered spending gate. Scroll Craft's uniqueness reference explicitly warns that changing imagery within the same page structure is a reskin. Scroll World's useful contribution is continuous camera progress with exact endpoint handling. Its DOM-generating runtime will not be copied wholesale into this publication.

## Art specification

Palette: near-black graphite, chalk white, electric mint used for active elements, copper light in the sculpture. Typography: tightly set geometric sans-serif display, plain readable body text, compact technical annotations. No simulated patient outcomes, diagnostic confidence percentages, or invented medical apparatus labels.

Opening composition: large headline occupies the left half; a detailed neural sculpture enters through the right and slightly overlaps the visual field. The object is tangible, layered, and dramatically lit. A compact edition block and genuine featured-story link establish that this is a publication.

Shot beats: identify the neural form → move closer into its luminous pathways → pull outward toward a connected research field. On mobile, the object sits above a compact title with readable actions; the desktop widescreen film is not blindly cropped behind text.

## Paid pilot prompt — image

Create a cinematic scientific art photograph for a medical AI publication called HealthCode Analysis. One anatomically recognizable but explicitly illustrative human brain, suspended in a near-black graphite studio, three-quarter lateral view. Highly detailed organic cortical folds constructed from pale titanium tissue-like strands and translucent optical fibers; sparse mint-colored light travels through fine internal pathways. Copper rim lighting from the upper right, cool white softbox from the left, convincing shadows and volumetric depth. Premium scientific visualization, tangible material detail, macro lens clarity, subtle natural imperfections. The brain occupies the right 55 percent of a wide 16:9 frame, with the left 45 percent clean near-black negative space for a large HTML headline. Keep the complete silhouette visible and leave breathing room around it. No text, symbols, interface panels, numbers, logos, neon city, stock medical icons, circuit-board globe, floating glass plates, fake data, or cartoon styling. This is editorial illustration, not a diagnostic image.

## Paid pilot prompt — video

Use the approved neural illustration as the first-frame reference. Eight seconds, 16:9, 720p, no audio. A single deliberate scientific camera shot. Seconds 0–2: a very slow clockwise camera orbit around the suspended titanium-and-optical-fiber brain, preserving its recognizable shape and the dark studio. Seconds 2–5: a controlled dolly toward the cortical surface, revealing fine illuminated pathways without changing the object's anatomy or inventing text. Seconds 5–8: a gentle pullback settles into a three-quarter view with the sculpture on the right and clear negative space on the left. Copper rim light and sparse mint pathway illumination remain consistent. No cuts, no flashes, no additional objects, no readable text, no medical claims, no morphing into a different object. Stable camera, consistent studio, no audio.

The image must be inspected before submitting the video. A rejected image does not automatically authorize paid retries. First-frame conditioning does not guarantee the precise camera path; the resulting clip must be reviewed.

## Hero refinement — acceptance criteria (before implementation)

Owner accepts the overall direction but finds the hero weak. Working assumption pending feedback: composition is the primary issue.

1. Clearly balanced headline/artwork at 1440×1000 and 1280×720; primary actions visible in the first viewport.
2. Intentional headline line breaks and publication-specific copy; artwork no longer overwhelms the text.
3. Shorter native scroll sequence, forward/reverse seeking and pause preserved; caption enters after the close-up.
4. Mobile composition at 390px and 320px has readable actions, no overlap/overflow; reduced motion and failed media remain usable.
5. Only hero styling/content changes; existing navigation, content and tools preserved. No additional paid generation or deployment.

## Wide-screen balance and deployment acceptance

1. At the supplied1903×905 viewport, constrain artwork within the centered page frame and leave breathing room on the right; preserve the brain.
2. Slow the film modestly by increasing sequence from175svh to200svh; native scroll and motion controls remain functional.
3. Build and exercise all routes/tools locally; configure canonical origin for healthcodeanalysis.zahidul-islam.com.
4. Deploy isolated versioned static release to existing VPS, loopback-only binding, with nginx/Caddy native validation and origin/public TLS,404,range and application-flow checks.
5. Prove all release file hashes match local; record previous/absent DNS/site state, rollback and restore evidence; keep checkpoints, dossier, credentials and shared ownership registry current.
